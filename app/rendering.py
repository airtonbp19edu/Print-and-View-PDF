import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

VENDOR = Path(__file__).resolve().parent / 'vendor'
if str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

from pypdf import PdfReader  # type: ignore  # noqa: E402


def _run(cmd, timeout=120):
    env = os.environ.copy()
    env['LC_ALL'] = 'C'
    env['LANG'] = 'C'
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=True, timeout=timeout, env=env)


def document_info(path):
    reader = PdfReader(path)
    if reader.is_encrypted:
        try:
            reader.decrypt('')
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError('O PDF está protegido por senha e não pôde ser aberto sem senha.') from exc
    sizes = []
    for page in reader.pages:
        box = page.cropbox
        size = (float(box.width), float(box.height))
        sizes.append(size[::-1] if page.rotation % 180 else size)
    md = reader.metadata or {}
    meta = {
        'title': str(md.get('/Title') or ''),
        'author': str(md.get('/Author') or ''),
        'subject': str(md.get('/Subject') or ''),
        'creator': str(md.get('/Creator') or ''),
        'producer': str(md.get('/Producer') or ''),
    }
    return {'pages': len(reader.pages), 'sizes': sizes, 'metadata': meta}


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _valid_png(filename):
    """Cheap integrity check used before a cached render is exposed to GTK."""
    try:
        p = Path(filename)
        # A valid rendered page is much larger than the PNG header alone.
        if not p.is_file() or p.stat().st_size < 64:
            return False
        with p.open('rb') as fh:
            if fh.read(8) != PNG_SIGNATURE:
                return False
            # Verify the file was fully finalized, not merely started by pdftocairo.
            fh.seek(-12, os.SEEK_END)
            tail = fh.read(12)
        return tail[4:8] == b'IEND' and tail[8:] == b'\xaeB`\x82'
    except (OSError, ValueError):
        return False


def render_page(path, page_index, target_width, cache_dir, key='main'):
    """Render one page with Poppler and atomically publish a validated PNG.

    Multiple GTK actions may request the same page/size concurrently.  Older
    versions wrote directly to the shared cache filename, allowing another
    worker to see a partially-written PNG.  Each worker now renders to its own
    temporary prefix and os.replace() publishes only a complete file.
    """
    target_width = max(120, min(int(target_width), 5200))
    page_no = int(page_index) + 1
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    source = Path(path).resolve()
    stat = source.stat()
    identity = repr((str(source), stat.st_dev, stat.st_ino, stat.st_size,
                     stat.st_mtime_ns, stat.st_ctime_ns)).encode('utf-8')
    source_key = hashlib.sha256(identity).hexdigest()[:24]
    out = cache / f'{source_key}-{key}-p{page_no}-w{target_width}'
    png = Path(str(out) + '.png')

    if _valid_png(png):
        return str(png)
    # Never retain a broken cache entry: it would otherwise be retried forever.
    try:
        png.unlink(missing_ok=True)
    except OSError:
        pass

    if not shutil.which('pdftocairo'):
        raise RuntimeError('pdftocairo não está instalado (pacote poppler-utils).')

    # Unique destination per worker/process avoids cache races entirely.
    fd, tmp_name = tempfile.mkstemp(prefix=f'.{out.name}-', dir=str(cache))
    os.close(fd)
    try:
        os.unlink(tmp_name)
    except OSError:
        pass
    tmp_prefix = Path(tmp_name)
    tmp_png = Path(str(tmp_prefix) + '.png')

    try:
        cmd = [
            'pdftocairo', '-cropbox', '-png', '-singlefile', '-f', str(page_no), '-l', str(page_no),
            '-scale-to-x', str(target_width), '-scale-to-y', '-1', path, str(tmp_prefix)
        ]
        _run(cmd, timeout=120)
        if not _valid_png(tmp_png):
            raise RuntimeError('O renderizador produziu um PNG incompleto ou inválido.')

        # Atomic on the same filesystem. Readers see either the old complete
        # file or this complete replacement, never the in-progress render.
        os.replace(tmp_png, png)
        if not _valid_png(png):
            try:
                png.unlink(missing_ok=True)
            except OSError:
                pass
            raise RuntimeError('Falha ao validar a miniatura renderizada.')
        return str(png)
    finally:
        for leftover in (tmp_png, tmp_prefix):
            try:
                Path(leftover).unlink(missing_ok=True)
            except OSError:
                pass


def render_page_to_png(path, page_index, output_path, dpi=180):
    page_no = int(page_index) + 1
    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='print-view-export-') as td:
        prefix = Path(td) / 'page'
        _run(['pdftocairo', '-cropbox', '-png', '-singlefile', '-f', str(page_no), '-l', str(page_no),
              '-r', str(int(dpi)), path, str(prefix)], timeout=180)
        generated = Path(str(prefix) + '.png')
        if not generated.exists():
            raise RuntimeError('Falha ao exportar a página para PNG.')
        shutil.copy2(generated, dest)
    return str(dest)


def extract_page_text(path, page_index):
    page_no = int(page_index) + 1
    proc = _run(['pdftotext', '-f', str(page_no), '-l', str(page_no), '-layout', path, '-'], timeout=90)
    return proc.stdout.decode('utf-8', errors='replace').strip()


def search_text(path, query, max_hits=5000, **options):
    from search_engine import TextSearchIndex
    return TextSearchIndex(path).search(query, max_hits=max_hits, **options)


def safe_filename_from_pdf(path, suffix=''):
    stem = Path(path).stem
    stem = re.sub(r'[^\w. -]+', '_', stem, flags=re.UNICODE).strip() or 'documento'
    return f'{stem}{suffix}'


def _parse_word_pages(data):
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise RuntimeError('Não foi possível obter o mapa de texto desta página.') from exc
    tag = lambda el: el.tag.rsplit('}', 1)[-1]
    pages = []
    for page_el in (el for el in root.iter() if tag(el) == 'page'):
        words = []
        for block_id, block in enumerate(el for el in page_el.iter() if tag(el) == 'block'):
            for line_id, line in enumerate(el for el in block.iter() if tag(el) == 'line'):
                for el in (el for el in line.iter() if tag(el) == 'word'):
                    words.append({'text': ''.join(el.itertext()), 'block': block_id, 'line': line_id,
                                  'x0': float(el.attrib['xMin']), 'y0': float(el.attrib['yMin']),
                                  'x1': float(el.attrib['xMax']), 'y1': float(el.attrib['yMax'])})
        pages.append({'width': float(page_el.attrib['width']),
                      'height': float(page_el.attrib['height']), 'words': words})
    return pages


def extract_page_words(path, page_index, page_size=None):
    """Crop-relative Poppler word boxes with structural block/line identity."""
    page_no = int(page_index) + 1
    proc = _run(['pdftotext', '-cropbox', '-bbox-layout', '-f', str(page_no), '-l', str(page_no), path, '-'], timeout=120)
    pages = _parse_word_pages(proc.stdout)
    if pages and page_size is not None:
        pages[0]['width'], pages[0]['height'] = page_size
    elif pages:
        reader = PdfReader(path)
        if reader.is_encrypted:
            reader.decrypt('')
        page = reader.pages[int(page_index)]
        width, height = float(page.cropbox.width), float(page.cropbox.height)
        pages[0]['width'], pages[0]['height'] = (height, width) if page.rotation % 180 else (width, height)
    return pages[0] if pages else {'width': 0.0, 'height': 0.0, 'words': []}
