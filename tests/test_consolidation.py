import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from test_regressions import APP
sys.path.insert(0, str(APP))
import rendering
from cancel_state import set_event


class ConsolidationTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get('DISPLAY'), 'Requires an X display')
    def test_fresh_system_theme_initializes_and_migrates_legacy(self):
        with tempfile.TemporaryDirectory() as temp:
            env = {**os.environ, 'XDG_CONFIG_HOME': temp}
            code = (f'import sys; sys.path.insert(0,{str(APP)!r}); '
                    'from appearance import AppearanceController; '
                    f'c=AppearanceController({str(APP)!r}); assert c.mode=="system"; c.close()')
            subprocess.run([sys.executable, '-c', code], env=env, check=True, timeout=5)
            legacy = Path(temp) / 'winux-pdf/settings.json'
            legacy.parent.mkdir(); legacy.write_text('{"appearance":"dark"}')
            code = (f'import sys; sys.path.insert(0,{str(APP)!r}); '
                    'from themes import read_theme; assert read_theme()=="dark"')
            subprocess.run([sys.executable, '-c', code], env=env, check=True, timeout=5)
            self.assertTrue((Path(temp) / 'print-view-pdf/preferences.json').is_file())

    def test_active_process_cancellation(self):
        event = threading.Event()
        trigger = threading.Timer(.2, event.set)
        set_event(event); trigger.start(); started = time.monotonic()
        try:
            with self.assertRaisesRegex(RuntimeError, 'cancelada'):
                rendering._run([sys.executable, '-c', 'import time; time.sleep(10)'], timeout=15)
            self.assertLess(time.monotonic() - started, 2)
        finally:
            set_event(None); trigger.join()
