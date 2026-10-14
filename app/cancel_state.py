"""Cancellation context shared by background tasks and Poppler subprocesses."""
import threading

_local = threading.local()


def get_event():
    return getattr(_local, 'event', None)


def set_event(event):
    _local.event = event
