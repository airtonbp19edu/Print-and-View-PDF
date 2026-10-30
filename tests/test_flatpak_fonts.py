"""The Flatpak fontconfig must keep the interface in a sans-serif face."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
sys.path.insert(0, str(ROOT / 'scripts'))
DEJAVU = Path('/usr/share/fonts/truetype/dejavu')


@unittest.skipUnless(shutil.which('fc-match') and (DEJAVU / 'DejaVuSans.ttf').is_file(),
                     'Requires fontconfig and the DejaVu fonts')
class FlatpakFontconfigTests(unittest.TestCase):
    def match(self, pattern, system):
        from build_flatpak import fontconfig_xml
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / 'fonts.conf'
            config.write_text(fontconfig_xml(bundled=str(DEJAVU), system=str(system)), encoding='utf-8')
            env = dict(os.environ, FONTCONFIG_FILE=str(config), XDG_CACHE_HOME=temp)
            result = subprocess.run(['fc-match', '-f', '%{family[0]}', pattern], env=env,
                                    capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_generic_families_fall_back_to_dejavu_without_runtime_configuration(self):
        # No runtime fonts.conf: other fonts on the machine must not win by sort order.
        missing = Path('/nonexistent/print-view-pdf/fonts.conf')
        self.assertEqual(self.match('Sans', missing), 'DejaVu Sans')
        self.assertEqual(self.match('sans-serif', missing), 'DejaVu Sans')
        self.assertEqual(self.match('serif', missing), 'DejaVu Serif')
        if (DEJAVU / 'DejaVuSansMono.ttf').is_file():
            self.assertEqual(self.match('monospace', missing), 'DejaVu Sans Mono')

    @unittest.skipUnless(Path('/etc/fonts/fonts.conf').is_file(), 'Requires the system fontconfig')
    def test_runtime_configuration_keeps_priority(self):
        system = Path('/etc/fonts/fonts.conf')
        default = subprocess.run(['fc-match', '-f', '%{family[0]}', 'sans-serif'],
                                 capture_output=True, text=True, timeout=120).stdout.strip()
        self.assertEqual(self.match('sans-serif', system), default)

    def test_generated_configuration_is_wellformed(self):
        import xml.etree.ElementTree as ET
        from build_flatpak import fontconfig_xml
        root = ET.fromstring(fontconfig_xml().split('?>', 1)[1].replace(
            '<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">', ''))
        self.assertEqual(root.tag, 'fontconfig')
        self.assertEqual(root.find('include').text, '/etc/fonts/fonts.conf')
        self.assertIn('/app/share/fonts', [d.text for d in root.findall('dir')])


if __name__ == '__main__':
    unittest.main()
