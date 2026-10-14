#!/usr/bin/env python3
import json
try:
    import resource
except ImportError:  # Windows has no POSIX resource module.
    resource = None
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from imposition import prepare_output
from rendering import document_info


def _rasterize_pdf_in_place(path, dpi):
    try:
        from PIL import Image
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError('Imprimir como imagem requer o pacote python3-pil.') from exc
    dpi = max(72, min(600, int(dpi)))
    with tempfile.TemporaryDirectory(prefix='winux-raster-') as td:
        # Render and encode one page at a time. The former all-pages list could
        # retain multiple gigabytes of decoded pixels for large print jobs.
        from rendering import document_info
        info = document_info(path)
        page_count = int(info['pages'])
        for w, h in info['sizes']:
            if w * h * (dpi / 72) ** 2 > 45_000_000:
                raise RuntimeError('Imprimir como imagem excede o limite de 45 MP por página.')
        page_pdfs = []
        for page_no in range(1, page_count + 1):
            prefix = os.path.join(td, f'page-{page_no:06d}')
            proc = subprocess.run(
                ['pdftocairo', '-f', str(page_no), '-l', str(page_no), '-singlefile',
                 '-png', '-r', str(dpi), path, prefix],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=600)
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr.strip() or f'Falha ao rasterizar a página {page_no}.')
            png = prefix + '.png'
            if not os.path.isfile(png):
                raise RuntimeError(f'A rasterização da página {page_no} não gerou imagem.')
            page_pdf = prefix + '.pdf'
            with Image.open(png) as source:
                image = source.convert('RGB')
                image.save(page_pdf, 'PDF', resolution=float(dpi))
                image.close()
            page_pdfs.append(page_pdf)
            os.unlink(png)
        temp_pdf = str(Path(path).with_suffix('.raster.pdf'))
        try:
            os.unlink(temp_pdf)
        except FileNotFoundError:
            pass
        if len(page_pdfs) == 1:
            os.replace(page_pdfs[0], temp_pdf)
        elif page_pdfs:
            proc = subprocess.run(['pdfunite', *page_pdfs, temp_pdf],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True, timeout=600)
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr.strip() or 'Falha ao juntar as páginas rasterizadas.')
        else:
            raise RuntimeError('O documento não contém páginas para rasterizar.')
        os.replace(temp_pdf, path)


def main(argv):
    # Bound untrusted PDF parsing/imposition CPU and memory in the worker.
    for limit, amount in (() if resource is None else
                          ((resource.RLIMIT_AS, 2 * 1024**3), (resource.RLIMIT_CPU, 540))):
        try:
            soft, hard = resource.getrlimit(limit)
            resource.setrlimit(limit, (min(soft, amount) if soft != resource.RLIM_INFINITY else amount,
                                       min(hard, amount) if hard != resource.RLIM_INFINITY else amount))
        except (OSError, ValueError):
            pass
    if len(argv) < 3:
        raise SystemExit(2)
    cmd = argv[1]
    if cmd == 'info':
        info = document_info(argv[2])
        print(json.dumps(info, ensure_ascii=False))
        return
    if cmd == 'panels':
        from pdf_panels import inspect_document_panels
        print(json.dumps(inspect_document_panels(argv[2]), ensure_ascii=False))
        return
    if cmd == 'prepare':
        if len(argv) < 4:
            raise SystemExit(2)
        input_path, output_path = argv[2], argv[3]
        try:
            job = json.load(sys.stdin)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise RuntimeError('Opções de impressão inválidas.') from exc
        prepare_output(input_path, output_path, job)
        if job.get('print_as_image'):
            _rasterize_pdf_in_place(output_path, job.get('image_dpi', 300))
        print(output_path)
        return
    raise SystemExit(2)


if __name__ == '__main__':
    main(sys.argv)
