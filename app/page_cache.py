from collections import OrderedDict


class PageCache:
    """GTK-thread-owned decoded image cache with count and byte budgets."""
    def __init__(self, max_pages=8, max_bytes=96 * 1024 * 1024):
        self.max_pages = max_pages
        self.max_bytes = max_bytes
        self.images = OrderedDict()
        self.bytes = 0

    def get(self, key):
        image = self.images.get(key)
        if image is not None:
            self.images.move_to_end(key)
        return image

    def put(self, key, image):
        old = self.images.pop(key, None)
        if old is not None:
            self.bytes -= old.get_rowstride() * old.get_height()
        size = image.get_rowstride() * image.get_height()
        if size > self.max_bytes:
            return
        self.images[key] = image
        self.bytes += size
        while self.bytes > self.max_bytes or len(self.images) > self.max_pages:
            _, old = self.images.popitem(last=False)
            self.bytes -= old.get_rowstride() * old.get_height()

    def clear(self):
        self.images.clear(); self.bytes = 0
