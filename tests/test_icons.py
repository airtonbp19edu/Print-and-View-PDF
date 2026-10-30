"""Every symbolic icon the interface asks for must exist on a stock Adwaita system."""
import os
from pathlib import Path
import re
import sys
import unittest

APP = Path(__file__).resolve().parents[1] / 'app'
sys.path.insert(0, str(APP))
from main import Gtk, register_app_icons


@unittest.skipUnless(os.name == 'nt' or os.environ.get('DISPLAY'), 'Requires a graphical session')
class IconAvailabilityTests(unittest.TestCase):
    def test_referenced_symbolic_icons_resolve_without_extra_themes(self):
        names = set()
        for source in APP.glob('*.py'):
            names.update(re.findall(r"['\"]([a-z0-9]+(?:-[a-z0-9]+)*-symbolic)['\"]",
                                    source.read_text(encoding='utf-8')))
        self.assertGreater(len(names), 20)
        register_app_icons()
        theme = Gtk.IconTheme.new()
        theme.set_custom_theme('Adwaita')
        theme.set_search_path([*Gtk.IconTheme.get_default().get_search_path()])
        missing = sorted(name for name in names if not theme.has_icon(name))
        self.assertEqual(missing, [], 'Icons missing from Adwaita and from the application')

    def test_application_icons_render_as_symbolic(self):
        register_app_icons()
        theme = Gtk.IconTheme.get_default()
        for name in ('zoom-fit-width-symbolic', 'application-pdf-symbolic'):
            info = theme.lookup_icon(name, 16, 0)
            self.assertIsNotNone(info, name)
            self.assertTrue(info.get_filename().endswith(name + '.svg'))
            self.assertIsNotNone(info.load_symbolic(Gtk.StyleContext().get_color(Gtk.StateFlags.NORMAL))[0])


if __name__ == '__main__':
    unittest.main()
