"""Winner drawer with modern styling."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from ..entity import Entity
from ..config import CanvasConfig, WinnerScreenConfig
from ..image_cache import get_image_cache


class WinnerDrawer:
    """Draws the winner celebration with modern styling."""

    def __init__(
        self,
        canvas: CanvasConfig,
        config: WinnerScreenConfig,
        font: ImageFont.FreeTypeFont,
        corner_radius: int = 20,
        shadow_enabled: bool = True
    ):
        self.canvas = canvas
        self.config = config
        self.font = font
        self.corner_radius = corner_radius
        self.shadow_enabled = shadow_enabled
        self.image_cache = get_image_cache()

    def draw(self, target: ImageDraw.Draw, winner: Entity, frame_num: int = 0) -> None:
        from ..idle_animation import get_idle_animator

        cfg = self.config
        canvas_img = target._image
        animator = get_idle_animator()

        # Title with subtle movement
        title_dx, title_dy = animator.get_offset(frame_num, 0, 2)

        bbox = target.textbbox((0, 0), cfg.title_text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.canvas.width - text_width) // 2 + int(title_dx * 0.5)
        text_y = int(self.canvas.height * cfg.title_y_ratio) + int(title_dy * 0.5)
        target.text((text_x, text_y), cfg.title_text, fill=cfg.title_color, font=self.font)

        # Winner box with idle animation
        box_dx, box_dy = animator.get_offset(frame_num, 1, 2)
        box_scale = animator.get_scale(frame_num, 1, 2)

        base_box_size = int(min(self.canvas.width, self.canvas.height) * cfg.box_size_ratio)
        box_size = int(base_box_size * box_scale)
        box_x = (self.canvas.width - box_size) // 2 + int(box_dx)
        box_y = (self.canvas.height - box_size) // 2 + int(box_dy)

        # Shadow
        if self.shadow_enabled:
            shadow = self._create_shadow(box_size)
            shadow_x = box_x - 20 + 4
            shadow_y = box_y - 20 + 8
            canvas_img.paste(shadow, (shadow_x, shadow_y), shadow)

        # Winner image or colored box
        if winner.image_path is not None:
            img = self.image_cache.get(winner.image_path, box_size)
            if img is not None:
                img = self._apply_rounded_corners(img, self.corner_radius)
                canvas_img.paste(img, (box_x, box_y), img)
            else:
                self._draw_rounded_rect(target, box_x, box_y, box_size, winner.color)
        else:
            self._draw_rounded_rect(target, box_x, box_y, box_size, winner.color)

        # Winner name with movement
        bbox = target.textbbox((0, 0), winner.name, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.canvas.width - text_width) // 2 + int(box_dx * 0.5)
        text_y = box_y + box_size + 40
        target.text((text_x, text_y), winner.name, fill="white", font=self.font)

    def _create_shadow(self, size: int) -> Image.Image:
        """Create soft shadow."""
        blur = 20
        shadow_size = size + blur * 2
        shadow = Image.new('RGBA', (shadow_size, shadow_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow)

        margin = blur // 2
        self._draw_rounded_rect_raw(draw, margin, margin, size, (0, 0, 0, 120), self.corner_radius)

        shadow = shadow.filter(ImageFilter.GaussianBlur(blur // 2))
        return shadow

    def _draw_rounded_rect(self, draw: ImageDraw.Draw, x: int, y: int, size: int, color: str) -> None:
        """Draw rounded rectangle."""
        r = self.corner_radius
        draw.rectangle([x + r, y, x + size - r, y + size], fill=color)
        draw.rectangle([x, y + r, x + size, y + size - r], fill=color)
        draw.ellipse([x, y, x + r * 2, y + r * 2], fill=color)
        draw.ellipse([x + size - r * 2, y, x + size, y + r * 2], fill=color)
        draw.ellipse([x, y + size - r * 2, x + r * 2, y + size], fill=color)
        draw.ellipse([x + size - r * 2, y + size - r * 2, x + size, y + size], fill=color)

    def _draw_rounded_rect_raw(self, draw: ImageDraw.Draw, x: int, y: int, size: int, color: tuple, radius: int) -> None:
        """Draw rounded rect with RGBA color."""
        r = radius
        draw.rectangle([x + r, y, x + size - r, y + size], fill=color)
        draw.rectangle([x, y + r, x + size, y + size - r], fill=color)
        draw.ellipse([x, y, x + r * 2, y + r * 2], fill=color)
        draw.ellipse([x + size - r * 2, y, x + size, y + r * 2], fill=color)
        draw.ellipse([x, y + size - r * 2, x + r * 2, y + size], fill=color)
        draw.ellipse([x + size - r * 2, y + size - r * 2, x + size, y + size], fill=color)

    def _apply_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        """Apply rounded corners to image."""
        if radius <= 0:
            return img

        size = img.size[0]
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)

        r = radius
        draw.rectangle([r, 0, size - r, size], fill=255)
        draw.rectangle([0, r, size, size - r], fill=255)
        draw.ellipse([0, 0, r * 2, r * 2], fill=255)
        draw.ellipse([size - r * 2, 0, size, r * 2], fill=255)
        draw.ellipse([0, size - r * 2, r * 2, size], fill=255)
        draw.ellipse([size - r * 2, size - r * 2, size, size], fill=255)

        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        result = Image.new('RGBA', img.size, (0, 0, 0, 0))
        result.paste(img, (0, 0), mask)
        return result
