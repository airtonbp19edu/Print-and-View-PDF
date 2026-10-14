"""Theme compatibility API backed by the consolidated Winux controller."""
from pathlib import Path
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk
from appearance import AppearanceController, config_file, read_mode, save_mode

_controller = None
_controller_config = None
_light_provider = None
_loading = False


def preferences_path():
    return config_file()


def read_theme():
    mode = read_mode()
    return 'auto' if mode == 'system' else mode


def save_theme(mode):
    save_mode('system' if mode == 'auto' else mode)


def load_theme(mode='auto'):
    global _controller, _controller_config, _light_provider, _loading
    if _loading:
        return False
    _loading = True
    try:
        if _light_provider is None:
            _light_provider = Gtk.CssProvider()
            _light_provider.load_from_path(str(Path(__file__).parent / 'style.css'))
            Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), _light_provider,
                                                     Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        if _controller is None or _controller_config != config_file():
            if _controller is not None:
                _controller.close()
            _controller = AppearanceController(Path(__file__).parent)
            _controller_config = config_file()
        _controller.mode = 'system' if mode == 'auto' else mode
        _controller.apply()
        return bool(Gtk.Settings.get_default().get_property('gtk-application-prefer-dark-theme'))
    finally:
        _loading = False
