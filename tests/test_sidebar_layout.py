"""The side panel must never be narrower than its content, whatever the UI font."""
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'app'))
from main import PDFWindow, Gtk, GLib, load_css


def pump(seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        context = GLib.MainContext.default()
        while context.pending():
            context.iteration(False)
        time.sleep(.01)


@unittest.skipUnless(os.name == 'nt' or os.environ.get('DISPLAY'), 'Requires a graphical session')
class SidebarLayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        env = patch.dict(os.environ, {'XDG_CONFIG_HOME': str(Path(self.temp.name) / 'config')})
        env.start(); self.addCleanup(env.stop)
        quit_patch = patch.object(Gtk, 'main_quit'); quit_patch.start(); self.addCleanup(quit_patch.stop)
        settings = Gtk.Settings.get_default()
        self.font = settings.get_property('gtk-font-name')
        self.addCleanup(settings.set_property, 'gtk-font-name', self.font)
        load_css()

    def tearDown(self):
        self.window.destroy()
        self.temp.cleanup()

    def open_with_font(self, font):
        Gtk.Settings.get_default().set_property('gtk-font-name', font)
        self.window = PDFWindow()
        pump(1.5)

    def test_rail_and_panel_are_not_clipped_with_wide_or_large_fonts(self):
        for font in ('Sans 10', 'DejaVu Sans 10', 'DejaVu Sans 13', 'Sans 16'):
            with self.subTest(font=font):
                self.open_with_font(font)
                needed = self.window.sidebar_container.get_preferred_width()[0]
                self.assertGreaterEqual(self.window.body_paned.get_position(), needed)
                self.assertGreaterEqual(self.window.sidebar_container.get_allocated_width(), needed)
                for button in self.window.sidebar_rail_buttons:
                    self.assertGreaterEqual(button.get_allocated_width(), button.get_preferred_width()[0])
                self.window.destroy()
        self.window = PDFWindow()


if __name__ == '__main__':
    unittest.main()
