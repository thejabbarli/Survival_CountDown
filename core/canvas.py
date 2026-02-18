"""Canvas utilities."""

from PIL import Image, ImageDraw
from pathlib import Path
from typing import Optional

from .config import CanvasConfig


class CanvasFactory:
    """Creates canvases with effects."""

    def __init__(self, config: CanvasConfig, total_frames: int = 1):
        self.config = config
        self.total_frames = total_frames
        self._static_bg_cache: Optional[Image.Image] = None

    def _create_static_background(self) -> Image.Image:
        """Create static background (cached)."""
        cfg = self.config

        if cfg.greenscreen:
            return Image.new('RGB', (cfg.width, cfg.height), "#00FF00")

        if cfg.transparent:
            return Image.new('RGBA', (cfg.width, cfg.height), (0, 0, 0, 0))

        if cfg.background_image:
            path = Path(cfg.background_image)
            if path.exists():
                img = Image.open(path).convert('RGB')
                img = img.resize((cfg.width, cfg.height), Image.Resampling.LANCZOS)
                return img

        if cfg.gradient_enabled and not cfg.animated_gradient:
            from .effects import create_gradient_fast, add_vignette
            img = create_gradient_fast(
                cfg.width, cfg.height,
                cfg.gradient_top,
                cfg.gradient_bottom
            )
            if cfg.vignette_enabled:
                img = add_vignette(img, cfg.vignette_strength)
            return img

        return Image.new('RGB', (cfg.width, cfg.height), cfg.background_color)

    def _create_animated_background(self, frame: int) -> Image.Image:
        """Create animated gradient for specific frame."""
        cfg = self.config

        from .effects import create_animated_gradient, add_vignette

        img = create_animated_gradient(
            cfg.width, cfg.height,
            frame=frame,
            total_frames=self.total_frames,
            color1_start=cfg.gradient_top,
            color1_end=cfg.gradient_top_end,
            color2_start=cfg.gradient_bottom,
            color2_end=cfg.gradient_bottom_end,
            cycle_speed=cfg.gradient_cycle_speed
        )

        if cfg.vignette_enabled:
            img = add_vignette(img, cfg.vignette_strength)

        return img

    def create(self, frame: int = 0) -> tuple[Image.Image, ImageDraw.Draw]:
        """Create canvas with background."""
        cfg = self.config

        if cfg.animated_gradient and not cfg.greenscreen and not cfg.transparent:
            img = self._create_animated_background(frame)
        else:
            if self._static_bg_cache is None:
                self._static_bg_cache = self._create_static_background()
            img = self._static_bg_cache.copy()

        return img, ImageDraw.Draw(img)
