#!/usr/bin/env python3
"""Run the source preferences UI with an optional installed Windows runtime."""
import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--runtime', type=Path, help='Installed PrintViewPDF directory, containing python/gtk/poppler')
parser.add_argument('--profile', type=Path, default=ROOT / '.runtime/preferences-preview',
                    help='Separate profile; never changes your normal reader preferences')
parser.add_argument('--screenshot', type=Path)
parser.add_argument('--page', choices=['appearance', 'interface', 'reading', 'search'], default='appearance')
parser.add_argument('--tests', choices=['preferences', 'all'])
parser.add_argument('--test-name', help='Optional unittest module or case for a focused rerun')
parser.add_argument('--test-report', type=Path, help='Write execution results and source hashes as JSON')
parser.add_argument('--close-after-capture', action='store_true')
args = parser.parse_args()
profile = args.profile.resolve()
profile.mkdir(parents=True, exist_ok=True)
os.environ['XDG_CONFIG_HOME'] = str(profile / 'config')
os.environ['XDG_CACHE_HOME'] = str(profile / 'cache')
os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.path.insert(0, str(ROOT / 'app'))
handles = []
if os.name == 'nt' and args.runtime:
    runtime = args.runtime.resolve()
    gtk, poppler = runtime / 'gtk', runtime / 'poppler'
    for folder in (gtk / 'bin', poppler / 'bin'):
        handles.append(os.add_dll_directory(str(folder)))
    os.environ['PATH'] = os.pathsep.join([str(gtk / 'bin'), str(poppler / 'bin'), os.environ.get('PATH', '')])
    os.environ['GI_TYPELIB_PATH'] = str(gtk / 'lib/girepository-1.0')
    os.environ['GSETTINGS_SCHEMA_DIR'] = str(gtk / 'share/glib-2.0/schemas')
    os.environ['XDG_DATA_DIRS'] = os.pathsep.join([str(ROOT / 'assets'), str(runtime / 'share'), str(gtk / 'share')])
    cache = profile / 'cache'; cache.mkdir(exist_ok=True)
    loader = gtk / 'lib/gdk-pixbuf-2.0/2.10.0/loaders.cache'
    if loader.is_file():
        lines = []
        for line in loader.read_text(encoding='utf-8').splitlines():
            if line.startswith('"lib') and line.endswith('.dll"'):
                relative = line[1:-1].replace('\\\\', '\\')
                line = '"' + (gtk / relative).as_posix() + '"'
            lines.append(line)
        relocated = cache / 'pixbuf-loaders.cache'
        relocated.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        os.environ['GDK_PIXBUF_MODULE_FILE'] = str(relocated)

# Load GTK before Cairo/Poppler consumers to avoid Windows DLL-name collisions
# in test discovery (the reader's normal main module also imports GTK first).
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

if args.tests:
    import unittest
    if os.name == 'nt' and args.runtime:
        # A -c child has no bootstrap script. Give it the same private runtime
        # DLL search path, without modifying the installed interpreter or user config.
        bootstrap = profile / 'native-test-bootstrap'
        bootstrap.mkdir(exist_ok=True)
        (bootstrap / 'sitecustomize.py').write_text(
            "import os\nfrom pathlib import Path\n"
            "_r = Path(os.environ['PRINT_VIEW_NATIVE_RUNTIME'])\n"
            "_dll_handles = [os.add_dll_directory(str(_r / 'gtk' / 'bin'))]\n",
            encoding='utf-8')
        os.environ['PRINT_VIEW_NATIVE_RUNTIME'] = str(args.runtime.resolve())
        os.environ['PYTHONPATH'] = os.pathsep.join(filter(None, [str(bootstrap), os.environ.get('PYTHONPATH', '')]))

    # Existing GUI tests use DISPLAY as their availability gate. On native
    # Windows GTK uses Win32, so allow these same tests without an X server.
    if os.name == 'nt':
        os.environ['DISPLAY'] = 'native-win32-test-session'
    pattern = 'test_preferences*.py' if args.tests == 'preferences' else 'test_*.py'
    sys.path.insert(0, str(ROOT / 'tests'))
    suite = (unittest.defaultTestLoader.loadTestsFromName(args.test_name) if args.test_name else
             unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern=pattern))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if args.test_report:
        import hashlib, json
        args.test_report.parent.mkdir(parents=True, exist_ok=True)
        report = {
            'date': '2026-10-30', 'environment': 'native Windows GTK 3' if os.name == 'nt' else sys.platform,
            'python': sys.version, 'runtime': str(args.runtime) if args.runtime else None,
            'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
            'skipped': len(result.skipped), 'passed': result.wasSuccessful(),
            'failure_details': [{'test': test.id(), 'traceback': trace} for test, trace in result.failures + result.errors],
            'source_sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in sorted((ROOT / 'app').glob('*.py'))},
        }
        args.test_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)

from main import PDFWindow, load_css, Gtk, GLib, Gdk
load_css()
window = PDFWindow()
window._open_preferences()
dialog = window.preferences_dialog
dialog.stack.set_visible_child_name(args.page)

if args.screenshot:
    def capture():
        native = dialog.get_window()
        if native is None or not dialog.get_mapped():
            return True
        args.screenshot.parent.mkdir(parents=True, exist_ok=True)
        width, height = native.get_width(), native.get_height()
        # Render the actual GTK widgets, independent of desktop occlusion or
        # remote-session screen capture returning a solid black bitmap.
        import cairo
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        dialog.draw(cairo.Context(surface))
        surface.write_to_png(str(args.screenshot))
        from PIL import Image
        with Image.open(args.screenshot) as image:
            if len(image.convert('RGB').getcolors(1_000_000) or []) < 10:
                raise RuntimeError('Preferences image is blank; visual QA required')
        print(str(args.screenshot), flush=True)
        if args.close_after_capture:
            window.destroy()
        return False
    GLib.timeout_add(1000, capture)
Gtk.main()
