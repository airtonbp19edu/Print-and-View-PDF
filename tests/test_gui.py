import os
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from test_regressions import APP, make_pdf
sys.path.insert(0, str(APP))
from main import PDFWindow, load_css
from print_window import PrintWindow


def wait_for(predicate, timeout=12):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        context = GLib.MainContext.default()
        while context.pending():
            context.iteration(False)
        if predicate():
            return
        time.sleep(.02)
    raise AssertionError('GTK readiness timeout')


@unittest.skipUnless(os.environ.get('DISPLAY'), 'Requires an X display')
class GUIRegressionTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pdf = self.root / 'reader.pdf'
        make_pdf(self.pdf, ['ação ação'] + [f'PAGE{i}' for i in range(2, 9)])
        load_css()
        self.quit_patch = patch.object(Gtk, 'main_quit')
        self.quit_patch.start()
        self.errors = []
        self.window = PDFWindow()
        self.window._error = lambda msg: self.errors.append(msg)
        self.window.open_document(str(self.pdf))
        wait_for(lambda: self.window.page_count == 8 and self.window.current_pixbuf is not None)
        self.assertEqual(self.errors, [])

    def tearDown(self):
        self.window.destroy()
        self.quit_patch.stop()
        self.temp.cleanup()

    def test_search_navigation_selection_and_rotation(self):
        w = self.window
        w.find_entry.set_text('ação')
        wait_for(lambda: len(w.search_hits) == 2 and not w.search_running)
        self.assertEqual(w.find_status.get_text(), '1 de 2')
        w._find_next(); self.assertEqual(w.search_pos, 1)
        w._find_prev(); self.assertEqual(w.search_pos, 0)
        hit = w.search_hits[0]
        for rotation in (0, 90, 180, 270):
            w.rotation = rotation
            displayed = w._pdf_rect_to_display(hit['rects'][0], hit)
            restored = w._display_rect_to_pdf(displayed, hit)
            for a, b in zip(restored, hit['rects'][0]):
                self.assertAlmostEqual(a, b)
        w.rotation = 0
        rect = w._pdf_rect_to_display(hit['rects'][0], hit)
        w._finish_text_selection(rect)
        wait_for(lambda: bool(w.selected_words))
        self.assertEqual(w.selected_words[0]['text'], 'ação')
        w.find_entry.set_text('')
        self.assertEqual(w.search_hits, [])

    def test_search_sidebar_scroll_and_all_booklet_faces(self):
        w = self.window
        w.find_entry.set_text('PAGE')
        wait_for(lambda: not w.search_running and len(w.search_hits) == 7)
        self.assertEqual(len(w.find_results_list.get_children()), 7)
        w._select_search_hit(6)
        wait_for(lambda: w.displayed_page == 7 and not w._search_scroll_pending)
        p = PrintWindow(w, w.runner, str(self.pdf), 8, w.page_sizes, 0, w.cache_dir, lambda job: None)
        try:
            p.mode_stack.set_visible_child_name('booklet')
            for sides, count in [('both', 4), ('front', 2), ('back', 2)]:
                p.book_sides.set_active_id(sides)
                faces = p._booklet_faces()
                self.assertEqual(len(faces), count)
                p.booklet_preview_index = 0
                for index, face in enumerate(faces):
                    self.assertEqual(p._current_booklet_face(), face)
                    self.assertEqual(p.booklet_preview_index, index)
                    p._booklet_step(None, 1)
        finally:
            p.destroy()

    def test_booklet_preview_sides_binding_and_submit(self):
        w = self.window
        jobs = []
        p = PrintWindow(w, w.runner, str(self.pdf), 8, w.page_sizes, 0, w.cache_dir, jobs.append)
        try:
            p.mode_stack.set_visible_child_name('booklet')
            p.book_sides.set_active_id('front')
            self.assertEqual(p._mode_thumbnail_indices(), [7, 0])
            p.book_sides.set_active_id('back')
            self.assertEqual(p._mode_thumbnail_indices(), [1, 6])
            self.assertIn('verso', p.preview_info.get_text())
            self.assertFalse(p.auto_duplex.get_sensitive())
            p.binding.set_active_id('right')
            self.assertEqual(p._mode_thumbnail_indices(), [6, 1])
            p._controls_changed()
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 500)
            self.assertFalse(p._draw_preview(p.preview, cairo.Context(surface)))
            p.dest_combo.append('cups:TestPrinter', 'TestPrinter')
            p.dest_combo.set_active_id('cups:TestPrinter')
            p._submit()
            self.assertEqual(jobs[0]['booklet_sides'], 'back')
            self.assertEqual(jobs[0]['booklet_binding'], 'right')
        finally:
            p.destroy()

    def test_search_results_arrive_before_end_and_options_cancel_old_query(self):
        import threading
        from search_engine import TextSearchIndex
        w = self.window
        index = TextSearchIndex(str(self.pdf), page_sizes=w.page_sizes)
        original = index.page
        release = threading.Event()
        def slow_page(page):
            if page == 1:
                release.wait(5)
            return original(page)
        index.page = slow_page
        w.search_index = index
        try:
            w.find_entry.set_text('ação')
            wait_for(lambda: len(w.search_hits) == 2 and w.search_running)
            self.assertIn('1/8 páginas', w.find_status.get_text())
            old_cancel = w.search_cancel
            w.find_options['match_case'].set_active(True)
            w.find_entry.set_text('AÇÃO')
            self.assertTrue(old_cancel.is_set())
            release.set()
            wait_for(lambda: not w.search_running and w.find_status.get_text() == 'Nenhuma ocorrência')
            self.assertEqual(w.search_hits, [])
            w.find_options['match_case'].set_active(False)
            w.find_options['ignore_accents'].set_active(True)
            w.find_entry.set_text('acao')
            wait_for(lambda: len(w.search_hits) == 2 and not w.search_running)
        finally:
            release.set()


if __name__ == '__main__':
    unittest.main()
