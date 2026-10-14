import threading
from concurrent.futures import ThreadPoolExecutor

import gi
gi.require_version('GLib', '2.0')
from gi.repository import GLib


class BackgroundRunner:
    """Runs blocking work outside GTK and delivers only the newest result per channel."""

    def __init__(self, workers=3):
        self._pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix='printviewpdf')
        self._lock = threading.Lock()
        self._seq = {}
        self._closed = False

    def invalidate(self, channel):
        with self._lock:
            self._seq[channel] = self._seq.get(channel, 0) + 1
            return self._seq[channel]

    def submit(self, channel, func, on_success=None, on_error=None):
        with self._lock:
            if self._closed:
                return None
            token = self._seq.get(channel, 0) + 1
            self._seq[channel] = token

        future = self._pool.submit(func)

        def done(fut):
            try:
                value = fut.result()
                err = None
            except Exception as exc:  # noqa: BLE001
                value = None
                err = exc

            def deliver():
                with self._lock:
                    current = self._seq.get(channel)
                    closed = self._closed
                if closed or current != token:
                    return False
                if err is None:
                    if on_success:
                        on_success(value)
                elif on_error:
                    on_error(err)
                return False

            GLib.idle_add(deliver, priority=GLib.PRIORITY_DEFAULT_IDLE)

        future.add_done_callback(done)
        return future

    def shutdown(self):
        with self._lock:
            if self._closed:
                return
            self._closed = True
        self._pool.shutdown(wait=False, cancel_futures=True)
