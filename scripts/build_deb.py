#!/usr/bin/env python3
"""Build the renamed application without installing or touching the system."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / 'app'))
from version import VERSION


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
                    ROOT / 'docs/TESTAR-3.3.7.md', ROOT / 'docs/TESTAR-TEST2.md',
                    ROOT / 'docs/ENGENHARIA-REVERSA-FOXIT-UPDF.md',
                    ROOT / 'docs/ENTREGA-3.4.0.md'):
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
            ' Continues Winux PDF 3.3.11 with progressive search, themes, presentation,\n'
            ' booklet, poster and N-up printing through CUPS.\n')
        (control / 'postinst').write_text('#!/bin/sh\nset -e\nif [ "$1" = configure ]; then\n  if command -v py3compile >/dev/null 2>&1; then py3compile /usr/share/print-view-pdf; fi\n  if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database -q; fi\n  if command -v gtk-update-icon-cache >/dev/null 2>&1; then gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true; fi\nfi\n')
        (control / 'postrm').write_text('#!/bin/sh\nset -e\nif command -v py3clean >/dev/null 2>&1; then py3clean -p print-view-pdf; fi\nif command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database -q; fi\nif command -v gtk-update-icon-cache >/dev/null 2>&1; then gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true; fi\n')
        (doc / 'copyright').write_text('Print&View PDF: MIT, see LICENSE.\nBundled pypdf 6.20.1: BSD-3-Clause, see pypdf-LICENSE.txt.\nOriginal Winux source continued with authorization from its authors.\n')
        for p in stage.rglob('*'):
            if p.is_dir(): p.chmod(0o755)
            elif p == launcher or p.name in ('postinst', 'postrm'): p.chmod(0o755)
            else: p.chmod(0o644)
        output = dist / f'print-view-pdf_{VERSION}_all.deb'
        subprocess.run(['dpkg-deb', '--root-owner-group', '--build', str(stage), str(output)], check=True)
    return output


if __name__ == '__main__':
    print(build())
