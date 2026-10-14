"""Metadata panels for Print&View PDF.

Uses pypdf in a background worker to expose document navigation structures
without touching GTK.  This module uses no external viewer assets.
"""
from pathlib import Path
import sys

VENDOR = Path(__file__).resolve().parent / 'vendor'
if str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

from pypdf import PdfReader  # type: ignore  # noqa: E402


def _obj(value):
    try:
        return value.get_object()
    except Exception:
        return value


def _text(value):
    if value is None:
        return ''
    try:
        return str(value)
    except Exception:
        return ''


def inspect_document_panels(path):
    reader = PdfReader(path)
    if reader.is_encrypted:
        try:
            reader.decrypt('')
        except Exception:
            return {'bookmarks': [], 'comments': [], 'layers': []}

    bookmarks = []

    def walk_outline(items, level=0):
        for item in items or []:
            if isinstance(item, list):
                walk_outline(item, level + 1)
                continue
            title = _text(getattr(item, 'title', '') or item)
            page = None
            try:
                page = reader.get_destination_page_number(item)
            except Exception:
                pass
            if title:
                bookmarks.append({'title': title, 'page': page, 'level': level})

    try:
        walk_outline(reader.outline, 0)
    except Exception:
        pass

    comments = []
    comment_subtypes = {
        '/Text': 'Nota', '/FreeText': 'Texto', '/Highlight': 'Destaque',
        '/Underline': 'Sublinhado', '/StrikeOut': 'Tachado', '/Squiggly': 'Ondulado',
        '/Stamp': 'Carimbo', '/Ink': 'Desenho', '/Line': 'Linha', '/Square': 'Retângulo',
        '/Circle': 'Elipse', '/Polygon': 'Polígono', '/PolyLine': 'Polilinha',
        '/FileAttachment': 'Anexo', '/Caret': 'Inserção',
    }
    for pidx, page in enumerate(reader.pages):
        try:
            annots = _obj(page.get('/Annots')) or []
        except Exception:
            annots = []
        for ref in annots:
            try:
                annot = _obj(ref)
                subtype = _text(annot.get('/Subtype'))
                if subtype not in comment_subtypes:
                    continue
                contents = _text(annot.get('/Contents')).strip()
                author = _text(annot.get('/T')).strip()
                subject = _text(annot.get('/Subj')).strip()
                label = subject or contents or comment_subtypes.get(subtype, subtype.strip('/'))
                comments.append({
                    'page': pidx,
                    'type': comment_subtypes.get(subtype, subtype.strip('/')),
                    'author': author,
                    'text': label,
                })
            except Exception:
                continue

    layers = []
    try:
        root = _obj(reader.trailer['/Root'])
        ocprops = _obj(root.get('/OCProperties'))
        if ocprops:
            for ref in _obj(ocprops.get('/OCGs')) or []:
                ocg = _obj(ref)
                name = _text(ocg.get('/Name')).strip()
                if name:
                    layers.append({'name': name})
    except Exception:
        pass

    return {'bookmarks': bookmarks, 'comments': comments, 'layers': layers}
