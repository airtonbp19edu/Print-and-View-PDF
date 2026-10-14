"""Page-wise text search using the same geometry as reader selection."""
from collections import OrderedDict
from pathlib import Path
import threading
import unicodedata

from rendering import document_info, extract_page_words


def normalized(text, match_case=False, ignore_accents=False):
    text = unicodedata.normalize('NFC', text)
    if not match_case:
        text = text.casefold()
    if ignore_accents:
        text = ''.join(c for c in unicodedata.normalize('NFD', text)
                       if unicodedata.category(c) != 'Mn')
    return text


def page_hits(data, query, page_index, match_case=False, whole_words=False,
              ignore_accents=False, join_hyphens=False):
    needle = ' '.join(normalized(query, match_case, ignore_accents).split())
    if not needle:
        return []
    blocks = {}
    for word in data['words']:
        blocks.setdefault(word['block'], []).append(word)
    hits = []
    for words in blocks.values():
        chars, owners = [], []
        for idx, word in enumerate(words):
            join = (idx > 0 and join_hyphens and word['line'] != words[idx - 1]['line']
                    and words[idx - 1]['text'].endswith(('-', '\u00ad')))
            if join:
                if chars and chars[-1] in ('-', '\u00ad'):
                    chars.pop(); owners.pop()
            elif idx:
                chars.append(' '); owners.append(None)
            folded = normalized(word['text'], match_case, ignore_accents)
            chars.extend(folded); owners.extend([idx] * len(folded))
        text = ''.join(chars)
        start = 0
        while True:
            pos = text.find(needle, start)
            if pos < 0:
                break
            end = pos + len(needle)
            is_word = lambda ch: ch.isalnum() or ch == '_'
            bounded = ((pos == 0 or not is_word(text[pos - 1]))
                       and (end == len(text) or not is_word(text[end])))
            if not whole_words or bounded:
                selected = sorted({owner for owner in owners[pos:end] if owner is not None})
                hits.append({'page': page_index, 'width': data['width'], 'height': data['height'],
                             'rects': [[words[i][key] for key in ('x0', 'y0', 'x1', 'y1')] for i in selected],
                             'text': ' '.join(words[i]['text'] for i in selected)})
            start = end
    return hits


class TextSearchIndex:
    """Retain at most 64 page maps; searches can stop between page extractions."""
    def __init__(self, path, page_count=None, max_cached_pages=64, page_sizes=None):
        self.path = str(Path(path).resolve())
        self.identity = self._identity()
        if page_sizes is None:
            info = document_info(self.path)
            page_sizes = info['sizes']
        self.page_sizes = page_sizes
        self.page_count = page_count if page_count is not None else len(page_sizes)
        self.max_cached_pages = max(1, int(max_cached_pages))
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def _identity(self):
        stat = Path(self.path).stat()
        return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns

    def page(self, index):
        if self._identity() != self.identity:
            raise RuntimeError('O PDF foi alterado. Reabra o documento para pesquisar.')
        with self.lock:
            data = self.cache.get(index)
            if data is not None:
                self.cache.move_to_end(index)
                return data
        data = extract_page_words(self.path, index, page_size=self.page_sizes[index])
        if self._identity() != self.identity:
            raise RuntimeError('O PDF foi alterado durante a pesquisa. Reabra o documento.')
        with self.lock:
            self.cache[index] = data
            self.cache.move_to_end(index)
            while len(self.cache) > self.max_cached_pages:
                self.cache.popitem(last=False)
        return data

    def search(self, query, max_hits=5000, cancel=None, on_page=None, **options):
        if not query.strip() or max_hits <= 0:
            return []
        hits = []
        for index in range(self.page_count):
            if cancel is not None and cancel.is_set():
                break
            data = self.page(index)
            if cancel is not None and cancel.is_set():
                break
            batch = page_hits(data, query, index, **options)[:max_hits - len(hits)]
            hits.extend(batch)
            if on_page is not None:
                on_page(index + 1, batch)
            if len(hits) >= max_hits:
                break
        return hits
