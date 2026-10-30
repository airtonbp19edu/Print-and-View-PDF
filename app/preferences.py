"""Validated application preferences, independent of GTK and PDF runtimes."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import time


DEFAULTS = {
    'appearance': 'system',
    'interface': {'remember_layout': True, 'sidebar_visible': True,
                  'ribbon_collapsed': True, 'window_width': 1180, 'window_height': 780},
    'reading': {'zoom_mode': 'fit-width', 'zoom_percent': 100, 'remember_document': False},
    'search': {'match_case': False, 'whole_words': False, 'ignore_accents': False,
               'join_hyphens': False, 'show_results': False},
}
SECTIONS = ('appearance', 'interface', 'reading', 'search')
ZOOM_MODES = ('fit-page', 'fit-width', 'percent')


def config_file():
    root = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config')
    return root / 'print-view-pdf' / 'preferences.json'


def _integer(value, default, low, high):
    return value if type(value) is int and low <= value <= high else default


def validated(raw):
    """Keep unfamiliar keys while normalizing the settings this version consumes."""
    result = copy.deepcopy(raw) if isinstance(raw, dict) else {}
    mode = result.get('appearance', result.get('theme', 'system'))
    if mode == 'auto':
        mode = 'system'
    result['appearance'] = mode if mode in ('system', 'light', 'dark') else 'system'
    result['theme'] = 'auto' if result['appearance'] == 'system' else result['appearance']
    for section in ('interface', 'reading', 'search'):
        values = result.get(section)
        values = values if isinstance(values, dict) else {}
        for key, default in DEFAULTS[section].items():
            value = values.get(key, default)
            if isinstance(default, bool):
                values[key] = value if type(value) is bool else default
            elif key == 'zoom_mode':
                values[key] = value if value in ZOOM_MODES else default
            else:
                bounds = {'window_width': (760, 3840), 'window_height': (500, 2160),
                          'zoom_percent': (25, 400)}[key]
                values[key] = _integer(value, default, *bounds)
        result[section] = values
    return result


class PreferencesStore:
    def __init__(self, path=None):
        self.path = Path(path) if path is not None else config_file()

    def load(self):
        try:
            raw = json.loads(self.path.read_text(encoding='utf-8'))
        except FileNotFoundError:
            raw = {}
            legacy = self.path.parent.parent / 'winux-pdf' / 'settings.json'
            try:
                old = json.loads(legacy.read_text(encoding='utf-8'))
                mode = old.get('appearance') if isinstance(old, dict) else None
                if mode in ('system', 'light', 'dark'):
                    raw['appearance'] = mode
                    self._write(validated(raw))
            except (OSError, ValueError, TypeError):
                pass
        except (OSError, ValueError, TypeError):
            raw = {}
        return validated(raw)

    def _write(self, values):
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd, temporary = tempfile.mkstemp(prefix='.settings-', suffix='.tmp', dir=self.path.parent)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as output:
                json.dump(values, output, ensure_ascii=False, indent=2)
                output.write('\n')
            os.replace(temporary, self.path)
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass

    def save(self, changes):
        """Merge into the newest file, preserving future keys and document records."""
        values = self.load()
        for section in SECTIONS:
            if section not in changes:
                continue
            if section == 'appearance':
                values[section] = changes[section]
            else:
                candidate = changes[section]
                if isinstance(candidate, dict):
                    values[section].update(copy.deepcopy(candidate))
        values = validated(values)
        self._write(values)
        return values

    @staticmethod
    def _document_identity(path):
        path = Path(path).resolve()
        stat = path.stat()
        key = hashlib.sha256(os.path.normcase(str(path)).encode('utf-8')).hexdigest()
        return key, [stat.st_size, stat.st_mtime_ns]

    def remember_document(self, path, state):
        values = self.load()
        if not values['reading']['remember_document']:
            return
        try:
            key, identity = self._document_identity(path)
        except OSError:
            return
        documents = values.get('document_states')
        documents = documents if isinstance(documents, dict) else {}
        documents[key] = {
            'identity': identity, 'page': _integer(state.get('page'), 0, 0, 10_000_000),
            'rotation': state.get('rotation') if type(state.get('rotation')) is int and
            state['rotation'] in (0, 90, 180, 270) else 0,
            'zoom_mode': state.get('zoom_mode') if state.get('zoom_mode') in ZOOM_MODES else 'fit-width',
            'zoom_percent': _integer(state.get('zoom_percent'), 100, 25, 400),
            'saved_at': time.time(),
        }
        def saved_at(item):
            value = item[1].get('saved_at', 0) if isinstance(item[1], dict) else 0
            return value if isinstance(value, (int, float)) else 0
        values['document_states'] = dict(sorted(documents.items(), key=saved_at, reverse=True)[:50])
        self._write(values)

    def document_state(self, path):
        values = self.load()
        if not values['reading']['remember_document']:
            return None
        try:
            key, identity = self._document_identity(path)
            documents = values.get('document_states', {})
            state = documents.get(key) if isinstance(documents, dict) else None
        except OSError:
            return None
        if not isinstance(state, dict) or state.get('identity') != identity:
            return None
        if (type(state.get('page')) is not int or not 0 <= state['page'] <= 10_000_000
                or type(state.get('rotation')) is not int or state['rotation'] not in (0, 90, 180, 270)
                or state.get('zoom_mode') not in ZOOM_MODES
                or _integer(state.get('zoom_percent'), None, 25, 400) is None):
            return None
        return copy.deepcopy(state)


class PreferencesDraft:
    """Applying establishes a new baseline; cancelling only discards the draft."""
    def __init__(self, store):
        self.store = store
        self.values = copy.deepcopy(store.load())

    def reset(self, section):
        if section not in SECTIONS:
            raise ValueError('Unknown preferences section')
        # Reset known settings only; keep data from newer versions intact.
        defaults = copy.deepcopy(DEFAULTS[section])
        if isinstance(defaults, dict):
            self.values[section].update(defaults)
        else:
            self.values[section] = defaults

    def apply(self):
        changes = {'appearance': self.values['appearance']}
        for section in ('interface', 'reading', 'search'):
            changes[section] = {key: self.values[section][key] for key in DEFAULTS[section]}
        committed = self.store.save(changes)
        self.values = copy.deepcopy(committed)
        return committed
