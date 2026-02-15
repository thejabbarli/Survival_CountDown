"""Canvas utilities."""

from PIL import Image, ImageDraw
from pathlib import Path
from typing import Optional

from .config import CanvasConfig


class CanvasFactory:
    """Creates canvases with effects."""

    def __init__(self, config: CanvasConfig):
        self.config = config
        self._bg_cache: Optional[Image.Image] = None

    def _create_background(self) -> Image.Image:
        """Create or load background."""
        cfg = self.config

        # Custom image
        if cfg.background_image:
            path = Path(cfg.background_image)
            if path.exists():
                img = Image.open(path).convert('RGB')
                img = img.resize((cfg.width, cfg.height), Image.Resampling.LANCZOS)
                return img

        # Gradient
        if cfg.gradient_enabled:
            from .effects import create_gradient_fast, add_vignette
            img = create_gradient_fast(
                cfg.width, cfg.height,
                cfg.gradient_top,
                cfg.gradient_bottom
            )
            if cfg.vignette_enabled:
                img = add_vignette(img, cfg.vignette_strength)
            return img

        # Solid color
        return Image.new('RGB', (cfg.width, cfg.height), cfg.background_color)

    def create(self) -> tuple[Image.Image, ImageDraw.Draw]:
        """Create canvas with background."""
        if self._bg_cache is None:
            self._bg_cache = self._create_background()

        img = self._bg_cache.copy()
        return img, ImageDraw.Draw(img)
