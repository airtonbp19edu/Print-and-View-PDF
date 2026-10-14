import threading
from concurrent.futures import CancelledError, ThreadPoolExecutor
from cancel_state import set_event

import gi
gi.require_version('GLib', '2.0')
from gi.repository import GLib


class BackgroundRunner:
    """Separate interactive navigation from speculative background rendering."""

    def __init__(self, workers=3, latest_only=False):
        self._pool = ThreadPoolExecutor(max_workers=max(1, workers), thread_name_prefix='printviewpdf')
        self._background_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix='printviewpdf-bg')
        self._lock = threading.Lock()
        self._seq = {}
        self._futures = {}
        self._cancel_events = {}
        self._closed = False

    def invalidate(self, channel):
        with self._lock:
            self._seq[channel] = self._seq.get(channel, 0) + 1
            token = self._seq[channel]
            future = self._futures.pop(channel, None)
            event = self._cancel_events.pop(channel, None)
        if event is not None:
            event.set()
        if future is not None:
            future.cancel()
        return token

    def submit(self, channel, func, on_success=None, on_error=None, priority='foreground'):
        with self._lock:
            if self._closed:
                return None
            token = self._seq.get(channel, 0) + 1
            self._seq[channel] = token
            previous = self._futures.pop(channel, None)
            previous_event = self._cancel_events.pop(channel, None)
        if previous_event is not None:
            previous_event.set()
        if previous is not None:
            previous.cancel()  # Does not interrupt an already running render.
        pool = self._background_pool if priority == 'background' else self._pool
        event = threading.Event()
        def cancellable():
            set_event(event)
            try:
                return func()
            finally:
                set_event(None)
        future = pool.submit(cancellable)
        with self._lock:
            if self._closed:
                event.set()
                future.cancel()
                return None
            self._futures[channel] = future
            self._cancel_events[channel] = event

        def done(fut):
            try:
                value = fut.result()
                err = None
            except CancelledError:
                return
            except Exception as exc:  # noqa: BLE001
                value = None
                err = exc

            def deliver():
                with self._lock:
                    if self._futures.get(channel) is fut:
                        self._futures.pop(channel, None)
                        self._cancel_events.pop(channel, None)
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
            futures = list(self._futures.values())
            events = list(self._cancel_events.values())
            self._futures.clear()
            self._cancel_events.clear()
        for event in events:
            event.set()
        for future in futures:
            future.cancel()
        self._background_pool.shutdown(wait=False, cancel_futures=True)
        self._pool.shutdown(wait=False, cancel_futures=True)
