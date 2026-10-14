import os
import re
import shutil
import subprocess
import tempfile
from functools import lru_cache
from urllib.parse import urlparse


def _run(args, timeout=15, check=True):
    env = os.environ.copy()
    env['LC_ALL'] = 'C'
    env['LANG'] = 'C'
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, timeout=timeout, check=check, env=env)


def available():
    if os.name == 'nt':
        return True
    return bool(shutil.which('lpstat') and shutil.which('lp'))


def get_default_printer():
    if not shutil.which('lpstat'):
        return None
    try:
        out = _run(['lpstat', '-d'], timeout=8).stdout.strip()
        marker = 'system default destination:'
        if marker in out:
            return out.split(marker, 1)[1].strip()
    except Exception:
        pass
    return None


def _device_uris():
    uris = {}
    if not shutil.which('lpstat'):
        return uris
    try:
        for line in _run(['lpstat', '-v'], timeout=10).stdout.splitlines():
            m = re.match(r'device for\s+(.+?):\s*(.+)$', line.strip())
            if m:
                uris[m.group(1).strip()] = m.group(2).strip()
    except Exception:
        pass
    return uris


def _uri_identity(uri):
    """Return a conservative physical-device identity for deduplication."""
    if not uri:
        return None
    low = uri.lower()
    # Direct USB queues for the same URI are safely duplicates.
    if low.startswith(('usb://', 'serial://', 'parallel://')):
        return low.split('?', 1)[0]
    try:
        parsed = urlparse(uri)
    except Exception:
        parsed = None
    if parsed and parsed.scheme in ('ipp', 'ipps', 'http', 'https', 'socket', 'lpd'):
        host = (parsed.hostname or '').lower().rstrip('.')
        # Host/IP + scheme is stable enough for the common driverless duplicate case.
        if host:
            return f'net:{host}'
    if low.startswith('dnssd://'):
        # DNS-SD queue names often contain the model/service name before ._ipp.
        service = low.split('://', 1)[1].split('._', 1)[0]
        service = re.sub(r'[%+._-]+', ' ', service)
        service = re.sub(r'\s+', ' ', service).strip()
        return f'dnssd:{service}' if service else low
    return low.split('?', 1)[0]


def list_printers(include_discovered=False):
    if os.name == 'nt':
        from windows_print import list_printers as native_printers
        return native_printers()
    """List installed CUPS queues, deduplicated by physical device when possible.

    Historically lpstat -e was used first, but that includes temporary/discovered
    destinations and commonly causes the same network printer to appear twice.
    Installed queues from lpstat -p are now authoritative. Discovered-only entries
    are used only as a fallback or when explicitly requested.
    """
    if not shutil.which('lpstat'):
        return []
    states = {}
    names = []
    try:
        for line in _run(['lpstat', '-p'], timeout=10).stdout.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] == 'printer':
                name = parts[1]
                low = line.lower()
                states[name] = {'stopped': 'disabled' in low or 'stopped' in low}
                if name not in names:
                    names.append(name)
    except Exception:
        pass

    if include_discovered or not names:
        try:
            for line in _run(['lpstat', '-e'], timeout=10).stdout.splitlines():
                name = line.strip()
                if name and name not in names:
                    names.append(name)
        except Exception:
            pass

    uris = _device_uris()
    default = get_default_printer()
    result = []
    seen = {}
    for name in names:
        uri = uris.get(name, '')
        ident = _uri_identity(uri) or ('queue:' + name.lower())
        # Prefer the configured default queue if two installed queues resolve to
        # the exact same device identity; otherwise keep the first stable queue.
        if ident in seen:
            existing_idx = seen[ident]
            if name == default and result[existing_idx]['name'] != default:
                result[existing_idx] = {
                    'name': name, 'stopped': states.get(name, {}).get('stopped', False),
                    'default': True, 'device_uri': uri,
                }
            continue
        seen[ident] = len(result)
        result.append({
            'name': name,
            'stopped': states.get(name, {}).get('stopped', False),
            'default': name == default,
            'device_uri': uri,
        })
    return result


def get_ppd_options(printer_name):
    """Read CUPS/PPD options using lpoptions -l. Values stay as driver tokens."""
    if not printer_name or not shutil.which('lpoptions'):
        return {}
    try:
        output = _run(['lpoptions', '-p', printer_name, '-l'], timeout=15).stdout
    except Exception:
        return {}
    result = {}
    for line in output.splitlines():
        if ':' not in line:
            continue
        left, values = line.split(':', 1)
        if '/' in left:
            key, label = left.split('/', 1)
        else:
            key = label = left
        choices = []
        current = None
        for token in values.strip().split():
            selected = token.startswith('*')
            value = token[1:] if selected else token
            if not value:
                continue
            choices.append(value)
            if selected:
                current = value
        if choices:
            result[key.strip()] = {
                'label': label.strip() or key.strip(),
                'choices': choices,
                'current': current or choices[0],
            }
    return result


def get_printer_details(printer_name):
    details = {'name': printer_name, 'device_uri': _device_uris().get(printer_name, '')}
    if shutil.which('lpstat'):
        try:
            details['status'] = _run(['lpstat', '-l', '-p', printer_name], timeout=10, check=False).stdout.strip()
        except Exception:
            details['status'] = ''
    details['maintenance_commands'] = get_maintenance_commands(printer_name)
    details['epson_utility'] = any(os.path.isfile(p) and os.access(p, os.X_OK)
                                   for p in ('/usr/bin/epson-printer-utility',
                                             '/usr/local/bin/epson-printer-utility'))
    return details


def _ppd_path(printer_name):
    # Most distributions keep PPDs here. Reading may be restricted, so failure is harmless.
    name = os.path.basename(str(printer_name or ''))
    if name != str(printer_name or '') or not re.fullmatch(r'[A-Za-z0-9_.-]{1,127}', name) or name in {'.', '..'}:
        return None
    path = os.path.join('/etc/cups/ppd', name + '.ppd')
    return path if os.path.isfile(path) and os.access(path, os.R_OK) else None




def _fallback_media_size_points(media_name):
    raw = (media_name or 'A4').upper().replace('_', '').replace('-', '')
    pt_per_in = 72.0
    mm = 72.0 / 25.4
    if 'A3' in raw:
        return 297.0 * mm, 420.0 * mm
    if 'A5' in raw:
        return 148.0 * mm, 210.0 * mm
    if 'A6' in raw:
        return 105.0 * mm, 148.0 * mm
    if 'LETTER' in raw:
        return 8.5 * pt_per_in, 11.0 * pt_per_in
    if 'LEGAL' in raw:
        return 8.5 * pt_per_in, 14.0 * pt_per_in
    if 'TABLOID' in raw or 'LEDGER' in raw:
        return 11.0 * pt_per_in, 17.0 * pt_per_in
    if '3.5X5' in raw or '3.5X5' in (media_name or '').upper():
        return 3.5 * pt_per_in, 5.0 * pt_per_in
    if '4X6' in raw:
        return 4.0 * pt_per_in, 6.0 * pt_per_in
    if '5X7' in raw:
        return 5.0 * pt_per_in, 7.0 * pt_per_in
    if '8X10' in raw:
        return 8.0 * pt_per_in, 10.0 * pt_per_in
    if 'ENV10' in raw:
        return 4.125 * pt_per_in, 9.5 * pt_per_in
    return 210.0 * mm, 297.0 * mm


@lru_cache(maxsize=128)
def get_media_geometry(printer_name, media_name='A4', orientation='portrait'):
    """Return physical paper and imageable rectangle in PostScript points.

    Poster tiling uses the selected printer's printable/imageable area rather
    than inventing an extra poster margin.  Legacy CUPS queues expose the exact
    geometry in the PPD through *PaperDimension and *ImageableArea.

    The return value is a dict with:
      paper_width, paper_height, imageable=[left,bottom,right,top], source
    """
    media = (media_name or 'A4').strip()
    paper_w, paper_h = _fallback_media_size_points(media)
    imageable = None
    source = 'fallback'
    ppd = _ppd_path(printer_name) if printer_name else None
    if ppd:
        dims = {}
        areas = {}
        try:
            with open(ppd, 'r', encoding='latin-1', errors='ignore') as fh:
                for raw in fh:
                    line = raw.strip()
                    m = re.match(r'^\*PaperDimension\s+([^/:]+)(?:/[^:]+)?:\s*"([^"]+)"', line)
                    if m:
                        vals = [float(x) for x in m.group(2).split()[:2]]
                        if len(vals) == 2:
                            dims[m.group(1)] = tuple(vals)
                        continue
                    m = re.match(r'^\*ImageableArea\s+([^/:]+)(?:/[^:]+)?:\s*"([^"]+)"', line)
                    if m:
                        vals = [float(x) for x in m.group(2).split()[:4]]
                        if len(vals) == 4:
                            areas[m.group(1)] = tuple(vals)
        except Exception:
            dims = {}; areas = {}

        def choose(mapping):
            if media in mapping:
                return mapping[media]
            low = media.lower()
            for key, val in mapping.items():
                if key.lower() == low:
                    return val
            # Some drivers prepend media keywords while the visible choice keeps
            # only A4/A4.Borderless etc.
            compact = re.sub(r'[^a-z0-9]+', '', low)
            for key, val in mapping.items():
                if re.sub(r'[^a-z0-9]+', '', key.lower()) == compact:
                    return val
            return None

        dim = choose(dims)
        area = choose(areas)
        if dim:
            paper_w, paper_h = dim
            source = 'ppd'
        if area:
            l, b, r, t = area
            # Clamp malformed drivers to the physical media.
            l = max(0.0, min(float(l), paper_w)); r = max(l, min(float(r), paper_w))
            b = max(0.0, min(float(b), paper_h)); t = max(b, min(float(t), paper_h))
            if r - l > 1 and t - b > 1:
                imageable = (l, b, r, t)
                source = 'ppd'

    if imageable is None:
        # Borderless media may legitimately expose the whole page. For unknown
        # non-borderless destinations keep a conservative 5 mm hardware margin.
        if 'borderless' in media.lower():
            imageable = (0.0, 0.0, paper_w, paper_h)
        else:
            m = 5.0 * 72.0 / 25.4
            imageable = (m, m, max(m, paper_w - m), max(m, paper_h - m))

    orientation = (orientation or 'portrait').lower()
    if orientation == 'landscape' and paper_h > paper_w:
        old_w = paper_w
        l, b, r, t = imageable
        paper_w, paper_h = paper_h, paper_w
        # Clockwise rotation of the PPD imageable rectangle.
        imageable = (b, old_w - r, t, old_w - l)
    elif orientation == 'portrait' and paper_w > paper_h:
        old_h = paper_h
        l, b, r, t = imageable
        paper_w, paper_h = paper_h, paper_w
        # Counter-clockwise rotation back to portrait.
        imageable = (old_h - t, l, old_h - b, r)

    l, b, r, t = imageable
    return {
        'paper_width': float(paper_w), 'paper_height': float(paper_h),
        'imageable': [float(l), float(b), float(r), float(t)],
        'source': source,
    }

def get_maintenance_commands(printer_name):
    commands = []
    ppd = _ppd_path(printer_name)
    if ppd:
        try:
            with open(ppd, 'r', encoding='latin-1', errors='ignore') as f:
                for line in f:
                    if line.startswith('*cupsCommands:'):
                        value = line.split(':', 1)[1].strip().strip('"')
                        commands.extend(token for token in value.split() if re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', token))
                        break
        except Exception:
            pass
    # The standard CUPS command filter requires at least PrintSelfTestPage;
    # these are offered as best-effort when a legacy driver does not advertise.
    return list(dict.fromkeys(commands))


def send_maintenance_command(printer_name, command):
    if not shutil.which('lp'):
        raise RuntimeError('O comando lp não está instalado.')
    if command not in get_maintenance_commands(printer_name):
        raise ValueError('Comando de manutenção não anunciado pelo driver.')
    fd, path = tempfile.mkstemp(prefix='winux-cups-command-', suffix='.txt')
    try:
        with os.fdopen(fd, 'w', encoding='ascii', errors='ignore') as f:
            f.write('#CUPS-COMMAND\n')
            f.write(command.strip() + '\n')
        cmd = ['lp', '-d', printer_name, '-o', 'document-format=application/vnd.cups-command', path]
        proc = _run(cmd, timeout=30, check=False)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or 'Comando de manutenção não aceito pelo driver.')
        return proc.stdout.strip() or 'Comando enviado ao CUPS.'
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def print_test_page(printer_name):
    candidates = ['/usr/share/cups/data/testprint', '/usr/share/cups/data/default-testpage.pdf']
    path = next((p for p in candidates if os.path.isfile(p)), None)
    if not path:
        raise RuntimeError('Página de teste do CUPS não encontrada.')
    proc = _run(['lp', '-d', printer_name, path], timeout=30, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or 'Falha ao imprimir página de teste.')
    return proc.stdout.strip() or 'Página de teste enviada.'


def launch_vendor_utility(printer_name=None):
    exe = next((p for p in ('/usr/bin/epson-printer-utility',
                            '/usr/local/bin/epson-printer-utility')
                if os.path.isfile(p) and os.access(p, os.X_OK)), None)
    if not exe:
        raise RuntimeError('Epson Printer Utility não está instalado.')
    subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     start_new_session=True)
    return 'Epson Printer Utility aberto.'


def supports_duplex(printer_name):
    opts = get_ppd_options(printer_name)
    for key in ('Duplex', 'sides'):
        meta = opts.get(key)
        if meta and len(meta.get('choices', [])) > 1:
            return True
    return False


def print_file(printer_name, filepath, job):
    if not shutil.which('lp'):
        raise RuntimeError('O comando lp não está instalado. Instale cups-client.')
    if not printer_name:
        raise RuntimeError('Nenhuma impressora selecionada.')
    cmd = ['lp', '-d', printer_name, '-n', str(max(1, int(job.get('copies', 1))))]
    options = dict(job.get('printer_options') or {})

    # Do not let CUPS silently shrink an already prepared PDF.
    options.setdefault('fit-to-page', 'false')
    options.setdefault('print-scaling', 'none')

    if job.get('collate'):
        options.setdefault('multiple-document-handling', 'separate-documents-collated-copies')
    if job.get('print_mode') == 'booklet' and job.get('booklet_sides') in ('front', 'back'):
        # These PDFs contain only one physical side of each sheet: never
        # duplex them with a saved printer setting or printer default.
        options.pop('Duplex', None)
        options['sides'] = 'one-sided'
    elif job.get('print_mode') == 'booklet' and job.get('booklet_auto_duplex'):
        options.pop('Duplex', None)
        options['sides'] = 'two-sided-short-edge'

    if job.get('grayscale'):
        ppd = get_ppd_options(printer_name)
        if 'print-color-mode' in ppd:
            options['print-color-mode'] = 'monochrome'
        elif 'ColorModel' in ppd:
            choices = ppd['ColorModel']['choices']
            gray = next((x for x in choices if x.lower() in ('gray', 'grey', 'grayscale', 'mono', 'monochrome')), None)
            if gray:
                options['ColorModel'] = gray
        elif 'cupsColorModel' in ppd:
            choices = ppd['cupsColorModel']['choices']
            gray = next((x for x in choices if 'gray' in x.lower() or 'mono' in x.lower()), None)
            if gray:
                options['cupsColorModel'] = gray
        else:
            options['print-color-mode'] = 'monochrome'

    safe_option = re.compile(r'[A-Za-z][A-Za-z0-9_.-]{0,79}\Z')
    for key, value in options.items():
        if value is None or value == '':
            continue
        key, value = str(key), str(value)
        if (not safe_option.fullmatch(key) or len(value) > 160 or
                any(ch in value for ch in '\r\n\x00') or '=' in value):
            raise ValueError('Opção de impressora inválida.')
        cmd += ['-o', f'{key}={value}']
    cmd.append(filepath)
    proc = _run(cmd, timeout=60, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or 'Falha ao enviar o trabalho ao CUPS.')
    return proc.stdout.strip() or 'Trabalho enviado para a impressora.'
