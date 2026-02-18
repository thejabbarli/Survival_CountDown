"""Image caching and processing utilities."""

from pathlib import Path
from typing import Optional
from PIL import Image


class ImageCache:
    """Caches loaded and resized images."""

    def __init__(self):
        self._cache: dict[tuple[Path, int], Image.Image] = {}
        self._grayscale_cache: dict[tuple[Path, int], Image.Image] = {}

    def get(self, path: Path, size: int) -> Optional[Image.Image]:
        """Get image resized to size x size."""
        key = (path, size)

        if key in self._cache:
            return self._cache[key]

        img = self._load_and_resize(path, size)
        if img is not None:
            self._cache[key] = img

        return img

    def get_grayscale(self, path: Path, size: int) -> Optional[Image.Image]:
        """Get grayscale version of image."""
        key = (path, size)

        if key in self._grayscale_cache:
            return self._grayscale_cache[key]

        color_img = self.get(path, size)
        if color_img is None:
            return None

        gray = color_img.convert('LA').convert('RGBA')
        self._grayscale_cache[key] = gray
        return gray

    def _load_and_resize(self, path: Path, size: int) -> Optional[Image.Image]:
        """Load image from disk and resize to square."""
        try:
            img = Image.open(path)

            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            img.thumbnail((size, size), Image.Resampling.LANCZOS)

            square = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            offset_x = (size - img.width) // 2
            offset_y = (size - img.height) // 2
            square.paste(img, (offset_x, offset_y), img)

            return square
        except Exception:
            return None

    def clear(self) -> None:
        """Clear all cached images."""
        self._cache.clear()
        self._grayscale_cache.clear()


_global_cache: Optional[ImageCache] = None


def get_image_cache() -> ImageCache:
    """Get the global image cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = ImageCache()
    return _global_cache
