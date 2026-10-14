import os
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import cairo
import test_regressions as fixtures
from test_gui import wait_for
from test_regressions import APP
sys.path.insert(0, str(APP))
from main import PDFWindow, Gtk, GdkPixbuf, GLib
from presentation import PresentationWindow
from async_core import BackgroundRunner
from themes import read_theme, load_theme


@unittest.skipUnless(os.environ.get('DISPLAY'), 'Requires an X display')
class ViewerTests(unittest.TestCase):
    setUp_fixture = fixtures.CoreRegressionTests.setUp
    tearDown_fixture = fixtures.CoreRegressionTests.tearDown

    def setUp(self):
        self.setUp_fixture()
        self.env = patch.dict(os.environ, {'XDG_CONFIG_HOME': str(self.root / 'config')}); self.env.start()
        self.quit = patch.object(Gtk, 'main_quit'); self.quit.start()
        self.w = PDFWindow(str(self.pdf))
        self.errors = []; self.w._error = self.errors.append
        wait_for(lambda: self.w.displayed_page == 0)

    def tearDown(self):
        self.w.destroy(); self.quit.stop(); self.env.stop(); self.tearDown_fixture()

    def test_theme_persistence_and_contrast(self):
        self.w.theme_combo.set_active_id('dark')
        self.assertEqual(read_theme(), 'dark')
        settings = Gtk.Settings.get_default()
        self.assertTrue(settings.get_property('gtk-application-prefer-dark-theme'))
        color = self.w.status_file.get_style_context().get_color(Gtk.StateFlags.NORMAL)
        self.assertGreater((color.red + color.green + color.blue) / 3, .65)
        self.w.theme_combo.set_active_id('light')
        self.assertFalse(settings.get_property('gtk-application-prefer-dark-theme'))
        color = self.w.status_file.get_style_context().get_color(Gtk.StateFlags.NORMAL)
        self.assertLess((color.red + color.green + color.blue) / 3, .5)
        self.assertEqual(read_theme(), 'light')

    def test_repeated_requests_do_not_cancel_same_running_render(self):
        from cancel_state import get_event
        started = threading.Event(); release = threading.Event(); events = []
        real_load = self.w._reader_pixbuf
        def slow(*args):
            events.append(get_event()); started.set(); release.wait(5)
            return real_load(*args)
        self.w.page_cache.clear()
        try:
            with patch.object(self.w, '_reader_pixbuf', side_effect=slow):
                self.w.goto_page(5)
                wait_for(started.is_set)
                for _ in range(20):
                    self.w.request_render()
                self.assertFalse(events[0].is_set())
                release.set()
                wait_for(lambda: self.w.displayed_page == 5)
        finally:
            release.set()

    def test_historical_reading_mode_keeps_top_at_250_percent(self):
        p = PresentationWindow(self.w, self.w.runner, str(self.pdf), self.w.page_sizes, 0, self.w.cache_dir)
        try:
            wait_for(lambda: p.pixbuf is not None and not p._loading)
            p.fit_combo.set_active_id('reading')
            wait_for(lambda: p.rendered_zoom == 250 and not p._loading)
            self.assertTrue(p._top_anchor)
            self.assertEqual(p.pan_y, p._pan_bounds()[3])
            p._goto(1)
            wait_for(lambda: p.page == 1 and not p._loading)
            self.assertEqual(p.zoom, 250)
            self.assertEqual(p.pan_y, p._pan_bounds()[3])
        finally:
            p.destroy()

    def test_prefetched_reader_page_is_immediate(self):
        wait_for(lambda: any(key[1] == 1 for key in self.w.page_cache.images))
        before = time.monotonic(); self.w.goto_page(1)
        self.assertEqual(self.w.displayed_page, 1)
        self.assertLess(time.monotonic() - before, .2)
        self.assertLessEqual(self.w.page_cache.bytes, self.w.page_cache.max_bytes)

    def test_presentation_fit_fill_center_and_error(self):
        p = PresentationWindow(self.w, self.w.runner, str(self.pdf), self.w.page_sizes, 0, self.w.cache_dir)
        try:
            wait_for(lambda: p.pixbuf is not None and not p._loading)
            W, H = p._canvas_size(); available = H - p._controls_height()
            self.assertLessEqual(p.pixbuf.get_width(), W)
            self.assertLessEqual(p.pixbuf.get_height(), available)
            self.assertGreater(p.pixbuf.get_height(), available * .88)
            self.assertEqual((p.pan_x, p.pan_y), (0, 0))
            p.fit_combo.set_active_id('fill')
            wait_for(lambda: not p._loading)
            self.assertGreaterEqual(p.pixbuf.get_width(), W - 30)
            old = p.pixbuf
            with patch.object(p, '_load_page_pixbuf', side_effect=RuntimeError('test render failure')):
                p._goto(5)
                wait_for(lambda: p._render_error is not None)
                self.assertIs(p.pixbuf, old)
                surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
                self.assertFalse(p._draw(p.canvas, cairo.Context(surface)))
                self.assertIn('test render failure', p._render_error)
            transparent = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 100, 100)
            transparent.fill(0); p.pixbuf = transparent
            p._loading = False; p._render_error = None
            p.pan_x = p.pan_y = 0
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
            p._draw(p.canvas, cairo.Context(surface)); surface.flush()
            y = int((H - p._controls_height()) / 2)
            offset = y * surface.get_stride() + (W // 2) * 4
            self.assertEqual(bytes(surface.get_data()[offset:offset + 3]), b'\xff\xff\xff')
        finally:
            p.destroy()

    def test_cached_presentation_page_invalidates_old_render(self):
        p = PresentationWindow(self.w, self.w.runner, str(self.pdf), self.w.page_sizes, 0, self.w.cache_dir)
        release = threading.Event()
        started = threading.Event()
        try:
            wait_for(lambda: p.pixbuf is not None and not p._loading)
            key = (0, p._target_width_for(0)); original = p.pixbuf
            p._cache_put(key, original)
            real_load = p._load_page_pixbuf
            def slow(page, target):
                if page == 5:
                    started.set(); release.wait(5)
                return real_load(page, target)
            with patch.object(p, '_load_page_pixbuf', side_effect=slow):
                p._goto(5); wait_for(started.is_set); p._goto(0)
                self.assertIs(p.pixbuf, original)
                release.set()
                deadline = time.monotonic() + .3
                while time.monotonic() < deadline:
                    while GLib.MainContext.default().pending(): GLib.MainContext.default().iteration(False)
                    time.sleep(.01)
                self.assertIs(p.pixbuf, original)
                self.assertEqual(p.page, 0)
        finally:
            release.set(); p.destroy()

    def test_render_is_not_blocked_by_auxiliary_workers(self):
        release = threading.Event(); started = [threading.Event() for _ in range(4)]
        def block(event):
            event.set(); release.wait(5)
        try:
            for i, event in enumerate(started):
                self.w.runner.submit(f'busy-{i}', lambda event=event: block(event))
            wait_for(lambda: all(event.is_set() for event in started))
            self.w.goto_page(5)
            wait_for(lambda: self.w.displayed_page == 5, timeout=3)
            self.assertFalse(release.is_set())
        finally:
            release.set()

    def test_latest_renderer_skips_obsolete_queue_entries(self):
        runner = BackgroundRunner(workers=1, latest_only=True)
        release = threading.Event(); started = threading.Event(); calls = []
        try:
            runner.submit('hold', lambda: (started.set(), release.wait(5)))
            wait_for(started.is_set)
            old = runner.submit('page', lambda: calls.append('old'))
            runner.submit('page', lambda: calls.append('new'))
            self.assertTrue(old.cancelled())
            release.set(); wait_for(lambda: calls == ['new'])
        finally:
            release.set(); runner.shutdown()

    def test_presentation_handles_portrait_and_landscape(self):
        from pypdf import PdfReader, PdfWriter
        from rendering import document_info
        reader = PdfReader(self.pdf); writer = PdfWriter()
        writer.add_page(reader.pages[0]); writer.add_page(reader.pages[1].rotate(90))
        path = self.root / 'mixed.pdf'; writer.write(path)
        p = PresentationWindow(self.w, self.w.runner, str(path), document_info(path)['sizes'], 0, self.w.cache_dir)
        try:
            wait_for(lambda: p.pixbuf is not None and not p._loading)
            p._goto(1); wait_for(lambda: not p._loading)
            W, H = p._canvas_size()
            self.assertGreater(p.pixbuf.get_width(), p.pixbuf.get_height())
            self.assertLessEqual(p.pixbuf.get_height(), H - p._controls_height())
            available = H - p._controls_height()
            self.assertTrue(abs(p.pixbuf.get_width() - (W - 24)) <= 3
                            or abs(p.pixbuf.get_height() - (available - 24)) <= 3)
            self.assertEqual((p.pan_x, p.pan_y), (0, 0))
        finally:
            p.destroy()
