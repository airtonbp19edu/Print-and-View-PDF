import copy
import math
import os
import re
import sys
import tempfile
from pathlib import Path

from pdf_dependency import configure_pdf_library
configure_pdf_library()

from pypdf import PdfReader, PdfWriter, Transformation  # type: ignore  # noqa: E402
from pypdf._page import PageObject  # type: ignore  # noqa: E402

PT_PER_MM = 72.0 / 25.4
MAX_POSTER_TILES = 100
MAX_POSTER_JOB_TILES = 300
VALID_NUP_COUNTS = {1, 2, 4, 6, 9, 16}

PAPER_SIZES = {
    'A3': (297.0 * PT_PER_MM, 420.0 * PT_PER_MM),
    'A4': (210.0 * PT_PER_MM, 297.0 * PT_PER_MM),
    'A5': (148.0 * PT_PER_MM, 210.0 * PT_PER_MM),
    'A6': (105.0 * PT_PER_MM, 148.0 * PT_PER_MM),
    '3.5X5': (3.5 * 72.0, 5.0 * 72.0),
    '4X6': (4.0 * 72.0, 6.0 * 72.0),
    '5X7': (5.0 * 72.0, 7.0 * 72.0),
    '8X10': (8.0 * 72.0, 10.0 * 72.0),
    'ENV10': (4.125 * 72.0, 9.5 * 72.0),
    'LETTER': (612.0, 792.0),
    'LEGAL': (612.0, 1008.0),
    'TABLOID': (792.0, 1224.0),
}


def paper_size_points(name='A4'):
    raw = (name or 'A4').upper()
    if 'A3' in raw or 'ISO_A3' in raw:
        return PAPER_SIZES['A3']
    if 'A5' in raw or 'ISO_A5' in raw:
        return PAPER_SIZES['A5']
    if 'A6' in raw or 'ISO_A6' in raw:
        return PAPER_SIZES['A6']
    if '3.5X5' in raw:
        return PAPER_SIZES['3.5X5']
    if '4X6' in raw:
        return PAPER_SIZES['4X6']
    if '5X7' in raw:
        return PAPER_SIZES['5X7']
    if '8X10' in raw:
        return PAPER_SIZES['8X10']
    if 'ENV10' in raw:
        return PAPER_SIZES['ENV10']
    if 'LETTER' in raw or 'NA_LETTER' in raw:
        return PAPER_SIZES['LETTER']
    if 'LEGAL' in raw or 'NA_LEGAL' in raw:
        return PAPER_SIZES['LEGAL']
    if 'TABLOID' in raw or 'LEDGER' in raw:
        return PAPER_SIZES['TABLOID']
    return PAPER_SIZES['A4']


def oriented_paper(name, orientation='portrait'):
    w, h = paper_size_points(name)
    if orientation == 'landscape' and h > w:
        return h, w
    if orientation == 'portrait' and w > h:
        return h, w
    return w, h


def parse_page_range(spec, page_count):
    page_count = max(0, int(page_count))
    if not spec:
        return list(range(page_count))
    result = []
    seen = set()
    for token in re.split(r'[,;\s]+', spec.strip()):
        if not token:
            continue
        if '-' in token:
            left, right = token.split('-', 1)
            try:
                a, b = int(left), int(right)
            except ValueError:
                continue
            # Clamp before constructing/iterating a range. Malformed input such
            # as 1-9999999999 must cost at most O(page_count), never O(token).
            step = 1 if b >= a else -1
            if step > 0:
                lo, hi = max(1, a), min(page_count, b)
                nums = range(lo, hi + 1) if lo <= hi else ()
            else:
                hi, lo = min(page_count, a), max(1, b)
                nums = range(hi, lo - 1, -1) if hi >= lo else ()
        else:
            try:
                nums = [int(token)]
            except ValueError:
                continue
        for num in nums:
            idx = num - 1
            if 0 <= idx < page_count and idx not in seen:
                seen.add(idx)
                result.append(idx)
    return result


def select_page_indices(page_count, page_range=None, page_set='all', reverse=False):
    indices = parse_page_range(page_range, page_count)
    if page_set == 'odd':
        indices = [i for i in indices if (i + 1) % 2 == 1]
    elif page_set == 'even':
        indices = [i for i in indices if (i + 1) % 2 == 0]
    if reverse:
        indices.reverse()
    return indices


def _reader(path):
    reader = PdfReader(path)
    if reader.is_encrypted:
        try:
            reader.decrypt('')
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError('PDF protegido por senha não pode ser preparado para impressão.') from exc
    return reader


def _normalized_page(page):
    p = copy.copy(page)
    try:
        if getattr(p, 'rotation', 0):
            p.transfer_rotation_to_content()
    except Exception:
        pass
    return p


def _place(dst, src, x, y, box_w, box_h, scale_mode='fit'):
    src = _normalized_page(src)
    sw = float(src.cropbox.width)
    sh = float(src.cropbox.height)
    if sw <= 0 or sh <= 0:
        return
    if scale_mode == 'actual':
        scale = 1.0
    else:
        scale = min(box_w / sw, box_h / sh)
    tx = x + (box_w - sw * scale) / 2.0
    ty = y + (box_h - sh * scale) / 2.0
    dst.merge_transformed_page(src, Transformation().scale(scale).translate(tx, ty), expand=False)


def _blank(width, height):
    return PageObject.create_blank_page(width=float(width), height=float(height))


def _write(writer, output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as fh:
        writer.write(fh)
    return output_path


def create_sized(input_path, output_path, page_range=None, page_set='all', reverse=False,
                 paper_size='A4', orientation='portrait', scale_mode='actual'):
    reader = _reader(input_path)
    indices = select_page_indices(len(reader.pages), page_range, page_set, reverse)
    pw, ph = oriented_paper(paper_size, orientation)
    writer = PdfWriter()
    for idx in indices:
        dst = _blank(pw, ph)
        _place(dst, reader.pages[idx], 0, 0, pw, ph, 'fit' if scale_mode == 'fit' else 'actual')
        writer.add_page(dst)
    return _write(writer, output_path)


def _grid_for_nup(n):
    return {1: (1, 1), 2: (2, 1), 4: (2, 2), 6: (3, 2), 9: (3, 3), 16: (4, 4)}.get(int(n), (2, 2))


def _cell_order(cols, rows, layout):
    xs = list(range(cols))
    ys_top = list(range(rows))
    if layout.startswith('rl'):
        xs.reverse()
    if layout.endswith('bt'):
        ys_top.reverse()
    return [(x, y) for y in ys_top for x in xs]


def create_nup(input_path, output_path, page_range=None, page_set='all', reverse=False,
               paper_size='A4', orientation='portrait', pages_per_sheet=4, layout='lrtb', margin_mm=4.0):
    requested_nup = pages_per_sheet
    try:
        pages_per_sheet = int(requested_nup)
        valid_integer = float(requested_nup) == pages_per_sheet
    except (TypeError, ValueError, OverflowError):
        valid_integer = False
        pages_per_sheet = 0
    if not valid_integer or pages_per_sheet not in VALID_NUP_COUNTS:
        raise ValueError('Páginas por folha deve ser 1, 2, 4, 6, 9 ou 16.')
    reader = _reader(input_path)
    indices = select_page_indices(len(reader.pages), page_range, page_set, reverse)
    pw, ph = oriented_paper(paper_size, orientation)
    cols, rows = _grid_for_nup(pages_per_sheet)
    margin = max(0.0, float(margin_mm)) * PT_PER_MM
    cell_w, cell_h = pw / cols, ph / rows
    order = _cell_order(cols, rows, layout)
    writer = PdfWriter()
    for start in range(0, len(indices), pages_per_sheet):
        dst = _blank(pw, ph)
        chunk = indices[start:start + pages_per_sheet]
        for pos, idx in enumerate(chunk):
            col, top_row = order[pos]
            row_from_bottom = rows - 1 - top_row
            x = col * cell_w + margin
            y = row_from_bottom * cell_h + margin
            bw = max(1.0, cell_w - 2 * margin)
            bh = max(1.0, cell_h - 2 * margin)
            _place(dst, reader.pages[idx], x, y, bw, bh, 'fit')
        writer.add_page(dst)
    return _write(writer, output_path)


def booklet_pairs(indices):
    padded = list(indices)
    while len(padded) % 4:
        padded.append(None)
    pairs = []
    left, right = 0, len(padded) - 1
    while left < right:
        pairs.append(('front', padded[right], padded[left]))
        pairs.append(('back', padded[left + 1], padded[right - 1]))
        left += 2
        right -= 2
    return pairs


def booklet_print_pairs(indices, sides='both'):
    """Printable booklet faces in the same order as the generated PDF.

    A physical booklet sheet contains a front and a back. Selecting just one
    side must not affect sheet pairing or reorder the source pages.
    """
    if sides not in ('both', 'front', 'back'):
        raise ValueError('Lados do livreto inválidos: ' + str(sides))
    pairs = booklet_pairs(indices)
    if sides == 'both':
        return pairs
    return [pair for pair in pairs if pair[0] == sides]


def create_booklet(input_path, output_path, page_range=None, page_set='all', reverse=False,
                   paper_size='A4', binding='left', sides='both', safety_margin_mm=5.0,
                   gutter_margin_mm=3.0):
    reader = _reader(input_path)
    indices = select_page_indices(len(reader.pages), page_range, page_set, reverse)
    # Booklets conventionally print on landscape sheets.
    pw, ph = oriented_paper(paper_size, 'landscape')
    half = pw / 2.0
    safety = max(0.0, float(safety_margin_mm)) * PT_PER_MM
    gutter = max(0.0, float(gutter_margin_mm)) * PT_PER_MM
    avail_w = max(1.0, half - 2 * safety - gutter)
    avail_h = max(1.0, ph - 2 * safety)
    writer = PdfWriter()
    for kind, left_idx, right_idx in booklet_print_pairs(indices, sides):
        if binding == 'right':
            left_idx, right_idx = right_idx, left_idx
        dst = _blank(pw, ph)
        # Left half: extra gutter is adjacent to the fold (right edge).
        lx = safety
        # Right half: extra gutter is adjacent to the fold (left edge).
        rx = half + safety + gutter
        y = safety
        if left_idx is not None:
            _place(dst, reader.pages[left_idx], lx, y, avail_w, avail_h, 'fit')
        if right_idx is not None:
            _place(dst, reader.pages[right_idx], rx, y, avail_w, avail_h, 'fit')
        writer.add_page(dst)
    return _write(writer, output_path)



def _poster_geometry(paper_size='A4', orientation='portrait', paper_width_pt=None,
                     paper_height_pt=None, imageable_area=None):
    """Return physical page and printer-imageable rectangle.

    Poster tiling uses the printer's usable/imageable rectangle.  The rectangle
    is supplied by the CUPS/PPD layer when available.  For Save as PDF or queues
    without geometry, the whole media is usable.
    """
    if paper_width_pt and paper_height_pt:
        pw, ph = float(paper_width_pt), float(paper_height_pt)
    else:
        pw, ph = oriented_paper(paper_size, orientation)
    if imageable_area and len(imageable_area) == 4:
        l, b, r, t = [float(v) for v in imageable_area]
        l = max(0.0, min(l, pw)); r = max(l, min(r, pw))
        b = max(0.0, min(b, ph)); t = max(b, min(t, ph))
        if r - l > 1.0 and t - b > 1.0:
            return pw, ph, (l, b, r, t)
    return pw, ph, (0.0, 0.0, pw, ph)


def _merge_poster_marks(dst, pw, ph, imageable, row, col, rows, cols,
                        overlap_pt, cut_marks=True, labels=True,
                        document_name='', source_page_number=1):
    """Overlay Tiling marks without changing poster geometry.

    The poster controls are scale, overlap, cut marks and labels.
    There is no extra 'mark margin'.  Cut marks indicate the trim boundary of
    the incoming overlap (left/top on every tile after the first column/row),
    while labels contain document name + source page number.
    """
    if not (cut_marks or labels):
        return
    try:
        import cairo
    except Exception:
        return

    l, b, r, t = [float(v) for v in imageable]
    # Cairo PDF user space is used visually from top-left here.
    left, right = l, r
    top, bottom = ph - t, ph - b
    fd, overlay_path = tempfile.mkstemp(prefix='winux-poster-marks-', suffix='.pdf')
    os.close(fd)
    try:
        surface = cairo.PDFSurface(overlay_path, pw, ph)
        cr = cairo.Context(surface)
        cr.set_antialias(cairo.ANTIALIAS_BEST)

        # Simulate the real hardware clipping rectangle in the generated PDF.
        # This keeps preview/PDF output consistent with what the printer can
        # physically put on paper, without inventing a poster-specific margin.
        cr.set_source_rgb(1, 1, 1)
        if top > 0:
            cr.rectangle(0, 0, pw, top); cr.fill()
        if bottom < ph:
            cr.rectangle(0, bottom, pw, ph - bottom); cr.fill()
        if left > 0:
            cr.rectangle(0, top, left, max(0, bottom - top)); cr.fill()
        if right < pw:
            cr.rectangle(right, top, pw - right, max(0, bottom - top)); cr.fill()

        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1.0)

        # The incoming duplicated band belongs to tiles after the first
        # column/row. Trimming at overlap distance removes that duplicate and
        # lets the remaining artwork butt exactly against the previous tile.
        trim_x = left + overlap_pt if col > 0 and overlap_pt > 0 else None
        trim_y = top + overlap_pt if row > 0 and overlap_pt > 0 else None

        if cut_marks and overlap_pt > 0:
            # Cut marks identify the trim edge of the duplicated overlap.
            # Use short perpendicular ticks, not a dashed line through the
            # artwork: for a vertical trim boundary the marks are horizontal;
            # for a horizontal boundary they are vertical.  Where both trim
            # boundaries meet the two ticks naturally form a small cross.
            # Dotted cut line on each trim edge (left/top).  Round black dots
            # sit on a white halo, so the line stays visible over dark or
            # coloured artwork; the scissors follow the dots.
            pitch = 4.6

            def dotted(x0, y0, x1, y1):
                cr.set_line_cap(cairo.LINE_CAP_ROUND)
                for color, width in (((1, 1, 1), 3.6), ((0, 0, 0), 1.7)):
                    cr.set_source_rgb(*color)
                    cr.set_line_width(width)
                    cr.set_dash([0.01, pitch])
                    cr.move_to(x0, y0); cr.line_to(x1, y1); cr.stroke()
                cr.set_dash([])
                cr.set_line_cap(cairo.LINE_CAP_BUTT)

            if trim_x is not None and trim_x < right:
                dotted(trim_x, top + 2.0, trim_x, bottom - 2.0)
            if trim_y is not None and trim_y < bottom:
                dotted(left + 2.0, trim_y, right - 2.0, trim_y)

        if cut_marks and overlap_pt > 0:
            # Matching registration ticks at identical relative distances on
            # the two adjoining sheets.  A trimmed left/top edge meets the
            # preceding sheet's full right/bottom printable edge.
            def register(x, y, vertical):
                cr.set_line_cap(cairo.LINE_CAP_ROUND)
                for rgba, lw in (((1, 1, 1, 1), 4.2), ((0.07, 0.07, 0.07, 1), 1.3)):
                    cr.set_source_rgba(*rgba)
                    cr.set_line_width(lw)
                    cr.move_to(x - (6 if vertical else 0), y - (0 if vertical else 6))
                    cr.line_to(x + (6 if vertical else 0), y + (0 if vertical else 6))
                    cr.stroke()
                cr.set_line_cap(cairo.LINE_CAP_BUTT)

            # Both sides use the same fractions of the *printable* span.
            for fraction in (0.18, 0.50, 0.82):
                y = top + fraction * (bottom - top)
                x = left + fraction * (right - left)
                if col < cols - 1:
                    register(right - 3, y, True)  # outgoing right edge
                if trim_x is not None:
                    register(trim_x, y, True)      # incoming cut edge
                if row < rows - 1:
                    register(x, bottom - 3, False) # outgoing bottom edge
                if trim_y is not None:
                    register(x, trim_y, False)     # incoming cut edge

        # Sheet coordinates are always printed when labels are enabled.
        # The joining instructions distinguish outgoing (keep) vs incoming
        # (trim and overlap) sides, even when no clipping margin is available.
        if labels:
            def note(message, x, y, limit):
                cr.select_font_face('Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                cr.set_font_size(6.3)
                text = message
                while text and cr.text_extents(text).width > max(16.0, limit - 7.0):
                    text = text[:-2]
                if text != message:
                    text = text.rstrip() + '…'
                width = min(max(16.0, limit), cr.text_extents(text).width + 6)
                cr.set_source_rgba(1, 1, 1, .94)
                cr.rectangle(x, y - 8, width, 10)
                cr.fill()
                cr.set_source_rgb(.12, .12, .12)
                cr.move_to(x + 3, y)
                cr.show_text(text)

            code = f'F{row+1}C{col+1} de {rows}x{cols}'
            note(code, left + 3, top + 10, right - left - 6)
            # Column/row pairs tell the operator exactly which side mates.
            if col > 0:
                note(f'← CORTAR • alinhar F{row+1}C{col}',
                     min(right - 30, left + max(4, overlap_pt + 5)), top + 22,
                     max(25, right - left - overlap_pt - 8))
            if col < cols - 1:
                note(f'→ ENCAIXE F{row+1}C{col+2} • manter borda',
                     left + 3, top + 34, right - left - 6)
            if row > 0:
                note(f'↑ CORTAR • alinhar F{row}C{col+1}',
                     left + 3, top + 46, right - left - 6)
            if row < rows - 1:
                note(f'↓ ENCAIXE F{row+2}C{col+1} • manter borda',
                     left + 3, top + 58, right - left - 6)

        if labels:
            base = os.path.basename(document_name or '') or 'Documento'
            label = f'{base}  —  página {source_page_number}'
            cr.select_font_face('Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(6.5)
            ext = cr.text_extents(label)
            pad = 3.0
            max_w = max(20.0, right - left - 8.0)
            box_w = min(max_w, ext.width + pad * 2)
            baseline = max(top + 10.0, bottom - 5.0)
            cr.set_source_rgba(1, 1, 1, 0.90)
            cr.rectangle(left + 3.0, baseline - 8.5, box_w, 10.5); cr.fill()
            cr.set_source_rgb(0.12, 0.12, 0.12)
            cr.move_to(left + 3.0 + pad, baseline); cr.show_text(label)

        surface.finish()
        overlay_reader = PdfReader(overlay_path)
        if overlay_reader.pages:
            dst.merge_page(overlay_reader.pages[0])
    finally:
        try:
            os.unlink(overlay_path)
        except OSError:
            pass


def poster_grid_for_size(page_w, page_h, paper_size='A4', orientation='portrait',
                         scale_percent=100.0, overlap_mm=0.0, imageable_area=None,
                         paper_width_pt=None, paper_height_pt=None, mark_margin_mm=None):
    """Return tile grid and final assembled poster size.

    This follows a tiled poster model: Page Zoom scales the source;
    every physical tile uses the printer imageable rectangle; Overlap reduces
    the stride between adjacent tiles. Cut marks/labels never change the grid.
    `mark_margin_mm` remains accepted only for backward API compatibility and
    is intentionally ignored.
    """
    pw, ph, area = _poster_geometry(
        paper_size, orientation, paper_width_pt, paper_height_pt, imageable_area)
    l, b, r, t = area
    tile_w = max(1.0, r - l)
    tile_h = max(1.0, t - b)
    scale = max(0.01, float(scale_percent) / 100.0)
    sw, sh = float(page_w) * scale, float(page_h) * scale
    overlap = max(0.0, float(overlap_mm)) * PT_PER_MM
    overlap = min(overlap, max(0.0, tile_w - 1.0), max(0.0, tile_h - 1.0))
    step_x = max(1.0, tile_w - overlap)
    step_y = max(1.0, tile_h - overlap)
    eps = 0.25
    cols = 1 if sw <= tile_w + eps else 1 + int(math.ceil((sw - tile_w - eps) / step_x))
    rows = 1 if sh <= tile_h + eps else 1 + int(math.ceil((sh - tile_h - eps) / step_y))
    if cols * rows > MAX_POSTER_TILES:
        raise ValueError(f'O pôster exigiria {cols * rows} folhas por página. O limite é {MAX_POSTER_TILES}; reduza o zoom ou a sobreposição.')
    return max(1, cols), max(1, rows), sw, sh


def create_poster(input_path, output_path, page_range=None, page_set='all', reverse=False,
                  paper_size='A4', orientation='portrait', scale_percent=100.0,
                  overlap_mm=0.0, large_pages_only=True, cut_marks=True, labels=True,
                  glue_guides=False, mark_margin_mm=0.0, imageable_area=None,
                  paper_width_pt=None, paper_height_pt=None):
    """Create tiled poster pages.

    `glue_guides` and `mark_margin_mm` are retained for compatibility with jobs
    saved by older Winux builds but are no longer used. This mode has no
    separate glue-guide or mark-margin controls in Tile Large Pages.
    """
    reader = _reader(input_path)
    indices = select_page_indices(len(reader.pages), page_range, page_set, reverse)
    pw, ph, area = _poster_geometry(
        paper_size, orientation, paper_width_pt, paper_height_pt, imageable_area)
    l, b, r, t = area
    tile_w, tile_h = max(1.0, r - l), max(1.0, t - b)
    scale = max(0.01, float(scale_percent) / 100.0)
    overlap = max(0.0, float(overlap_mm)) * PT_PER_MM
    overlap = min(overlap, max(0.0, tile_w - 1.0), max(0.0, tile_h - 1.0))
    step_x = max(1.0, tile_w - overlap)
    step_y = max(1.0, tile_h - overlap)
    writer = PdfWriter()
    doc_name = os.path.basename(input_path)

    total_tiles = 0
    for idx in indices:
        src = _normalized_page(reader.pages[idx])
        w, h = float(src.cropbox.width), float(src.cropbox.height)
        sw, sh = w * scale, h * scale
        cols, rows, _sw, _sh = poster_grid_for_size(
            w, h, paper_size, orientation, scale_percent, overlap_mm,
            imageable_area=area, paper_width_pt=pw, paper_height_pt=ph)

        required = (1 if large_pages_only and sw <= pw + 0.25 and sh <= ph + 0.25
                    else cols * rows)
        total_tiles += required
        if total_tiles > MAX_POSTER_JOB_TILES:
            raise ValueError(f'O trabalho excede {MAX_POSTER_JOB_TILES} folhas; reduza o intervalo ou a escala.')

        # Large-page tiling splits only pages that exceed the paper after scale. A page that still fits
        # the selected physical paper at Page Zoom is printed once, not split
        # merely because the printer has hardware margins.
        if large_pages_only and sw <= pw + 0.25 and sh <= ph + 0.25:
            dst = _blank(pw, ph)
            tx = (pw - sw) / 2.0
            ty = (ph - sh) / 2.0
            dst.merge_transformed_page(src, Transformation().scale(scale).translate(tx, ty), expand=False)
            writer.add_page(dst)
            continue

        for top_row in range(rows):
            for col in range(cols):
                dst = _blank(pw, ph)
                # Source window in assembled-poster coordinates. top_row=0 is
                # the top-most tile. Translate the complete scaled source so
                # that this window lands exactly in the printer imageable area.
                source_x = col * step_x
                source_top = top_row * step_y
                source_bottom = sh - (source_top + tile_h)
                tx = l - source_x
                ty = b - source_bottom
                dst.merge_transformed_page(
                    src, Transformation().scale(scale).translate(tx, ty), expand=False)
                _merge_poster_marks(
                    dst, pw, ph, area, top_row, col, rows, cols, overlap,
                    cut_marks=cut_marks, labels=labels,
                    document_name=doc_name, source_page_number=idx + 1)
                writer.add_page(dst)
    return _write(writer, output_path)

def prepare_output(input_path, output_path, job):
    mode = job.get('print_mode', 'size')
    common = dict(
        page_range=job.get('page_range'),
        page_set=job.get('page_set', 'all'),
        reverse=bool(job.get('reverse', False)),
        paper_size=job.get('paper_size', 'A4'),
    )
    if mode == 'poster':
        return create_poster(
            input_path, output_path, orientation=job.get('orientation', 'portrait'),
            scale_percent=job.get('poster_scale', 100.0),
            overlap_mm=job.get('poster_overlap_mm', 0.0),
            large_pages_only=bool(job.get('poster_large_only', True)),
            cut_marks=bool(job.get('poster_cut_marks', True)),
            labels=bool(job.get('poster_labels', True)),
            glue_guides=False, mark_margin_mm=0.0,
            imageable_area=job.get('poster_imageable_area'),
            paper_width_pt=job.get('poster_paper_width_pt'),
            paper_height_pt=job.get('poster_paper_height_pt'), **common)
    if mode == 'multiple':
        return create_nup(
            input_path, output_path, orientation=job.get('orientation', 'portrait'),
            pages_per_sheet=job.get('pages_per_sheet', 4),
            layout=job.get('number_up_layout', 'lrtb'),
            margin_mm=float(job.get('nup_margin_mm', 4.0)), **common)
    if mode == 'booklet':
        return create_booklet(
            input_path, output_path, binding=job.get('booklet_binding', 'left'),
            sides=job.get('booklet_sides', 'both'),
            safety_margin_mm=float(job.get('booklet_safety_mm', 5.0)),
            gutter_margin_mm=float(job.get('booklet_gutter_mm', 3.0)), **common)
    return create_sized(
        input_path, output_path, orientation=job.get('orientation', 'portrait'),
        scale_mode=job.get('scale_mode', 'actual'), **common)


def selected_booklet_pairs(indices, sides="both"):
    return booklet_print_pairs(indices, sides)
