import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import cairo

APP = Path(os.environ.get('PRINT_VIEW_TEST_APP', Path(__file__).resolve().parents[1] / 'app'))
sys.path.insert(0, str(APP))
import imposition
import rendering
import cups_backend
from pypdf import PdfReader


def make_pdf(path, pages, line_step=28):
    surface = cairo.PDFSurface(str(path), 420, 595)
    cr = cairo.Context(surface)
    cr.select_font_face('DejaVu Sans')
    cr.set_font_size(16)
    for text in pages:
        for row, line in enumerate(text.split('\n')):
            cr.move_to(40, 60 + row * line_step)
            cr.show_text(line)
        cr.show_page()
    surface.finish()


class CoreRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pdf = self.root / 'input.pdf'
        make_pdf(self.pdf, [f'PAGE{i}' for i in range(1, 9)])

    def tearDown(self):
        self.temp.cleanup()

    def test_cache_distinguishes_documents(self):
        other = self.root / 'other.pdf'
        make_pdf(other, ['DIFFERENT DOCUMENT'])
        a = rendering.render_page(str(self.pdf), 0, 420, self.root / 'cache')
        b = rendering.render_page(str(other), 0, 420, self.root / 'cache')
        self.assertNotEqual(__import__('hashlib').sha256(Path(a).read_bytes()).hexdigest(),
                            __import__('hashlib').sha256(Path(b).read_bytes()).hexdigest())

    def test_booklet_generated_sides_and_binding(self):
        for sides, expected in [('both', ['PAGE8', 'PAGE2', 'PAGE6', 'PAGE4']),
                                ('front', ['PAGE8', 'PAGE6']),
                                ('back', ['PAGE2', 'PAGE4'])]:
            out = self.root / f'{sides}.pdf'
            imposition.create_booklet(str(self.pdf), str(out), sides=sides)
            pages = PdfReader(out).pages
            self.assertEqual(len(pages), len(expected))
            for page, first in zip(pages, expected):
                self.assertTrue(page.extract_text().startswith(first))
        out = self.root / 'right.pdf'
        imposition.create_booklet(str(self.pdf), str(out), binding='right', sides='back')
        self.assertTrue(PdfReader(out).pages[0].extract_text().startswith('PAGE7'))

    def test_search_has_individual_occurrence_coordinates(self):
        make_pdf(self.pdf, ['ação ação\nSegundo texto', 'AÇÃO'])
        hits = rendering.search_text(str(self.pdf), 'ação')
        self.assertEqual([hit['page'] for hit in hits], [0, 0, 1])
        self.assertNotEqual(hits[0]['rects'], hits[1]['rects'])
        self.assertTrue(all(hit['width'] > 0 and hit['height'] > 0 for hit in hits))

    def test_manual_booklet_sides_are_not_duplex(self):
        job = {'print_mode': 'booklet', 'booklet_sides': 'back',
               'booklet_auto_duplex': True,
               'printer_options': {'sides': 'two-sided-long-edge'}}
        with patch.object(cups_backend.shutil, 'which', return_value='/usr/bin/lp'), \
             patch.object(cups_backend, '_run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, 'queued', '')
            cups_backend.print_file('TestPrinter', str(self.pdf), job)
        cmd = run.call_args.args[0]
        self.assertIn('sides=one-sided', cmd)
        self.assertNotIn('sides=two-sided-short-edge', cmd)

    def test_worker_prepares_nup_and_poster(self):
        for mode, opts, count in [('multiple', {'pages_per_sheet': 4}, 2),
                                  ('poster', {'poster_scale': 200, 'poster_large_only': False,
                                              'poster_cut_marks': False, 'poster_labels': False}, 32)]:
            out = self.root / f'{mode}.pdf'
            job = {'print_mode': mode, 'paper_size': 'A4', **opts}
            subprocess.run([sys.executable, str(APP / 'worker_cli.py'), 'prepare', str(self.pdf), str(out)],
                           input=json.dumps(job), text=True, capture_output=True, check=True)
            self.assertEqual(len(PdfReader(out).pages), count)

    def test_intrinsic_rotation_and_cropbox_match_text_geometry(self):
        reader = PdfReader(self.pdf)
        page = reader.pages[0]
        page.cropbox.lower_left = (20, 30)
        page.cropbox.upper_right = (400, 570)
        page.rotate(90)
        writer = imposition.PdfWriter(); writer.add_page(page)
        writer.write(self.root / 'rotated.pdf')
        path = str(self.root / 'rotated.pdf')
        data = rendering.extract_page_words(path, 0)
        self.assertEqual((data['width'], data['height']), (540, 380))
        self.assertEqual(rendering.document_info(path)['sizes'], [(540, 380)])
        png = rendering.render_page(path, 0, 540, self.root / 'cache')
        from PIL import Image
        with Image.open(png) as image:
            self.assertEqual(image.size, (540, 380))
        self.assertTrue(all(0 <= w['x0'] < w['x1'] <= data['width'] for w in data['words']))

    def test_search_phrases_and_casefold_expansion(self):
        make_pdf(self.pdf, ['Straße Straße\nação\nseguinte'], line_step=18)
        self.assertEqual(len(rendering.search_text(str(self.pdf), 'STRASSE')), 2)
        hits = rendering.search_text(str(self.pdf), 'ação seguinte')
        self.assertEqual(len(hits), 1)
        self.assertEqual(len(hits[0]['rects']), 2)
        self.assertEqual(rendering.search_text(str(self.pdf), 'ausente'), [])
        self.assertEqual(rendering.search_text(str(self.pdf), ''), [])

    def test_nup_worker_rejects_fractional_count(self):
        with self.assertRaises(ValueError):
            imposition.prepare_output(str(self.pdf), str(self.root / 'bad.pdf'),
                                      {'print_mode': 'multiple', 'pages_per_sheet': 4.9})


if __name__ == '__main__':
    unittest.main()
