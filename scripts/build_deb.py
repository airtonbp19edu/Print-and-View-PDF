#!/usr/bin/env python3
"""Build the renamed application without installing or touching the system."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = '3.3.7~test1'


def build():
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='print-view-package-') as temp:
        stage = Path(temp)
        app = stage / 'usr/share/print-view-pdf'
        shutil.copytree(ROOT / 'app', app, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for p in app.rglob('*'):
            p.chmod(0o755 if p.is_dir() else 0o644)
        bin_dir = stage / 'usr/bin'; bin_dir.mkdir(parents=True)
        launcher = bin_dir / 'print-view-pdf'
        launcher.write_text('#!/bin/sh\nexec /usr/bin/python3 /usr/share/print-view-pdf/main.py "$@"\n')
        launcher.chmod(0o755)
        desktop_dir = stage / 'usr/share/applications'; desktop_dir.mkdir(parents=True)
        shutil.copy2(ROOT / 'assets/print-view-pdf.desktop', desktop_dir)
        shutil.copytree(ROOT / 'assets/icons', stage / 'usr/share/icons/hicolor')
        doc = stage / 'usr/share/doc/print-view-pdf'; doc.mkdir(parents=True)
        for src in (ROOT / 'LICENSE', ROOT / 'README.md', ROOT / 'docs/pypdf-LICENSE.txt',
                    ROOT / 'docs/ANALISE.md', ROOT / 'docs/PROVENIENCIA.md',
                    ROOT / 'docs/TESTAR-3.3.7.md', ROOT / 'docs/ENGENHARIA-REVERSA-FOXIT-UPDF.md'):
            shutil.copy2(src, doc)
        control = stage / 'DEBIAN'; control.mkdir()
        (control / 'control').write_text(
            f'Package: print-view-pdf\nVersion: {VERSION}\nSection: graphics\nPriority: optional\n'
            'Architecture: all\nMaintainer: Print&View PDF contributors\n'
            'Depends: python3 (>= 3.9), python3-gi, python3-gi-cairo, gir1.2-gtk-3.0, '
            'python3-cairo, python3-cryptography, poppler-utils, cups-client, python3-pil\n'
            'Conflicts: winux-pdf\nReplaces: winux-pdf\n'
            f'Installed-Size: {sum(p.stat().st_size for p in stage.rglob("*") if p.is_file()) // 1024 + 1}\n'
            'Description: Print&View PDF reader and advanced printer for Linux\n'
            ' Based on Winux PDF 3.3.5, with incremental word search and advanced printing.\n')
        for p in stage.rglob('*'):
            if p.is_dir(): p.chmod(0o755)
            elif p != launcher: p.chmod(0o644)
        output = dist / f'print-view-pdf_{VERSION}_all.deb'
        subprocess.run(['dpkg-deb', '--root-owner-group', '--build', str(stage), str(output)], check=True)
    return output


if __name__ == '__main__':
    print(build())
