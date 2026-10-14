#!/usr/bin/env python3
"""Build an x64 Windows installer on Linux or Windows using pinned runtimes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
from version import VERSION


def extract(z, name, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(z.read(name))


def build(downloads, makensis, stage):
    downloads.mkdir(parents=True, exist_ok=True)
    items = json.loads((ROOT / 'packaging/windows-artifacts.json').read_text())
    for item in items:
        path = downloads / item['file']
        if not path.exists():
            with urllib.request.urlopen(item['url'], timeout=60) as response, path.open('wb') as out:
                shutil.copyfileobj(response, out)
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise RuntimeError('Dependency checksum mismatch: ' + item['file'])
    if stage.exists():
        raise RuntimeError('Use a new staging directory; existing files are preserved.')
    stage.mkdir(parents=True)
    with zipfile.ZipFile(downloads / 'python.3.14.0.nupkg') as z:
        for name in z.namelist():
            if name.startswith('tools/') and not name.endswith('/'):
                extract(z, name, stage / 'python' / name.removeprefix('tools/'))
    with zipfile.ZipFile(downloads / 'GTK3_Gvsbuild_2026.8.0_x64.zip') as z:
        for name in z.namelist():
            keep = ((name.startswith('bin/') and name.endswith('.dll')) or
                    name.startswith(('lib/girepository-1.0/', 'lib/gdk-pixbuf-2.0/',
                                     'share/glib-2.0/', 'share/icons/', 'share/doc/',
                                     'share/fontconfig/', 'etc/fonts/')))
            if keep and not name.endswith('/') and not name.endswith(('.pdb', '.lib', '.a')):
                extract(z, name, stage / 'gtk' / name)
        for name in z.namelist():
            if name.startswith('wheels/') and name.endswith('.whl'):
                wheel = downloads / Path(name).name
                extract(z, name, wheel)
    with zipfile.ZipFile(downloads / 'Release-26.09.0-0.zip') as z:
        prefix = 'poppler-26.09.0/Library/'
        for name in z.namelist():
            if name.startswith(prefix) and not name.endswith('/'):
                relative = name.removeprefix(prefix)
                if relative.startswith('bin/') and (relative.endswith('.dll') or Path(relative).name in
                        ('pdfinfo.exe', 'pdftocairo.exe', 'pdftotext.exe', 'pdfunite.exe')):
                    extract(z, name, stage / 'poppler' / relative)
                elif relative.startswith('share/'):
                    extract(z, name, stage / 'poppler' / relative)
            elif name.startswith('poppler-26.09.0/share/') and not name.endswith('/'):
                extract(z, name, stage / 'poppler' / name.removeprefix('poppler-26.09.0/'))
    for wheel in downloads.glob('*.whl'):
        # Only the locked Windows wheels and GTK's cp314 wheels, not the Linux build environment.
        if wheel.name not in {i['file'] for i in items} and not wheel.name.startswith(('pygobject-', 'pycairo-')):
            continue
        with zipfile.ZipFile(wheel) as z:
            for name in z.namelist():
                if not name.endswith('/'):
                    if '..' in Path(name).parts or Path(name).is_absolute():
                        raise RuntimeError('Invalid wheel path')
                    extract(z, name, stage / 'python/Lib/site-packages' / name)
    shutil.copytree(ROOT / 'app', stage / 'app', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copytree(ROOT / 'assets/icons', stage / 'share/icons/hicolor')
    shutil.copytree(ROOT / 'docs', stage / 'docs')
    shutil.copy2(ROOT / 'LICENSE', stage / 'LICENSE.txt')
    shutil.copy2(ROOT / 'README.md', stage / 'README.md')
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    subprocess.run([makensis, '-V2', f'-DAPP_VERSION={VERSION}', f'-DSTAGE={stage.resolve()}',
                    str(ROOT / 'packaging/windows-launcher.nsi')], check=True)
    output = dist / f'PrintViewPDF-{VERSION}-Setup-x64.exe'
    subprocess.run([makensis, '-V2', f'-DAPP_VERSION={VERSION}', f'-DSTAGE={stage.resolve()}',
                    f'-DOUTPUT={output.resolve()}', str(ROOT / 'packaging/windows-installer.nsi')], check=True)
    print(output)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--downloads', type=Path, default=ROOT / 'dist/windows-downloads')
    parser.add_argument('--stage', type=Path, default=ROOT / 'dist/windows-stage')
    parser.add_argument('--makensis', default='makensis')
    args = parser.parse_args()
    build(args.downloads, args.makensis, args.stage)
