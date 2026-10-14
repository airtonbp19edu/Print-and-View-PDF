import json
import os
from pathlib import Path
import re

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

_provider = None
_system_dark = None


def load_theme(mode='light'):
    global _provider, _system_dark
    settings = Gtk.Settings.get_default()
    if _system_dark is None:
        _system_dark = settings.get_property('gtk-application-prefer-dark-theme')
    dark = mode == 'dark' or (mode == 'auto' and
            (_system_dark or 'dark' in settings.get_property('gtk-theme-name').lower()))
    settings.set_property('gtk-application-prefer-dark-theme', dark)
    css = (Path(__file__).parent / 'style.css').read_text()
    if dark:
        colors = {'#ffffff': '#252933', '#f3f4f6': '#20242c', '#f7f7f8': '#292e38',
                  '#fafafa': '#242832', '#fbfbfc': '#242832', '#202124': '#edf0f5',
                  '#34373c': '#e4e7ee', '#53565c': '#d3d8e2', '#4e5258': '#d3d8e2',
                  '#35393e': '#edf0f5', '#454a50': '#d3d8e2', '#3e4349': '#d3d8e2',
                  '#5c338a': '#c9a5ff', '#6a4097': '#b98cff'}
        def replace(match):
            color = match.group().lower()
            if color in colors: return colors[color]
            rgb = [int(color[i:i+2], 16) for i in (1, 3, 5)]
            if min(rgb) > 185: return '#434955' if max(rgb) - min(rgb) > 25 else '#303641'
            return color
        css = re.sub(r'#[0-9a-fA-F]{6}', replace, css)
        css += '''
window, label, image, entry, spinbutton, combobox button, button, checkbutton, radiobutton { color: #edf0f5; }
entry, spinbutton, combobox button, menu, menuitem, popover { background-color: #303641; color: #edf0f5; }
button { background-image: none; background-color: #303641; }
button:hover, menuitem:hover { background-color: #434b5a; }
scale trough { background-color: #596273; }
scale highlight { background-color: #b98cff; }
scale slider { background-image: none; background-color: #d3dbe9; border-color: #8993a4; }
checkbutton check, radiobutton radio { background-color: #303641; border-color: #abb5c5; color: #ffffff; }
checkbutton check:checked, radiobutton radio:checked { background-image: none; background-color: #8256bd; }
.muted { color: #b8c2d4; }
.page-frame { background: #ffffff; }
.app-mark, .presentation-toolbar label, .presentation-toolbar checkbutton label { color: #ffffff; }
button:disabled, label:disabled { color: #8993a4; }
'''
    provider = Gtk.CssProvider(); provider.load_from_data(css.encode())
    screen = Gdk.Screen.get_default()
    if _provider is not None: Gtk.StyleContext.remove_provider_for_screen(screen, _provider)
    Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    _provider = provider
    return dark


def preferences_path():
    root = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    return root / 'print-view-pdf' / 'preferences.json'


def read_theme():
    try:
        mode = json.loads(preferences_path().read_text()).get('theme', 'auto')
        return mode if mode in ('light', 'dark', 'auto') else 'auto'
    except (OSError, ValueError, AttributeError):
        return 'auto'


def save_theme(mode):
    path = preferences_path(); path.parent.mkdir(parents=True, exist_ok=True)
    try: settings = json.loads(path.read_text())
    except (OSError, ValueError): settings = {}
    if not isinstance(settings, dict): settings = {}
    settings['theme'] = mode
    temp = path.with_suffix('.tmp'); temp.write_text(json.dumps(settings) + '\n'); temp.replace(path)
