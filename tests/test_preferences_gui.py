"""Real GTK preference transactions and reader integration; isolated config."""
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from main import PDFWindow, Gtk, GLib, load_css
from preferences import PreferencesStore
from pypdf import PdfWriter


def wait_for(predicate, timeout=60):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        context = GLib.MainContext.default()
        while context.pending():
            context.iteration(False)
        if predicate():
            return
        time.sleep(.02)
    raise AssertionError('GTK operation did not finish')


@unittest.skipUnless(os.name == 'nt' or os.environ.get('DISPLAY'), 'Requires a graphical session')
class PreferencesGUITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.env = patch.dict(os.environ, {'XDG_CONFIG_HOME': str(self.root / 'config')})
        self.env.start()
        self.quit = patch.object(Gtk, 'main_quit'); self.quit.start()
        self.store = PreferencesStore()
        self.store.save({'appearance': 'light'})
        load_css()
        self.callback_errors = []
        self.exception_hook = patch('sys.excepthook', side_effect=lambda _kind, error, _trace: self.callback_errors.append(str(error)))
        self.exception_hook.start()
        self.addCleanup(self.exception_hook.stop)
        self.window = PDFWindow()
        self.errors = []
        self.window._error = self.errors.append

    def tearDown(self):
        self.window.destroy()
        self.quit.stop(); self.env.stop(); self.temp.cleanup()
        self.assertEqual(self.callback_errors, [], "Unhandled GTK callback errors")

    def dialog(self):
        self.window._open_preferences()
        dialog = self.window.preferences_dialog
        wait_for(lambda: dialog.get_mapped())
        return dialog

    def make_document(self, filename):
        path = self.root / filename
        writer = PdfWriter()
        for _ in range(4):
            writer.add_blank_page(width=420, height=595)
        writer.write(path)
        return path

    @unittest.skipUnless(os.name == 'nt', 'Windows-specific ownership guard')
    def test_windows_does_not_cleanup_unverified_temp_cache_owners(self):
        from main import _cleanup_stale_render_caches
        with patch('main.tempfile.gettempdir', side_effect=AssertionError('must not scan unknown owners')):
            _cleanup_stale_render_caches()

    def test_preview_cancel_does_not_persist_theme(self):
        self.assertTrue(self.window.preferences_button.get_sensitive())
        self.window._set_sidebar_visible(False)
        self.assertFalse(self.window.sidebar_visible)
        self.assertTrue(all(not button.get_active() for button in self.window.sidebar_rail_buttons))
        dialog = self.dialog()
        self.assertFalse(dialog.controls[('interface', 'sidebar_visible')].get_active())
        before = self.store.path.read_bytes()
        dialog.theme_buttons['dark'].set_active(True)
        self.assertEqual(self.window.theme_mode, 'dark')
        self.assertEqual(self.store.path.read_bytes(), before)
        dialog.response(Gtk.ResponseType.CANCEL)
        self.assertEqual(self.window.theme_mode, 'light')
        self.assertIsNone(self.window.preferences_dialog)

    def test_apply_then_cancel_keeps_last_applied_theme_and_search(self):
        dialog = self.dialog()
        dialog.theme_buttons['dark'].set_active(True)
        dialog.controls[('search', 'ignore_accents')].set_active(True)
        dialog.response(Gtk.ResponseType.APPLY)
        self.assertTrue(self.window.find_options['ignore_accents'].get_active())
        self.assertTrue(self.store.load()['search']['ignore_accents'])
        dialog.theme_buttons['light'].set_active(True)
        dialog.response(Gtk.ResponseType.CANCEL)
        self.assertEqual(self.window.theme_mode, 'dark')
        self.assertEqual(self.store.load()['appearance'], 'dark')

    def test_section_reset_and_save_error_keep_dialog_open(self):
        dialog = self.dialog()
        dialog.controls[('reading', 'zoom_mode')].set_active_id('percent')
        dialog.zoom.set_value(200)
        dialog.controls[('search', 'whole_words')].set_active(True)
        dialog._reset('reading')
        self.assertEqual(dialog.zoom.get_value_as_int(), 100)
        self.assertTrue(dialog.controls[('search', 'whole_words')].get_active())
        with patch.object(self.store.__class__, '_write', side_effect=OSError('disk unavailable')):
            dialog.response(Gtk.ResponseType.OK)
        self.assertIs(self.window.preferences_dialog, dialog)
        self.assertIn('Não foi possível salvar', dialog.message.get_text())

    def test_document_reading_memory_does_not_leak_to_another_file(self):
        self.store.save({'reading': {'zoom_mode': 'percent', 'zoom_percent': 125,
                                     'remember_document': True}})
        a = self.make_document('first.pdf'); b = self.make_document('second.pdf')
        self.window.open_document(str(a))
        wait_for(lambda: self.window.displayed_page == 0 or self.errors)
        self.assertEqual(self.errors, [])
        self.assertEqual(self.window.zoom_percent, 125)
        self.window.goto_page(2)
        self.window.zoom_mode = 'percent'; self.window.zoom_percent = 200
        self.window.rotation = 90
        self.window.open_document(str(b))
        wait_for(lambda: self.window.displayed_page == 0 and self.window.page_count == 4)
        self.assertEqual(self.window.rotation, 0)
        self.assertEqual(self.window.zoom_percent, 125)
        self.window.open_document(str(a))
        wait_for(lambda: self.window.displayed_page == 2 and self.window.displayed_rotation == 90)
        self.assertEqual(self.window.zoom_percent, 200)
        self.assertEqual(self.errors, [])

    def test_toolbar_search_changes_persist_without_requiring_preferences_dialog(self):
        self.window.find_options['whole_words'].set_active(True)
        self.window.find_results_toggle.set_active(True)
        values = self.store.load()['search']
        self.assertTrue(values['whole_words'])
        self.assertTrue(values['show_results'])
        dialog = self.dialog()
        self.assertTrue(dialog.controls[('search', 'whole_words')].get_active())


if __name__ == '__main__':
    unittest.main()
