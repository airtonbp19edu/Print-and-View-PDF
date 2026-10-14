"""Relocate the Windows runtime and launch the same GTK application."""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parent.parent
GTK = ROOT / 'gtk'
POPPLER = ROOT / 'poppler'
DLL_HANDLES = []


def configure():
    global DLL_HANDLES
    os.environ['PATH'] = os.pathsep.join([str(GTK / 'bin'), str(POPPLER / 'bin'), os.environ.get('PATH', '')])
    os.environ['GI_TYPELIB_PATH'] = str(GTK / 'lib/girepository-1.0')
    os.environ['XDG_DATA_DIRS'] = os.pathsep.join([str(ROOT / 'share'), str(GTK / 'share')])
    os.environ['GSETTINGS_SCHEMA_DIR'] = str(GTK / 'share/glib-2.0/schemas')
    os.environ['XDG_CONFIG_HOME'] = str(Path(os.environ.get('APPDATA', Path.home())) / 'PrintView')
    os.environ['XDG_CACHE_HOME'] = str(Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'PrintView' / 'cache')
    os.environ['PYTHONUTF8'] = '1'
    DLL_HANDLES = [os.add_dll_directory(str(folder)) for folder in (GTK / 'bin', POPPLER / 'bin')]
    cache = Path(os.environ['XDG_CACHE_HOME'])
    cache.mkdir(parents=True, exist_ok=True)
    # Gvsbuild's SVG loader cache uses relative build paths; resolve them at launch.
    loader_cache = GTK / 'lib/gdk-pixbuf-2.0/2.10.0/loaders.cache'
    if loader_cache.exists():
        relocated = []
        for line in loader_cache.read_text(encoding='utf-8').splitlines():
            if line.startswith('"lib') and line.endswith('.dll"'):
                relative = line[1:-1].replace('\\\\', '\\')
                line = '"' + (GTK / relative).as_posix() + '"'
            relocated.append(line)
        local_cache = cache / 'pixbuf-loaders.cache'
        local_cache.write_text('\n'.join(relocated) + '\n', encoding='utf-8')
        os.environ['GDK_PIXBUF_MODULE_FILE'] = str(local_cache)
    log = (cache / 'diagnostics.log').open('a', encoding='utf-8', buffering=1)
    sys.stdout = sys.stderr = log


if __name__ == "__main__":
    configure()
    import main
    main.main()
