import sys
import threading
import unittest
from unittest.mock import patch
import test_regressions as fixtures
from test_regressions import make_pdf, APP
sys.path.insert(0, str(APP))
from search_engine import TextSearchIndex, page_hits


class SearchTests(unittest.TestCase):
    setUp = fixtures.CoreRegressionTests.setUp
    tearDown = fixtures.CoreRegressionTests.tearDown
    def test_options_and_real_pdf(self):
        make_pdf(self.pdf, ['ação AÇÃO acoes\nStraße STRASSE\nagir reagir'])
        index = TextSearchIndex(str(self.pdf))
        self.assertEqual(len(index.search('AÇÃO', match_case=True)), 1)
        self.assertEqual(len(index.search('ação')), 2)
        self.assertEqual(len(index.search('acao')), 0)
        self.assertEqual(len(index.search('acao', ignore_accents=True)), 2)
        self.assertEqual(len(index.search('agir')), 2)
        self.assertEqual(len(index.search('agir', whole_words=True)), 1)
        self.assertEqual(len(index.search('strasse', whole_words=True)), 2)

    def test_cache_reuse_and_cancellation_progress(self):
        index = TextSearchIndex(str(self.pdf))
        with patch('search_engine.extract_page_words', wraps=__import__('rendering').extract_page_words) as extract:
            self.assertEqual(len(index.search('PAGE1')), 1)
            self.assertEqual(len(index.search('PAGE2')), 1)
            self.assertEqual(extract.call_count, 8)
        cancel = threading.Event(); seen = []
        def progress(page, batch):
            seen.append(page)
            if page == 2: cancel.set()
        self.assertEqual(len(index.search('PAGE', cancel=cancel, on_page=progress)), 2)
        self.assertEqual(seen, [1, 2])
        self.assertEqual(index.search('PAGE', cancel=cancel), [])

    def test_hyphenation_does_not_join_columns(self):
        data = {'width': 420, 'height': 595, 'words': [
            {'text': 'impres-', 'block': 0, 'line': 0, 'x0': 10, 'y0': 10, 'x1': 60, 'y1': 25},
            {'text': 'são', 'block': 0, 'line': 1, 'x0': 10, 'y0': 26, 'x1': 40, 'y1': 41},
            {'text': 'outra', 'block': 1, 'line': 0, 'x0': 200, 'y0': 10, 'x1': 250, 'y1': 25}]}
        self.assertEqual(page_hits(data, 'impressão', 0), [])
        hits = page_hits(data, 'impressão', 0, join_hyphens=True)
        self.assertEqual(len(hits), 1); self.assertEqual(len(hits[0]['rects']), 2)
        self.assertEqual(page_hits(data, 'são outra', 0), [])

    def test_cache_eviction_and_changed_file(self):
        index = TextSearchIndex(str(self.pdf), max_cached_pages=2)
        index.search('PAGE')
        self.assertEqual(len(index.cache), 2)
        make_pdf(self.pdf, ['CHANGED'])
        with self.assertRaises(RuntimeError): index.search('CHANGED')


