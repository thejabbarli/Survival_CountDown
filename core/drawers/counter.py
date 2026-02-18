"""Counter drawer with pulse animation."""

from PIL import ImageDraw, ImageFont, Image

from ..config import CanvasConfig, CounterDisplayConfig
from ..easing import pulse


class CounterDrawer:
    """Draws the remaining count with optional pulse."""

    def __init__(
            self,
            canvas: CanvasConfig,
            config: CounterDisplayConfig,
            font: ImageFont.FreeTypeFont
    ):
        self.canvas = canvas
        self.config = config
        self.font = font
        self.base_font_size = font.size if hasattr(font, 'size') else 72

    def draw(
        self,
        target: ImageDraw.Draw,
        count: int,
        pulse_progress: float = None
    ) -> None:
        text = self.config.format_string.format(count=count)

        bbox = target.textbbox((0, 0), text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        base_x = (self.canvas.width - text_width) // 2
        if self.config.position == "top":
            base_y = self.config.margin_top
        else:
            base_y = self.canvas.height - self.config.margin_bottom

        scale = 1.0
        if pulse_progress is not None and self.config.pulse_on_elimination:
            scale = pulse(pulse_progress, self.config.pulse_scale - 1)

        if scale != 1.0 and scale > 0.5:
            padding = 20
            text_img = Image.new('RGBA', (text_width + padding * 2, text_height + padding * 2), (0, 0, 0, 0))
            text_draw = ImageDraw.Draw(text_img)
            text_draw.text((padding, padding), text, fill=self.config.color, font=self.font)

            new_w = int(text_img.width * scale)
            new_h = int(text_img.height * scale)
            scaled = text_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            paste_x = base_x - padding - (new_w - text_img.width) // 2
            paste_y = base_y - padding - (new_h - text_img.height) // 2

            target._image.paste(scaled, (paste_x, paste_y), scaled)
        else:
            target.text((base_x, base_y), text, fill=self.config.color, font=self.font)
