"""Worker process settings shared by Linux and Windows builds."""
from pathlib import Path
import os
import sys


def worker_python():
    if os.environ.get('PRINT_VIEW_WORKER_PYTHON'):
        return os.environ['PRINT_VIEW_WORKER_PYTHON']
    if os.name == 'nt':
        console_python = Path(sys.executable).with_name('python.exe')
        if console_python.exists():
            return str(console_python)
    return sys.executable


def subprocess_options():
    return {'creationflags': 0x08000000} if os.name == 'nt' else {}
