"""Counter drawer - displays remaining count."""

from PIL import ImageDraw, ImageFont

from ..config import CanvasConfig, CounterDisplayConfig


class CounterDrawer:
    """Draws the remaining count on the canvas."""

    def __init__(
            self,
            canvas: CanvasConfig,
            config: CounterDisplayConfig,
            font: ImageFont.FreeTypeFont
    ):
        self.canvas = canvas
        self.config = config
        self.font = font

    def draw(self, target: ImageDraw.Draw, count: int) -> None:
        """
        Draw counter on the canvas.

        Args:
            target: PIL ImageDraw object to draw on
            count: Number to display
        """
        text = self.config.format_string.format(count=count)

        bbox = target.textbbox((0, 0), text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.canvas.width - text_width) // 2

        if self.config.position == "top":
            text_y = self.config.margin_top
        else:
            text_y = self.canvas.height - self.config.margin_bottom

        target.text((text_x, text_y), text, fill=self.config.color, font=self.font)
