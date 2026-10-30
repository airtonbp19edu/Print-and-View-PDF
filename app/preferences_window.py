"""Preferences UI for PV-CFG-01 through PV-CFG-04."""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from preferences import PreferencesDraft


class PreferencesWindow(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title='Preferências — Print&View PDF', transient_for=parent, modal=True)
        self.parent_window = parent
        self.draft = PreferencesDraft(parent.preferences_store)
        width, height = parent.get_size()
        self.draft.values['interface'].update({
            'sidebar_visible': parent.sidebar_visible, 'ribbon_collapsed': parent.ribbon_collapsed,
            'window_width': max(760, min(3840, width)),
            'window_height': max(500, min(2160, height)),
        })
        self.baseline_theme = parent.theme_mode
        self._syncing = False
        self._committed_on_close = False
        self.set_default_size(860, 650)
        self.set_size_request(720, 540)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.get_style_context().add_class('preferences-window')
        self.controls = {}
        content = self.get_content_area()
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=24)
        title = Gtk.Label(label='Preferências', xalign=0)
        title.get_style_context().add_class('preferences-title')
        header.pack_start(title, False, False, 0)
        subtitle = Gtk.Label(label='Ajuste a interface, a leitura e a busca ao seu jeito.', xalign=0)
        subtitle.get_style_context().add_class('preferences-description')
        header.pack_start(subtitle, False, False, 0)
        content.pack_start(header, False, False, 0)
        content.pack_start(Gtk.Separator(), False, False, 0)
        body = Gtk.Box(spacing=0)
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(120)
        self.stack.set_hhomogeneous(False)
        self.stack.set_vhomogeneous(False)
        sidebar = Gtk.StackSidebar()
        sidebar.set_stack(self.stack)
        sidebar.set_size_request(175, -1)
        sidebar.get_style_context().add_class('preferences-sidebar')
        body.pack_start(sidebar, False, False, 0)
        body.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)
        body.pack_start(self.stack, True, True, 0)
        self._appearance_page()
        self._interface_page()
        self._reading_page()
        self._search_page()
        content.pack_start(body, True, True, 0)
        self.message = Gtk.Label(label='As alterações são salvas ao clicar em Aplicar ou Salvar.', xalign=0)
        self.message.set_line_wrap(True)
        self.message.set_margin_start(24)
        self.message.set_margin_end(24)
        self.message.set_margin_top(12)
        self.message.set_margin_bottom(12)
        self.message.get_style_context().add_class('preferences-description')
        content.pack_start(self.message, False, False, 0)
        restore = Gtk.Button(label='Restaurar seção')
        restore.set_tooltip_text('Restaurar os padrões da seção selecionada; clique em Aplicar para salvar.')
        restore.connect('clicked', lambda *_: self._reset(self.stack.get_visible_child_name()))
        actions = self.get_action_area()
        actions.add(restore)
        actions.set_child_secondary(restore, True)
        self.add_button('Cancelar', Gtk.ResponseType.CANCEL)
        self.apply_button = self.add_button('Aplicar', Gtk.ResponseType.APPLY)
        self.add_button('Salvar e fechar', Gtk.ResponseType.OK).get_style_context().add_class('suggested-action')
        self.connect('response', self._response)
        self.connect('destroy', self._destroyed)
        self.connect('key-press-event', self._key)
        self._populate()
        self.stack.set_visible_child_name('appearance')

    def _page(self, key, title, description):
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16, margin=24)
        heading = Gtk.Label(label=title, xalign=0)
        heading.get_style_context().add_class('preferences-section-title')
        box.pack_start(heading, False, False, 0)
        desc = Gtk.Label(label=description, xalign=0)
        desc.set_line_wrap(True)
        desc.set_max_width_chars(54)
        desc.get_style_context().add_class('preferences-description')
        box.pack_start(desc, False, False, 0)
        scroll.add(box)
        self.stack.add_titled(scroll, key, title)
        return box

    def _note(self, box, text):
        label = Gtk.Label(label=text, xalign=0)
        label.set_line_wrap(True)
        label.set_max_width_chars(54)
        label.get_style_context().add_class('preferences-description')
        box.pack_start(label, False, False, 0)

    def _check(self, box, section, key, label):
        button = Gtk.CheckButton(label=label)
        button.connect('toggled', lambda widget: self._changed(section, key, widget.get_active()))
        box.pack_start(button, False, False, 0)
        self.controls[(section, key)] = button
        return button

    def _appearance_page(self):
        box = self._page('appearance', 'Aparência', 'Escolha como o Print&View PDF aparece para você.')
        self.theme_buttons = {}
        group = None
        for mode, title, description in [
            ('system', 'Acompanhar o sistema', 'Usa o tema claro ou escuro reconhecido pelo GTK.'),
            ('light', 'Claro', 'Interface clara para ambientes bem iluminados.'),
            ('dark', 'Escuro', 'Interface escura para uma leitura mais confortável.')]:
            button = Gtk.RadioButton.new_with_label_from_widget(group, title)
            if group is None:
                group = button
            button.connect('toggled', self._theme_toggled, mode)
            box.pack_start(button, False, False, 0)
            self._note(box, description)
            self.theme_buttons[mode] = button
        self._note(box, 'A prévia do tema é imediata. Cancelar restaura o último tema aplicado. '
                   'As cores das páginas do PDF permanecem originais.')

    def _interface_page(self):
        box = self._page('interface', 'Interface', 'Defina como a janela e os painéis devem abrir.')
        self._check(box, 'interface', 'remember_layout', 'Lembrar o tamanho da janela e o estado dos painéis')
        self._check(box, 'interface', 'sidebar_visible', 'Mostrar painel lateral')
        self._check(box, 'interface', 'ribbon_collapsed', 'Manter a faixa de comandos recolhida')
        self._note(box, 'Com a memória de interface ativa, o tamanho da janela e o estado dos painéis '
                   'são atualizados ao fechar o aplicativo.')

    def _reading_page(self):
        box = self._page('reading', 'Leitura', 'Escolha a visualização inicial para os documentos.')
        box.pack_start(Gtk.Label(label='Ao abrir um PDF', xalign=0), False, False, 0)
        combo = Gtk.ComboBoxText()
        for key, label in [('fit-page', 'Ajustar página inteira'), ('fit-width', 'Ajustar à largura'),
                           ('percent', 'Usar percentual de zoom')]:
            combo.append(key, label)
        combo.connect('changed', lambda widget: self._changed('reading', 'zoom_mode', widget.get_active_id()))
        box.pack_start(combo, False, False, 0)
        self.controls[('reading', 'zoom_mode')] = combo
        row = Gtk.Box(spacing=12)
        row.pack_start(Gtk.Label(label='Zoom inicial', xalign=0), False, False, 0)
        self.zoom = Gtk.SpinButton.new_with_range(25, 400, 5)
        self.zoom.set_numeric(True)
        self.zoom.connect('value-changed', lambda widget: self._changed('reading', 'zoom_percent', widget.get_value_as_int()))
        self.controls[('reading', 'zoom_percent')] = self.zoom
        row.pack_start(self.zoom, False, False, 0)
        row.pack_start(Gtk.Label(label='%'), False, False, 0)
        box.pack_start(row, False, False, 0)
        self._check(box, 'reading', 'remember_document', 'Retomar página, zoom e rotação de cada PDF')
        self._note(box, 'O estado de cada arquivo tem prioridade sobre o zoom inicial. '
                   'Se o arquivo for alterado, ele abre com a configuração global. '
                   'São lembrados até 50 documentos; o PDF não é modificado.')
        self._note(box, 'O zoom inicial será usado na próxima abertura de um documento.')

    def _search_page(self):
        box = self._page('search', 'Busca', 'Escolha as opções iniciais da pesquisa textual.')
        for key, label in [('match_case', 'Diferenciar maiúsculas e minúsculas'),
                           ('whole_words', 'Localizar somente palavras inteiras'),
                           ('ignore_accents', 'Ignorar acentos'),
                           ('join_hyphens', 'Unir palavras hifenizadas entre linhas'),
                           ('show_results', 'Mostrar o painel de resultados ao pesquisar')]:
            self._check(box, 'search', key, label)
        self._note(box, 'As opções também podem ser alteradas na barra de pesquisa. '
                   'Ao aplicar novos padrões, uma busca em andamento é refeita com as opções escolhidas.')

    def _changed(self, section, key, value):
        if self._syncing:
            return
        self.draft.values[section][key] = value
        if section == 'reading':
            self.zoom.set_sensitive(self.draft.values['reading']['zoom_mode'] == 'percent')
        self.message.set_text('Alterações ainda não salvas.')

    def _theme_toggled(self, button, mode):
        if not button.get_active() or self._syncing:
            return
        self.draft.values['appearance'] = mode
        self.parent_window._preview_theme(mode)
        self.message.set_text('Prévia do tema. Clique em Aplicar para manter ou em Cancelar para desfazer.')

    def _populate(self):
        self._syncing = True
        try:
            self.theme_buttons[self.draft.values['appearance']].set_active(True)
            for (section, key), widget in self.controls.items():
                value = self.draft.values[section][key]
                if isinstance(widget, Gtk.ComboBoxText):
                    widget.set_active_id(value)
                elif isinstance(widget, Gtk.SpinButton):
                    widget.set_value(value)
                else:
                    widget.set_active(value)
            self.zoom.set_sensitive(self.draft.values['reading']['zoom_mode'] == 'percent')
        finally:
            self._syncing = False

    def _reset(self, section):
        self.draft.reset(section)
        self._populate()
        if section == 'appearance':
            self.parent_window._preview_theme(self.draft.values['appearance'])
        self.message.set_text('Padrões restaurados nesta seção. Clique em Aplicar para salvar.')

    def _response(self, _dialog, response):
        if response in (Gtk.ResponseType.APPLY, Gtk.ResponseType.OK):
            try:
                values = self.draft.apply()
            except (OSError, ValueError, TypeError) as exc:
                self.message.set_text(f'Não foi possível salvar. As alterações foram mantidas na janela. {exc}')
                return
            self.baseline_theme = 'auto' if values['appearance'] == 'system' else values['appearance']
            self.parent_window._apply_preferences(values)
            self.message.set_text('Preferências salvas.')
            if response == Gtk.ResponseType.OK:
                self._committed_on_close = True
                self.destroy()
        else:
            self.destroy()

    def _destroyed(self, *_args):
        if not self._committed_on_close:
            mode = 'system' if self.baseline_theme == 'auto' else self.baseline_theme
            self.parent_window._preview_theme(mode)
        self.parent_window.preferences_dialog = None

    def _key(self, _window, event):
        if Gdk.keyval_name(event.keyval) == 'Escape':
            self.response(Gtk.ResponseType.CANCEL)
            return True
        return False
