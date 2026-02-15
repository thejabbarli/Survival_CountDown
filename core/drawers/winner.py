"""Winner drawer - displays winner celebration elements."""

from PIL import ImageDraw, ImageFont

from ..entity import Entity
from ..config import CanvasConfig, WinnerScreenConfig
from ..image_cache import get_image_cache


class WinnerDrawer:
    """Draws the winner celebration elements on a canvas."""

    def __init__(
        self,
        canvas: CanvasConfig,
        config: WinnerScreenConfig,
        font: ImageFont.FreeTypeFont
    ):
        self.canvas = canvas
        self.config = config
        self.font = font
        self.image_cache = get_image_cache()

    def draw(self, target: ImageDraw.Draw, winner: Entity) -> None:
        cfg = self.config

        # Title
        bbox = target.textbbox((0, 0), cfg.title_text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.canvas.width - text_width) // 2
        text_y = int(self.canvas.height * cfg.title_y_ratio)
        target.text((text_x, text_y), cfg.title_text, fill=cfg.title_color, font=self.font)

        # Winner box
        box_size = int(min(self.canvas.width, self.canvas.height) * cfg.box_size_ratio)
        box_x = (self.canvas.width - box_size) // 2
        box_y = (self.canvas.height - box_size) // 2

        # Try image first
        if winner.image_path is not None:
            img = self.image_cache.get(winner.image_path, box_size)
            if img is not None:
                canvas = target._image
                canvas.paste(img, (box_x, box_y), img)
            else:
                target.rectangle([box_x, box_y, box_x + box_size, box_y + box_size], fill=winner.color)
        else:
            target.rectangle([box_x, box_y, box_x + box_size, box_y + box_size], fill=winner.color)

        # Winner name below box
        bbox = target.textbbox((0, 0), winner.name, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.canvas.width - text_width) // 2
        text_y = box_y + box_size + 30
        target.text((text_x, text_y), winner.name, fill="white", font=self.font)
