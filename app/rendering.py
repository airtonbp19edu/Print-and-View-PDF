import os
import re
import hashlib
import time
import math
import signal
import unicodedata
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from pdf_dependency import configure_pdf_library
configure_pdf_library()

from pypdf import PdfReader  # type: ignore  # noqa: E402
from cancel_state import get_event
from platform_runtime import subprocess_options


def _run(cmd, timeout=120):
    env = os.environ.copy()
    env['LC_ALL'] = 'C'
    env['LANG'] = 'C'
    # Bound address space / CPU in Poppler; use util-linux prlimit when present,
    # rather than unsafe preexec_fn in a multithreaded GTK process.
    if os.name != 'nt' and shutil.which('prlimit'):
        cmd = ['prlimit', '--as=1610612736', f'--cpu={max(30, int(timeout) + 10)}', '--', *cmd]
    event = get_event()
    if event is not None and event.is_set():
        raise RuntimeError('Tarefa de renderização cancelada.')
    if event is None:
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              check=True, timeout=timeout, env=env, **subprocess_options())
    # Cooperative cancellation interrupts the actual OS process group, not
    # merely its obsolete GTK callback. A timeout still applies independently.
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=env, start_new_session=True, **subprocess_options())
    deadline = time.monotonic() + timeout
    try:
        while True:
            if event.is_set():
                raise RuntimeError('Tarefa de renderização cancelada.')
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(cmd, timeout)
            try:
                out, err = proc.communicate(timeout=min(.15, remaining))
                if proc.returncode:
                    raise subprocess.CalledProcessError(proc.returncode, cmd, out, err)
                return subprocess.CompletedProcess(cmd, proc.returncode, out, err)
            except subprocess.TimeoutExpired:
                continue
    except BaseException:
        try:
            if os.name == 'nt':
                proc.kill()
            else:
                os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.communicate()
        raise


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


def _valid_jpeg(filename):
    """Only expose fully completed JPEGs to the image decoder."""
    try:
        p = Path(filename)
        if not p.is_file() or p.stat().st_size < 64:
            return False
        with p.open('rb') as fh:
            if fh.read(2) != b'\xff\xd8':
                return False
            fh.seek(-2, os.SEEK_END)
            return fh.read(2) == b'\xff\xd9'
    except (OSError, ValueError):
        return False


def render_page(path, page_index, target_width, cache_dir, key='main', image_format='png'):
    """Render a PDF page, publishing an atomic, validated cache entry.

    JPEG (quality 94) is used only for on-screen display.  Poppler's lossless
    PNG encoding is far slower for large/complex pages, particularly at 250%
    presentation zoom. PNG is retained for export and print workflows.
    """
    target_width = max(120, min(int(target_width), 5200))
    page_no = int(page_index) + 1
    # Poppler's -scale-to-x respects aspect ratio only with -scale-to-y=-1.
    # Constrain the width *before* rendering to avoid JPEG's 65535px limit and
    # pathological allocations for PDFs with very tall/narrow page boxes.
    try:
        info = _run(['pdfinfo', '-f', str(page_no), '-l', str(page_no), path], timeout=30).stdout
        dims = re.search(rb'Page\s+' + str(page_no).encode() + rb' size:\s+([\d.]+) x ([\d.]+) pts', info)
        if dims is None:
            raise RuntimeError('O PDF não informa dimensões válidas para renderização.')
        w, h = float(dims.group(1)), float(dims.group(2))
        if w <= 0 or h <= 0 or not math.isfinite(w*h):
            raise RuntimeError('Dimensões de página inválidas.')
        target_width = max(1, min(target_width, int(9000 * w / h),
                                  int(math.sqrt(40_000_000 * w / h))))
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError('Falha ao validar o tamanho da página PDF.') from exc
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    jpeg = image_format == 'jpeg'
    if image_format not in ('png', 'jpeg'):
        raise ValueError(f'Formato de renderização não suportado: {image_format}')
    valid = _valid_jpeg if jpeg else _valid_png
    extension = '.jpg' if jpeg else '.png'
    # Include file identity: no page can be reused across different documents,
    # even if page index, format and zoom coincide (or a path is replaced).
    src = Path(path).stat()
    identity = f'{Path(path).resolve()}:{src.st_dev}:{src.st_ino}:{src.st_size}:{src.st_mtime_ns}:{src.st_ctime_ns}'
    fingerprint = hashlib.sha256(identity.encode('utf-8')).hexdigest()[:20]
    out = cache / f'{fingerprint}-{key}-p{page_no}-w{target_width}'
    output = Path(str(out) + extension)

    if valid(output):
        return str(output)
    # Broken cache entries must never be reused.
    try:
        output.unlink(missing_ok=True)
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
    temporary_output = Path(str(tmp_prefix) + extension)

    try:
        cmd = ['pdftocairo']
        cmd += ['-jpeg', '-jpegopt', 'quality=94'] if jpeg else ['-png']
        cmd += [
            '-cropbox', '-singlefile', '-f', str(page_no), '-l', str(page_no),
            '-scale-to-x', str(target_width), '-scale-to-y', '-1', path, str(tmp_prefix)
        ]
        _run(cmd, timeout=120)
        if not valid(temporary_output):
            raise RuntimeError('O renderizador produziu uma imagem incompleta ou inválida.')

        # Atomic on same filesystem: no partial image is exposed to GTK.
        os.replace(temporary_output, output)
        _prune_image_cache(cache, keep=str(output))
        if not valid(output):
            try:
                output.unlink(missing_ok=True)
            except OSError:
                pass
            raise RuntimeError('Falha ao validar a página renderizada.')
        return str(output)
    finally:
        for leftover in (temporary_output, tmp_prefix):
            try:
                Path(leftover).unlink(missing_ok=True)
            except OSError:
                pass



def _prune_image_cache(cache, keep=None, max_bytes=400 * 1024 * 1024, max_files=350):
    """Best effort cap on private render cache. Ignore in-progress dotfiles."""
    try:
        entries = sorted((f for f in Path(cache).iterdir()
                          if f.is_file() and not f.name.startswith('.') and f.suffix in ('.png', '.jpg')),
                         key=lambda x: x.stat().st_mtime, reverse=True)
        total = 0
        for index, f in enumerate(entries):
            try:
                size = f.stat().st_size
                total += size
                if (index >= max_files or total > max_bytes) and str(f) != keep:
                    f.unlink(missing_ok=True)
                    total -= size
            except OSError:
                pass
    except OSError:
        pass


def _page_limit(path, page_number, dpi, max_pixels=45_000_000):
    """Reject impossible raster output before launching pdftocairo."""
    result = _run(['pdfinfo', '-f', str(page_number), '-l', str(page_number), path], timeout=30)
    matched = re.search(rb'Page\s+' + str(page_number).encode() + rb' size:\s+([\d.]+) x ([\d.]+) pts', result.stdout)
    if not matched:
        raise RuntimeError('Dimensões da página indisponíveis para exportação segura.')
    if matched:
        w, h = float(matched.group(1)), float(matched.group(2))
        if not math.isfinite(w * h) or w * h * (dpi / 72.0) ** 2 > max_pixels:
            raise RuntimeError('Esta página ultrapassa o limite seguro de pixels para exportação.')


def render_page_to_png(path, page_index, output_path, dpi=180):
    page_no = int(page_index) + 1
    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dpi = max(72, min(600, int(dpi)))
    _page_limit(path, page_no, dpi)
    with tempfile.TemporaryDirectory(prefix='winux-export-') as td:
        prefix = Path(td) / 'page'
        _run(['pdftocairo', '-png', '-singlefile', '-f', str(page_no), '-l', str(page_no),
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


def _word_match_rectangle(word, box, first_char, last_char):
    """Crop a word bbox to the matching substring; no full-word overpainting."""
    x0, y0, x1, y1 = box
    n = max(1, len(word))
    a = max(0.0, min(1.0, first_char / n))
    b = max(a, min(1.0, last_char / n))
    return [x0 + (x1-x0) * a, y0, x0 + (x1-x0) * b, y1]


def _parse_search_page(page, query_pattern, page_idx, max_remaining):
    """Keep Poppler's line structure instead of flattening the whole PDF."""
    import bisect
    pw = float(page.attrib.get('width') or 0)
    ph = float(page.attrib.get('height') or 0)
    matches = []
    # Poppler blocks delimit columns/paragraphs; allow wrapped phrases inside
    # one block without stitching unrelated columns together.
    blocks = [el for el in page.iter() if el.tag.rsplit('}', 1)[-1] == 'block']
    if not blocks:
        blocks = [el for el in page.iter() if el.tag.rsplit('}', 1)[-1] == 'line']
    for block in blocks:
        words = []
        for el in block.iter():
            if el.tag.rsplit('}', 1)[-1] != 'word':
                continue
            try:
                word = ''.join(el.itertext()).strip()
                bbox = tuple(float(el.attrib[k]) for k in ('xMin', 'yMin', 'xMax', 'yMax'))
                if word and bbox[2] > bbox[0] and bbox[3] > bbox[1]:
                    words.append((word, bbox))
            except (KeyError, ValueError):
                pass
        if not words:
            continue
        starts = []
        text = ''
        for word, _ in words:
            if text:
                text += ' '
            starts.append(len(text))
            text += word
        for match in query_pattern.finditer(text):
            first = max(0, bisect.bisect_right(starts, match.start()) - 1)
            last = max(first, min(len(words) - 1, bisect.bisect_left(starts, match.end()) - 1))
            rectangles = []
            for i in range(first, last + 1):
                word, bbox = words[i]
                a = max(0, match.start() - starts[i])
                b = min(len(word), match.end() - starts[i])
                if b <= a:
                    continue
                rectangles.append(_word_match_rectangle(word, bbox, a, b))
            if rectangles:
                c0, c1 = max(0, match.start()-45), min(len(text), match.end()+45)
                matches.append({'page': page_idx, 'rects': rectangles, 'width': pw, 'height': ph,
                                'snippet': ('…' if c0 else '') + text[c0:c1] +
                                ('…' if c1 < len(text) else '')})
            if len(matches) >= max_remaining:
                return matches
    return matches


def search_text(path, query, max_hits=5000, **options):
    from search_engine import TextSearchIndex
    return TextSearchIndex(path).search(query, max_hits=max_hits, **options)


def safe_filename_from_pdf(path, suffix=''):
    stem = Path(path).stem
    stem = re.sub(r'[^\w. -]+', '_', stem, flags=re.UNICODE).strip() or 'documento'
    return f'{stem}{suffix}'


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
