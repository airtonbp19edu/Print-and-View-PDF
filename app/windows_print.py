"""Windows printers and native GTK/Win32 print dialog for prepared PDFs."""
import ctypes
from ctypes import wintypes
import os


def show_properties(name):
    spool = ctypes.WinDLL('winspool.drv', use_last_error=True)
    handle = wintypes.HANDLE()
    spool.OpenPrinterW.argtypes = [wintypes.LPWSTR, ctypes.POINTER(wintypes.HANDLE), ctypes.c_void_p]
    spool.PrinterProperties.argtypes = [wintypes.HWND, wintypes.HANDLE]
    spool.ClosePrinter.argtypes = [wintypes.HANDLE]
    if not spool.OpenPrinterW(name, ctypes.byref(handle), None):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        spool.PrinterProperties(None, handle)
    finally:
        spool.ClosePrinter(handle)


def list_printers():
    spool = ctypes.WinDLL('winspool.drv', use_last_error=True)
    class PRINTER_INFO_4(ctypes.Structure):
        _fields_ = [('name', wintypes.LPWSTR), ('server', wintypes.LPWSTR), ('attributes', wintypes.DWORD)]
    needed = wintypes.DWORD()
    count = wintypes.DWORD()
    spool.EnumPrintersW(6, None, 4, None, 0, ctypes.byref(needed), ctypes.byref(count))
    if not needed.value:
        return []
    buf = ctypes.create_string_buffer(needed.value)
    if not spool.EnumPrintersW(6, None, 4, buf, len(buf), ctypes.byref(needed), ctypes.byref(count)):
        raise ctypes.WinError(ctypes.get_last_error())
    rows = ctypes.cast(buf, ctypes.POINTER(PRINTER_INFO_4))
    size = wintypes.DWORD()
    spool.GetDefaultPrinterW(None, ctypes.byref(size))
    default_buf = ctypes.create_unicode_buffer(max(1, size.value))
    spool.GetDefaultPrinterW(default_buf, ctypes.byref(size))
    return [{'name': rows[i].name, 'default': rows[i].name == default_buf.value,
             'description': rows[i].name, 'device_uri': 'winspool:' + rows[i].name}
            for i in range(count.value)]


def print_dialog(parent, filepath, job):
    """Draw the already imposed PDF; the system dialog chooses device options."""
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
    from rendering import document_info, render_page_to_png
    import cairo
    import tempfile
    from pathlib import Path

    info = document_info(filepath)
    operation = Gtk.PrintOperation()
    operation.set_job_name('Print&View PDF')
    operation.set_n_pages(info['pages'])
    operation.set_use_full_page(True)
    settings = Gtk.PrintSettings()
    if job.get('printer'):
        settings.set_printer(job['printer'])
    settings.set_n_copies(max(1, int(job.get('copies', 1))))
    settings.set_collate(bool(job.get('collate')))
    settings.set_use_color(not job.get('grayscale'))
    if job.get('booklet_auto_duplex') and job.get('booklet_sides') == 'both':
        settings.set_duplex(Gtk.PrintDuplex.HORIZONTAL)
    else:
        settings.set_duplex(Gtk.PrintDuplex.SIMPLEX)
    operation.set_print_settings(settings)
    # Native dialog intentionally exposes printer/driver choices on Windows.
    # Rasterization is bounded by rendering.py and retains PDF paper geometry.
    with tempfile.TemporaryDirectory(prefix='print-view-native-print-') as td:
        def setup(_op, _context, page, page_setup):
            width, height = info['sizes'][page]
            paper = Gtk.PaperSize.new_custom('prepared', 'Documento preparado', width, height, Gtk.Unit.POINTS)
            page_setup.set_paper_size(paper)
            for edge in ('top', 'bottom', 'left', 'right'):
                getattr(page_setup, 'set_' + edge + '_margin')(0, Gtk.Unit.POINTS)
        failures = []
        def draw(_op, context, page):
            try:
                out = render_page_to_png(filepath, page, str(Path(td) / f'{page}.png'), dpi=180)
                surface = cairo.ImageSurface.create_from_png(out)
                cr = context.get_cairo_context()
                cr.scale(context.get_width() / surface.get_width(), context.get_height() / surface.get_height())
                cr.set_source_surface(surface, 0, 0)
                cr.paint()
            except Exception as exc:
                failures.append(exc)
                operation.cancel()
        operation.connect('request-page-setup', setup)
        operation.connect('draw-page', draw)
        result = operation.run(Gtk.PrintOperationAction.PRINT_DIALOG, parent)
        if failures:
            raise RuntimeError(str(failures[0]))
        if result == Gtk.PrintOperationResult.ERROR:
            raise RuntimeError(str(operation.get_error()))
        return 'Impressão cancelada.' if result == Gtk.PrintOperationResult.CANCEL else 'Trabalho enviado à impressora.'
