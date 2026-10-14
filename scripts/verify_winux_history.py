import atexit
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

# Audit checks for the original Winux 3.3.11 source, not the current app/.
# Isolate appearance settings from the user's desktop preferences.
_check_config = tempfile.TemporaryDirectory(prefix='winux-history-checks-')
atexit.register(_check_config.cleanup)
os.environ['XDG_CONFIG_HOME'] = str(Path(_check_config.name) / 'config')
if not os.environ.get('WINUX_HISTORY_APP'):
    raise SystemExit('Set WINUX_HISTORY_APP to an extracted Winux 3.3.11 source directory.')
if not os.environ.get('DISPLAY'):
    raise SystemExit('A usable DISPLAY is required; no GUI checks may be silently skipped.')
APP = Path(os.environ['WINUX_HISTORY_APP']).resolve()
if not (APP / 'cancel_state.py').is_file():
    raise SystemExit('Winux 3.3.11 modules were not found at WINUX_HISTORY_APP.')
sys.path.insert(0, str(APP))
import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import rendering
import imposition
import cups_backend
import cancel_state
import appearance
from main import PDFWindow, load_css
from presentation import PresentationWindow
from print_window import PrintWindow
from pypdf import PdfReader


def make_pdf(path, texts):
    surface = cairo.PDFSurface(str(path), 420, 595)
    cr = cairo.Context(surface)
    cr.select_font_face('DejaVu Sans')
    cr.set_font_size(16)
    for text in texts:
        for row, line in enumerate(text.split('\n')):
            cr.move_to(40, 60 + row * 28)
            cr.show_text(line)
        cr.show_page()
    surface.finish()


def wait_for(predicate, timeout=15):
    until = time.monotonic() + timeout
    while time.monotonic() < until:
        context = GLib.MainContext.default()
        for _ in range(100):
            if not context.pending():
                break
            context.iteration(False)
        if predicate():
            return
        time.sleep(.02)
    raise AssertionError('GTK readiness timeout')


class HistoryChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pdf = self.root / 'sample.pdf'
        make_pdf(self.pdf, ['ação ação\nAÇÃO ações'] + [f'PAGE{i}' for i in range(2, 9)])
        self.windows = []
        self.quit_patch = patch.object(Gtk, 'main_quit')
        self.quit_patch.start()

    def tearDown(self):
        for window in reversed(self.windows):
            window.destroy()
        self.quit_patch.stop()
        self.temp.cleanup()

    def reader(self):
        # Explicit mode avoids the separate system-mode defect checked below.
        appearance.save_mode('light')
        load_css()
        window = PDFWindow()
        self.windows.append(window)
        errors = []
        window._error = errors.append
        window.open_document(str(self.pdf))
        wait_for(lambda: window.page_count == 8 and window.current_pixbuf is not None)
        self.assertEqual(errors, [])
        return window

    def test_search_occurrences_case_and_whole_words(self):
        hits = rendering.search_text(str(self.pdf), 'ação', whole_words=True)
        self.assertEqual(len(hits), 3)
        self.assertNotEqual(hits[0]['rects'], hits[1]['rects'])
        self.assertTrue(all(hit['snippet'] and hit['width'] and hit['height'] for hit in hits))
        self.assertEqual(len(rendering.search_text(str(self.pdf), 'ação', match_case=True, whole_words=True)), 2)

    def test_search_query_bound(self):
        with self.assertRaises(ValueError):
            rendering.search_text(str(self.pdf), 'x' * 257)

    def test_jpeg_png_and_document_cache_identity(self):
        jpeg = rendering.render_page(str(self.pdf), 0, 420, self.root / 'cache', image_format='jpeg')
        png = rendering.render_page(str(self.pdf), 0, 420, self.root / 'cache')
        self.assertTrue(rendering._valid_jpeg(jpeg))
        self.assertTrue(rendering._valid_png(png))
        make_pdf(self.pdf, ['MODIFIED DOCUMENT'])
        changed = rendering.render_page(str(self.pdf), 0, 420, self.root / 'cache', image_format='jpeg')
        self.assertNotEqual(jpeg, changed)

    def test_booklet_output_all_sides(self):
        for sides, expected in [('both', 4), ('front', 2), ('back', 2)]:
            out = self.root / f'{sides}.pdf'
            imposition.create_booklet(str(self.pdf), str(out), sides=sides)
            self.assertEqual(len(PdfReader(out).pages), expected)
            self.assertEqual(len(imposition.booklet_print_pairs(list(range(8)), sides)), expected)

    def test_running_process_cancellation(self):
        event = threading.Event()
        def trigger():
            time.sleep(.2)
            event.set()
        trigger_thread = threading.Thread(target=trigger)
        trigger_thread.start()
        cancel_state.set_event(event)
        start = time.monotonic()
        try:
            with self.assertRaisesRegex(RuntimeError, 'cancelada'):
                rendering._run([sys.executable, '-c', 'import time; time.sleep(10)'], timeout=15)
            self.assertLess(time.monotonic() - start, 2)
        finally:
            cancel_state.set_event(None)
            trigger_thread.join()

    def test_cups_option_validation_without_printing(self):
        with patch.object(cups_backend.shutil, 'which', return_value='/usr/bin/lp'), patch.object(cups_backend, '_run') as run:
            for key, value in [('media', 'A4\nBAD'), ('bad=key', 'A4'), ('media', 'x' * 161)]:
                with self.assertRaises(ValueError):
                    cups_backend.print_file('TestPrinter', str(self.pdf), {'printer_options': {key: value}})
            run.assert_not_called()

    def test_theme_persistence_preserves_other_settings(self):
        path = self.root / 'settings' / 'settings.json'
        path.parent.mkdir()
        path.write_text('{"other": 42}')
        for mode in ('dark', 'light', 'system'):
            appearance.save_mode(mode, path)
            self.assertEqual(appearance.read_mode(path), mode)
            self.assertEqual(json.loads(path.read_text())['other'], 42)
        self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)

    def test_system_theme_controller_initializes(self):
        env = os.environ.copy()
        env['XDG_CONFIG_HOME'] = str(self.root / 'fresh-system-config')
        code = (f'import sys; sys.path.insert(0, {str(APP)!r}); '
                'from appearance import AppearanceController; '
                f'AppearanceController({str(APP)!r}); print("initialized", flush=True)')
        result = subprocess.run([sys.executable, '-c', code], env=env,
                                capture_output=True, text=True, timeout=4)
        self.assertIn('initialized', result.stdout)

    def test_reader_search_sidebar_and_navigation(self):
        w = self.reader()
        w.find_entry.set_text('PAGE')
        wait_for(lambda: len(w.search_hits) == 7)
        self.assertEqual(len(w.find_results_list.get_children()), 7)
        w._select_search_hit(6)
        wait_for(lambda: w.page == 7 and not w._search_scroll_pending)
        self.assertEqual(w.find_status.get_text(), '7 de 7')

    def test_presentation_initial_zoom_top_and_navigation(self):
        w = self.reader()
        p = PresentationWindow(w, w.runner, str(self.pdf), w.page_sizes, 0, w.cache_dir)
        self.windows.append(p)
        # Bare Xorg has no window manager to honor fullscreen requests.
        p.set_default_size(1280, 900)
        p.resize(1280, 900)
        wait_for(lambda: p.pixbuf is not None)
        self.assertEqual(p.zoom, 250)
        self.assertTrue(p._top_anchor)
        p._goto(1)
        wait_for(lambda: p.page == 1 and p.rendered_zoom == 250 and p.pixbuf is not None)
        self.assertTrue(p._top_anchor)

    def test_booklet_preview_browses_all_faces(self):
        w = self.reader()
        p = PrintWindow(w, w.runner, str(self.pdf), 8, w.page_sizes, 0, w.cache_dir, lambda job: None)
        self.windows.append(p)
        p.mode_stack.set_visible_child_name('booklet')
        for sides in ('both', 'front', 'back'):
            p.book_sides.set_active_id(sides)
            faces = p._booklet_faces()
            p.booklet_preview_index = 0
            for index, face in enumerate(faces):
                self.assertEqual(p._current_booklet_face(), face)
                self.assertEqual(p.booklet_preview_index, index)
                p._booklet_step(None, 1)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HistoryChecks)
    names = [test.id().rsplit('.', 1)[-1] for test in suite]
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    errors = {test.id().rsplit('.', 1)[-1] for test, _ in result.errors}
    failures = {test.id().rsplit('.', 1)[-1] for test, _ in result.failures}
    report = {
        'target': 'Winux PDF 3.3.11 original extracted source',
        'tests_run': result.testsRun,
        'passed': result.testsRun - len(result.errors) - len(result.failures) - len(result.skipped),
        'errors': len(result.errors), 'failures': len(result.failures),
        'skipped': len(result.skipped),
        'tests': [{'name': n, 'status': 'error' if n in errors else 'failed' if n in failures else 'passed'} for n in names],
        'source_module_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(APP.glob('*.py'))},
        'conditions': ['GTK 3 and real Poppler', 'Synthetic eight-page PDF',
                       'Explicit light mode in reader tests; separate fresh system-mode subprocess',
                       'Explicit presentation size for bare Xorg without a window manager',
                       'CUPS command execution mocked; no printer jobs submitted'],
        'limits': ['No physical printing', 'No package manager installation',
                   'No heavy-document benchmark', 'No Windows readers executed'],
    }
    if os.environ.get('WINUX_HISTORY_RESULTS'):
        Path(os.environ['WINUX_HISTORY_RESULTS']).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
