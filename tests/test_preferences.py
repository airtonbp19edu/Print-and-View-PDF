import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

APP = Path(__file__).resolve().parents[1] / 'app'
sys.path.insert(0, str(APP))
from preferences import DEFAULTS, PreferencesStore, PreferencesDraft


class PreferencesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.path = self.root / 'print-view-pdf/preferences.json'
        self.store = PreferencesStore(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_migrates_theme_and_preserves_future_keys(self):
        old = self.root / 'winux-pdf/settings.json'
        old.parent.mkdir()
        old.write_text('{"appearance":"dark"}')
        self.assertEqual(self.store.load()['appearance'], 'dark')
        self.assertTrue(self.path.is_file())
        raw = self.store.load()
        raw.update({'future_section': {'name': 'unchanged'}, 'schema_version': 12})
        raw['reading']['future_option'] = 42
        self.path.write_text(json.dumps(raw))
        self.store.save({'appearance': 'light', 'reading': {'zoom_percent': 175}})
        values = json.loads(self.path.read_text())
        self.assertEqual(values['future_section'], {'name': 'unchanged'})
        self.assertEqual(values['reading']['future_option'], 42)
        self.assertEqual(values['schema_version'], 12)
        self.assertEqual(values['theme'], 'light')

    def test_rejects_invalid_types_and_unsafe_ranges(self):
        self.path.parent.mkdir()
        self.path.write_text(json.dumps({'appearance': 'pink', 'interface': {
            'remember_layout': 'false', 'window_width': -1},
            'reading': {'zoom_mode': 'unsafe', 'zoom_percent': True}, 'search': []}))
        values = self.store.load()
        self.assertEqual(values['appearance'], 'system')
        self.assertEqual(values['reading'], DEFAULTS['reading'])
        self.assertEqual(values['interface']['window_width'], 1180)
        self.assertIs(values['interface']['remember_layout'], True)
        self.assertEqual(values['search'], DEFAULTS['search'])

    def test_malformed_json_uses_defaults_without_overwriting_on_read(self):
        self.path.parent.mkdir()
        self.path.write_text('{broken')
        self.assertEqual(self.store.load()['reading'], DEFAULTS['reading'])
        self.assertEqual(self.path.read_text(), '{broken')

    def test_draft_cancel_reset_and_apply_baseline(self):
        self.store.save({'appearance': 'dark', 'search': {'ignore_accents': True}})
        before = self.path.read_bytes()
        draft = PreferencesDraft(self.store)
        draft.values['appearance'] = 'light'
        draft.values['reading']['zoom_percent'] = 200
        draft.reset('reading')
        self.assertEqual(draft.values['reading'], DEFAULTS['reading'])
        self.assertEqual(self.path.read_bytes(), before)
        self.assertTrue(draft.values['search']['ignore_accents'])
        draft.apply()
        draft.values['appearance'] = 'dark'  # discarded by closing without apply
        self.assertEqual(self.store.load()['appearance'], 'light')

    def test_atomic_write_failure_preserves_last_saved_file(self):
        self.store.save({'appearance': 'dark'})
        before = self.path.read_bytes()
        with patch('preferences.os.replace', side_effect=OSError('disk unavailable')):
            with self.assertRaises(OSError):
                self.store.save({'appearance': 'light'})
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.path.parent.glob('.settings-*')), [])

    def test_document_state_is_separate_and_invalidated_after_file_changes(self):
        a = self.root / 'a.pdf'; b = self.root / 'b.pdf'
        a.write_bytes(b'first'); b.write_bytes(b'second')
        self.store.save({'reading': {'remember_document': True, 'zoom_percent': 120}})
        state = {'page': 7, 'rotation': 90, 'zoom_mode': 'percent', 'zoom_percent': 200}
        self.store.remember_document(a, state)
        self.assertEqual(self.store.document_state(a)['page'], 7)
        self.assertEqual(self.store.document_state(a)['zoom_percent'], 200)
        self.assertIsNone(self.store.document_state(b))
        self.assertEqual(self.store.load()['reading']['zoom_percent'], 120)
        a.write_bytes(b'changed document')
        self.assertIsNone(self.store.document_state(a))
        a.unlink()
        self.assertIsNone(self.store.document_state(a))

    def test_document_memory_is_opt_in_and_bounded(self):
        document = self.root / 'a.pdf'; document.write_bytes(b'pdf')
        self.store.remember_document(document, {'page': 2})
        self.assertFalse(self.path.exists())
        self.store.save({'reading': {'remember_document': True}})
        for index in range(53):
            path = self.root / f'doc-{index}.pdf'; path.write_bytes(b'pdf')
            self.store.remember_document(path, {'page': index})
        self.assertEqual(len(self.store.load()['document_states']), 50)
        self.store.save({'reading': {'remember_document': False}})
        self.assertIsNone(self.store.document_state(self.root / 'doc-52.pdf'))

    def test_apply_merges_document_state_saved_after_draft_was_opened(self):
        self.store.save({'reading': {'remember_document': True, 'future_option': 'old'}})
        draft = PreferencesDraft(self.store)
        self.store.save({'reading': {'future_option': 'newer'}})
        doc = self.root / 'a.pdf'; doc.write_bytes(b'pdf')
        self.store.remember_document(doc, {'page': 8})
        draft.values['search']['whole_words'] = True
        draft.apply()
        self.assertEqual(self.store.document_state(doc)['page'], 8)
        self.assertTrue(self.store.load()['search']['whole_words'])
        self.assertEqual(self.store.load()['reading']['future_option'], 'newer')


if __name__ == '__main__':
    unittest.main()
