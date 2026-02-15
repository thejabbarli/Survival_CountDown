"""Winner drawer - displays winner celebration elements."""

from PIL import ImageDraw, ImageFont

from ..entity import Entity
from ..config import CanvasConfig, WinnerScreenConfig
from ..utils import get_contrast_color


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

    def draw(self, target: ImageDraw.Draw, winner: Entity) -> None:
        """
        Draw winner elements on canvas.

        Args:
            target: PIL ImageDraw object to draw on
            winner: The winning entity
        """
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

        target.rectangle(
            [box_x, box_y, box_x + box_size, box_y + box_size],
            fill=winner.color
        )

        # Winner name
        bbox = target.textbbox((0, 0), winner.name, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.canvas.width - text_width) // 2
        text_y = box_y + (box_size // 2) + cfg.name_offset_y

        text_color = get_contrast_color(winner.color)
        target.text((text_x, text_y), winner.name, fill=text_color, font=self.font)
