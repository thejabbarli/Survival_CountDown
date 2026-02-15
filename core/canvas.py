"""Canvas utilities."""

from PIL import Image, ImageDraw

from .config import CanvasConfig


class CanvasFactory:
    """Creates blank canvases."""

    def __init__(self, config: CanvasConfig):
        self.config = config

    def create(self) -> tuple[Image.Image, ImageDraw.Draw]:
        """Create blank canvas with background color."""
        img = Image.new(
            'RGB',
            (self.config.width, self.config.height),
            self.config.background_color
        )
        return img, ImageDraw.Draw(img)
