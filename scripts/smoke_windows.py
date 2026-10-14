#!/usr/bin/env python3
"""Exercise the Windows runtime with a generated PDF, without printing."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--app', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
output = args.output.resolve()
sys.path.insert(0, str(args.app.resolve()))
from windows_bootstrap import configure
configure()
import cairo
from main import PDFWindow, load_css
from gi.repository import Gtk, GLib
from imposition import create_booklet
from pypdf import PdfReader

temp = tempfile.TemporaryDirectory(prefix='print-view-windows-smoke-', ignore_cleanup_errors=True)
pdf = Path(temp.name) / 'sample.pdf'
surface = cairo.PDFSurface(str(pdf), 420, 595)
cr = cairo.Context(surface)
cr.select_font_face('Arial')
cr.set_font_size(16)
for page in range(1, 5):
    cr.move_to(40, 60)
    cr.show_text('PAGE' + str(page))
    cr.show_page()
surface.finish()
load_css()
window = PDFWindow(str(pdf))
errors = []
window._error = errors.append
started = time.monotonic()
search_started = False
report = None


def poll():
    global search_started, report
    if errors or time.monotonic() - started > 30:
        report = {'passed': False, 'errors': errors, 'pages': window.page_count,
                  'image': window.current_pixbuf is not None, 'status': window.status_file.get_text()}
    elif window.page_count and window.current_pixbuf is not None:
        if not search_started:
            window.find_entry.set_text('PAGE')
            search_started = True
        elif not window.search_running and len(window.search_hits) == 4:
            booklet = Path(temp.name) / 'booklet.pdf'
            create_booklet(str(pdf), str(booklet), sides='back')
            report = {'passed': True, 'pages': window.page_count, 'hits': len(window.search_hits),
                      'sidebar_rows': len(window.find_results_list.get_children()),
                      'booklet_pages': len(PdfReader(booklet).pages),
                      'pixbuf': [window.current_pixbuf.get_width(), window.current_pixbuf.get_height()],
                      'python': sys.version, 'platform': sys.platform}
    if report is not None:
        output.write_text(json.dumps(report, indent=2) + '\n')
        window.destroy()
        return False
    return True


GLib.timeout_add(100, poll)
Gtk.main()
temp.cleanup()
raise SystemExit(0 if report and report['passed'] else 1)
