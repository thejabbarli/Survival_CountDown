"""Image caching for entity images."""

from typing import Dict, Optional, Tuple
from pathlib import Path
from PIL import Image


class ImageCache:
    """Caches loaded and resized images."""

    def __init__(self):
        self._cache: Dict[Tuple[str, int], Image.Image] = {}
        self._grayscale_cache: Dict[Tuple[str, int], Image.Image] = {}

    def get(self, path: Path, size: int) -> Optional[Image.Image]:
        """Get image resized to fit within size, keeping aspect ratio."""
        key = (str(path), size)

        if key in self._cache:
            return self._cache[key].copy()

        try:
            img = Image.open(path).convert('RGBA')

            # Resize keeping aspect ratio (fit within size x size)
            img.thumbnail((size, size), Image.Resampling.LANCZOS)

            # Center on transparent background of exact size
            result = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            offset_x = (size - img.width) // 2
            offset_y = (size - img.height) // 2
            result.paste(img, (offset_x, offset_y), img)

            self._cache[key] = result
            return result.copy()
        except Exception:
            return None

    def get_grayscale(self, path: Path, size: int) -> Optional[Image.Image]:
        """Get grayscale version of image."""
        key = (str(path), size)

        if key in self._grayscale_cache:
            return self._grayscale_cache[key].copy()

        img = self.get(path, size)
        if img is None:
            return None

        # Convert to grayscale while keeping alpha
        r, g, b, a = img.split()
        gray = Image.merge('RGB', (r, g, b)).convert('L')
        gray_rgba = Image.merge('RGBA', (gray, gray, gray, a))

        self._grayscale_cache[key] = gray_rgba
        return gray_rgba.copy()

    def clear(self):
        """Clear all cached images."""
        self._cache.clear()
        self._grayscale_cache.clear()


# Global instance
_image_cache: Optional[ImageCache] = None


def get_image_cache() -> ImageCache:
    """Get global image cache."""
    global _image_cache
    if _image_cache is None:
        _image_cache = ImageCache()
    return _image_cache
