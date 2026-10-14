import math
import os
from pathlib import Path

import cairo
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

import cups_backend as cups
from imposition import (booklet_print_pairs, oriented_paper, paper_size_points,
                        poster_grid_for_size, select_page_indices)
from rendering import render_page, safe_filename_from_pdf




def _system_language():
    raw = (os.environ.get('LC_ALL') or os.environ.get('LC_MESSAGES') or os.environ.get('LANG') or 'en').lower()
    if raw.startswith('pt'):
        return 'pt'
    if raw.startswith('es'):
        return 'es'
    return 'en'


_VALUE_TRANSLATIONS = {
    'pt': {
        # Papel / mídia
        'stationery': 'Papel comum', 'plain': 'Papel comum', 'plainpaper': 'Papel comum',
        'stationerycoated': 'Papel revestido', 'coated': 'Papel revestido',
        'photo': 'Papel fotográfico', 'photopaper': 'Papel fotográfico',
        'photographic': 'Papel fotográfico',
        'photographichighgloss': 'Papel fotográfico de alto brilho',
        'photographicsemigloss': 'Papel fotográfico semibrilho',
        'photographicglossy': 'Papel fotográfico brilhante',
        'photographicmatte': 'Papel fotográfico fosco',
        'glossy': 'Papel brilhante', 'photoglossy': 'Papel fotográfico brilhante',
        'semigloss': 'Semibrilho', 'matte': 'Papel fosco',
        'envelope': 'Envelope', 'labels': 'Etiquetas', 'cardstock': 'Papel cartão',
        'transparency': 'Transparência',

        # Cor
        'rgb': 'Colorido (RGB)', 'color': 'Colorido', 'colour': 'Colorido',
        'gray': 'Escala de cinza', 'grey': 'Escala de cinza', 'grayscale': 'Escala de cinza',
        'devicegray': 'Escala de cinza', 'autogray': 'Escala de cinza automática',
        'processgray': 'Escala de cinza processada', 'monochrome': 'Monocromático',
        'mono': 'Monocromático', 'black': 'Preto', 'cmyk': 'Colorido (CMYK)',

        # Qualidade
        'draft': 'Rascunho', 'low': 'Baixa', 'normal': 'Normal', 'standard': 'Padrão',
        'high': 'Alta', 'best': 'Melhor', 'economy': 'Econômica', 'fine': 'Fina',
        'photoquality': 'Qualidade fotográfica',

        # Gerais / alimentação
        'auto': 'Automático', 'automatic': 'Automático', 'manual': 'Manual',
        'rear': 'Traseira', 'reartray': 'Bandeja traseira', 'cassette': 'Gaveta',
        'tray1': 'Bandeja 1', 'tray2': 'Bandeja 2', 'none': 'Nenhum',
        'faceup': 'Face para cima', 'facedown': 'Face para baixo',
        'auto-fit': 'Ajuste automático', 'autofit': 'Ajuste automático',
        'fill': 'Preencher área imprimível', 'fit': 'Ajustar à área imprimível',
        'off': 'Desativado', 'on': 'Ativado', 'true': 'Ativado', 'false': 'Desativado',

        # Duplex
        'onesided': 'Um lado', 'one-sided': 'Um lado',
        'twosidedlongedge': 'Frente e verso — borda longa',
        'two-sided-long-edge': 'Frente e verso — borda longa',
        'duplexnotumble': 'Frente e verso — borda longa',
        'twosidedshortedge': 'Frente e verso — borda curta',
        'two-sided-short-edge': 'Frente e verso — borda curta',
        'duplextumble': 'Frente e verso — borda curta',

        # Formatos tradicionais
        'letter': 'Carta', 'legal': 'Ofício / Legal', 'executive': 'Executivo',
        'env10': 'Envelope nº 10', 'com10': 'Envelope nº 10',
        'dl': 'Envelope DL', 'c5': 'Envelope C5',
    },
    'es': {
        'stationery': 'Papel normal', 'plain': 'Papel normal', 'plainpaper': 'Papel normal',
        'stationerycoated': 'Papel revestido', 'photo': 'Papel fotográfico',
        'photographic': 'Papel fotográfico', 'photographichighgloss': 'Papel fotográfico de alto brillo',
        'photographicsemigloss': 'Papel fotográfico semibrillo',
        'photographicglossy': 'Papel fotográfico brillante',
        'photographicmatte': 'Papel fotográfico mate', 'glossy': 'Papel brillante',
        'matte': 'Papel mate', 'envelope': 'Sobre', 'labels': 'Etiquetas',
        'rgb': 'Color (RGB)', 'color': 'Color', 'gray': 'Escala de grises',
        'grayscale': 'Escala de grises', 'devicegray': 'Escala de grises',
        'autogray': 'Escala de grises automática', 'processgray': 'Escala de grises procesada',
        'monochrome': 'Monocromo', 'draft': 'Borrador', 'low': 'Baja',
        'normal': 'Normal', 'standard': 'Estándar', 'high': 'Alta', 'best': 'Óptima',
        'auto': 'Automático', 'automatic': 'Automático', 'manual': 'Manual',
        'none': 'Ninguno', 'off': 'Desactivado', 'on': 'Activado',
        'faceup': 'Cara hacia arriba', 'facedown': 'Cara hacia abajo',
        'autofit': 'Ajuste automático', 'auto-fit': 'Ajuste automático',
        'fill': 'Rellenar área imprimible', 'fit': 'Ajustar al área imprimible',
        'onesided': 'Una cara', 'two-sided-long-edge': 'Doble cara — borde largo',
        'two-sided-short-edge': 'Doble cara — borde corto', 'letter': 'Carta',
        'legal': 'Legal', 'env10': 'Sobre n.º 10',
    },
}


def _paper_size_display(text, lang):
    """Traduz tokens de tamanho/mídia comuns dos PPDs sem alterar o valor real enviado ao CUPS."""
    raw = str(text or '').strip()
    if not raw:
        return raw

    # PPDs Epson usam sufixos como A4.Borderless e 4x6.Borderless.
    parts = raw.split('.')
    base = parts[0]
    suffixes = {p.lower() for p in parts[1:]}
    borderless = 'borderless' in suffixes or raw.lower().endswith('borderless')

    table = _VALUE_TRANSLATIONS.get(lang, {})
    compact = ''.join(ch for ch in base.lower() if ch.isalnum() or ch == '-')
    if compact in table:
        base_label = table[compact]
    else:
        # Formatos fotográficos em polegadas: 3.5x5, 4x6, 5x7, 8x10 etc.
        import re
        m = re.fullmatch(r'(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)', base, re.I)
        if m:
            a, b = m.groups()
            if lang in ('pt', 'es'):
                a, b = a.replace('.', ','), b.replace('.', ',')
            unit = 'pol.' if lang == 'pt' else ('pulg.' if lang == 'es' else 'in')
            base_label = f'{a} × {b} {unit}'
        else:
            # A4/A6/B5 etc. já são identificadores universais.
            base_label = base

    if borderless:
        suffix = 'Sem bordas' if lang == 'pt' else ('Sin bordes' if lang == 'es' else 'Borderless')
        return f'{base_label} — {suffix}'
    return base_label


def _choice_display(value, option_key=None):
    text = str(value or '')
    lang = _system_language()
    if lang == 'en':
        return text
    # print-scaling option: 'none' means no resizing, not an absent setting.
    if (option_key or '').lower().replace('_', '-') in ('print-scaling', 'printscaling') and text.lower() == 'none':
        return 'Sem escala (tamanho original)' if lang == 'pt' else 'Sin escala (tamaño original)'

    # Primeiro trata formatos de papel e variantes Borderless de forma genérica.
    lower = text.lower()
    if ('.borderless' in lower or lower.endswith('borderless') or
            any(lower.startswith(prefix) for prefix in ('a3', 'a4', 'a5', 'a6', 'b4', 'b5', 'letter', 'legal', 'env', 'com')) or
            ('x' in lower and any(ch.isdigit() for ch in lower))):
        paper = _paper_size_display(text, lang)
        if paper != text:
            return paper

    key = ''.join(ch for ch in text.lower() if ch.isalnum() or ch == '-')
    table = _VALUE_TRANSLATIONS.get(lang, {})
    if key in table:
        return table[key]

    # Heurísticas para PPDs que concatenam palavras sem separadores.
    if lang == 'pt':
        lk = key.replace('-', '')
        if 'photographic' in lk:
            if 'highgloss' in lk:
                return 'Papel fotográfico de alto brilho'
            if 'semigloss' in lk:
                return 'Papel fotográfico semibrilho'
            if 'glossy' in lk:
                return 'Papel fotográfico brilhante'
            if 'matte' in lk:
                return 'Papel fotográfico fosco'
            return 'Papel fotográfico'
        if lk.endswith('borderless'):
            return _paper_size_display(text, lang)
        if 'gray' in lk or 'grey' in lk:
            if 'auto' in lk:
                return 'Escala de cinza automática'
            if 'process' in lk:
                return 'Escala de cinza processada'
            return 'Escala de cinza'
    elif lang == 'es':
        lk = key.replace('-', '')
        if 'photographic' in lk:
            if 'highgloss' in lk:
                return 'Papel fotográfico de alto brillo'
            if 'semigloss' in lk:
                return 'Papel fotográfico semibrillo'
            if 'glossy' in lk:
                return 'Papel fotográfico brillante'
            if 'matte' in lk:
                return 'Papel fotográfico mate'
            return 'Papel fotográfico'
        if 'gray' in lk or 'grey' in lk:
            if 'auto' in lk:
                return 'Escala de grises automática'
            if 'process' in lk:
                return 'Escala de grises procesada'
            return 'Escala de grises'

    return text

FRIENDLY = {
    'PageSize': 'Tamanho do papel', 'media': 'Tamanho do papel',
    'ColorModel': 'Cor', 'cupsColorModel': 'Cor', 'print-color-mode': 'Cor',
    'cupsPrintQuality': 'Qualidade', 'print-quality': 'Qualidade',
    'Duplex': 'Frente e verso', 'sides': 'Frente e verso',
    'InputSlot': 'Origem do papel', 'MediaType': 'Tipo de papel',
    'Resolution': 'Resolução', 'printer-resolution': 'Resolução',
    'print-content-optimize': 'Otimização de conteúdo', 'output-bin': 'Bandeja de saída',
    'finishings': 'Acabamento', 'job-sheets': 'Folhas de separação',
    'OutputTray': 'Bandeja de saída', 'output-tray': 'Bandeja de saída',
    'OutputBin': 'Bandeja de saída', 'print-scaling': 'Escala de impressão',
    'PrintScaling': 'Escala de impressão', 'printScaling': 'Escala de impressão',
}


class OptionPicker(Gtk.Dialog):
    def __init__(self, parent, title, choices, current, option_key=None):
        super().__init__(title=title, transient_for=parent, modal=True)
        self.set_default_size(420, 420)
        self.add_buttons('Cancelar', Gtk.ResponseType.CANCEL, 'Selecionar', Gtk.ResponseType.OK)
        self.value = current
        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, margin=12)
        sc.add(box)
        group = None
        for choice in choices:
            radio = Gtk.RadioButton.new_with_label_from_widget(group, _choice_display(choice, option_key))
            if group is None:
                group = radio
            radio.set_active(choice == current)
            radio.connect('toggled', self._on_choice, choice)
            box.pack_start(radio, False, False, 0)
        self.get_content_area().pack_start(sc, True, True, 0)
        self.show_all()

    def _on_choice(self, radio, value):
        if radio.get_active():
            self.value = value


class PrinterPropertiesWindow(Gtk.Dialog):
    def __init__(self, parent, printer, options, selected, details=None, runner=None):
        super().__init__(title=f'Propriedades — {printer}', transient_for=parent, modal=True)
        self.set_default_size(720, 620)
        self.set_resizable(True)
        self.add_buttons('Cancelar', Gtk.ResponseType.CANCEL, 'OK', Gtk.ResponseType.OK)
        self.printer = printer
        self.runner = runner
        self.options = options
        self.details = details or {}
        self.selected = dict(selected or {})
        self.value_buttons = {}

        notebook = Gtk.Notebook()
        self.get_content_area().pack_start(notebook, True, True, 0)
        preferred = {'PageSize', 'media', 'ColorModel', 'cupsColorModel', 'print-color-mode',
                     'cupsPrintQuality', 'print-quality', 'InputSlot', 'MediaType',
                     'Resolution', 'printer-resolution'}
        layout = {'Duplex', 'sides', 'output-bin', 'finishings', 'job-sheets',
                  'print-content-optimize'}
        notebook.append_page(self._make_page(lambda k: k in preferred), Gtk.Label(label='Papel e qualidade'))
        notebook.append_page(self._make_page(lambda k: k in layout), Gtk.Label(label='Layout e acabamento'))
        notebook.append_page(self._make_page(lambda k: k not in preferred and k not in layout), Gtk.Label(label='Avançado'))
        notebook.append_page(self._maintenance_page(), Gtk.Label(label='Manutenção'))
        self.show_all()

    def _format_cups_date(self, value):
        """Convert CUPS' C-locale date to a compact pt-BR representation."""
        import re
        months = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12',
        }
        m = re.search(r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+([A-Z][a-z]{2})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})\s+(\d{4})', value or '')
        if not m:
            return value or '—'
        mon, day, clock, year = m.groups()
        return f'{int(day):02d}/{months.get(mon, mon)}/{year} {clock}'

    def _maintenance_summary(self):
        """Return clean user-facing fields extracted from lpstat/URI details."""
        import re
        raw = self.details.get('status') or ''
        uri = self.details.get('device_uri') or ''
        low = raw.lower()

        if ' is idle' in low:
            state = 'Pronta'
        elif ' is processing' in low or ' now printing' in low:
            state = 'Imprimindo'
        elif 'disabled' in low or 'stopped' in low:
            state = 'Pausada'
        else:
            state = 'Disponível' if raw else 'Não informado'

        queue = 'Pausada' if ('disabled' in low or 'stopped' in low) else 'Ativa'
        since = '—'
        m = re.search(r'enabled since\s+(.+?)(?:\n|$)', raw, flags=re.I)
        if m:
            since = self._format_cups_date(m.group(1).strip())

        if uri.startswith('ipps://'):
            connection = 'Rede — IPP seguro (IPPS)'
        elif uri.startswith('ipp://'):
            connection = 'Rede — IPP'
        elif uri.startswith('dnssd://'):
            connection = 'Rede — descoberta automática'
        elif uri.startswith('socket://'):
            connection = 'Rede — AppSocket/JetDirect'
        elif uri.startswith('lpd://'):
            connection = 'Rede — LPD/LPR'
        elif uri.startswith('usb://'):
            connection = 'USB'
        elif uri:
            connection = 'Direta / outro protocolo'
        else:
            connection = 'Não informada'

        description = self.printer
        m = re.search(r'^\s*Description:\s*(.+)$', raw, flags=re.I | re.M)
        if m:
            description = m.group(1).strip() or self.printer

        interface = '—'
        m = re.search(r'^\s*Interface:\s*(.+)$', raw, flags=re.I | re.M)
        if m:
            interface = m.group(1).strip()
        driver = interface.rsplit('/', 1)[-1] if interface not in ('', '—') else 'CUPS / driverless'

        return {
            'Impressora': description,
            'Estado': state,
            'Fila de impressão': queue,
            'Conexão': connection,
            'Ativa desde': since,
            'Driver / PPD': driver,
        }

    def _maintenance_page(self):
        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sc.set_propagate_natural_height(True)
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14, margin=16)
        sc.add(root)

        # --- Status resumido -------------------------------------------------
        status_frame = Gtk.Frame(label='Status da impressora')
        status_grid = Gtk.Grid(column_spacing=18, row_spacing=8, margin=12)
        status_frame.add(status_grid)
        for row, (label, value) in enumerate(self._maintenance_summary().items()):
            k = Gtk.Label(label=label + ':', xalign=0)
            k.set_width_chars(19)
            k.get_style_context().add_class('maintenance-key')
            v = Gtk.Label(label=value, xalign=0, selectable=True)
            v.set_line_wrap(True)
            status_grid.attach(k, 0, row, 1, 1)
            status_grid.attach(v, 1, row, 1, 1)
        root.pack_start(status_frame, False, False, 0)

        # --- Ações rápidas ---------------------------------------------------
        action_frame = Gtk.Frame(label='Ações rápidas')
        action_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=12)
        action_frame.add(action_box)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        action_box.pack_start(grid, False, False, 0)

        def action_button(label, action, tooltip=None):
            btn = Gtk.Button(label=label)
            btn.set_hexpand(True)
            btn.set_size_request(190, 38)
            if tooltip:
                btn.set_tooltip_text(tooltip)
            btn.connect('clicked', self._maintenance_action, action)
            return btn

        test = action_button('Imprimir página de teste', 'test',
                             'Envia a página de teste padrão do CUPS para esta impressora.')
        selftest = action_button('Verificar jatos / autoteste', 'selftest',
                                 'Solicita o autoteste do equipamento quando o driver aceita o comando CUPS.')
        clean = action_button('Limpeza do cabeçote', 'clean',
                              'Executa limpeza quando o driver ou utilitário da impressora oferece suporte.')
        levels = action_button('Consultar níveis / status', 'levels',
                               'Solicita níveis de suprimentos/status quando o driver oferece suporte.')
        grid.attach(test, 0, 0, 1, 1)
        grid.attach(selftest, 1, 0, 1, 1)
        grid.attach(clean, 0, 1, 1, 1)
        grid.attach(levels, 1, 1, 1, 1)

        epson = action_button('Abrir Epson Printer Utility', 'epson',
                              'Abre o utilitário oficial da Epson, quando instalado.')
        epson.set_sensitive(bool(self.details.get('epson_utility')))
        grid.attach(epson, 0, 2, 2, 1)

        self.maintenance_feedback = Gtk.Label(label='Pronta para executar uma ação de manutenção.', xalign=0)
        self.maintenance_feedback.set_line_wrap(True)
        self.maintenance_feedback.get_style_context().add_class('muted')
        action_box.pack_start(self.maintenance_feedback, False, False, 0)

        if 'epson' in self.printer.lower() and not self.details.get('epson_utility'):
            vendor = Gtk.Label(
                label='Epson Printer Utility não encontrado. As ações CUPS continuam disponíveis quando o driver da impressora aceitar esses comandos.',
                xalign=0)
            vendor.set_line_wrap(True)
            vendor.get_style_context().add_class('muted')
            action_box.pack_start(vendor, False, False, 0)

        root.pack_start(action_frame, False, False, 0)

        # --- Detalhes técnicos, recolhidos por padrão ------------------------
        expander = Gtk.Expander(label='Mostrar detalhes técnicos')
        expander.set_expanded(False)
        tech_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin=10)
        expander.add(tech_box)

        uri = self.details.get('device_uri') or 'Não informado'
        commands = self.details.get('maintenance_commands') or []
        cmd_text = ', '.join(commands) if commands else 'Nenhum comando anunciado pelo PPD/driver'

        uri_lbl = Gtk.Label(label=f'URI do dispositivo: {uri}', xalign=0, selectable=True)
        uri_lbl.set_line_wrap(True)
        tech_box.pack_start(uri_lbl, False, False, 0)
        cmd_lbl = Gtk.Label(label=f'Comandos de manutenção anunciados: {cmd_text}', xalign=0, selectable=True)
        cmd_lbl.set_line_wrap(True)
        tech_box.pack_start(cmd_lbl, False, False, 0)

        raw = self.details.get('status') or 'Nenhum detalhe adicional fornecido pelo CUPS.'
        raw_scroll = Gtk.ScrolledWindow()
        raw_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        raw_scroll.set_size_request(-1, 170)
        raw_view = Gtk.TextView()
        raw_view.set_editable(False)
        raw_view.set_cursor_visible(False)
        raw_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        raw_view.set_monospace(True)
        raw_view.get_buffer().set_text(raw)
        raw_scroll.add(raw_view)
        tech_box.pack_start(raw_scroll, True, True, 0)
        root.pack_start(expander, False, False, 0)

        note = Gtk.Label(
            label='Observação: funções de manutenção dependem do que o driver/IPP e o fabricante expõem ao Linux. Recursos não anunciados não são simulados pelo Print&View PDF.',
            xalign=0)
        note.set_line_wrap(True)
        note.get_style_context().add_class('muted')
        root.pack_start(note, False, False, 0)
        return sc

    def _maintenance_action(self, btn, action):
        if action == 'clean':
            dlg = Gtk.MessageDialog(transient_for=self, modal=True,
                                    message_type=Gtk.MessageType.WARNING,
                                    buttons=Gtk.ButtonsType.OK_CANCEL,
                                    text='Executar limpeza do cabeçote?')
            dlg.format_secondary_text(
                'A limpeza consome tinta. Execute somente quando houver falhas de impressão ou a verificação de jatos indicar necessidade.')
            resp = dlg.run()
            dlg.destroy()
            if resp != Gtk.ResponseType.OK:
                return

        labels = {
            'test': 'Enviando página de teste…',
            'selftest': 'Solicitando verificação/autoteste…',
            'clean': 'Solicitando limpeza do cabeçote…',
            'levels': 'Consultando níveis/status…',
            'epson': 'Abrindo Epson Printer Utility…',
        }
        if hasattr(self, 'maintenance_feedback'):
            self.maintenance_feedback.set_markup(f'<span foreground="#5b6169">{labels.get(action, "Executando…")}</span>')
        if btn:
            btn.set_sensitive(False)

        def work():
            if action == 'test':
                return cups.print_test_page(self.printer)
            if action == 'selftest':
                return cups.send_maintenance_command(self.printer, 'PrintSelfTestPage')
            if action == 'clean':
                return cups.send_maintenance_command(self.printer, 'Clean all')
            if action == 'levels':
                return cups.send_maintenance_command(self.printer, 'ReportLevels')
            if action == 'epson':
                return cups.launch_vendor_utility(self.printer)
            return ''

        def friendly_success(message):
            low = (message or '').lower()
            if action == 'test':
                return 'Página de teste enviada para a fila de impressão.'
            if action == 'selftest':
                return 'Comando de verificação/autoteste enviado à impressora.'
            if action == 'clean':
                return 'Comando de limpeza enviado à impressora.'
            if action == 'levels':
                return 'Consulta de níveis/status enviada à impressora.'
            if action == 'epson':
                return 'Epson Printer Utility aberto.'
            if 'request id' in low:
                return 'Comando enviado à fila de impressão.'
            return message or 'Comando enviado.'

        def done(msg):
            if btn:
                btn.set_sensitive(True)
            if hasattr(self, 'maintenance_feedback'):
                safe = friendly_success(msg).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                self.maintenance_feedback.set_markup(f'<span foreground="#2f6e3b"><b>Concluído:</b> {safe}</span>')

        def failed(exc):
            if btn:
                btn.set_sensitive(True)
            if hasattr(self, 'maintenance_feedback'):
                safe = str(exc).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                self.maintenance_feedback.set_markup(f'<span foreground="#a12620"><b>Não foi possível executar:</b> {safe}</span>')

        if self.runner:
            self.runner.submit(f'maintenance-{action}', work, done, failed)
        else:
            try:
                done(work())
            except Exception as exc:
                failed(exc)

    def _make_page(self, predicate):
        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        grid = Gtk.Grid(column_spacing=16, row_spacing=10, margin=16)
        sc.add(grid)
        row = 0
        for key, meta in self.options.items():
            if not predicate(key):
                continue
            label = Gtk.Label(label=FRIENDLY.get(key, meta.get('label', key)), xalign=0)
            value = self.selected.get(key, meta.get('current'))
            choices = meta.get('choices', [])
            if len(choices) <= 1:
                # Do not advertise a selector when the driver exposes just one
                # possible value.  CUPS cannot switch to a nonadvertised tray.
                btn = Gtk.Label(label=_choice_display(value, key) if value else 'Não informado', xalign=0)
                btn.set_tooltip_text('Opção fixa: o driver CUPS da impressora não oferece alternativas.')
                btn.get_style_context().add_class('muted')
            else:
                btn = Gtk.Button(label=_choice_display(value, key) if value else 'Selecionar…')
                btn.connect('clicked', self._pick, key)
                self.value_buttons[key] = btn
            btn.set_hexpand(True)
            grid.attach(label, 0, row, 1, 1)
            grid.attach(btn, 1, row, 1, 1)
            row += 1
        if row == 0:
            grid.attach(Gtk.Label(label='Nenhuma opção exposta pelo driver nesta seção.', xalign=0), 0, 0, 2, 1)
        return sc

    def _pick(self, _button, key):
        meta = self.options[key]
        if len(meta.get('choices', [])) <= 1:
            return
        current = self.selected.get(key, meta.get('current'))
        dlg = OptionPicker(self, FRIENDLY.get(key, meta.get('label', key)), meta.get('choices', []), current, option_key=key)
        if dlg.run() == Gtk.ResponseType.OK:
            self.selected[key] = dlg.value
            self.value_buttons[key].set_label(_choice_display(dlg.value, key))
        dlg.destroy()

    def result(self):
        return dict(self.selected)


class PrintWindow(Gtk.Window):
    def __init__(self, parent, runner, filepath, page_count, page_sizes, current_page,
                 cache_dir, on_submit):
        super().__init__(title='Imprimir — Print&View PDF')
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_destroy_with_parent(True)
        self.set_resizable(True)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_role('print-view-pdf-print')
        self.set_icon_name('print-view-pdf')
        self._set_workarea_size()

        self.runner = runner
        self._closed = False
        self.connect('destroy', self._on_destroy)
        self.filepath = filepath
        self.page_count = page_count
        self.page_sizes = page_sizes
        self.current_page = current_page
        self.cache_dir = cache_dir
        self.on_submit = on_submit
        self.printers = []
        self.printer_options = {}
        self.selected_options = {}
        self.preview_pixbuf = None
        # Miniaturas reais usadas dentro do preview dos modos avançados.
        self.preview_thumbs = {}
        self.preview_thumb_pending = set()
        # Index into the actual printable booklet faces (not source pages).
        self.booklet_preview_index = 0

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin=10)
        self.add(root)
        root.pack_start(self._build_destination_bar(), False, False, 0)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_wide_handle(True)
        root.pack_start(paned, True, True, 0)
        paned.pack1(self._build_preview(), resize=False, shrink=True)
        paned.pack2(self._build_settings(), resize=True, shrink=True)
        paned.set_position(390)

        self._refresh_preview_labels()
        self._load_printers_async()
        self._request_preview_image()
        self.show_all()
        # show_all makes every child visible; hide booklet-only navigator
        # again until the user selects the Livreto mode.
        self._refresh_preview_labels()

    def _set_workarea_size(self):
        try:
            display = Gdk.Display.get_default()
            mon = display.get_monitor_at_window(self.get_transient_for().get_window()) if self.get_transient_for() and self.get_transient_for().get_window() else display.get_primary_monitor()
            area = mon.get_workarea()
            self.set_default_size(min(1180, max(880, area.width - 60)), min(720, max(540, area.height - 80)))
        except Exception:
            self.set_default_size(1100, 650)

    def _frame(self, title):
        frame = Gtk.Frame(label=title)
        frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        return frame

    def _build_destination_bar(self):
        frame = self._frame('Destino')
        grid = Gtk.Grid(column_spacing=10, row_spacing=6, margin=10)
        frame.add(grid)
        self.dest_combo = Gtk.ComboBoxText()
        self.dest_combo.append('save-pdf', 'Salvar como PDF…')
        self.dest_combo.set_active_id('save-pdf')
        self.dest_combo.set_hexpand(True)
        self.dest_combo.connect('changed', self._destination_changed)
        grid.attach(Gtk.Label(label='Destino:', xalign=0), 0, 0, 1, 1)
        grid.attach(self.dest_combo, 1, 0, 1, 1)

        self.props_btn = Gtk.Button(label='Propriedades…')
        self.props_btn.set_sensitive(False)
        self.props_btn.connect('clicked', self._open_properties)
        grid.attach(self.props_btn, 2, 0, 1, 1)

        grid.attach(Gtk.Label(label='Cópias:'), 3, 0, 1, 1)
        self.copies = Gtk.SpinButton.new_with_range(1, 999, 1)
        self.copies.set_value(1)
        grid.attach(self.copies, 4, 0, 1, 1)
        self.collate = Gtk.CheckButton(label='Agrupar')
        self.collate.set_active(True)
        grid.attach(self.collate, 5, 0, 1, 1)
        self.gray = Gtk.CheckButton(label='Escala de cinza')
        grid.attach(self.gray, 6, 0, 1, 1)

        actions = Gtk.Box(spacing=6)
        cancel = Gtk.Button(label='Cancelar')
        cancel.connect('clicked', lambda *_: self._close_window())
        self.action_btn = Gtk.Button(label='Salvar')
        self.action_btn.get_style_context().add_class('suggested-action')
        self.action_btn.connect('clicked', self._submit)
        actions.pack_start(cancel, False, False, 0)
        actions.pack_start(self.action_btn, False, False, 0)
        grid.attach(actions, 7, 0, 1, 1)

        self.dest_status = Gtk.Label(label='Carregando impressoras do CUPS…', xalign=0)
        self.dest_status.get_style_context().add_class('muted')
        grid.attach(self.dest_status, 1, 1, 2, 1)
        self.print_as_image = Gtk.CheckButton(label='Imprimir como imagem')
        grid.attach(self.print_as_image, 3, 1, 2, 1)
        self.image_dpi = Gtk.ComboBoxText()
        self.image_dpi.append('300', '300 DPI')
        self.image_dpi.append('600', '600 DPI')
        self.image_dpi.set_active_id('300')
        grid.attach(self.image_dpi, 5, 1, 1, 1)
        return frame

    def _build_preview(self):
        frame = self._frame('Visualização')
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=8)
        frame.add(box)
        self.preview_info = Gtk.Label(label='', xalign=0)
        self.preview_info.get_style_context().add_class('muted')
        box.pack_start(self.preview_info, False, False, 0)
        self.preview = Gtk.DrawingArea()
        self.preview.set_size_request(340, 430)
        self.preview.connect('draw', self._draw_preview)
        box.pack_start(self.preview, True, True, 0)
        self.booklet_nav = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.booklet_previous = Gtk.Button(label='◀ Anterior')
        self.booklet_previous.connect('clicked', self._booklet_step, -1)
        self.booklet_nav.pack_start(self.booklet_previous, False, False, 0)
        self.booklet_position = Gtk.Label(label='', xalign=0.5)
        self.booklet_position.set_hexpand(True)
        self.booklet_nav.pack_start(self.booklet_position, True, True, 0)
        self.booklet_next = Gtk.Button(label='Próxima ▶')
        self.booklet_next.connect('clicked', self._booklet_step, 1)
        self.booklet_nav.pack_start(self.booklet_next, False, False, 0)
        box.pack_start(self.booklet_nav, False, False, 0)
        self.preview_summary = Gtk.Label(label='', xalign=0)
        self.preview_summary.set_line_wrap(True)
        box.pack_start(self.preview_summary, False, False, 0)
        return frame

    def _build_settings(self):
        sc = Gtk.ScrolledWindow()
        sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin=2)
        sc.add(box)
        box.pack_start(self._build_range(), False, False, 0)
        box.pack_start(self._build_handling(), False, False, 0)
        return sc

    def _build_range(self):
        frame = self._frame('Intervalo de impressão')
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7, margin=10)
        frame.add(box)
        row = Gtk.Box(spacing=12)
        self.r_all = Gtk.RadioButton.new_with_label_from_widget(None, 'Todas')
        self.r_current = Gtk.RadioButton.new_with_label_from_widget(self.r_all, 'Página atual')
        self.r_pages = Gtk.RadioButton.new_with_label_from_widget(self.r_all, 'Páginas:')
        self.r_all.set_active(True)
        for w in (self.r_all, self.r_current, self.r_pages):
            w.connect('toggled', self._controls_changed)
            row.pack_start(w, False, False, 0)
        self.range_entry = Gtk.Entry(placeholder_text='ex.: 1-3,5,8-10')
        self.range_entry.set_sensitive(False)
        self.range_entry.connect('changed', self._controls_changed)
        row.pack_start(self.range_entry, True, True, 0)
        box.pack_start(row, False, False, 0)
        row2 = Gtk.Box(spacing=10)
        row2.pack_start(Gtk.Label(label='Subconjunto:'), False, False, 0)
        self.subset = Gtk.ComboBoxText()
        for x in ('Todas as páginas', 'Somente ímpares', 'Somente pares'):
            self.subset.append_text(x)
        self.subset.set_active(0)
        self.subset.connect('changed', self._controls_changed)
        row2.pack_start(self.subset, False, False, 0)
        self.reverse = Gtk.CheckButton(label='Ordem inversa')
        self.reverse.connect('toggled', self._controls_changed)
        row2.pack_start(self.reverse, False, False, 0)
        box.pack_start(row2, False, False, 0)
        return frame

    def _build_handling(self):
        frame = self._frame('Dimensionamento e manuseio de páginas')
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin=10)
        frame.add(box)
        orient = Gtk.Box(spacing=10)
        orient.pack_start(Gtk.Label(label='Orientação:'), False, False, 0)
        self.orientation = Gtk.ComboBoxText()
        self.orientation.append('portrait', 'Retrato')
        self.orientation.append('landscape', 'Paisagem')
        self.orientation.set_active_id('portrait')
        self.orientation.connect('changed', self._controls_changed)
        orient.pack_start(self.orientation, False, False, 0)
        self.paper_label = Gtk.Label(label='Papel: A4', xalign=0)
        self.paper_label.get_style_context().add_class('muted')
        orient.pack_start(self.paper_label, True, True, 0)
        box.pack_start(orient, False, False, 0)

        self.mode_stack = Gtk.Stack()
        self.mode_stack.set_transition_type(Gtk.StackTransitionType.NONE)
        self.mode_stack.add_titled(self._size_page(), 'size', 'Tamanho')
        self.mode_stack.add_titled(self._poster_page(), 'poster', 'Pôster')
        self.mode_stack.add_titled(self._multiple_page(), 'multiple', 'Várias')
        self.mode_stack.add_titled(self._booklet_page(), 'booklet', 'Livreto')
        self.mode_stack.connect('notify::visible-child-name', self._controls_changed)
        switch = Gtk.StackSwitcher()
        switch.set_stack(self.mode_stack)
        switch.set_hexpand(True)
        box.pack_start(switch, False, False, 0)
        box.pack_start(self.mode_stack, False, False, 0)
        return frame

    def _size_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin=8)
        self.scale = Gtk.ComboBoxText()
        self.scale.append('actual', 'Tamanho real (100%)')
        self.scale.append('fit', 'Ajustar à área da página')
        self.scale.set_active_id('actual')
        self.scale.connect('changed', self._controls_changed)
        row = Gtk.Box(spacing=10)
        row.pack_start(Gtk.Label(label='Escala:'), False, False, 0)
        row.pack_start(self.scale, False, False, 0)
        box.pack_start(row, False, False, 0)
        box.pack_start(Gtk.Label(label='Tamanho real bloqueia a redução automática do CUPS.', xalign=0), False, False, 0)
        return box

    def _poster_page(self):
        # Poster controls: scale, overlap, labels and cut marks.
        grid = Gtk.Grid(column_spacing=8, row_spacing=6, margin=7)
        grid.attach(Gtk.Label(label='Escala lado a lado:', xalign=0), 0, 0, 1, 1)
        self.poster_scale = Gtk.SpinButton.new_with_range(10, 1000, 5)
        self.poster_scale.set_value(100)
        self.poster_scale.connect('value-changed', self._controls_changed)
        grid.attach(self.poster_scale, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label='%'), 2, 0, 1, 1)

        grid.attach(Gtk.Label(label='Sobreposição:', xalign=0), 0, 1, 1, 1)
        self.poster_overlap = Gtk.SpinButton.new_with_range(0, 500, 1)
        self.poster_overlap.set_value(5)
        self.poster_overlap.connect('value-changed', self._controls_changed)
        grid.attach(self.poster_overlap, 1, 1, 1, 1)
        self.poster_overlap_unit = Gtk.ComboBoxText()
        for unit, label in (('mm', 'mm'), ('cm', 'cm'), ('in', 'pol.')):
            self.poster_overlap_unit.append(unit, label)
        self.poster_overlap_unit.set_active_id('mm')
        self.poster_overlap_unit.connect('changed', self._controls_changed)
        grid.attach(self.poster_overlap_unit, 2, 1, 1, 1)

        self.poster_cut_marks = Gtk.CheckButton(label='Marcas de corte')
        self.poster_cut_marks.set_active(True)
        self.poster_cut_marks.connect('toggled', self._controls_changed)
        grid.attach(self.poster_cut_marks, 0, 2, 1, 1)

        self.poster_labels = Gtk.CheckButton(label='Identificação e encaixe')
        self.poster_labels.set_active(True)
        self.poster_labels.connect('toggled', self._controls_changed)
        grid.attach(self.poster_labels, 1, 2, 2, 1)

        # Kept as internal compatibility switches for old job dictionaries.
        self.poster_large = Gtk.CheckButton()
        self.poster_large.set_active(True)
        self.poster_glue = Gtk.CheckButton()
        self.poster_glue.set_active(False)
        self.poster_mark_margin = Gtk.SpinButton.new_with_range(0, 0, 1)
        self.poster_mark_margin.set_value(0)

        self.poster_area_info = Gtk.Label(label='', xalign=0)
        self.poster_area_info.set_line_wrap(True)
        self.poster_area_info.get_style_context().add_class('muted')
        grid.attach(self.poster_area_info, 0, 3, 3, 1)

        hint = Gtk.Label(
            label='Modo pôster: Zoom da página define o tamanho final; Sobreposição repete uma faixa entre folhas. '
                  'Linhas pontilhadas indicam onde cortar. As marcas de registro devem ficar na mesma altura nas duas folhas. '
                  'As etiquetas identificam as bordas a manter, cortar e encaixar.',
            xalign=0)
        hint.set_line_wrap(True)
        hint.get_style_context().add_class('muted')
        grid.attach(hint, 0, 4, 3, 1)
        return grid

    def _poster_overlap_mm(self):
        value = float(self.poster_overlap.get_value())
        unit = self.poster_overlap_unit.get_active_id() or 'mm'
        return value * {'mm': 1.0, 'cm': 10.0, 'in': 25.4}.get(unit, 1.0)

    def _multiple_page(self):
        grid = Gtk.Grid(column_spacing=10, row_spacing=8, margin=8)
        grid.attach(Gtk.Label(label='Páginas por folha:', xalign=0), 0, 0, 1, 1)
        self.nup = Gtk.ComboBoxText()
        for n in (1, 2, 4, 6, 9, 16):
            self.nup.append(str(n), str(n))
        self.nup.set_active_id('4')
        self.nup.connect('changed', self._controls_changed)
        grid.attach(self.nup, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label='Ordem:', xalign=0), 0, 1, 1, 1)
        self.nup_layout = Gtk.ComboBoxText()
        for value, label in [('lrtb', 'Esq. → dir., cima → baixo'), ('lrbt', 'Esq. → dir., baixo → cima'),
                             ('rltb', 'Dir. → esq., cima → baixo'), ('rlbt', 'Dir. → esq., baixo → cima')]:
            self.nup_layout.append(value, label)
        self.nup_layout.set_active_id('lrtb')
        self.nup_layout.connect('changed', self._controls_changed)
        grid.attach(self.nup_layout, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label='Margem interna:', xalign=0), 0, 2, 1, 1)
        self.nup_margin = Gtk.SpinButton.new_with_range(0, 20, 1)
        self.nup_margin.set_value(4)
        self.nup_margin.connect('value-changed', self._controls_changed)
        grid.attach(self.nup_margin, 1, 2, 1, 1)
        grid.attach(Gtk.Label(label='mm'), 2, 2, 1, 1)
        return grid

    def _booklet_page(self):
        grid = Gtk.Grid(column_spacing=10, row_spacing=8, margin=8)
        grid.attach(Gtk.Label(label='Encadernação:', xalign=0), 0, 0, 1, 1)
        self.binding = Gtk.ComboBoxText()
        self.binding.append('left', 'Esquerda')
        self.binding.append('right', 'Direita')
        self.binding.set_active_id('left')
        self.binding.connect('changed', self._controls_changed)
        grid.attach(self.binding, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label='Lados:', xalign=0), 0, 1, 1, 1)
        self.book_sides = Gtk.ComboBoxText()
        self.book_sides.append('both', 'Ambos os lados')
        self.book_sides.append('front', 'Somente frente')
        self.book_sides.append('back', 'Somente verso')
        self.book_sides.set_active_id('both')
        self.book_sides.connect('changed', self._controls_changed)
        self.book_sides.set_tooltip_text('Selecione as faces que serão impressas. A visualização mostra apenas essas faces.')
        grid.attach(self.book_sides, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label='Margem de segurança:', xalign=0), 0, 2, 1, 1)
        self.book_safe = Gtk.SpinButton.new_with_range(0, 30, 1)
        self.book_safe.set_value(5)
        self.book_safe.connect('value-changed', self._controls_changed)
        grid.attach(self.book_safe, 1, 2, 1, 1)
        grid.attach(Gtk.Label(label='mm'), 2, 2, 1, 1)
        grid.attach(Gtk.Label(label='Margem da dobra:', xalign=0), 0, 3, 1, 1)
        self.book_gutter = Gtk.SpinButton.new_with_range(0, 30, 1)
        self.book_gutter.set_value(3)
        self.book_gutter.connect('value-changed', self._controls_changed)
        grid.attach(self.book_gutter, 1, 3, 1, 1)
        grid.attach(Gtk.Label(label='mm'), 2, 3, 1, 1)
        self.auto_duplex = Gtk.CheckButton(label='Frente e verso automático (borda curta)')
        self.auto_duplex.set_tooltip_text('Disponível apenas em Ambos os lados, quando a impressora oferece duplex automático.')
        grid.attach(self.auto_duplex, 0, 4, 3, 1)
        return grid

    def _load_printers_async(self):
        def ok(printers):
            if self._closed:
                return
            self.printers = printers
            default_id = None
            for p in printers:
                dest = 'cups:' + p['name']
                self.dest_combo.append(dest, p['name'])
                if p.get('default'):
                    default_id = dest
            if default_id:
                self.dest_combo.set_active_id(default_id)
            self.dest_status.set_text('Pronto.' if printers else 'Nenhuma impressora encontrada; Salvar como PDF continua disponível.')
        self.runner.submit('print-printers', cups.list_printers, ok,
                           lambda e: self._set_label_text(self.dest_status, f'Falha ao consultar CUPS: {e}') if not self._closed else None)

    def _destination_changed(self, *_args):
        is_save = self.dest_combo.get_active_id() == 'save-pdf'
        self.action_btn.set_label('Salvar' if is_save else 'Imprimir')
        self.props_btn.set_sensitive(not is_save and bool(self.dest_combo.get_active_id()))
        # Poster geometry depends on the selected printer's PPD imageable area.
        if hasattr(self, 'paper_label'):
            self._update_paper_label()
        if hasattr(self, 'preview'):
            self._refresh_preview_labels()
            self.preview.queue_draw()

    def _open_properties(self, *_args):
        if os.name == 'nt':
            from windows_print import show_properties
            destination = self.dest_combo.get_active_id() or ''
            if destination.startswith('cups:'):
                try:
                    show_properties(destination[5:])
                except Exception as exc:
                    self.dest_status.set_text(str(exc))
            return
        dest = self.dest_combo.get_active_id() or ''
        if not dest.startswith('cups:'):
            return
        printer = dest[5:]
        self.props_btn.set_sensitive(False)
        self.dest_status.set_text('Carregando propriedades da impressora…')
        def ok(payload):
            if self._closed:
                return
            options, details = payload
            self.props_btn.set_sensitive(True)
            self.dest_status.set_text('Pronto.')
            dlg = PrinterPropertiesWindow(self, printer, options, self.selected_options, details, self.runner)
            if dlg.run() == Gtk.ResponseType.OK:
                self.selected_options = dlg.result()
                self._update_paper_label()
                self.preview.queue_draw()
            dlg.destroy()
        def err(exc):
            if self._closed:
                return
            self.props_btn.set_sensitive(True)
            self.dest_status.set_text(f'Falha ao ler propriedades: {exc}')
        self.runner.submit('printer-properties', lambda: (cups.get_ppd_options(printer), cups.get_printer_details(printer)), ok, err)

    def _request_preview_image(self):
        if self._closed:
            return
        self.runner.submit('print-thumb', lambda: render_page(self.filepath, self.current_page, 300, self.cache_dir, 'print'),
                           self._preview_loaded, lambda _e: None)
        self._request_mode_thumbnails()

    def _preview_loaded(self, path):
        if self._closed:
            return
        try:
            self.preview_pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
            self.preview.queue_draw()
        except Exception:
            pass

    def _booklet_faces(self, indices=None):
        """Exactly the faces that create_booklet will write to the print PDF."""
        if indices is None:
            indices = self._selected_indices()
        return booklet_print_pairs(indices, self.book_sides.get_active_id() or 'both')

    def _current_booklet_face(self, indices=None):
        faces = self._booklet_faces(indices)
        self.booklet_preview_index = min(max(0, self.booklet_preview_index), max(0, len(faces) - 1))
        return faces[self.booklet_preview_index] if faces else None

    def _booklet_step(self, _button, amount):
        faces = self._booklet_faces()
        self.booklet_preview_index = min(max(0, self.booklet_preview_index + amount), max(0, len(faces) - 1))
        self._refresh_preview_labels()
        self._request_mode_thumbnails()
        self.preview.queue_draw()

    def _mode_thumbnail_indices(self):
        indices = self._selected_indices()
        if not indices:
            return []
        mode = self.mode_stack.get_visible_child_name() or 'size'
        if mode == 'poster':
            return indices[:1]
        if mode == 'multiple':
            try:
                nup = int(self.nup.get_active_id() or 4)
            except Exception:
                nup = 4
            return indices[:max(1, min(16, nup))]
        if mode == 'booklet':
            pair = self._current_booklet_face(indices)
            if not pair:
                return []
            pages = pair[1:]
            if self.binding.get_active_id() == 'right': pages = pages[::-1]
            return [idx for idx in pages if idx is not None]
        return indices[:1]

    def _request_mode_thumbnails(self):
        if self._closed:
            return
        for idx in self._mode_thumbnail_indices():
            if idx in self.preview_thumbs or idx in self.preview_thumb_pending:
                continue
            self.preview_thumb_pending.add(idx)
            channel = f'print-mode-thumb-{idx}'
            def work(page_idx=idx):
                return page_idx, render_page(self.filepath, page_idx, 220, self.cache_dir, 'print-mode')
            def ok(result):
                page_idx, path = result
                self.preview_thumb_pending.discard(page_idx)
                if self._closed:
                    return
                try:
                    self.preview_thumbs[page_idx] = GdkPixbuf.Pixbuf.new_from_file(path)
                except Exception:
                    return
                self.preview.queue_draw()
            def err(_exc, page_idx=idx):
                self.preview_thumb_pending.discard(page_idx)
            self.runner.submit(channel, work, ok, err)

    @staticmethod
    def _draw_pixbuf_in_rect(cr, pixbuf, x, y, w, h, margin=4):
        if not pixbuf or w <= 2 or h <= 2:
            return
        avail_w = max(1, w - margin * 2)
        avail_h = max(1, h - margin * 2)
        ratio = min(avail_w / pixbuf.get_width(), avail_h / pixbuf.get_height())
        tw = max(1, int(pixbuf.get_width() * ratio))
        th = max(1, int(pixbuf.get_height() * ratio))
        scaled = pixbuf.scale_simple(tw, th, GdkPixbuf.InterpType.BILINEAR)
        px = x + (w - tw) / 2
        py = y + (h - th) / 2
        Gdk.cairo_set_source_pixbuf(cr, scaled, px, py)
        cr.paint()

    def _controls_changed(self, *_args):
        if self._closed:
            return
        if _args and _args[0] in (self.book_sides, self.mode_stack, self.r_all,
                                  self.r_current, self.r_pages, self.range_entry,
                                  self.subset, self.reverse):
            self.booklet_preview_index = 0
        self.range_entry.set_sensitive(self.r_pages.get_active())
        if self.mode_stack.get_visible_child_name() == 'booklet':
            self.orientation.set_active_id('landscape')
            self.orientation.set_sensitive(False)
            # Front-only/back-only jobs must remain single-sided, independent
            # of any duplex selection retained from earlier booklet jobs.
            self.auto_duplex.set_sensitive(self.book_sides.get_active_id() == 'both')
        else:
            self.orientation.set_sensitive(True)
        self._update_paper_label()
        self._refresh_preview_labels()
        self._request_mode_thumbnails()
        self.preview.queue_draw()

    @staticmethod
    def _set_label_text(label, text):
        """Avoid GTK relayouts from repeated, identical draw-time updates."""
        if label.get_text() != text:
            label.set_text(text)

    def _refresh_preview_labels(self):
        """Update text summaries when controls change, outside the draw callback."""
        if not hasattr(self, 'preview') or self._closed:
            return
        over_limit = False
        indices = self._selected_indices()
        mode = self.mode_stack.get_visible_child_name() or 'size'
        if mode == 'poster' and indices:
            idx = indices[0]
            geom = self._poster_media_geometry()
            try:
                cols, rows, out_w, out_h = poster_grid_for_size(
                    *self.page_sizes[idx], self._paper_name(),
                    self.orientation.get_active_id() or 'portrait',
                    self.poster_scale.get_value(), self._poster_overlap_mm(),
                    imageable_area=geom['imageable'],
                    paper_width_pt=geom['paper_width'], paper_height_pt=geom['paper_height'])
                self._set_label_text(self.preview_info, f'Pôster: {cols} × {rows} folhas = {cols * rows} por página')
                l, b, rr, t = [float(v) for v in geom['imageable']]
                tile_w, tile_h = max(1.0, rr - l), max(1.0, t - b)
                self._set_label_text(self.poster_area_info,
                    f'Área imprimível do destino: {tile_w / 72 * 25.4:.1f} × {tile_h / 72 * 25.4:.1f} mm  •  '
                    f'margens L {l / 72 * 25.4:.1f}, R {(geom["paper_width"] - rr) / 72 * 25.4:.1f}, '
                    f'S {(geom["paper_height"] - t) / 72 * 25.4:.1f}, I {b / 72 * 25.4:.1f} mm')
                self._set_label_text(
                    self.preview_summary,
                    f'Escala {self.poster_scale.get_value():.0f}% • Sobreposição {self._poster_overlap_mm():.1f} mm • '
                    f'Tamanho montado {out_w / 72 * 2.54:.1f} × {out_h / 72 * 2.54:.1f} cm • '
                    f'Marcas de corte {"sim" if self.poster_cut_marks.get_active() else "não"} • '
                    f'Instruções de encaixe {"sim" if self.poster_labels.get_active() else "não"}')
            except ValueError as exc:
                over_limit = True
                self._set_label_text(self.preview_info, 'Limite de 100 folhas por página excedido')
                self._set_label_text(self.preview_summary, str(exc))
        elif mode == 'multiple':
            nup = int(self.nup.get_active_id() or 4)
            sheets = math.ceil(len(indices) / nup) if indices else 0
            self._set_label_text(self.preview_info, f'{nup} páginas por folha — miniaturas reais')
            self._set_label_text(self.preview_summary, f'{len(indices)} página(s) selecionada(s) → {sheets} folha(s).')
        elif mode == 'booklet':
            sheets = math.ceil(len(indices) / 4) if indices else 0
            faces = self._booklet_faces(indices)
            current = self._current_booklet_face(indices)
            side_label = {'both': 'Ambos os lados', 'front': 'Somente frente',
                          'back': 'Somente verso'}.get(self.book_sides.get_active_id(), 'Ambos os lados')
            self._set_label_text(self.preview_info, f'Livreto — {sheets} folha(s) físicas — {side_label}')
            if hasattr(self, 'booklet_nav'):
                self.booklet_nav.set_visible(True)
                self.booklet_previous.set_sensitive(bool(faces) and self.booklet_preview_index > 0)
                self.booklet_next.set_sensitive(bool(faces) and self.booklet_preview_index < len(faces) - 1)
                kind = 'Frente' if current and current[0] == 'front' else 'Verso'
                sheet_number = (self.booklet_preview_index // 2 + 1) if side_label == 'Ambos os lados' else self.booklet_preview_index + 1
                if current:
                    self._set_label_text(self.booklet_position,
                        f'{kind} · folha {sheet_number}/{sheets} · face {self.booklet_preview_index + 1}/{len(faces)}')
                else:
                    self._set_label_text(self.booklet_position, 'Nenhuma face para visualizar')
            self._set_label_text(self.preview_summary,
                f'{len(faces)} face(s) a imprimir • Margem segura {self.book_safe.get_value():.0f} mm • '
                f'Dobra {self.book_gutter.get_value():.0f} mm')
        else:
            self._set_label_text(self.preview_info,
                'Tamanho real (100%)' if self.scale.get_active_id() == 'actual' else 'Ajustar à área da página')
            self._set_label_text(self.preview_summary, f'{len(indices)} página(s) selecionada(s).')
        if mode != 'booklet' and hasattr(self, 'booklet_nav'):
            self.booklet_nav.set_visible(False)
        if hasattr(self, 'action_btn'):
            self.action_btn.set_sensitive(not over_limit)

    def _close_window(self):
        # Release the modal grab before destroying so the main window never
        # keeps a stale grab and stops accepting clicks.
        try:
            self.set_modal(False)
        except Exception:
            pass
        self.destroy()

    def _on_destroy(self, *_args):
        if self._closed:
            return
        self._closed = True
        parent = self.get_transient_for()
        if parent is not None:
            def refocus(p=parent):
                try:
                    if p.get_window() is not None:
                        p.present()
                except Exception:
                    pass
                return False
            GLib.idle_add(refocus)
        self.runner.invalidate('print-thumb')
        self.runner.invalidate('print-printers')
        self.runner.invalidate('printer-properties')
        for idx in tuple(self.preview_thumb_pending):
            self.runner.invalidate(f'print-mode-thumb-{idx}')
        self.preview_thumb_pending.clear()

    def _page_range(self):
        if self.r_current.get_active():
            return str(self.current_page + 1)
        if self.r_pages.get_active():
            return self.range_entry.get_text().strip() or None
        return None

    def _page_set(self):
        return ('all', 'odd', 'even')[max(0, self.subset.get_active())]

    def _selected_indices(self):
        return select_page_indices(self.page_count, self._page_range(), self._page_set(), self.reverse.get_active())

    def _paper_name(self):
        return self.selected_options.get('PageSize') or self.selected_options.get('media') or 'A4'

    def _poster_media_geometry(self, orientation=None):
        orient = orientation or (self.orientation.get_active_id() or 'portrait')
        name = self._paper_name()
        dest = self.dest_combo.get_active_id() or ''
        if dest.startswith('cups:'):
            try:
                return cups.get_media_geometry(dest[5:], name, orient)
            except Exception:
                pass
        w, h = oriented_paper(name, orient)
        return {'paper_width': w, 'paper_height': h, 'imageable': [0.0, 0.0, w, h], 'source': 'pdf'}

    def _update_paper_label(self):
        name = self._paper_name()
        geom = self._poster_media_geometry()
        w, h = geom['paper_width'], geom['paper_height']
        self.paper_label.set_text(f'Papel: {name} — {w / 72 * 2.54:.1f} × {h / 72 * 2.54:.1f} cm')

    @staticmethod
    def _draw_dotted(cr, x0, y0, x1, y1):
        """Dotted cut line: black round dots over a white halo."""
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        for color, width in (((1, 1, 1), 3.4), ((0, 0, 0), 1.8)):
            cr.set_source_rgb(*color)
            cr.set_line_width(width)
            cr.set_dash([0.01, 4.4])
            cr.move_to(x0, y0); cr.line_to(x1, y1); cr.stroke()
        cr.set_dash([])
        cr.set_line_cap(cairo.LINE_CAP_BUTT)

    def _draw_sheet(self, cr, x, y, w, h):
        cr.set_source_rgb(1, 1, 1)
        cr.rectangle(x, y, w, h)
        cr.fill_preserve()
        cr.set_source_rgb(.45, .47, .50)
        cr.set_line_width(1)
        cr.stroke()

    def _draw_preview(self, widget, cr):
        alloc = widget.get_allocation()
        W, H = alloc.width, alloc.height
        cr.set_source_rgb(.86, .87, .89)
        cr.paint()
        indices = self._selected_indices()
        mode = self.mode_stack.get_visible_child_name() or 'size'
        orientation = self.orientation.get_active_id() or 'portrait'
        paper = self._paper_name()
        pw, ph = oriented_paper(paper, 'landscape' if mode == 'booklet' else orientation)
        maxw, maxh = W - 44, H - 54
        factor = min(maxw / pw, maxh / ph)
        sw, sh = pw * factor, ph * factor
        sx, sy = (W - sw) / 2, (H - sh) / 2
        # Poster mode draws its own assembled sheet; drawing a single sheet
        # first left a stray outline behind the poster preview.
        if mode != 'poster':
            self._draw_sheet(cr, sx, sy, sw, sh)

        if mode == 'poster' and indices:
            pidx = indices[0]
            page_w, page_h = self.page_sizes[pidx]
            geom = self._poster_media_geometry(orientation)
            pw = float(geom['paper_width']); ph = float(geom['paper_height'])
            imageable = [float(v) for v in geom['imageable']]
            l, b, rr, t = imageable
            tile_w = max(1.0, rr - l); tile_h = max(1.0, t - b)
            try:
                cols, rows, out_w, out_h = poster_grid_for_size(
                    page_w, page_h, paper, orientation,
                    self.poster_scale.get_value(), self._poster_overlap_mm(),
                    imageable_area=imageable, paper_width_pt=pw, paper_height_pt=ph)
            except ValueError as exc:
                cr.select_font_face('Sans')
                cr.set_font_size(14)
                cr.set_source_rgb(.65, .08, .08)
                cr.move_to(24, 38)
                cr.show_text('Pôster excede o limite de folhas')
                return False

            # Large-page tiling only splits pages that are larger than
            # the selected physical media after Page Zoom is applied.
            if self.poster_large.get_active() and out_w <= pw + .25 and out_h <= ph + .25:
                cols = rows = 1

            # Preview the final assembled poster at its true Page Zoom size.
            pf = min((W - 50) / max(1.0, out_w), (H - 65) / max(1.0, out_h))
            rw, rh = out_w * pf, out_h * pf
            rx, ry = (W - rw) / 2, (H - rh) / 2
            cr.set_source_rgb(1, 1, 1)
            cr.rectangle(rx, ry, rw, rh)
            cr.fill_preserve()
            cr.set_source_rgb(.35, .35, .35)
            cr.stroke()
            pb = self.preview_thumbs.get(pidx)
            if pb:
                self._draw_pixbuf_in_rect(cr, pb, rx, ry, rw, rh, margin=0)
            else:
                self._request_mode_thumbnails()

            overlap_pt = max(0.0, self._poster_overlap_mm() * 72 / 25.4)
            overlap_pt = min(overlap_pt, max(0.0, tile_w - 1.0), max(0.0, tile_h - 1.0))
            step_x = max(1.0, tile_w - overlap_pt)
            step_y = max(1.0, tile_h - overlap_pt)

            # In the assembled poster, the seam is the far edge of the first
            # tile and then advances by tile_width-overlap.  The band directly
            # before that seam is the duplicated overlap that gets trimmed.
            if cols > 1:
                for c in range(1, cols):
                    seam = tile_w + (c - 1) * step_x
                    if seam >= out_w + .5:
                        continue
                    x = rx + (seam / out_w) * rw
                    if self.poster_cut_marks.get_active() and overlap_pt > 0:
                        self._draw_dotted(cr, x, ry, x, ry + rh)
                    else:
                        cr.set_source_rgba(.12, .22, .34, .72)
                        cr.set_line_width(1)
                        cr.set_dash([4, 3])
                        cr.move_to(x, ry); cr.line_to(x, ry + rh); cr.stroke()
                        cr.set_dash([])
                    if overlap_pt > 0:
                        band_x = rx + ((seam - overlap_pt) / out_w) * rw
                        cr.set_source_rgba(1.0, .76, .12, .20)
                        cr.rectangle(band_x, ry, max(1.0, x - band_x), rh); cr.fill()

            if rows > 1:
                for r_idx in range(1, rows):
                    seam = tile_h + (r_idx - 1) * step_y
                    if seam >= out_h + .5:
                        continue
                    y = ry + (seam / out_h) * rh
                    if self.poster_cut_marks.get_active() and overlap_pt > 0:
                        self._draw_dotted(cr, rx, y, rx + rw, y)
                    else:
                        cr.set_source_rgba(.12, .22, .34, .72)
                        cr.set_line_width(1)
                        cr.set_dash([4, 3])
                        cr.move_to(rx, y); cr.line_to(rx + rw, y); cr.stroke()
                        cr.set_dash([])
                    if overlap_pt > 0:
                        band_y = ry + ((seam - overlap_pt) / out_h) * rh
                        cr.set_source_rgba(1.0, .76, .12, .20)
                        cr.rectangle(rx, band_y, rw, max(1.0, y - band_y)); cr.fill()

            # Sheet numbers are preview-only orientation aids. Printed
            # Labels are document name + source page number, not tile numbers.
            if cols * rows > 1:
                cr.select_font_face('Sans')
                cr.set_font_size(9)
                number = 1
                for r_idx in range(rows):
                    for c in range(cols):
                        sx0 = c * step_x
                        sy0 = r_idx * step_y
                        sx1 = min(out_w, sx0 + tile_w)
                        sy1 = min(out_h, sy0 + tile_h)
                        cx = rx + ((sx0 + sx1) / 2 / out_w) * rw
                        cy = ry + ((sy0 + sy1) / 2 / out_h) * rh
                        cr.set_source_rgba(1, 1, 1, .82)
                        cr.rectangle(cx - 14, cy - 9, 28, 16); cr.fill()
                        cr.set_source_rgba(.2, .2, .2, .82)
                        cr.move_to(cx - 10, cy + 3); cr.show_text(str(number))
                        number += 1

            return False

        if mode == 'multiple':
            nup = int(self.nup.get_active_id() or 4)
            cols, rows = {1:(1,1), 2:(2,1), 4:(2,2), 6:(3,2), 9:(3,3), 16:(4,4)}[nup]
            cell_w, cell_h = sw / cols, sh / rows
            cr.set_source_rgb(.55, .57, .60)
            cr.set_line_width(1)
            for c in range(1, cols):
                x = sx + sw * c / cols
                cr.move_to(x, sy); cr.line_to(x, sy + sh); cr.stroke()
            for r in range(1, rows):
                y = sy + sh * r / rows
                cr.move_to(sx, y); cr.line_to(sx + sw, y); cr.stroke()
            for i in range(min(nup, len(indices))):
                c, r = i % cols, i // cols
                idx = indices[i]
                x, y = sx + c * cell_w, sy + r * cell_h
                pb = self.preview_thumbs.get(idx)
                if pb:
                    self._draw_pixbuf_in_rect(cr, pb, x, y, cell_w, cell_h, margin=5)
                else:
                    cr.set_source_rgb(.25, .25, .25)
                    cr.set_font_size(10)
                    cr.move_to(x + 8, y + 18)
                    cr.show_text(f'Página {idx + 1}')
            self._request_mode_thumbnails()
            sheets = math.ceil(len(indices) / nup) if indices else 0
            return False

        if mode == 'booklet':
            cr.set_source_rgb(.85, .12, .10)
            cr.set_line_width(1.4)
            cr.set_dash([5, 4])
            cr.move_to(sx + sw / 2, sy); cr.line_to(sx + sw / 2, sy + sh); cr.stroke()
            cr.set_dash([])
            safe = self.book_safe.get_value() * 72 / 25.4 * factor
            gutter = self.book_gutter.get_value() * 72 / 25.4 * factor
            left_rect = (sx + safe, sy + safe,
                         max(1, sw / 2 - 2 * safe - gutter), max(1, sh - 2 * safe))
            right_rect = (sx + sw / 2 + safe + gutter, sy + safe,
                          max(1, sw / 2 - 2 * safe - gutter), max(1, sh - 2 * safe))
            cr.set_source_rgb(.14, .42, .75)
            cr.set_dash([3, 3])
            cr.rectangle(*left_rect)
            cr.rectangle(*right_rect)
            cr.stroke()
            cr.set_dash([])
            pair = self._current_booklet_face(indices) or ('front', None, None)
            left, right = pair[1], pair[2]
            if self.binding.get_active_id() == 'right':
                left, right = right, left
            for idx, rect in ((left, left_rect), (right, right_rect)):
                if idx is None:
                    cr.set_source_rgb(.35, .35, .35)
                    cr.set_font_size(11)
                    cr.move_to(rect[0] + rect[2] * .32, rect[1] + rect[3] * .52)
                    cr.show_text('Em branco')
                    continue
                pb = self.preview_thumbs.get(idx)
                if pb:
                    self._draw_pixbuf_in_rect(cr, pb, *rect, margin=2)
                else:
                    cr.set_source_rgb(.2, .2, .2)
                    cr.set_font_size(11)
                    cr.move_to(rect[0] + 8, rect[1] + 18)
                    cr.show_text(f'Página {idx + 1}')
            self._request_mode_thumbnails()
            sheets = math.ceil(len(indices) / 4) if indices else 0
            return False

        # Size mode: show current source thumbnail centered on the target sheet.
        if self.preview_pixbuf:
            pb = self.preview_pixbuf
            ratio = min((sw - 20) / pb.get_width(), (sh - 20) / pb.get_height())
            if self.scale.get_active_id() == 'actual':
                ratio = min(ratio, 1.0)
            tw, th = max(1, int(pb.get_width() * ratio)), max(1, int(pb.get_height() * ratio))
            scaled = pb.scale_simple(tw, th, GdkPixbuf.InterpType.BILINEAR)
            Gdk.cairo_set_source_pixbuf(cr, scaled, sx + (sw - tw) / 2, sy + (sh - th) / 2)
            cr.paint()
        return False

    def _submit(self, *_args):
        dest = self.dest_combo.get_active_id()
        if not dest:
            self.dest_status.set_text('Selecione um destino.')
            return
        save_path = None
        if dest == 'save-pdf':
            chooser = Gtk.FileChooserDialog(title='Salvar impressão como PDF', parent=self,
                                            action=Gtk.FileChooserAction.SAVE)
            chooser.add_buttons('Cancelar', Gtk.ResponseType.CANCEL, 'Salvar', Gtk.ResponseType.OK)
            chooser.set_do_overwrite_confirmation(True)
            chooser.set_current_name(safe_filename_from_pdf(self.filepath, '-impresso.pdf'))
            filt = Gtk.FileFilter(); filt.set_name('PDF'); filt.add_mime_type('application/pdf'); chooser.add_filter(filt)
            if chooser.run() != Gtk.ResponseType.OK:
                chooser.destroy(); return
            save_path = chooser.get_filename()
            if not save_path.lower().endswith('.pdf'):
                save_path += '.pdf'
            chooser.destroy()

        mode = self.mode_stack.get_visible_child_name() or 'size'
        poster_geom = self._poster_media_geometry(self.orientation.get_active_id() or 'portrait') if mode == 'poster' else None
        job = {
            'destination': dest,
            'printer': dest[5:] if dest.startswith('cups:') else None,
            'save_path': save_path,
            'copies': int(self.copies.get_value()), 'collate': self.collate.get_active(),
            'grayscale': self.gray.get_active(), 'printer_options': dict(self.selected_options),
            'page_range': self._page_range(), 'page_set': self._page_set(), 'reverse': self.reverse.get_active(),
            'print_mode': mode, 'paper_size': self._paper_name(),
            'orientation': 'landscape' if mode == 'booklet' else (self.orientation.get_active_id() or 'portrait'),
            'scale_mode': self.scale.get_active_id() or 'actual',
            'poster_scale': float(self.poster_scale.get_value()),
            'poster_overlap_mm': self._poster_overlap_mm(),
            'poster_large_only': True,
            'poster_cut_marks': self.poster_cut_marks.get_active(),
            'poster_labels': self.poster_labels.get_active(),
            'poster_glue_guides': False,
            'poster_mark_margin_mm': 0.0,
            'poster_imageable_area': poster_geom['imageable'] if poster_geom else None,
            'poster_paper_width_pt': poster_geom['paper_width'] if poster_geom else None,
            'poster_paper_height_pt': poster_geom['paper_height'] if poster_geom else None,
            'pages_per_sheet': int(self.nup.get_active_id() or 4),
            'number_up_layout': self.nup_layout.get_active_id() or 'lrtb',
            'nup_margin_mm': float(self.nup_margin.get_value()),
            'booklet_binding': self.binding.get_active_id() or 'left',
            'booklet_sides': self.book_sides.get_active_id() or 'both',
            'booklet_safety_mm': float(self.book_safe.get_value()),
            'booklet_gutter_mm': float(self.book_gutter.get_value()),
            'booklet_auto_duplex': (mode == 'booklet' and self.book_sides.get_active_id() == 'both'
                                    and self.auto_duplex.get_active()),
            'print_as_image': self.print_as_image.get_active(),
            'image_dpi': int(self.image_dpi.get_active_id() or 300),
        }
        self._close_window()
        self.on_submit(job)
