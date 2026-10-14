import math

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('GLib', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

from rendering import render_page
from async_core import BackgroundRunner
from page_cache import PageCache

LASER_COLORS = {
    'Vermelho': (1.0, 0.08, 0.06),
    'Verde': (0.10, 1.0, 0.22),
    'Azul': (0.08, 0.42, 1.0),
    'Amarelo': (1.0, 0.86, 0.05),
    'Magenta': (1.0, 0.08, 0.72),
    'Ciano': (0.05, 0.92, 1.0),
}


class PresentationWindow(Gtk.Window):
    """Presentation view with asynchronous rendering and smooth panning.

    Navigation model:
      Left/Right = previous/next page.
      Up/Down and mouse wheel = smooth vertical pan inside the current page.
      Shift+wheel = horizontal pan.
      Ctrl+wheel / Ctrl +/- = zoom.
    """

    PAN_STEP = 110.0
    WHEEL_STEP = 95.0
    ANIM_MS = 16
    ANIM_EASE = 0.28

    def __init__(self, parent, runner, filepath, page_sizes, start_page, cache_dir, laser_color='Vermelho'):
        super().__init__(title='Apresentação — Print&View PDF')
        self.set_transient_for(parent)
        self.set_destroy_with_parent(True)
        self.set_icon_name('print-view-pdf')
        self.set_role('print-view-pdf-presentation')
        display = Gdk.Display.get_default()
        monitor = display.get_monitor_at_window(parent.get_window()) if parent.get_window() else display.get_primary_monitor()
        if monitor is not None:
            geometry = monitor.get_geometry()
            self.set_default_size(geometry.width, geometry.height)
        self.runner = BackgroundRunner(workers=1, latest_only=True)
        self.prefetch_runner = BackgroundRunner(workers=1, latest_only=True)
        self._closed = False
        self._loading = True
        self._render_error = None
        self.fit_mode = 'page'
        self._top_anchor = False
        self.filepath = filepath
        self.page_sizes = page_sizes
        self.page_count = len(page_sizes)
        self.page = max(0, min(start_page, self.page_count - 1))
        self.cache_dir = cache_dir
        self.zoom = 100
        self.pixbuf = None
        self.rendered_zoom = None
        # In-memory page cache + neighbour prefetch make page changes instant.
        self._image_cache = PageCache()
        self._pix_cache = self._image_cache.images
        self._pix_pending = set()
        self._prefetch_tasks = {}
        self._alloc_size = None
        self._resize_source = None

        # Current and target pan positions.  Target based animation makes wheel
        # and keyboard movement feel continuous instead of jumping in chunks.
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.target_pan_x = 0.0
        self.target_pan_y = 0.0
        self._anim_source = None
        self.dragging = False
        self.drag_origin = None

        self.laser_enabled = True
        self.laser_color_name = laser_color if laser_color in LASER_COLORS else 'Vermelho'
        self.pointer = None
        self.controls_visible = True

        overlay = Gtk.Overlay()
        self.add(overlay)
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_can_focus(True)
        self.canvas.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.SCROLL_MASK |
            Gdk.EventMask.SMOOTH_SCROLL_MASK | Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.BUTTON_MOTION_MASK
        )
        self.canvas.connect('draw', self._draw)
        self.canvas.connect('motion-notify-event', self._motion)
        self.canvas.connect('scroll-event', self._scroll)
        self.canvas.connect('button-press-event', self._button_press)
        self.canvas.connect('button-release-event', self._button_release)
        self.canvas.connect('size-allocate', self._size_allocate)
        overlay.add(self.canvas)

        self.revealer = Gtk.Revealer()
        self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        self.revealer.set_halign(Gtk.Align.FILL)
        self.revealer.set_valign(Gtk.Align.END)
        self.revealer.add(self._toolbar())
        overlay.add_overlay(self.revealer)
        self.revealer.set_reveal_child(True)

        self.connect('key-press-event', self._key)
        self.connect('destroy', self._destroyed)
        self.fullscreen()
        self.show_all()
        self.canvas.grab_focus()
        # Rendering starts from the first size-allocate: asking now would see a
        # 1x1 canvas and render a tiny page that never gets redrawn.

    def _destroyed(self, *_args):
        self._closed = True
        self.runner.shutdown(); self.prefetch_runner.shutdown()
        if self._resize_source:
            try:
                GLib.source_remove(self._resize_source)
            except Exception:
                pass
            self._resize_source = None
        if self._anim_source:
            try:
                GLib.source_remove(self._anim_source)
            except Exception:
                pass
            self._anim_source = None

    def _toolbar(self):
        bar = Gtk.Box(spacing=6, margin=8)
        bar.get_style_context().add_class('presentation-toolbar')
        prev = Gtk.Button(label='‹'); prev.connect('clicked', lambda *_: self._goto(self.page - 1)); bar.pack_start(prev, False, False, 0)
        self.page_label = Gtk.Label(); bar.pack_start(self.page_label, False, False, 0)
        nxt = Gtk.Button(label='›'); nxt.connect('clicked', lambda *_: self._goto(self.page + 1)); bar.pack_start(nxt, False, False, 0)
        bar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 4)
        minus = Gtk.Button(label='−'); minus.connect('clicked', lambda *_: self._set_zoom(self.zoom - 25)); bar.pack_start(minus, False, False, 0)
        self.zoom_label = Gtk.Label(); bar.pack_start(self.zoom_label, False, False, 0)
        plus = Gtk.Button(label='+'); plus.connect('clicked', lambda *_: self._set_zoom(self.zoom + 25)); bar.pack_start(plus, False, False, 0)
        self.zoom_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 25, 400, 5)
        self.zoom_scale.set_value(100); self.zoom_scale.set_size_request(110, -1); self.zoom_scale.set_draw_value(False)
        self.zoom_scale.connect('value-changed', lambda s: self._set_zoom(int(s.get_value()), update_scale=False))
        bar.pack_start(self.zoom_scale, False, False, 0)
        fit = Gtk.Button(label='Ajustar'); fit.connect('clicked', lambda *_: self._set_zoom(100)); bar.pack_start(fit, False, False, 0)
        self.fit_combo = Gtk.ComboBoxText()
        self.fit_combo.append('page', 'Página inteira')
        self.fit_combo.append('fill', 'Preencher tela')
        self.fit_combo.append('reading', 'Leitura a 250%')
        self.fit_combo.set_active_id('page')
        self.fit_combo.set_tooltip_text('Preencher tela amplia a página; use a roda ou arraste para ver as bordas.')
        self.fit_combo.connect('changed', self._fit_changed)
        bar.pack_start(self.fit_combo, False, False, 0)
        bar.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 4)
        hint = Gtk.Label(label='↑↓: deslizar')
        hint.get_style_context().add_class('muted')
        bar.pack_start(hint, False, False, 4)
        self.laser_toggle = Gtk.CheckButton(label='Laser')
        self.laser_toggle.set_active(True); self.laser_toggle.connect('toggled', self._laser_toggle); bar.pack_start(self.laser_toggle, False, False, 0)
        self.color_combo = Gtk.ComboBoxText()
        for name in LASER_COLORS: self.color_combo.append_text(name)
        names = list(LASER_COLORS); self.color_combo.set_active(names.index(self.laser_color_name))
        self.color_combo.connect('changed', self._color_changed); bar.pack_start(self.color_combo, False, False, 0)
        exit_btn = Gtk.Button(label='Sair'); exit_btn.connect('clicked', lambda *_: self.destroy()); bar.pack_end(exit_btn, False, False, 0)
        self._update_labels()
        return bar

    def _update_labels(self):
        if hasattr(self, 'page_label'):
            self.page_label.set_text(f'Página {self.page + 1} / {self.page_count}')
        if hasattr(self, 'zoom_label'):
            self.zoom_label.set_text(f'{self.zoom}%')

    def _goto(self, page):
        page = max(0, min(page, self.page_count - 1))
        if page == self.page:
            return
        self.page = page
        self._top_anchor = self.fit_mode == 'reading'
        self.pan_x = self.pan_y = 0.0
        self.target_pan_x = self.target_pan_y = 0.0
        self._update_labels()
        self._request_render()

    def _set_zoom(self, value, update_scale=True):
        value = max(25, min(400, int(value)))
        if value == self.zoom:
            if update_scale and hasattr(self, 'zoom_scale') and int(self.zoom_scale.get_value()) != value:
                self.zoom_scale.set_value(value)
            return
        old_zoom = max(1, self.zoom)
        ratio = value / old_zoom
        self.zoom = value
        # Preserve the viewed region while zooming rather than snapping to center.
        self.pan_x *= ratio
        self.pan_y *= ratio
        self.target_pan_x *= ratio
        self.target_pan_y *= ratio
        if update_scale and hasattr(self, 'zoom_scale') and int(self.zoom_scale.get_value()) != value:
            self.zoom_scale.set_value(value)
        self._update_labels()
        self._request_render()

    def _canvas_size(self):
        if self._alloc_size:
            return self._alloc_size
        alloc = self.canvas.get_allocation()
        return alloc.width, alloc.height

    def _base_width_for(self, page):
        """Use the available viewport above the controls, preserving aspect ratio."""
        W, H = self._canvas_size()
        W, H = max(300, W), max(250, H)
        pw, ph = self.page_sizes[page]
        H = max(100, H - self._controls_height())
        if self.fit_mode == 'reading':
            return min(W - 24, (H * .80) * pw / ph)
        fit_w = (max if self.fit_mode == 'fill' else min)(W - 24, (H - 24) * pw / ph)
        return fit_w

    def _controls_height(self):
        return self.revealer.get_allocated_height() if self.controls_visible else 0

    def _fit_changed(self, combo):
        self.fit_mode = combo.get_active_id() or 'page'
        self._top_anchor = self.fit_mode == 'reading'
        self.pan_x = self.pan_y = self.target_pan_x = self.target_pan_y = 0
        zoom = 250 if self.fit_mode == 'reading' else 100
        if self.zoom == zoom: self._request_render()
        else: self._set_zoom(zoom)

    def _target_width_for(self, page):
        return max(240, int(self._base_width_for(page) * self.zoom / 100.0))

    def _target_width(self):
        return self._target_width_for(self.page)

    def _cache_get(self, key):
        return self._image_cache.get(key)

    def _cache_put(self, key, pixbuf):
        self._image_cache.put(key, pixbuf)

    def _apply_pixbuf(self, pixbuf, zoom):
        self._loading = False; self._render_error = None
        self.pixbuf = pixbuf
        self.rendered_zoom = zoom
        self._clamp_target_pan()
        bounds = self._pan_bounds()
        self.pan_x = min(max(self.pan_x, bounds[0]), bounds[1])
        self.pan_y = min(max(self.pan_y, bounds[2]), bounds[3])
        if self._top_anchor:
            self.pan_y = self.target_pan_y = bounds[3]
        self.canvas.queue_draw()

    def _load_page_pixbuf(self, page, target):
        path = render_page(self.filepath, page, target, self.cache_dir, 'present', image_format='jpeg')
        return GdkPixbuf.Pixbuf.new_from_file(path)

    def _request_render(self):
        if self._closed or not self._alloc_size:
            return  # wait for the first real size-allocate
        target = self._target_width()
        page = self.page
        zoom = self.zoom
        key = (page, target)
        self.runner.invalidate('presentation-render')

        cached = self._cache_get(key)
        if cached is not None:
            self._apply_pixbuf(cached, zoom)
            self._prefetch_neighbours()
            return

        def ok(pixbuf):
            self._cache_put(key, pixbuf)
            if page != self.page or zoom != self.zoom:
                return
            if target != self._target_width():
                self._request_render()
                return
            self._apply_pixbuf(pixbuf, zoom)
            self._prefetch_neighbours()

        self._loading = True; self._render_error = None
        self.canvas.queue_draw()
        def error(exc):
            self._loading = False
            self._render_error = f'Não foi possível carregar a página {page + 1}: {exc}'
            self.canvas.queue_draw()
        self.runner.submit(
            'presentation-render',
            lambda: self._load_page_pixbuf(page, target),
            ok,
            error,
        )

    def _prefetch_neighbours(self):
        """Render the next pages (and the previous one) in the background."""
        if not self._alloc_size:
            return
        wanted = set()
        for offset in (1, -1):
            p = self.page + offset
            if p < 0 or p >= self.page_count:
                continue
            target = self._target_width_for(p)
            key = (p, target)
            wanted.add(key)
            future = self._prefetch_tasks.get(key)
            if key in self._pix_cache or (future is not None and not future.done()):
                continue
            self._pix_pending.add(key)

            def ok(pixbuf, key=key):
                self._pix_pending.discard(key)
                self._cache_put(key, pixbuf)

            def err(_e, key=key):
                self._pix_pending.discard(key)

            self._prefetch_tasks[key] = self.prefetch_runner.submit(
                str(key),
                lambda p=p, target=target: self._load_page_pixbuf(p, target),
                ok, err,
            )
        for key in list(self._prefetch_tasks):
            if key not in wanted:
                self.prefetch_runner.invalidate(str(key))
                self._prefetch_tasks.pop(key).cancel()
                self._pix_pending.discard(key)

    def _pan_bounds(self):
        """Return min/max pan offsets that keep the whole page reachable."""
        if not self.pixbuf:
            return (0.0, 0.0, 0.0, 0.0)
        alloc = self.canvas.get_allocation()
        W, H = max(1, alloc.width), max(1, alloc.height - self._controls_height())
        pw, ph = self.pixbuf.get_width(), self.pixbuf.get_height()
        # When the page is smaller than the viewport, it stays centered on that
        # axis. When larger, allow panning until either page edge meets the view.
        x_extra = max(0.0, (pw - W) / 2.0)
        y_extra = max(0.0, (ph - H) / 2.0)
        return (-x_extra, x_extra, -y_extra, y_extra)

    def _clamp_target_pan(self):
        minx, maxx, miny, maxy = self._pan_bounds()
        self.target_pan_x = min(max(self.target_pan_x, minx), maxx)
        self.target_pan_y = min(max(self.target_pan_y, miny), maxy)

    def _set_pan_target(self, x=None, y=None, animate=True):
        if x is not None:
            self.target_pan_x = float(x)
        if y is not None:
            self.target_pan_y = float(y)
        self._clamp_target_pan()
        if not animate:
            self.pan_x = self.target_pan_x
            self.pan_y = self.target_pan_y
            self.canvas.queue_draw()
            return
        self._ensure_animation()

    def _pan_by(self, dx=0.0, dy=0.0):
        if dy:
            self._top_anchor = False
        self._set_pan_target(self.target_pan_x + dx, self.target_pan_y + dy, animate=True)

    def _ensure_animation(self):
        if self._anim_source is None:
            self._anim_source = GLib.timeout_add(self.ANIM_MS, self._animate_pan)

    def _animate_pan(self):
        dx = self.target_pan_x - self.pan_x
        dy = self.target_pan_y - self.pan_y
        if abs(dx) < 0.35 and abs(dy) < 0.35:
            self.pan_x = self.target_pan_x
            self.pan_y = self.target_pan_y
            self._anim_source = None
            self.canvas.queue_draw()
            return False
        self.pan_x += dx * self.ANIM_EASE
        self.pan_y += dy * self.ANIM_EASE
        self.canvas.queue_draw()
        return True

    def _size_allocate(self, _widget, allocation=None, *_args):
        if allocation is not None and allocation.width > 1 and allocation.height > 1:
            size = (allocation.width, allocation.height)
            if size != self._alloc_size:
                first = self._alloc_size is None
                self._alloc_size = size
                if self._resize_source:
                    try:
                        GLib.source_remove(self._resize_source)
                    except Exception:
                        pass
                    self._resize_source = None

                def render_now():
                    self._resize_source = None
                    self._request_render()
                    return False
                self._resize_source = GLib.timeout_add(1 if first else 150, render_now)
        self._clamp_target_pan()
        self._set_pan_target(self.target_pan_x, self.target_pan_y, animate=False)

    def _draw(self, widget, cr):
        alloc = widget.get_allocation()
        W, H = alloc.width, alloc.height
        cr.set_source_rgb(.04, .04, .04)
        cr.paint()
        if self.pixbuf:
            x = (W - self.pixbuf.get_width()) / 2 + self.pan_x
            y = (H - self._controls_height() - self.pixbuf.get_height()) / 2 + self.pan_y
            cr.set_source_rgb(1, 1, 1)
            cr.rectangle(x, y, self.pixbuf.get_width(), self.pixbuf.get_height()); cr.fill()
            Gdk.cairo_set_source_pixbuf(cr, self.pixbuf, x, y)
            cr.paint()
        if self._loading or self._render_error:
            text = self._render_error or f'Carregando página {self.page + 1}…'
            cr.set_source_rgba(.10, .10, .10, .94); cr.rectangle(8, 8, max(200, W - 16), 36); cr.fill()
            cr.set_source_rgb(1, .75 if self._render_error else 1, .75 if self._render_error else 1)
            cr.set_font_size(14); cr.move_to(18, 32); cr.show_text(text[:140])
        if self.laser_enabled and self.pointer:
            x, y = self.pointer
            r, g, b = LASER_COLORS[self.laser_color_name]
            cr.set_source_rgba(r, g, b, .18); cr.arc(x, y, 18, 0, 2 * math.pi); cr.fill()
            cr.set_source_rgba(r, g, b, .45); cr.arc(x, y, 10, 0, 2 * math.pi); cr.fill()
            cr.set_source_rgb(r, g, b); cr.arc(x, y, 4.5, 0, 2 * math.pi); cr.fill()
            cr.set_source_rgb(1, 1, 1); cr.arc(x, y, 1.4, 0, 2 * math.pi); cr.fill()
        return False

    def _motion(self, _w, event):
        self.pointer = (event.x, event.y)
        if self.dragging and self.drag_origin:
            ox, oy, px, py = self.drag_origin
            self._set_pan_target(ox + event.x - px, oy + event.y - py, animate=False)
        self.canvas.queue_draw()
        return True

    def _button_press(self, _w, event):
        if event.button == 2:
            self.dragging = True
            self.drag_origin = (self.pan_x, self.pan_y, event.x, event.y)
            return True
        return False

    def _button_release(self, _w, event):
        if event.button == 2:
            self.dragging = False
            self.drag_origin = None
            self.target_pan_x = self.pan_x
            self.target_pan_y = self.pan_y
            self._clamp_target_pan()
            return True
        return False

    def _scroll(self, _w, event):
        ctrl = bool(event.state & Gdk.ModifierType.CONTROL_MASK)
        shift = bool(event.state & Gdk.ModifierType.SHIFT_MASK)

        # Smooth touchpad deltas when available.
        dx = dy = 0.0
        if event.direction == Gdk.ScrollDirection.SMOOTH:
            try:
                ok, dx, dy = event.get_scroll_deltas()
                if not ok:
                    dx = dy = 0.0
            except Exception:
                dx = dy = 0.0
        else:
            if event.direction == Gdk.ScrollDirection.UP:
                dy = -1.0
            elif event.direction == Gdk.ScrollDirection.DOWN:
                dy = 1.0
            elif event.direction == Gdk.ScrollDirection.LEFT:
                dx = -1.0
            elif event.direction == Gdk.ScrollDirection.RIGHT:
                dx = 1.0

        if ctrl:
            delta = dy if abs(dy) >= abs(dx) else dx
            if delta < 0:
                self._set_zoom(self.zoom + 25)
            elif delta > 0:
                self._set_zoom(self.zoom - 25)
            return True

        if shift:
            delta = dx if abs(dx) > 0.01 else dy
            self._pan_by(dx=-delta * self.WHEEL_STEP)
        else:
            # Wheel now pans through the current page; it never changes page.
            self._pan_by(dx=-dx * self.WHEEL_STEP, dy=-dy * self.WHEEL_STEP)
        return True

    def _laser_toggle(self, w):
        self.laser_enabled = w.get_active()
        self.canvas.queue_draw()

    def _color_changed(self, combo):
        text = combo.get_active_text()
        if text in LASER_COLORS:
            self.laser_color_name = text
            self.canvas.queue_draw()

    def _key(self, _w, event):
        key = Gdk.keyval_name(event.keyval) or ''
        ctrl = bool(event.state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and key in ('plus', 'equal', 'KP_Add'):
            self._set_zoom(self.zoom + 25); return True
        if ctrl and key in ('minus', 'KP_Subtract'):
            self._set_zoom(self.zoom - 25); return True
        if ctrl and key in ('0', 'KP_0'):
            self._set_zoom(100); return True

        # Requested navigation: horizontal arrows change the whole page;
        # vertical arrows move within the current page.
        if key in ('Right', 'Page_Down', 'space'):
            self._goto(self.page + 1); return True
        if key in ('Left', 'Page_Up', 'BackSpace'):
            self._goto(self.page - 1); return True
        if key == 'Down':
            self._pan_by(dy=-self.PAN_STEP); return True
        if key == 'Up':
            self._pan_by(dy=self.PAN_STEP); return True

        if ctrl and key == 'Home':
            self._goto(0); return True
        if ctrl and key == 'End':
            self._goto(self.page_count - 1); return True
        if key == 'Home':
            # Home/End without Ctrl move to the top/bottom of the current page.
            minx, maxx, miny, maxy = self._pan_bounds()
            self._set_pan_target(y=maxy); return True
        if key == 'End':
            minx, maxx, miny, maxy = self._pan_bounds()
            self._set_pan_target(y=miny); return True
        if key == 'Escape':
            self.destroy(); return True
        if key == 'Tab':
            self.controls_visible = not self.controls_visible
            self.revealer.set_reveal_child(self.controls_visible)
            GLib.timeout_add(250, lambda: (self._request_render(), False)[1] if not self._closed else False)
            return True

        low = key.lower()
        if low == 'l':
            self.laser_toggle.set_active(not self.laser_toggle.get_active()); return True
        mapping = {'r': 'Vermelho', 'g': 'Verde', 'b': 'Azul', 'y': 'Amarelo', 'm': 'Magenta', 'c': 'Ciano'}
        if low in mapping:
            self.laser_color_name = mapping[low]
            self.color_combo.set_active(list(LASER_COLORS).index(self.laser_color_name))
            return True
        return False
