#!/usr/bin/env python3
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Pango

from async_core import BackgroundRunner
import cups_backend as cups
from print_window import PrintWindow
from presentation import PresentationWindow, LASER_COLORS
from rendering import render_page, render_page_to_png, extract_page_text, extract_page_words
from pdf_panels import inspect_document_panels
from search_engine import TextSearchIndex
from page_cache import PageCache
from themes import load_theme, read_theme, save_theme

APP_DIR = Path(__file__).resolve().parent
WORKER = APP_DIR / 'worker_cli.py'

GLib.set_prgname('print-view-pdf')
GLib.set_application_name('Print&View PDF')
try:
    Gdk.set_program_class('print-view-pdf')
except Exception:
    pass
Gtk.Window.set_default_icon_name('print-view-pdf')


def load_css():
    load_theme(read_theme())


class PDFWindow(Gtk.Window):
    def __init__(self, initial_file=None):
        super().__init__(title='Print&View PDF')
        self.set_default_size(1180, 780)
        self.set_size_request(760, 500)
        self.set_resizable(True)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_role('print-view-pdf')
        try:
            self.set_wmclass('print-view-pdf', 'print-view-pdf')
        except Exception:
            pass
        self.set_icon_name('print-view-pdf')
        self.connect('destroy', self._on_destroy)
        self.connect('key-press-event', self._on_key)
        self.connect('size-allocate', self._on_resize)

        self.runner = BackgroundRunner(workers=4)
        self.render_runner = BackgroundRunner(workers=1, latest_only=True)
        self.prefetch_runner = BackgroundRunner(workers=1, latest_only=True)
        self.page_cache = PageCache()
        self.prefetch_tasks = {}
        self.theme_mode = read_theme()
        load_theme(self.theme_mode)
        self.theme_signal = Gtk.Settings.get_default().connect('notify::gtk-theme-name', self._system_theme_changed)
        self.cache_dir = tempfile.mkdtemp(prefix='print-view-pdf-cache-')
        self.filepath = None
        self.page_count = 0
        self.page_sizes = []
        self.metadata = {}
        self.page = 0
        self.rotation = 0
        self.zoom_mode = 'fit-page'  # fit-page, fit-width, percent
        self.zoom_percent = 100
        self.render_serial = 0
        self.resize_timer = None
        self.zoom_slider_timer = None
        self._zoom_scale_sync = False
        self.sidebar_visible = True
        self.sidebar_panel_visible = True
        self.ribbon_collapsed = True
        self.read_mode = False
        self.search_timer = None
        self.search_hits = []
        self.search_pos = -1
        self.search_cancel = threading.Event()
        self.search_index = None
        self.search_scanned = 0
        self.search_running = False
        self.thumb_rows = {}
        self.thumb_requested = set()
        self.thumb_build_next = 0
        self.laser_color = 'Vermelho'
        # Interactive reading tools inspired by familiar desktop PDF readers.
        self.active_tool = 'hand'
        self._tool_sync = False
        self.tool_buttons = {}
        self.current_pixbuf = None
        self.displayed_page = None
        self.displayed_rotation = None
        self.rendered_pixbuf = None
        self.selection_rect = None
        self.drag_start = None
        self.hand_origin = None
        self.loupe_pos = None
        self.measure_result = None
        self.text_word_cache = {}
        self.selected_words = []
        self.selection_data = None

        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.root)
        self.root.pack_start(self._build_ribbon(), False, False, 0)
        self.root.pack_start(self._build_document_tabs(), False, False, 0)
        self.root.pack_start(self._build_findbar(), False, False, 0)
        self.root.pack_start(self._build_body(), True, True, 0)
        self.root.pack_start(self._build_status(), False, False, 0)

        self._set_actions_enabled(False)
        self.show_all()
        self.find_revealer.set_reveal_child(False)
        if initial_file:
            GLib.idle_add(lambda: (self.open_document(initial_file), False)[1])

    # ---------- Compact document shell ----------
    def _command_button(self, icon, label, callback, tooltip=None, compact=True):
        btn = Gtk.Button()
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL if compact else Gtk.Orientation.VERTICAL,
                          spacing=5 if compact else 2)
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON if compact else Gtk.IconSize.LARGE_TOOLBAR)
        content.pack_start(image, False, False, 0)
        lbl = Gtk.Label(label=label)
        content.pack_start(lbl, False, False, 0)
        btn.add(content)
        btn.set_relief(Gtk.ReliefStyle.NONE)
        if tooltip:
            btn.set_tooltip_text(tooltip)
        btn.connect('clicked', callback)
        btn.get_style_context().add_class('ribbon-command-small' if compact else 'ribbon-command')
        self.action_widgets.append(btn)
        return btn

    def _command_toggle(self, icon, label, tool, tooltip=None, compact=True):
        btn = Gtk.ToggleButton()
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL if compact else Gtk.Orientation.VERTICAL,
                          spacing=5 if compact else 2)
        content.pack_start(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON if compact else Gtk.IconSize.LARGE_TOOLBAR), False, False, 0)
        content.pack_start(Gtk.Label(label=label), False, False, 0)
        btn.add(content)
        btn.set_relief(Gtk.ReliefStyle.NONE)
        if tooltip:
            btn.set_tooltip_text(tooltip)
        btn.connect('toggled', self._tool_toggled, tool)
        btn.get_style_context().add_class('ribbon-command-small' if compact else 'ribbon-command')
        self.tool_buttons.setdefault(tool, []).append(btn)
        self.action_widgets.append(btn)
        return btn

    def _ribbon_group(self, title, widgets, vertical=False):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        outer.get_style_context().add_class('ribbon-group')
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL if vertical else Gtk.Orientation.HORIZONTAL,
                       spacing=2, margin=1)
        for w in widgets:
            body.pack_start(w, False, False, 0)
        outer.pack_start(body, True, True, 0)
        cap = Gtk.Label(label=title)
        cap.get_style_context().add_class('ribbon-group-title')
        outer.pack_end(cap, False, False, 0)
        return outer

    def _ribbon_page(self, groups):
        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        sc.get_style_context().add_class('ribbon-page-scroll')
        row = Gtk.Box(spacing=0, margin=1)
        for i, group in enumerate(groups):
            row.pack_start(group, False, False, 0)
            if i != len(groups)-1:
                sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
                sep.get_style_context().add_class('ribbon-separator')
                row.pack_start(sep, False, False, 2)
        sc.add(row)
        return sc

    def _select_ribbon_tab(self, name):
        if not hasattr(self, 'ribbon_stack'):
            return
        self.ribbon_stack.set_visible_child_name(name)
        for key, btn in self.ribbon_tab_buttons.items():
            ctx = btn.get_style_context()
            if key == name:
                ctx.add_class('active-ribbon-tab')
            else:
                ctx.remove_class('active-ribbon-tab')

    def _activate_ribbon_tab(self, name):
        self._select_ribbon_tab(name)
        if self.ribbon_collapsed:
            self._toggle_ribbon_stack()

    def _build_ribbon(self):
        self.action_widgets = []
        self.tool_buttons = {}
        self.ribbon_tab_buttons = {}

        shell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        shell.get_style_context().add_class('ribbon-shell')

        # Quick access bar: keeps frequent actions in a compact command row.
        quick = Gtk.Box(spacing=1, margin_start=5, margin_end=5, margin_top=2, margin_bottom=2)
        quick.get_style_context().add_class('quick-access')
        app_mark = Gtk.Label(label='P')
        app_mark.get_style_context().add_class('app-mark')
        quick.pack_start(app_mark, False, False, 4)
        quick.pack_start(self._command_button('document-open-symbolic', 'Abrir', self._choose_open, compact=True), False, False, 0)
        quick.pack_start(self._command_button('document-save-as-symbolic', 'Salvar', self._save_copy, compact=True), False, False, 0)
        quick.pack_start(self._command_button('document-print-symbolic', 'Imprimir', self._print, compact=True), False, False, 0)
        quick.pack_start(self._command_button('dialog-information-symbolic', 'Propriedades', self._properties, compact=True), False, False, 0)
        quick.pack_start(self._command_button('window-close-symbolic', 'Fechar', self._close_document, compact=True), False, False, 0)
        title = Gtk.Label(label='Print&View PDF')
        title.get_style_context().add_class('quick-title')
        quick.pack_start(title, True, True, 10)
        self.theme_combo = Gtk.ComboBoxText()
        for key, label in [('auto', 'Tema: automático'), ('light', 'Tema: claro'), ('dark', 'Tema: escuro')]:
            self.theme_combo.append(key, label)
        self.theme_combo.set_active_id(self.theme_mode)
        self.theme_combo.connect('changed', self._theme_changed)
        quick.pack_end(self.theme_combo, False, False, 4)
        shell.pack_start(quick, False, False, 0)

        # Tab strip. Only tabs with real functionality are exposed.
        tabbar = Gtk.Box(spacing=0)
        tabbar.get_style_context().add_class('ribbon-tabbar')
        for key, label in [
            ('file','Arquivo'), ('home','Início'), ('comment','Comentário'),
            ('view','Exibir'), ('tools','Ferramentas'), ('presentation','Apresentação')]:
            if key == 'file':
                menu = Gtk.Menu()
                for text, callback in (
                    ('Abrir PDF…', self._choose_open), ('Salvar cópia…', self._save_copy),
                    ('Imprimir…', self._print), ('Propriedades do documento', self._properties),
                    ('Fechar PDF', self._close_document)):
                    item = Gtk.MenuItem(label=text)
                    # Defer so the popup menu releases its grab before any modal
                    # window or dialog opens.
                    item.connect('activate', lambda _i, cb=callback: GLib.idle_add(lambda: (cb(), False)[1]))
                    menu.append(item)
                menu.show_all()
                b = Gtk.MenuButton(label=label)
                b.set_popup(menu)
                b.set_relief(Gtk.ReliefStyle.NONE)
                b.get_style_context().add_class('ribbon-tab')
            else:
                b = Gtk.Button(label=label)
                b.set_relief(Gtk.ReliefStyle.NONE)
                b.get_style_context().add_class('ribbon-tab')
                b.connect('clicked', lambda _b, k=key: self._activate_ribbon_tab(k))
            tabbar.pack_start(b, False, False, 0)
            self.ribbon_tab_buttons[key] = b
        self.ribbon_collapse_btn = Gtk.ToggleButton()
        self.ribbon_collapse_btn.set_relief(Gtk.ReliefStyle.NONE)
        self.ribbon_collapse_btn.set_image(Gtk.Image.new_from_icon_name('pan-up-symbolic', Gtk.IconSize.MENU))
        self.ribbon_collapse_btn.set_tooltip_text('Ocultar/mostrar faixa de comandos (Ctrl+F1)')
        self.ribbon_collapse_btn.get_style_context().add_class('ribbon-collapse')
        self.ribbon_collapse_btn.connect('toggled', self._toggle_ribbon_stack)
        tabbar.pack_end(self.ribbon_collapse_btn, False, False, 3)
        shell.pack_start(tabbar, False, False, 0)

        self.ribbon_stack = Gtk.Stack()
        self.ribbon_stack.set_transition_type(Gtk.StackTransitionType.NONE)
        try: self.ribbon_stack.set_homogeneous(False)
        except Exception: pass
        self.ribbon_stack.get_style_context().add_class('ribbon-stack')

        # HOME — compact one-row navigation/zoom groups to preserve document space.
        nav_col = Gtk.Box(spacing=2)
        nav_col.pack_start(self._command_button('go-first-symbolic','Primeira',lambda *_: self.goto_page(0), compact=True), False, False, 0)
        nav_col.pack_start(self._command_button('go-previous-symbolic','Anterior',lambda *_: self.goto_page(self.page-1), compact=True), False, False, 0)
        self.page_entry = Gtk.Entry(); self.page_entry.set_width_chars(4); self.page_entry.set_text('0')
        self.page_entry.connect('activate', self._page_entry_activate)
        self.page_entry.connect('focus-out-event', lambda *_: (self._page_entry_activate(self.page_entry), False)[1])
        nav_col.pack_start(self.page_entry, False, False, 1)
        nav_col.pack_start(Gtk.Label(label='/'), False, False, 0)
        self.page_total_top = Gtk.Label(label='0')
        nav_col.pack_start(self.page_total_top, False, False, 0)
        nav_col.pack_start(self._command_button('go-next-symbolic','Próxima',lambda *_: self.goto_page(self.page+1), compact=True), False, False, 0)
        nav_col.pack_start(self._command_button('go-last-symbolic','Última',lambda *_: self.goto_page(self.page_count-1), compact=True), False, False, 0)

        zoom_col = Gtk.Box(spacing=2)
        zoom_col.pack_start(self._command_button('zoom-out-symbolic','−',lambda *_: self._zoom_delta(-25), compact=True), False, False, 0)
        self.zoom_label_top = Gtk.Label(label='100%'); self.zoom_label_top.set_width_chars(7)
        zoom_col.pack_start(self.zoom_label_top, False, False, 0)
        zoom_col.pack_start(self._command_button('zoom-in-symbolic','+',lambda *_: self._zoom_delta(25), compact=True), False, False, 0)
        zoom_col.pack_start(self._command_button('zoom-fit-best-symbolic','Página',self._fit_page, compact=True), False, False, 0)
        zoom_col.pack_start(self._command_button('zoom-fit-width-symbolic','Largura',self._fit_width, compact=True), False, False, 0)

        hand_home = self._command_toggle('pan-down-symbolic','Mão','hand','Arraste a página para navegar')
        select_home = self._command_toggle('edit-select-all-symbolic','Selecionar','select','Selecione texto por região')
        snapshot_home = self._command_toggle('camera-photo-symbolic','Snapshot','snapshot','Copie uma região como imagem')
        self.ribbon_stack.add_named(self._ribbon_page([
            self._ribbon_group('Arquivo', [
                self._command_button('document-open-symbolic','Abrir',self._choose_open),
                self._command_button('document-print-symbolic','Imprimir',self._print),
            ]),
            self._ribbon_group('Selecionar', [hand_home, select_home, snapshot_home]),
            self._ribbon_group('Navegação', [nav_col]),
            self._ribbon_group('Zoom', [zoom_col]),
            self._ribbon_group('Localizar', [self._command_button('edit-find-symbolic','Localizar',self._show_find)]),
            self._ribbon_group('Apresentação', [self._command_button('media-playback-start-symbolic','Apresentar',self._present)]),
        ]), 'home')

        # COMMENT — actions that are actually implemented in the current engine.
        self.ribbon_stack.add_named(self._ribbon_page([
            self._ribbon_group('Painéis', [
                self._command_button('mail-message-new-symbolic','Comentários',lambda *_: self._show_side_panel(2)),
                self._command_button('user-bookmarks-symbolic','Marcadores',lambda *_: self._show_side_panel(1)),
            ]),
            self._ribbon_group('Captura e revisão', [
                self._command_toggle('camera-photo-symbolic','Snapshot','snapshot','Copiar uma área da página'),
                self._command_toggle('accessories-calculator-symbolic','Medir','measure','Medir distância no PDF'),
                self._command_button('edit-copy-symbolic','Copiar texto',self._copy_page_text),
            ]),
        ]), 'comment')

        # VIEW
        self.ribbon_stack.add_named(self._ribbon_page([
            self._ribbon_group('Painéis', [
                self._command_button('view-list-symbolic','Painel',self._toggle_sidebar),
                self._command_button('view-list-symbolic','Páginas',lambda *_: self._show_side_panel(0)),
                self._command_button('user-bookmarks-symbolic','Marcadores',lambda *_: self._show_side_panel(1)),
                self._command_button('mail-message-new-symbolic','Comentários',lambda *_: self._show_side_panel(2)),
                self._command_button('view-grid-symbolic','Camadas',lambda *_: self._show_side_panel(3)),
            ]),
            self._ribbon_group('Visualização', [
                self._command_button('object-rotate-left-symbolic','Girar ←',lambda *_: self._rotate(-90)),
                self._command_button('object-rotate-right-symbolic','Girar →',lambda *_: self._rotate(90)),
                self._command_button('zoom-original-symbolic','100%',self._zoom_100),
                self._command_button('zoom-fit-best-symbolic','Ajustar',self._fit_page),
                self._command_button('zoom-fit-width-symbolic','Largura',self._fit_width),
            ]),
            self._ribbon_group('Janela', [
                self._command_button('view-fullscreen-symbolic','Tela cheia',self._fullscreen_toggle),
                self._command_button('view-restore-symbolic','Modo leitura',self._reading_mode_toggle),
                self._command_button('media-playback-start-symbolic','Apresentação',self._present),
            ]),
        ]), 'view')

        # TOOLS
        self.ribbon_stack.add_named(self._ribbon_page([
            self._ribbon_group('Ferramentas básicas', [
                self._command_toggle('pan-down-symbolic','Mão','hand'),
                self._command_toggle('edit-select-all-symbolic','Selecionar texto','select'),
                self._command_toggle('camera-photo-symbolic','Snapshot','snapshot'),
                self._command_toggle('zoom-in-symbolic','Lupa','loupe'),
                self._command_toggle('accessories-calculator-symbolic','Medir','measure'),
            ]),
            self._ribbon_group('Conteúdo', [
                self._command_button('edit-find-symbolic','Localizar',self._show_find),
                self._command_button('edit-copy-symbolic','Copiar página',self._copy_page_text),
                self._command_button('image-x-generic-symbolic','Exportar PNG',self._export_png),
            ]),
            self._ribbon_group('Documento', [self._command_button('dialog-information-symbolic','Propriedades',self._properties)]),
        ]), 'tools')

        # PRESENTATION
        pres_color = Gtk.ComboBoxText()
        for name in LASER_COLORS:
            pres_color.append_text(name)
        pres_color.set_active(0)
        pres_color.connect('changed', lambda c: setattr(self, 'laser_color', c.get_active_text() or 'Vermelho'))
        color_wrap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin=4)
        color_wrap.pack_start(Gtk.Label(label='Cor do laser'), False, False, 0)
        color_wrap.pack_start(pres_color, False, False, 0)
        tips = Gtk.Label(label='Ctrl + / Ctrl − / Ctrl 0\nCtrl + roda = zoom')
        tips.set_justify(Gtk.Justification.LEFT)
        self.ribbon_stack.add_named(self._ribbon_page([
            self._ribbon_group('Apresentação', [self._command_button('media-playback-start-symbolic','Iniciar',self._present)]),
            self._ribbon_group('Apontador', [color_wrap]),
            self._ribbon_group('Atalhos', [tips]),
        ]), 'presentation')

        shell.pack_start(self.ribbon_stack, False, False, 0)
        self.ribbon = shell
        self._select_ribbon_tab('home')
        # Show every page first: Gtk.Stack can only switch to a visible child,
        # and set_no_show_all() would stop show_all() from ever reaching them,
        # leaving the expanded ribbon empty (buttons missing).
        self.ribbon_stack.show_all()
        self.ribbon_stack.set_no_show_all(True)
        self.ribbon_stack.hide()
        self.ribbon_collapse_btn.set_active(True)
        for b in self.tool_buttons.get('hand', []):
            b.set_active(True)
        return shell

    def _build_document_tabs(self):
        bar = Gtk.Box(spacing=0)
        bar.get_style_context().add_class('document-tabbar')
        self.document_tab = Gtk.Box(spacing=5)
        self.document_tab.get_style_context().add_class('document-tab')
        self.document_tab.pack_start(Gtk.Image.new_from_icon_name('application-pdf-symbolic', Gtk.IconSize.MENU), False, False, 4)
        self.document_tab_label = Gtk.Label(label='')
        self.document_tab_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.document_tab_label.set_max_width_chars(30)
        self.document_tab.pack_start(self.document_tab_label, True, True, 0)
        close = Gtk.Button.new_from_icon_name('window-close-symbolic', Gtk.IconSize.MENU)
        close.set_relief(Gtk.ReliefStyle.NONE)
        close.connect('clicked', self._close_document)
        close.get_style_context().add_class('document-tab-close')
        self.document_tab.pack_end(close, False, False, 0)
        bar.pack_start(self.document_tab, False, False, 0)
        filler = Gtk.Box(); filler.get_style_context().add_class('document-tab-filler')
        bar.pack_start(filler, True, True, 0)
        self.document_tabbar = bar
        bar.set_no_show_all(True)
        bar.hide()
        return bar

    # ---------- find ----------
    def _build_findbar(self):
        self.find_revealer = Gtk.Revealer()
        box = Gtk.Box(spacing=6, margin=6)
        box.get_style_context().add_class('findbar')
        box.pack_start(Gtk.Label(label='Localizar:'), False, False, 0)
        self.find_entry = Gtk.Entry(); self.find_entry.set_hexpand(True)
        self.find_entry.connect('changed', self._find_changed)
        self.find_entry.connect('activate', lambda *_: self._find_next())
        box.pack_start(self.find_entry, True, True, 0)
        prev = Gtk.Button(label='Anterior'); prev.connect('clicked', lambda *_: self._find_prev()); box.pack_start(prev, False, False, 0)
        nxt = Gtk.Button(label='Próximo'); nxt.connect('clicked', lambda *_: self._find_next()); box.pack_start(nxt, False, False, 0)
        self.find_status = Gtk.Label(label=''); box.pack_start(self.find_status, False, False, 0)
        close = Gtk.Button.new_from_icon_name('window-close-symbolic', Gtk.IconSize.BUTTON)
        close.connect('clicked', lambda *_: self.find_revealer.set_reveal_child(False)); box.pack_start(close, False, False, 0)
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        container.pack_start(box, False, False, 0)
        options = Gtk.Box(spacing=12, margin_start=8, margin_end=8, margin_bottom=4)
        self.find_options = {}
        for key, label in [('match_case', 'Maiúsc./minúsc.'), ('whole_words', 'Palavra inteira'),
                           ('ignore_accents', 'Ignorar acentos'), ('join_hyphens', 'Unir hifenização')]:
            button = Gtk.CheckButton(label=label)
            button.connect('toggled', self._find_changed)
            options.pack_start(button, False, False, 0)
            self.find_options[key] = button
        container.pack_start(options, False, False, 0)
        self.find_revealer.add(container)
        return self.find_revealer

    def _toggle_ribbon_stack(self, button=None):
        self.ribbon_collapsed = bool(button.get_active()) if button is not None else not self.ribbon_collapsed
        if hasattr(self, 'ribbon_stack'):
            self.ribbon_stack.set_visible(not self.ribbon_collapsed)
        if hasattr(self, 'ribbon_collapse_btn'):
            if self.ribbon_collapse_btn.get_active() != self.ribbon_collapsed:
                self.ribbon_collapse_btn.set_active(self.ribbon_collapsed)
            icon = 'pan-down-symbolic' if self.ribbon_collapsed else 'pan-up-symbolic'
            self.ribbon_collapse_btn.set_image(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.MENU))
            self.ribbon_collapse_btn.set_tooltip_text(('Mostrar' if self.ribbon_collapsed else 'Ocultar') + ' faixa de comandos (Ctrl+F1)')

    # ---------- body ----------
    def _sidebar_rail_button(self, icon, tooltip, page_index):
        btn = Gtk.ToggleButton()
        btn.set_relief(Gtk.ReliefStyle.NONE)
        btn.set_image(Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.BUTTON))
        btn.set_tooltip_text(tooltip)
        btn.get_style_context().add_class('sidebar-rail-button')
        btn.connect('clicked', lambda *_: self._show_side_panel(page_index))
        self.sidebar_rail_buttons.append(btn)
        return btn

    def _set_sidebar_visible(self, visible):
        """Show/hide the whole sidebar, including the icon rail.

        Older versions hid only the notebook and left a blank white strip.  The
        complete first pane is now collapsed so the PDF immediately uses the
        released width.
        """
        if not hasattr(self, 'sidebar_container'):
            return
        visible = bool(visible)
        self.sidebar_visible = visible
        self.sidebar_panel_visible = visible
        if visible:
            self.sidebar_container.set_no_show_all(False)
            self.sidebar_container.show_all()
            if hasattr(self, 'sidebar_notebook'):
                self.sidebar_notebook.show()
            pos = getattr(self, 'sidebar_last_position', 158)
            if hasattr(self, 'body_paned'):
                self.body_paned.set_position(max(132, pos))
        else:
            if hasattr(self, 'body_paned'):
                pos = self.body_paned.get_position()
                if pos > 40:
                    self.sidebar_last_position = pos
                self.body_paned.set_position(0)
            self.sidebar_container.set_no_show_all(True)
            self.sidebar_container.hide()
            for btn in getattr(self, 'sidebar_rail_buttons', []):
                btn.set_active(False)
        # Fit modes depend on available viewport width.
        if self.filepath and self.zoom_mode != 'percent':
            GLib.idle_add(lambda: (self.request_render(), False)[1])

    def _show_side_panel(self, index):
        if not hasattr(self, 'sidebar_notebook'):
            return
        current = self.sidebar_notebook.get_current_page()
        if self.sidebar_visible and current == index:
            self._set_sidebar_visible(False)
            return
        self.sidebar_notebook.set_current_page(index)
        self._set_sidebar_visible(True)
        for i, btn in enumerate(getattr(self, 'sidebar_rail_buttons', [])):
            btn.set_active(i == index)

    def _build_body(self):
        self.body_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.body_paned.set_wide_handle(False)

        self.sidebar_container = Gtk.Box(spacing=0)
        self.sidebar_container.get_style_context().add_class('sidebar-container')
        self.sidebar_rail = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        self.sidebar_rail.get_style_context().add_class('sidebar-rail')
        self.sidebar_rail_buttons = []
        for icon, tip, idx in [
            ('view-list-symbolic','Páginas',0),
            ('user-bookmarks-symbolic','Marcadores',1),
            ('mail-message-new-symbolic','Comentários',2),
            ('view-grid-symbolic','Camadas',3),
        ]:
            self.sidebar_rail.pack_start(self._sidebar_rail_button(icon, tip, idx), False, False, 0)
        hide_btn = Gtk.Button.new_from_icon_name('go-previous-symbolic', Gtk.IconSize.BUTTON)
        hide_btn.set_relief(Gtk.ReliefStyle.NONE); hide_btn.set_tooltip_text('Ocultar painel')
        hide_btn.connect('clicked', self._toggle_sidebar); hide_btn.get_style_context().add_class('sidebar-rail-button')
        self.sidebar_rail.pack_end(hide_btn, False, False, 2)
        self.sidebar_container.pack_start(self.sidebar_rail, False, False, 0)

        self.sidebar_notebook = Gtk.Notebook()
        self.sidebar_notebook.set_show_tabs(False)
        self.sidebar_notebook.set_show_border(False)
        self.sidebar_notebook.set_size_request(126, -1)
        self.sidebar_notebook.get_style_context().add_class('side-panels')

        def panel_with_title(title, child):
            wrap = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            head = Gtk.Box(spacing=4, margin=7); head.get_style_context().add_class('side-panel-header')
            lbl = Gtk.Label(label=title, xalign=0); lbl.get_style_context().add_class('side-panel-title')
            head.pack_start(lbl, True, True, 0)
            close_panel = Gtk.Button.new_from_icon_name('window-close-symbolic', Gtk.IconSize.MENU)
            close_panel.set_relief(Gtk.ReliefStyle.NONE)
            close_panel.set_tooltip_text('Ocultar painel lateral')
            close_panel.get_style_context().add_class('side-panel-close')
            close_panel.connect('clicked', self._toggle_sidebar)
            head.pack_end(close_panel, False, False, 0)
            wrap.pack_start(head, False, False, 0); wrap.pack_start(child, True, True, 0)
            return wrap

        self.sidebar_scroller = Gtk.ScrolledWindow(); self.sidebar_scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.thumb_list = Gtk.ListBox(); self.thumb_list.set_selection_mode(Gtk.SelectionMode.SINGLE); self.thumb_list.connect('row-selected', self._thumb_selected); self.sidebar_scroller.add(self.thumb_list)
        self.sidebar_notebook.append_page(panel_with_title('Páginas', self.sidebar_scroller), None)

        self.bookmark_list = Gtk.ListBox(); self.bookmark_list.set_selection_mode(Gtk.SelectionMode.SINGLE); self.bookmark_list.connect('row-activated', self._bookmark_activated)
        self.bookmark_scroll = Gtk.ScrolledWindow(); self.bookmark_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC); self.bookmark_scroll.add(self.bookmark_list)
        self.sidebar_notebook.append_page(panel_with_title('Marcadores', self.bookmark_scroll), None)

        self.comment_list = Gtk.ListBox(); self.comment_list.set_selection_mode(Gtk.SelectionMode.SINGLE); self.comment_list.connect('row-activated', self._comment_activated)
        self.comment_scroll = Gtk.ScrolledWindow(); self.comment_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC); self.comment_scroll.add(self.comment_list)
        self.sidebar_notebook.append_page(panel_with_title('Comentários', self.comment_scroll), None)

        self.layer_list = Gtk.ListBox(); self.layer_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.layer_scroll = Gtk.ScrolledWindow(); self.layer_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC); self.layer_scroll.add(self.layer_list)
        self.sidebar_notebook.append_page(panel_with_title('Camadas', self.layer_scroll), None)
        self.sidebar_container.pack_start(self.sidebar_notebook, True, True, 0)
        self.body_paned.pack1(self.sidebar_container, resize=False, shrink=True)

        self.viewer_scroll = Gtk.ScrolledWindow(); self.viewer_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.viewer_scroll.add_events(Gdk.EventMask.SCROLL_MASK | Gdk.EventMask.SMOOTH_SCROLL_MASK)
        self.viewer_scroll.connect('scroll-event', self._viewer_scroll_event)
        self.viewer_scroll.get_style_context().add_class('viewer-scroll')
        self.viewer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER, valign=Gtk.Align.START, margin=24)
        self.page_frame = Gtk.Frame(); self.page_frame.get_style_context().add_class('page-frame')
        self.page_overlay = Gtk.Overlay(); self.page_image = Gtk.Image(); self.page_overlay.add(self.page_image)
        self.interaction_layer = Gtk.DrawingArea(); self.interaction_layer.set_app_paintable(True); self.interaction_layer.set_can_focus(True)
        self.interaction_layer.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.interaction_layer.connect('draw', self._interaction_draw); self.interaction_layer.connect('button-press-event', self._interaction_press)
        self.interaction_layer.connect('button-release-event', self._interaction_release); self.interaction_layer.connect('motion-notify-event', self._interaction_motion)
        self.interaction_layer.connect('leave-notify-event', self._interaction_leave); self.interaction_layer.connect('realize', lambda *_: self._update_tool_cursor())
        self.interaction_layer.get_style_context().add_class('interaction-layer'); self.page_overlay.add_overlay(self.interaction_layer)
        self.page_frame.add(self.page_overlay); self.viewer_box.pack_start(self.page_frame, False, False, 0)
        self.viewer_scroll.add_with_viewport(self.viewer_box); self.body_paned.pack2(self.viewer_scroll, resize=True, shrink=True)
        self.sidebar_last_position = 158
        self.body_paned.set_position(self.sidebar_last_position)
        self.sidebar_notebook.set_current_page(0)
        for i, btn in enumerate(self.sidebar_rail_buttons):
            btn.set_active(i == 0)
        return self.body_paned

    def _build_status(self):
        bar = Gtk.Box(spacing=8, margin_start=7, margin_end=7, margin_top=3, margin_bottom=3)
        bar.get_style_context().add_class('statusbar')
        self.status_file = Gtk.Label(label='Nenhum PDF aberto', xalign=0)
        self.status_file.set_ellipsize(Pango.EllipsizeMode.END)
        bar.pack_start(self.status_file, True, True, 0)

        nav = Gtk.Box(spacing=3)
        pprev = Gtk.Button.new_from_icon_name('go-previous-symbolic', Gtk.IconSize.MENU); pprev.set_relief(Gtk.ReliefStyle.NONE); pprev.connect('clicked', lambda *_: self.goto_page(self.page-1))
        nav.pack_start(pprev, False, False, 0)
        self.status_page_entry = Gtk.Entry(); self.status_page_entry.set_width_chars(4); self.status_page_entry.set_text('0'); self.status_page_entry.connect('activate', self._status_page_activate)
        nav.pack_start(self.status_page_entry, False, False, 0)
        self.status_page = Gtk.Label(label='de 0'); nav.pack_start(self.status_page, False, False, 0)
        pnxt = Gtk.Button.new_from_icon_name('go-next-symbolic', Gtk.IconSize.MENU); pnxt.set_relief(Gtk.ReliefStyle.NONE); pnxt.connect('clicked', lambda *_: self.goto_page(self.page+1)); nav.pack_start(pnxt, False, False, 0)
        bar.pack_start(nav, False, False, 10)

        zminus = Gtk.Button.new_from_icon_name('zoom-out-symbolic', Gtk.IconSize.MENU); zminus.set_relief(Gtk.ReliefStyle.NONE); zminus.connect('clicked', lambda *_: self._zoom_delta(-10)); bar.pack_start(zminus, False, False, 0)
        self.zoom_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 25, 400, 5); self.zoom_scale.set_draw_value(False); self.zoom_scale.set_size_request(135, -1); self.zoom_scale.set_value(100); self.zoom_scale.connect('value-changed', self._status_zoom_changed); bar.pack_start(self.zoom_scale, False, False, 0)
        zplus = Gtk.Button.new_from_icon_name('zoom-in-symbolic', Gtk.IconSize.MENU); zplus.set_relief(Gtk.ReliefStyle.NONE); zplus.connect('clicked', lambda *_: self._zoom_delta(10)); bar.pack_start(zplus, False, False, 0)
        self.status_zoom = Gtk.Label(label='100%'); self.status_zoom.set_width_chars(14); bar.pack_start(self.status_zoom, False, False, 0)
        self.status = bar
        return bar

    def _status_page_activate(self, entry):
        try:
            self.goto_page(int(entry.get_text()) - 1)
        except Exception:
            entry.set_text(str(self.page + 1 if self.page_count else 0))

    def _status_zoom_changed(self, scale):
        if self._zoom_scale_sync or not self.filepath:
            return
        self.zoom_mode = 'percent'; self.zoom_percent = int(round(scale.get_value()))
        self._update_zoom_labels()
        self._apply_zoom_preview()
        if self.zoom_slider_timer:
            try: GLib.source_remove(self.zoom_slider_timer)
            except Exception: pass
        self.zoom_slider_timer = GLib.timeout_add(120, self._apply_status_zoom)

    def _apply_status_zoom(self):
        self.zoom_slider_timer = None
        self.request_render()
        return False

    # ---------- document lifecycle ----------
    def _choose_open(self, *_args):
        dlg = Gtk.FileChooserDialog(title='Abrir PDF', parent=self, action=Gtk.FileChooserAction.OPEN)
        dlg.add_buttons('Cancelar', Gtk.ResponseType.CANCEL, 'Abrir', Gtk.ResponseType.OK)
        filt = Gtk.FileFilter(); filt.set_name('Documentos PDF'); filt.add_mime_type('application/pdf'); filt.add_pattern('*.pdf'); dlg.add_filter(filt)
        if dlg.run() == Gtk.ResponseType.OK:
            path = dlg.get_filename(); dlg.destroy(); self.open_document(path); return
        dlg.destroy()

    def open_document(self, path):
        path = os.path.abspath(path)
        if not os.path.isfile(path):
            self._error('Arquivo não encontrado.')
            return
        self._clear_document_state()
        self.filepath = path
        self.status_file.set_text(f'Abrindo {Path(path).name}…')
        self._set_actions_enabled(False)

        def task():
            proc = subprocess.run([sys.executable, str(WORKER), 'info', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr.strip() or 'Falha ao ler o PDF.')
            return json.loads(proc.stdout)

        def ok(info):
            if self.filepath != path: return
            self.page_count = int(info['pages']); self.page_sizes = [tuple(x) for x in info['sizes']]; self.metadata = info.get('metadata', {})
            self.page = 0; self.rotation = 0; self.zoom_mode = 'fit-width'; self.zoom_percent = 100
            self.status_file.set_text(Path(path).name)
            self.set_title(f'{Path(path).name} — Print&View PDF')
            self.document_tab_label.set_text(Path(path).name)
            self.document_tab_label.set_tooltip_text(Path(path).name)
            self.document_tabbar.set_no_show_all(False)
            self.document_tabbar.show_all()
            self._set_actions_enabled(True)
            self._start_thumb_build()
            self._load_side_panels()
            self.goto_page(0, force=True)
        self.runner.submit('document-info', task, ok, lambda e: self._load_failed(path, e))

    def _load_failed(self, path, exc):
        if self.filepath == path:
            self._clear_document_state(); self._error(str(exc))

    def _clear_document_state(self):
        self.render_runner.invalidate('main-render')
        self.page_cache.clear()
        for key, future in self.prefetch_tasks.items():
            future.cancel()
            self.prefetch_runner.invalidate(str(key))
        self.prefetch_tasks.clear()
        self.search_cancel.set(); self.search_index = None; self.search_running = False
        self.runner.invalidate('main-render'); self.runner.invalidate('search'); self.runner.invalidate('panels')
        self.runner.invalidate('selection-words')
        self.filepath = None; self.page_count = 0; self.page_sizes = []; self.metadata = {}; self.page = 0
        self.search_hits = []; self.search_pos = -1
        self.selected_words = []; self.selection_data = None; self.selection_rect = None
        self.displayed_page = None; self.displayed_rotation = None
        self.find_status.set_text('')
        self.page_image.clear(); self.current_pixbuf = None; self.rendered_pixbuf = None; self.text_word_cache.clear(); self._clear_thumbnails(); self._clear_side_panels()
        self.status_page.set_text('de 0'); self.status_file.set_text('Nenhum PDF aberto')
        if hasattr(self, 'status_page_entry'): self.status_page_entry.set_text('0')
        if hasattr(self, 'page_total_top'): self.page_total_top.set_text('0')
        if hasattr(self, 'document_tabbar'): self.document_tabbar.hide()
        self.set_title('Print&View PDF')

    def _close_document(self, *_args):
        self._clear_document_state(); self._set_actions_enabled(False)

    def _set_actions_enabled(self, enabled):
        for widget in getattr(self, 'action_widgets', []):
            # Abrir remains available even with no document.
            label = ''
            child = widget.get_child()
            if isinstance(child, Gtk.Box):
                labels = [c.get_text() for c in child.get_children() if isinstance(c, Gtk.Label)]
                label = labels[-1] if labels else ''
            widget.set_sensitive(True if label == 'Abrir' else enabled)
        if hasattr(self, 'page_entry'): self.page_entry.set_sensitive(enabled)
        if hasattr(self, 'status_page_entry'): self.status_page_entry.set_sensitive(enabled)

    # ---------- rendering ----------
    def _page_dimensions_rotated(self):
        if not self.page_sizes: return (612.0, 792.0)
        w, h = self.page_sizes[self.page]
        return (h, w) if self.rotation % 180 else (w, h)

    def _target_final_width(self):
        w, h = self._page_dimensions_rotated()
        alloc = self.viewer_scroll.get_allocation()
        vw, vh = max(300, alloc.width - 60), max(260, alloc.height - 60)
        if self.zoom_mode == 'fit-width':
            return max(120, int(vw * 0.92))
        if self.zoom_mode == 'fit-page':
            return max(120, min(vw, int(vh * w / h)))
        return max(120, int((w / 72.0) * 96.0 * self.zoom_percent / 100.0))

    def _render_width_for_poppler(self, final_width):
        if self.rotation % 180 == 0 or not self.page_sizes:
            return final_width
        ow, oh = self.page_sizes[self.page]
        return max(120, int(final_width * ow / oh))

    def request_render(self):
        if not self.filepath or not self.page_sizes: return
        page = self.page; rotation = self.rotation; target_final = self._target_final_width(); target = self._render_width_for_poppler(target_final)
        path = self.filepath
        cache_dir = self.cache_dir
        key = (path, page, rotation, target)
        self.render_runner.invalidate('main-render')
        self.status_page.set_text(f'de {self.page_count}')
        def apply(pb):
            self.rendered_pixbuf = pb
            self.displayed_page = page; self.displayed_rotation = rotation
            self._display_pixbuf(pb)
            self.status_file.set_text(Path(path).name)
            self._update_zoom_labels()
            self._request_nearby_thumbnails()
            self._prefetch_reader_pages()
        cached = self.page_cache.get(key)
        if cached is not None:
            apply(cached)
            return
        self.status_file.set_text(f'Carregando página {page + 1}…')
        def task():
            return self._reader_pixbuf(path, page, rotation, target, cache_dir)
        def ok(pb):
            if page != self.page or rotation != self.rotation or path != self.filepath: return
            try:
                self.page_cache.put(key, pb)
                apply(pb)
            except Exception as exc: self._error(str(exc))
        self.render_runner.submit('main-render', task, ok,
                           lambda e: self.status_file.set_text(f'Falha ao renderizar: {e}'))

    @staticmethod
    def _reader_pixbuf(path, page, rotation, target, cache_dir):
        png = render_page(path, page, target, cache_dir, f'main-r{rotation}')
        pb = GdkPixbuf.Pixbuf.new_from_file(png)
        rotations = {90: GdkPixbuf.PixbufRotation.CLOCKWISE,
                     180: GdkPixbuf.PixbufRotation.UPSIDEDOWN,
                     270: GdkPixbuf.PixbufRotation.COUNTERCLOCKWISE}
        return pb.rotate_simple(rotations[rotation]) if rotation in rotations else pb

    def _prefetch_reader_pages(self):
        path, rotation, cache_dir = self.filepath, self.rotation, self.cache_dir
        wanted = set()
        for page in (self.page + 1, self.page - 1):
            if not 0 <= page < self.page_count: continue
            pw, ph = self.page_sizes[page]
            w, h = (ph, pw) if rotation % 180 else (pw, ph)
            alloc = self.viewer_scroll.get_allocation()
            vw, vh = max(300, alloc.width - 60), max(260, alloc.height - 60)
            if self.zoom_mode == 'fit-width': final = max(120, int(vw * .92))
            elif self.zoom_mode == 'fit-page': final = max(120, min(vw, int(vh * w / h)))
            else: final = max(120, int(w / 72 * 96 * self.zoom_percent / 100))
            target = final if not rotation % 180 else max(120, int(final * pw / ph))
            key = (path, page, rotation, target); wanted.add(key)
            future = self.prefetch_tasks.get(key)
            if self.page_cache.get(key) is not None or (future is not None and not future.done()): continue
            def ok(pb, key=key):
                if key[0] == self.filepath: self.page_cache.put(key, pb)
                self.prefetch_tasks.pop(key, None)
            future = self.prefetch_runner.submit(str(key),
                lambda p=page, t=target: self._reader_pixbuf(path, p, rotation, t, cache_dir), ok)
            self.prefetch_tasks[key] = future
        for key in list(self.prefetch_tasks):
            if key not in wanted:
                self.prefetch_runner.invalidate(str(key))
                self.prefetch_tasks.pop(key).cancel()

    def _theme_changed(self, combo):
        self.theme_mode = combo.get_active_id() or 'auto'
        load_theme(self.theme_mode)
        try: save_theme(self.theme_mode)
        except OSError as exc: self.status_file.set_text(f'Tema aplicado; não foi possível salvar: {exc}')

    def _system_theme_changed(self, *_args):
        if self.theme_mode == 'auto': load_theme('auto')

    def _display_pixbuf(self, pb):
        """Display a pixbuf and force the page overlay to adopt its real size."""
        if pb is None:
            return
        self.current_pixbuf = pb
        self.page_image.set_from_pixbuf(pb)
        w, h = pb.get_width(), pb.get_height()
        try:
            self.page_overlay.set_size_request(w, h)
            self.interaction_layer.set_size_request(w, h)
            self.page_frame.set_size_request(w, h)
        except Exception:
            pass
        if hasattr(self, 'interaction_layer'):
            self.interaction_layer.queue_draw()
        self.viewer_box.queue_resize()

    def _apply_zoom_preview(self):
        """Give immediate visual zoom feedback while a sharp render is prepared."""
        pb = self.rendered_pixbuf or self.current_pixbuf
        if pb is None or not self.filepath:
            return
        try:
            target_w = max(120, int(self._target_final_width()))
            if abs(pb.get_width() - target_w) <= 2:
                self._display_pixbuf(pb)
                return
            target_h = max(1, int(round(pb.get_height() * target_w / float(pb.get_width()))))
            scaled = pb.scale_simple(target_w, target_h, GdkPixbuf.InterpType.BILINEAR)
            if scaled is not None:
                self._display_pixbuf(scaled)
        except Exception:
            pass

    def _viewer_scroll_event(self, _widget, event):
        """Ctrl+wheel zooms in the normal reader; ordinary wheel keeps scrolling."""
        try:
            if not (event.state & Gdk.ModifierType.CONTROL_MASK):
                return False
            direction = event.direction
            if direction == Gdk.ScrollDirection.UP:
                delta = 10
            elif direction == Gdk.ScrollDirection.DOWN:
                delta = -10
            elif direction == Gdk.ScrollDirection.SMOOTH:
                _ok, _dx, dy = event.get_scroll_deltas()
                delta = -10 if dy > 0 else 10
            else:
                return False
            self._zoom_delta(delta)
            return True
        except Exception:
            return False

    def goto_page(self, page, force=False):
        if not self.filepath or self.page_count <= 0: return
        page = max(0, min(int(page), self.page_count - 1))
        if page == self.page and not force: return
        self.page = page
        self.selected_words = []; self.selection_data = None; self.selection_rect = None
        self.runner.invalidate('selection-words')
        self.page_entry.set_text(str(page + 1))
        if hasattr(self, 'page_total_top'): self.page_total_top.set_text(str(self.page_count))
        if hasattr(self, 'status_page_entry'): self.status_page_entry.set_text(str(page + 1))
        self.status_page.set_text(f'de {self.page_count}')
        self.request_render(); self._select_thumb_row(page)

    def _page_entry_activate(self, entry):
        try: self.goto_page(int(entry.get_text()) - 1)
        except Exception: entry.set_text(str(self.page + 1 if self.page_count else 0))

    def _zoom_delta(self, delta):
        if not self.filepath:
            return
        if self.zoom_mode != 'percent':
            # Start manual zoom from the currently visible fitted size instead
            # of jumping blindly from an internal 100% state.
            try:
                pw, _ph = self._page_dimensions_rotated()
                current_w = self.current_pixbuf.get_width() if self.current_pixbuf else self._target_final_width()
                natural_w = max(1.0, (pw / 72.0) * 96.0)
                self.zoom_percent = int(round(current_w / natural_w * 100.0))
            except Exception:
                self.zoom_percent = 100
        self.zoom_mode = 'percent'
        self.zoom_percent = max(25, min(400, int(self.zoom_percent + delta)))
        self._update_zoom_labels()
        self._apply_zoom_preview()
        self.request_render()

    def _zoom_100(self, *_args):
        if not self.filepath: return
        self.zoom_mode = 'percent'; self.zoom_percent = 100
        self._update_zoom_labels(); self._apply_zoom_preview(); self.request_render()

    def _fit_page(self, *_args):
        if not self.filepath: return
        self.zoom_mode = 'fit-page'; self._update_zoom_labels(); self._apply_zoom_preview(); self.request_render()

    def _fit_width(self, *_args):
        if not self.filepath: return
        self.zoom_mode = 'fit-width'; self._update_zoom_labels(); self._apply_zoom_preview(); self.request_render()

    def _rotate(self, delta):
        if not self.filepath: return
        self.rotation = (self.rotation + delta) % 360; self.request_render()

    def _update_zoom_labels(self):
        if self.zoom_mode == 'fit-page': text = 'Ajustar página'
        elif self.zoom_mode == 'fit-width': text = 'Ajustar largura'
        else: text = f'{self.zoom_percent}%'
        self.status_zoom.set_text(text); self.zoom_label_top.set_text(text)
        if hasattr(self, 'zoom_scale') and self.zoom_mode == 'percent':
            self._zoom_scale_sync = True
            try: self.zoom_scale.set_value(self.zoom_percent)
            finally: self._zoom_scale_sync = False

    def _on_resize(self, *_args):
        if not self.filepath or self.zoom_mode == 'percent': return
        if self.resize_timer:
            try: GLib.source_remove(self.resize_timer)
            except Exception: pass
        self.resize_timer = GLib.timeout_add(220, self._resize_render)

    def _resize_render(self):
        self.resize_timer = None; self.request_render(); return False

    # ---------- thumbnails ----------
    def _clear_thumbnails(self):
        for row in self.thumb_list.get_children(): self.thumb_list.remove(row)
        self.thumb_rows.clear(); self.thumb_requested.clear(); self.thumb_build_next = 0

    def _start_thumb_build(self):
        self._clear_thumbnails(); self.thumb_build_next = 0; GLib.idle_add(self._build_thumb_batch)

    def _build_thumb_batch(self):
        if not self.filepath or self.thumb_build_next >= self.page_count: return False
        for _ in range(16):
            if self.thumb_build_next >= self.page_count: break
            idx = self.thumb_build_next; self.thumb_build_next += 1
            row = Gtk.ListBoxRow(); box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, margin=3)
            img = Gtk.Image(); img.set_size_request(82, 48); box.pack_start(img, False, False, 0)
            box.pack_start(Gtk.Label(label=str(idx + 1)), False, False, 0); row.add(box); row.page_index = idx; row.thumb_image = img
            self.thumb_list.add(row); self.thumb_rows[idx] = row
        self.thumb_list.show_all(); self._request_nearby_thumbnails()
        return self.thumb_build_next < self.page_count

    def _request_nearby_thumbnails(self):
        if not self.filepath: return
        for idx in range(max(0, self.page - 3), min(self.page_count, self.page + 4)):
            row = self.thumb_rows.get(idx)
            if row is None or idx in self.thumb_requested: continue
            self.thumb_requested.add(idx); path = self.filepath
            def ok(png, i=idx):
                row2 = self.thumb_rows.get(i)
                if not row2 or path != self.filepath: return
                try: row2.thumb_image.set_from_file(png)
                except Exception: pass
            self.runner.submit(f'thumb-{idx}', lambda i=idx: render_page(path, i, 82, self.cache_dir, 'thumb'), ok, lambda _e: None)

    def _thumb_selected(self, _list, row):
        if row is not None and hasattr(row, 'page_index') and row.page_index != self.page: self.goto_page(row.page_index)

    def _select_thumb_row(self, page):
        row = self.thumb_rows.get(page)
        if row:
            self.thumb_list.select_row(row); row.grab_focus()

    def _toggle_sidebar(self, *_args):
        if not hasattr(self, 'sidebar_notebook'):
            return
        self._set_sidebar_visible(not self.sidebar_visible)
        if self.sidebar_visible:
            idx = max(0, self.sidebar_notebook.get_current_page())
            for i, btn in enumerate(getattr(self, 'sidebar_rail_buttons', [])):
                btn.set_active(i == idx)

    # ---------- side panels ----------
    def _clear_listbox(self, box):
        if not hasattr(self, 'sidebar_notebook'):
            return
        for row in box.get_children():
            box.remove(row)

    def _clear_side_panels(self):
        if not hasattr(self, 'bookmark_list'):
            return
        for box in (self.bookmark_list, self.comment_list, self.layer_list):
            self._clear_listbox(box)

    def _info_row(self, text):
        row = Gtk.ListBoxRow()
        lbl = Gtk.Label(label=text, xalign=0, margin=8)
        lbl.set_line_wrap(True)
        lbl.get_style_context().add_class('muted')
        row.add(lbl)
        return row

    def _load_side_panels(self):
        if not self.filepath:
            return
        path = self.filepath
        self._clear_side_panels()
        self.bookmark_list.add(self._info_row('Carregando marcadores…'))
        self.comment_list.add(self._info_row('Carregando comentários…'))
        self.layer_list.add(self._info_row('Carregando camadas…'))
        for box in (self.bookmark_list, self.comment_list, self.layer_list):
            box.show_all()
        def ok(data):
            if path == self.filepath:
                self._populate_side_panels(data)
        self.runner.submit('panels', lambda: inspect_document_panels(path), ok, lambda _e: self._populate_side_panels({}))

    def _populate_side_panels(self, data):
        self._clear_side_panels()
        bookmarks = data.get('bookmarks') or []
        if not bookmarks:
            self.bookmark_list.add(self._info_row('Este PDF não possui marcadores.'))
        for item in bookmarks:
            row = Gtk.ListBoxRow(); row.page_index = item.get('page')
            box = Gtk.Box(spacing=6, margin=6)
            indent = max(0, int(item.get('level') or 0)) * 14
            lbl = Gtk.Label(label=str(item.get('title') or 'Marcador'), xalign=0)
            lbl.set_margin_start(indent)
            box.pack_start(lbl, True, True, 0)
            if item.get('page') is not None:
                pg = Gtk.Label(label=str(int(item['page']) + 1)); pg.get_style_context().add_class('muted'); box.pack_end(pg, False, False, 0)
            row.add(box); self.bookmark_list.add(row)
        comments = data.get('comments') or []
        if not comments:
            self.comment_list.add(self._info_row('Nenhum comentário/anotação detectado.'))
        for item in comments:
            row = Gtk.ListBoxRow(); row.page_index = item.get('page')
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, margin=6)
            title = f"{item.get('type') or 'Comentário'} • pág. {int(item.get('page') or 0) + 1}"
            lbl = Gtk.Label(label=title, xalign=0); lbl.get_style_context().add_class('panel-row-title'); box.pack_start(lbl, False, False, 0)
            text = item.get('text') or item.get('author') or ''
            if text:
                sub = Gtk.Label(label=str(text)[:180], xalign=0); sub.set_line_wrap(True); sub.get_style_context().add_class('muted'); box.pack_start(sub, False, False, 0)
            row.add(box); self.comment_list.add(row)
        layers = data.get('layers') or []
        if not layers:
            self.layer_list.add(self._info_row('Este PDF não possui camadas opcionais detectáveis.'))
        else:
            self.layer_list.add(self._info_row('Camadas detectadas. A visibilidade continua definida pelo PDF nesta versão.'))
            for item in layers:
                row = Gtk.ListBoxRow(); box = Gtk.Box(spacing=6, margin=6)
                box.pack_start(Gtk.Image.new_from_icon_name('view-list-symbolic', Gtk.IconSize.MENU), False, False, 0)
                box.pack_start(Gtk.Label(label=str(item.get('name') or 'Camada'), xalign=0), True, True, 0)
                row.add(box); self.layer_list.add(row)
        for box in (self.bookmark_list, self.comment_list, self.layer_list):
            box.show_all()

    def _bookmark_activated(self, _box, row):
        page = getattr(row, 'page_index', None)
        if page is not None: self.goto_page(page)

    def _comment_activated(self, _box, row):
        page = getattr(row, 'page_index', None)
        if page is not None: self.goto_page(page)

    # ---------- interactive reading tools ----------
    def _tool_toggled(self, button, tool):
        if self._tool_sync or not button.get_active(): return
        self._tool_sync = True
        try:
            self.active_tool = tool
            for name, buttons in self.tool_buttons.items():
                for b in buttons:
                    if b is not button: b.set_active(name == tool)
            self.selection_rect = None; self.drag_start = None; self.hand_origin = None; self.measure_result = None
            if tool != 'loupe': self.loupe_pos = None
            self._update_tool_cursor()
            if hasattr(self, 'interaction_layer'): self.interaction_layer.queue_draw()
            names = {'hand':'Mão','select':'Selecionar texto','snapshot':'Snapshot','loupe':'Lupa','measure':'Medir distância'}
            if self.filepath: self.status_file.set_text(f'Ferramenta: {names.get(tool, tool)}')
        finally:
            self._tool_sync = False

    def _update_tool_cursor(self):
        if not hasattr(self, 'interaction_layer') or not self.interaction_layer.get_window(): return
        names = {'hand':'grab','select':'text','snapshot':'crosshair','loupe':'zoom-in','measure':'crosshair'}
        try:
            self.interaction_layer.get_window().set_cursor(Gdk.Cursor.new_from_name(Gdk.Display.get_default(), names.get(self.active_tool, 'default')))
        except Exception: pass

    @staticmethod
    def _norm_rect(a, b):
        x0,y0=a; x1,y1=b
        return min(x0,x1),min(y0,y1),max(x0,x1),max(y0,y1)

    def _interaction_press(self, _w, event):
        if not self.filepath or event.button != 1: return False
        if self.displayed_page != self.page or self.displayed_rotation != self.rotation: return False
        self.interaction_layer.grab_focus()
        if self.active_tool == 'hand':
            ha,va=self.viewer_scroll.get_hadjustment(),self.viewer_scroll.get_vadjustment()
            self.hand_origin=(event.x_root,event.y_root,ha.get_value(),va.get_value())
            try: self.interaction_layer.get_window().set_cursor(Gdk.Cursor.new_from_name(Gdk.Display.get_default(),'grabbing'))
            except Exception: pass
            return True
        if self.active_tool in ('select','snapshot','measure'):
            self.selected_words = []; self.selection_data = None
            self.runner.invalidate('selection-words')
            self.drag_start=(event.x,event.y); self.selection_rect=(event.x,event.y,event.x,event.y); self.measure_result=None; self.interaction_layer.queue_draw(); return True
        if self.active_tool == 'loupe':
            self.loupe_pos=(event.x,event.y); self.interaction_layer.queue_draw(); return True
        return False

    def _interaction_motion(self, _w, event):
        if self.active_tool == 'hand' and self.hand_origin:
            sx,sy,hv,vv=self.hand_origin; ha,va=self.viewer_scroll.get_hadjustment(),self.viewer_scroll.get_vadjustment()
            nx=hv-(event.x_root-sx); ny=vv-(event.y_root-sy)
            ha.set_value(max(ha.get_lower(),min(nx,ha.get_upper()-ha.get_page_size())))
            va.set_value(max(va.get_lower(),min(ny,va.get_upper()-va.get_page_size())))
            return True
        if self.active_tool in ('select','snapshot','measure') and self.drag_start:
            self.selection_rect=self._norm_rect(self.drag_start,(event.x,event.y)); self.interaction_layer.queue_draw(); return True
        if self.active_tool == 'loupe':
            self.loupe_pos=(event.x,event.y); self.interaction_layer.queue_draw(); return True
        return False

    def _interaction_release(self, _w, event):
        if event.button != 1: return False
        if self.active_tool == 'hand' and self.hand_origin:
            self.hand_origin=None; self._update_tool_cursor(); return True
        if self.active_tool in ('select','snapshot','measure') and self.drag_start:
            rect=self._norm_rect(self.drag_start,(event.x,event.y)); self.drag_start=None; self.selection_rect=rect
            if rect[2]-rect[0] < 4 or rect[3]-rect[1] < 4:
                self.selection_rect=None; self.interaction_layer.queue_draw(); return True
            if self.active_tool == 'snapshot': self._finish_snapshot(rect)
            elif self.active_tool == 'select': self._finish_text_selection(rect)
            else: self._finish_measure(rect)
            self.interaction_layer.queue_draw(); return True
        return False

    def _interaction_leave(self, *_args):
        if self.active_tool == 'loupe': self.loupe_pos=None; self.interaction_layer.queue_draw()
        return False

    def _interaction_draw(self, widget, cr):
        if not self.current_pixbuf: return False
        if self.displayed_page != self.page or self.displayed_rotation != self.rotation: return False
        for pos, hit in enumerate(self.search_hits):
            if hit['page'] != self.page:
                continue
            cr.set_source_rgba(1.0, .55 if pos == self.search_pos else .85, .05, .40)
            for rect in hit['rects']:
                x0, y0, x1, y1 = self._pdf_rect_to_display(rect, hit)
                cr.rectangle(x0, y0, x1 - x0, y1 - y0); cr.fill()
        if self.selection_data:
            cr.set_source_rgba(.16, .48, .92, .30)
            for word in self.selected_words:
                x0, y0, x1, y1 = self._pdf_rect_to_display(
                    [word[k] for k in ('x0', 'y0', 'x1', 'y1')], self.selection_data)
                cr.rectangle(x0, y0, x1 - x0, y1 - y0); cr.fill()
        if self.selection_rect:
            x0,y0,x1,y1=self.selection_rect
            if self.active_tool == 'measure' or self.measure_result:
                cr.set_source_rgba(.86,.18,.16,.95); cr.set_line_width(2); cr.move_to(x0,y0); cr.line_to(x1,y1); cr.stroke()
                for x,y in ((x0,y0),(x1,y1)): cr.arc(x,y,4,0,2*math.pi); cr.fill()
                if self.measure_result:
                    tx,ty=(x0+x1)/2,(y0+y1)/2; cr.set_source_rgba(.08,.08,.08,.88); cr.rectangle(tx-38,ty-25,76,21); cr.fill(); cr.set_source_rgb(1,1,1); cr.move_to(tx-31,ty-10); cr.show_text(self.measure_result)
            else:
                cr.set_source_rgba(.16,.48,.92,.18); cr.rectangle(x0,y0,x1-x0,y1-y0); cr.fill_preserve(); cr.set_source_rgba(.16,.48,.92,.95); cr.set_line_width(1.5); cr.stroke()
        if self.active_tool == 'loupe' and self.loupe_pos:
            px,py=self.loupe_pos; W,H=self.current_pixbuf.get_width(),self.current_pixbuf.get_height(); size=72
            x=max(0,min(max(0,W-size),int(px-size/2))); y=max(0,min(max(0,H-size),int(py-size/2)))
            try:
                sub=self.current_pixbuf.new_subpixbuf(x,y,min(size,W-x),min(size,H-y)); mag=sub.scale_simple(180,180,GdkPixbuf.InterpType.BILINEAR)
                alloc=widget.get_allocation(); lx=min(max(8,px+22),max(8,alloc.width-190)); ly=min(max(8,py+22),max(8,alloc.height-190))
                cr.set_source_rgba(1,1,1,.96); cr.rectangle(lx-4,ly-4,188,188); cr.fill(); Gdk.cairo_set_source_pixbuf(cr,mag,lx,ly); cr.paint(); cr.set_source_rgb(.15,.15,.15); cr.set_line_width(2); cr.rectangle(lx-4,ly-4,188,188); cr.stroke(); cr.set_source_rgba(.85,.15,.12,.9); cr.move_to(lx+90,ly+80); cr.line_to(lx+90,ly+100); cr.move_to(lx+80,ly+90); cr.line_to(lx+100,ly+90); cr.stroke()
            except Exception: pass
        return False

    def _finish_snapshot(self, rect):
        if not self.current_pixbuf: return
        x0,y0,x1,y1=[int(round(v)) for v in rect]; W,H=self.current_pixbuf.get_width(),self.current_pixbuf.get_height()
        x0=max(0,min(W-1,x0)); y0=max(0,min(H-1,y0)); x1=max(x0+1,min(W,x1)); y1=max(y0+1,min(H,y1))
        try:
            crop=self.current_pixbuf.new_subpixbuf(x0,y0,x1-x0,y1-y0).copy(); Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_image(crop); self.status_file.set_text(f'Snapshot copiado ({x1-x0} × {y1-y0} px).')
        except Exception as exc: self._error(str(exc))
        self.selection_rect=None

    def _display_rect_to_pdf(self, rect, data):
        if not self.current_pixbuf: return rect
        W,H=self.current_pixbuf.get_width(),self.current_pixbuf.get_height(); ow,oh=float(data.get('width') or 0),float(data.get('height') or 0)
        if not ow or not oh: ow,oh=self.page_sizes[self.page]
        disp_w,disp_h=(oh,ow) if self.rotation % 180 else (ow,oh)
        def pt(x,y):
            xr=x/max(1,W)*disp_w; yr=y/max(1,H)*disp_h; r=self.rotation%360
            if r==90: return yr,oh-xr
            if r==180: return ow-xr,oh-yr
            if r==270: return ow-yr,xr
            return xr,yr
        x0,y0,x1,y1=rect; corners=[pt(x0,y0),pt(x1,y0),pt(x0,y1),pt(x1,y1)]; xs=[q[0] for q in corners]; ys=[q[1] for q in corners]
        return min(xs),min(ys),max(xs),max(ys)

    def _pdf_rect_to_display(self, rect, data):
        W, H = self.current_pixbuf.get_width(), self.current_pixbuf.get_height()
        ow, oh = float(data['width']), float(data['height'])
        r = self.rotation % 360
        dw, dh = (oh, ow) if r % 180 else (ow, oh)
        def pt(x, y):
            if r == 90: x, y = oh - y, x
            elif r == 180: x, y = ow - x, oh - y
            elif r == 270: x, y = y, ow - x
            return x / max(1, dw) * W, y / max(1, dh) * H
        x0, y0, x1, y1 = rect
        corners = [pt(x0, y0), pt(x1, y0), pt(x0, y1), pt(x1, y1)]
        return (min(p[0] for p in corners), min(p[1] for p in corners),
                max(p[0] for p in corners), max(p[1] for p in corners))

    def _finish_text_selection(self, rect):
        page=self.page; path=self.filepath
        if not path: return
        def use(data):
            if path != self.filepath or page != self.page: return
            self.text_word_cache[page]=data; x0,y0,x1,y1=self._display_rect_to_pdf(rect,data); chosen=[]
            for w in data.get('words',[]):
                if w['x1']>=x0 and w['x0']<=x1 and w['y1']>=y0 and w['y0']<=y1: chosen.append(w)
            self.selection_rect = None
            self.selected_words = chosen; self.selection_data = data
            self.interaction_layer.queue_draw()
            if not chosen: self.status_file.set_text('Nenhum texto detectado na seleção.'); return
            lines=[]; current=[]; last_line=None
            for w in chosen:
                line=(w['block'], w['line'])
                if last_line is not None and line != last_line and current: lines.append(' '.join(current)); current=[]
                current.append(w['text']); last_line=line
            if current: lines.append(' '.join(current))
            text='\n'.join(lines).strip()
            if text: Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(text,-1); self.status_file.set_text(f'Texto selecionado copiado ({len(text)} caracteres).')
        cached=self.text_word_cache.get(page)
        if cached is not None: use(cached)
        else: self.status_file.set_text('Lendo mapa de texto da página…'); self.runner.submit('selection-words',lambda:extract_page_words(path,page),use,lambda e:self.status_file.set_text(f'Falha ao selecionar texto: {e}'))

    def _finish_measure(self, rect):
        if not self.current_pixbuf or not self.page_sizes: return
        x0,y0,x1,y1=rect; pw,ph=self._page_dimensions_rotated(); W=self.current_pixbuf.get_width(); H=self.current_pixbuf.get_height(); sx=pw/max(1,W); sy=ph/max(1,H)
        points=math.hypot((x1-x0)*sx,(y1-y0)*sy); self.measure_result=f'{points/72.0*2.54:.2f} cm'; self.status_file.set_text(f'Distância medida: {self.measure_result}')

    # ---------- search ----------
    def _show_find(self, *_args):
        if not self.filepath: return
        self.find_revealer.set_reveal_child(True); self.find_entry.grab_focus(); self.find_entry.select_region(0, -1)

    def _find_changed(self, *_args):
        self.search_cancel.set()
        self.search_running = False
        self.runner.invalidate('search')
        self.search_hits = []; self.search_pos = -1
        self.interaction_layer.queue_draw()
        if self.search_timer:
            try: GLib.source_remove(self.search_timer)
            except Exception: pass
        self.search_timer = GLib.timeout_add(350, self._start_search)

    def _start_search(self):
        self.search_timer = None
        if not self.filepath: return False
        query = self.find_entry.get_text().strip(); path = self.filepath
        if not query:
            self.search_hits = []; self.search_pos = -1; self.find_status.set_text(''); return False
        self.find_status.set_text('Pesquisando…')
        cancel = threading.Event(); self.search_cancel = cancel
        options = {key: button.get_active() for key, button in self.find_options.items()}
        if self.search_index is None:
            self.search_index = TextSearchIndex(path, self.page_count, page_sizes=self.page_sizes)
        index = self.search_index
        self.search_scanned = 0; self.search_running = True
        def progress(scanned, batch):
            def deliver():
                if cancel.is_set() or self.filepath != path or self.search_cancel is not cancel:
                    return False
                first = not self.search_hits
                self.search_scanned = scanned; self.search_hits.extend(batch)
                if first and batch:
                    self.search_pos = 0; self.goto_page(batch[0]['page'])
                self._update_find_status()
                self.interaction_layer.queue_draw()
                return False
            GLib.idle_add(deliver, priority=GLib.PRIORITY_DEFAULT_IDLE)
        def ok(hits):
            if cancel.is_set() or self.search_cancel is not cancel or path != self.filepath: return
            self.search_running = False
            self.search_hits = hits
            self.search_pos = min(max(0, self.search_pos), len(hits) - 1) if hits else -1
            self._update_find_status()
            self.interaction_layer.queue_draw()
        def error(exc):
            if not cancel.is_set():
                self.search_running = False
                self.find_status.set_text(f'Erro: {exc}')
        self.runner.submit('search', lambda: index.search(query, cancel=cancel, on_page=progress, **options), ok, error)
        return False

    def _update_find_status(self):
        text = f'{self.search_pos + 1} de {len(self.search_hits)}' if self.search_hits else 'Nenhuma ocorrência'
        if self.search_running:
            text += f' • {self.search_scanned}/{self.page_count} páginas'
        elif len(self.search_hits) >= 5000:
            text += ' • limite de resultados'
        self.find_status.set_text(text)

    def _find_next(self):
        if not self.search_hits: return
        self.search_pos = (self.search_pos + 1) % len(self.search_hits); self._update_find_status(); self.goto_page(self.search_hits[self.search_pos]['page']); self.interaction_layer.queue_draw()

    def _find_prev(self):
        if not self.search_hits: return
        self.search_pos = (self.search_pos - 1) % len(self.search_hits); self._update_find_status(); self.goto_page(self.search_hits[self.search_pos]['page']); self.interaction_layer.queue_draw()

    # ---------- tools ----------
    def _save_copy(self, *_args):
        if not self.filepath: return
        dlg = Gtk.FileChooserDialog(title='Salvar cópia', parent=self, action=Gtk.FileChooserAction.SAVE)
        dlg.add_buttons('Cancelar', Gtk.ResponseType.CANCEL, 'Salvar', Gtk.ResponseType.OK); dlg.set_do_overwrite_confirmation(True); dlg.set_current_name(Path(self.filepath).name)
        if dlg.run() == Gtk.ResponseType.OK:
            dest = dlg.get_filename(); dlg.destroy()
            try: shutil.copy2(self.filepath, dest); self.status_file.set_text(f'Cópia salva: {Path(dest).name}')
            except Exception as e: self._error(str(e))
            return
        dlg.destroy()

    def _copy_page_text(self, *_args):
        if not self.filepath: return
        path, page = self.filepath, self.page; self.status_file.set_text('Extraindo texto da página…')
        def ok(text):
            if path != self.filepath: return
            Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(text, -1); self.status_file.set_text('Texto da página copiado para a área de transferência.')
        self.runner.submit('copy-text', lambda: extract_page_text(path, page), ok, lambda e: self._error(str(e)))

    def _export_png(self, *_args):
        if not self.filepath: return
        dlg = Gtk.FileChooserDialog(title='Exportar página como PNG', parent=self, action=Gtk.FileChooserAction.SAVE)
        dlg.add_buttons('Cancelar', Gtk.ResponseType.CANCEL, 'Salvar', Gtk.ResponseType.OK); dlg.set_do_overwrite_confirmation(True); dlg.set_current_name(f'{Path(self.filepath).stem}-pagina-{self.page+1}.png')
        if dlg.run() != Gtk.ResponseType.OK: dlg.destroy(); return
        dest = dlg.get_filename(); dlg.destroy(); path, page = self.filepath, self.page; self.status_file.set_text('Exportando PNG…')
        self.runner.submit('export-png', lambda: render_page_to_png(path, page, dest), lambda _p: self.status_file.set_text(f'PNG salvo: {Path(dest).name}'), lambda e: self._error(str(e)))

    def _properties(self, *_args):
        if not self.filepath: return
        lines = [f'Arquivo: {self.filepath}', f'Páginas: {self.page_count}']
        if self.page_sizes:
            w,h = self.page_sizes[self.page]; lines.append(f'Página atual: {w/72*2.54:.1f} × {h/72*2.54:.1f} cm')
        for key, label in [('title','Título'),('author','Autor'),('subject','Assunto'),('creator','Criador'),('producer','Produtor')]:
            if self.metadata.get(key): lines.append(f'{label}: {self.metadata[key]}')
        dlg = Gtk.MessageDialog(transient_for=self, modal=True, message_type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, text='Propriedades do PDF')
        dlg.format_secondary_text('\n'.join(lines)); dlg.run(); dlg.destroy()

    # ---------- presentation / modes ----------
    def _present(self, *_args):
        if not self.filepath: return
        win = PresentationWindow(self, self.runner, self.filepath, self.page_sizes, self.page, self.cache_dir, self.laser_color)
        win.show_all()

    def _fullscreen_toggle(self, *_args):
        state = self.get_window().get_state() if self.get_window() else 0
        if state & Gdk.WindowState.FULLSCREEN: self.unfullscreen()
        else: self.fullscreen()

    def _reading_mode_toggle(self, *_args):
        self.read_mode = not self.read_mode
        self.ribbon.set_visible(not self.read_mode); self.status.set_visible(not self.read_mode)
        if hasattr(self, 'document_tabbar'): self.document_tabbar.set_visible(False if self.read_mode else bool(self.filepath))
        if hasattr(self, 'sidebar_container'):
            if self.read_mode:
                self.sidebar_container.hide()
            elif self.sidebar_visible:
                self.sidebar_container.show_all()
                if hasattr(self, 'body_paned'):
                    self.body_paned.set_position(max(132, getattr(self, 'sidebar_last_position', 158)))

    # ---------- printing ----------
    def _print(self, *_args):
        if not self.filepath: return
        win = PrintWindow(self, self.runner, self.filepath, self.page_count, self.page_sizes, self.page, self.cache_dir, self._submit_print_job)
        win.show_all()

    def _submit_print_job(self, job):
        path = self.filepath
        if not path: return
        out = os.path.join(self.cache_dir, f'print-prepared-{GLib.get_monotonic_time()}.pdf')
        self.status_file.set_text('Preparando impressão em segundo plano…')
        job_json = json.dumps(job, ensure_ascii=False)
        def task():
            proc = subprocess.run([sys.executable, str(WORKER), 'prepare', path, out],
                                  input=job_json, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, timeout=600)
            if proc.returncode != 0: raise RuntimeError(proc.stderr.strip() or 'Falha ao preparar o PDF para impressão.')
            if job.get('destination') == 'save-pdf':
                shutil.copy2(out, job['save_path']); return f'PDF salvo em {job["save_path"]}'
            return cups.print_file(job.get('printer'), out, job)
        self.runner.submit('print-job', task, lambda msg: self.status_file.set_text(msg), lambda e: self._error(str(e)))

    # ---------- keyboard ----------
    def _on_key(self, _w, event):
        key = Gdk.keyval_name(event.keyval) or ''; ctrl = bool(event.state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and key.lower() == 'o': self._choose_open(); return True
        if ctrl and key.lower() == 'p': self._print(); return True
        if ctrl and key.lower() == 'f': self._show_find(); return True
        if ctrl and key in ('plus','equal','KP_Add'): self._zoom_delta(25); return True
        if ctrl and key in ('minus','KP_Subtract'): self._zoom_delta(-25); return True
        if ctrl and key in ('0','KP_0'): self._zoom_100(); return True
        if ctrl and key == 'F1': self._toggle_ribbon_stack(); return True
        if key == 'F4': self._toggle_sidebar(); return True
        if key == 'F5': self._present(); return True
        if key == 'F9': self._reading_mode_toggle(); return True
        if key == 'F11': self._fullscreen_toggle(); return True
        if key in ('Page_Down','Right','Down'): self.goto_page(self.page + 1); return True
        if key in ('Page_Up','Left','Up'): self.goto_page(self.page - 1); return True
        if key == 'Home': self.goto_page(0); return True
        if key == 'End': self.goto_page(self.page_count - 1); return True
        if key == 'Escape' and self.read_mode: self._reading_mode_toggle(); return True
        return False

    def _error(self, text):
        dlg = Gtk.MessageDialog(transient_for=self, modal=True, message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text='Print&View PDF')
        dlg.format_secondary_text(str(text)); dlg.run(); dlg.destroy()

    def _on_destroy(self, *_args):
        self.search_cancel.set()
        self.render_runner.shutdown(); self.prefetch_runner.shutdown()
        Gtk.Settings.get_default().disconnect(self.theme_signal)
        self.runner.shutdown()
        try: shutil.rmtree(self.cache_dir, ignore_errors=True)
        except Exception: pass
        Gtk.main_quit()


def _install_diagnostics():
    """Write exceptions and UI-freeze stack dumps to ~/.cache/print-view-pdf/diagnostics.log."""
    try:
        import faulthandler, threading, time, traceback
        log_dir = os.path.join(os.path.expanduser('~'), '.cache', 'print-view-pdf')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'diagnostics.log')
        if os.path.exists(log_path) and os.path.getsize(log_path) > 512 * 1024:
            os.replace(log_path, log_path + '.old')
        log = open(log_path, 'a', buffering=1, encoding='utf-8')
        log.write(f'\n=== Print&View PDF started {time.strftime("%Y-%m-%d %H:%M:%S")} ===\n')

        def hook(exc_type, exc, tb):
            log.write('Uncaught exception:\n' + ''.join(traceback.format_exception(exc_type, exc, tb)))
            sys.__excepthook__(exc_type, exc, tb)
        sys.excepthook = hook

        beat = {'t': time.monotonic(), 'dumped': False}

        def tick():
            beat['t'] = time.monotonic(); beat['dumped'] = False
            return True
        GLib.timeout_add(500, tick)

        def watchdog():
            while True:
                time.sleep(1.0)
                if time.monotonic() - beat['t'] > 4.0 and not beat['dumped']:
                    beat['dumped'] = True
                    log.write(f'UI thread blocked for more than 4 s at {time.strftime("%H:%M:%S")}; stacks:\n')
                    faulthandler.dump_traceback(file=log, all_threads=True)
        threading.Thread(target=watchdog, daemon=True, name='print-view-watchdog').start()
    except Exception:
        pass


def main():
    _install_diagnostics()
    load_css()
    initial = sys.argv[1] if len(sys.argv) > 1 else None
    PDFWindow(initial)
    Gtk.main()


if __name__ == '__main__':
    main()
