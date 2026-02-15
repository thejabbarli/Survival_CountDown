"""Font loading utilities."""

from typing import List, Optional
from PIL import ImageFont

from .config import FontConfig


class FontLoader:
    """Loads fonts with fallback support."""

    DEFAULT_PATHS: List[str] = [
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        # Mac
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]

    def __init__(
        self,
        config: FontConfig,
        custom_paths: Optional[List[str]] = None
    ):
        self.config = config
        self._font_paths = (custom_paths or []) + self.DEFAULT_PATHS
        self._cache: dict[int, ImageFont.FreeTypeFont] = {}

    def load(self, size: int) -> ImageFont.FreeTypeFont:
        """Load font at given size. Uses cache."""
        if size in self._cache:
            return self._cache[size]

        for path in self._font_paths:
            try:
                font = ImageFont.truetype(path, size)
                self._cache[size] = font
                return font
            except (OSError, IOError):
                continue

        font = ImageFont.load_default()
        self._cache[size] = font
        return font

    def get_large(self) -> ImageFont.FreeTypeFont:
        """Get large font."""
        return self.load(self.config.size_large)

    def get_small(self) -> ImageFont.FreeTypeFont:
        """Get small font."""
        return self.load(self.config.size_small)
