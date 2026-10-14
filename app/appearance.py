"""Persistent light/dark/system appearance selection for Print&View PDF (GTK 3)."""
import json
import os
import tempfile
from pathlib import Path

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Gio', '2.0')
from gi.repository import Gtk, Gdk, Gio

APPEARANCE_OPTIONS = ('system', 'light', 'dark')
def config_file():
    root = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config')
    return root / 'print-view-pdf' / 'preferences.json'


def read_mode(path=None):
    path = Path(path) if path is not None else config_file()
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        mode = data.get('appearance', data.get('theme', 'system'))
        if mode == 'auto': mode = 'system'
        return mode if mode in APPEARANCE_OPTIONS else 'system'
    except (OSError, ValueError, TypeError, AttributeError):
        legacy = path.parent.parent / 'winux-pdf' / 'settings.json'
        if legacy != path and legacy.is_file():
            try:
                mode = json.loads(legacy.read_text()).get('appearance', 'system')
                if mode in APPEARANCE_OPTIONS:
                    save_mode(mode, path)
                    return mode
            except (OSError, ValueError, AttributeError):
                pass
        return 'system'


def save_mode(mode, path=None):
    """Preserve settings from future versions instead of overwriting the file."""
    if mode not in APPEARANCE_OPTIONS:
        raise ValueError('Invalid appearance mode')
    path = Path(path) if path is not None else config_file()
    try:
        old = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(old, dict):
            old = {}
    except (OSError, ValueError, TypeError):
        old = {}
    old['appearance'] = mode
    old['theme'] = 'auto' if mode == 'system' else mode
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    fd, temp = tempfile.mkstemp(prefix='.settings-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(old, out, ensure_ascii=False, indent=2)
            out.write('\n')
        os.replace(temp, path)
    finally:
        try: os.unlink(temp)
        except FileNotFoundError: pass


class AppearanceController:
    def __init__(self, app_dir):
        self.mode = read_mode()
        self.app_dir = Path(app_dir)
        self.settings = Gtk.Settings.get_default()
        self.provider = Gtk.CssProvider()
        self.screen = Gdk.Screen.get_default()
        self._provider_attached = False
        self._applying = False
        self.system_settings = None
        self._handlers = []
        try:
            schema = Gio.SettingsSchemaSource.get_default().lookup('org.gnome.desktop.interface', True)
            if schema is not None:
                self.system_settings = Gio.Settings.new('org.gnome.desktop.interface')
                if schema.has_key('color-scheme'):
                    self._handlers.append((self.system_settings, self.system_settings.connect('changed::color-scheme', self._system_changed)))
                if schema.has_key('gtk-theme'):
                    self._handlers.append((self.system_settings, self.system_settings.connect('changed::gtk-theme', self._system_changed)))
        except (TypeError, ValueError, RuntimeError):
            self.system_settings = None
        if self.settings is not None:
            self._handlers.append((self.settings, self.settings.connect('notify::gtk-theme-name', self._system_changed)))
        self.apply()

    def _system_dark(self):
        if self.system_settings:
            try:
                scheme = self.system_settings.get_string('color-scheme')
                if scheme == 'prefer-dark':
                    return True
                if scheme == 'prefer-light':
                    return False
            except (ValueError, RuntimeError):
                pass
        # gtk-theme-name is the GTK 3 fallback on non-GNOME desktops.
        theme = ''
        if self.settings is not None:
            theme = str(self.settings.get_property('gtk-theme-name') or '')
        return 'dark' in theme.lower() or 'dark' in os.environ.get('GTK_THEME', '').lower()

    def _system_changed(self, *_args):
        if self.mode == 'system' and not self._applying:
            self.apply()

    def apply(self):
        if self._applying:
            return
        self._applying = True
        try:
            return self._apply()
        finally:
            self._applying = False

    def _apply(self):
        dark = self.mode == 'dark' or (self.mode == 'system' and self._system_dark())
        if self.settings is not None:
            # Explicit light/dark must not inherit a user's unrelated GTK theme.
            # Automatic mode restores the original GTK theme choice.
            if not hasattr(self, '_original_theme'):
                self._original_theme = self.settings.get_property('gtk-theme-name')
            theme = self._original_theme if self.mode == 'system' else 'Adwaita'
            if self.settings.get_property('gtk-theme-name') != theme:
                self.settings.set_property('gtk-theme-name', theme)
            if self.settings.get_property('gtk-application-prefer-dark-theme') != dark:
                self.settings.set_property('gtk-application-prefer-dark-theme', dark)
        if self.screen is None:
            return
        if dark:
            css_file = self.app_dir / 'style-dark.css'
            if css_file.exists():
                self.provider.load_from_path(str(css_file))
                if not self._provider_attached:
                    Gtk.StyleContext.add_provider_for_screen(
                        self.screen, self.provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)
                    self._provider_attached = True
        elif self._provider_attached:
            Gtk.StyleContext.remove_provider_for_screen(self.screen, self.provider)
            self._provider_attached = False

    def set_mode(self, mode):
        if mode not in APPEARANCE_OPTIONS:
            return
        self.mode = mode
        self.apply()
        save_mode(mode)

    def close(self):
        for obj, handler in self._handlers:
            obj.disconnect(handler)
        self._handlers.clear()
        if self._provider_attached and self.screen is not None:
            Gtk.StyleContext.remove_provider_for_screen(self.screen, self.provider)
            self._provider_attached = False
