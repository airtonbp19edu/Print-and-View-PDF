"""Use the pinned library shipped with this release on every platform."""
from pathlib import Path
import sys

def configure_pdf_library():
    vendor = str(Path(__file__).resolve().parent / 'vendor')
    if vendor not in sys.path:
        sys.path.insert(0, vendor)
    return 'bundled'
