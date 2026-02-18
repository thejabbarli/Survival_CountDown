"""Winner drawer with celebration screen."""

from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from ..entity import Entity
from ..config import CanvasConfig, WinnerScreenConfig
from ..image_cache import get_image_cache
from ..idle_animation import get_idle_animator, IdleAnimator


class WinnerDrawer:
    """Draws the winner celebration with modern styling."""

    def __init__(
        self,
        canvas: CanvasConfig,
        config: WinnerScreenConfig,
        font: ImageFont.FreeTypeFont,
        corner_radius: int = 20,
        shadow_enabled: bool = True,
        idle_animator: Optional[IdleAnimator] = None
    ):
        self.canvas = canvas
        self.config = config
        self.font = font
        self.corner_radius = corner_radius
        self.shadow_enabled = shadow_enabled
        self.image_cache = get_image_cache()
        self._idle_animator = idle_animator

    def _get_idle_animator(self) -> IdleAnimator:
        if self._idle_animator is not None:
            return self._idle_animator
        return get_idle_animator()

    def draw(self, target: ImageDraw.Draw, winner: Entity, frame_num: int = 0) -> None:
        cfg = self.config
        canvas_img = target._image
        animator = self._get_idle_animator()

        title_dx, title_dy = animator.get_offset(frame_num, 0, 2)

        bbox = target.textbbox((0, 0), cfg.title_text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.canvas.width - text_width) // 2 + int(title_dx * 0.5)
        text_y = int(self.canvas.height * cfg.title_y_ratio) + int(title_dy * 0.5)
        target.text((text_x, text_y), cfg.title_text, fill=cfg.title_color, font=self.font)

        box_dx, box_dy = animator.get_offset(frame_num, 1, 2)
        box_scale = animator.get_scale(frame_num, 1, 2)

        base_box_size = int(min(self.canvas.width, self.canvas.height) * cfg.box_size_ratio)
        box_size = int(base_box_size * box_scale)
        box_x = (self.canvas.width - box_size) // 2 + int(box_dx)
        box_y = (self.canvas.height - box_size) // 2 + int(box_dy)

        if self.shadow_enabled:
            shadow = self._create_shadow(box_size)
            shadow_x = box_x - 20 + 4
            shadow_y = box_y - 20 + 8
            canvas_img.paste(shadow, (shadow_x, shadow_y), shadow)

        if winner.image_path is not None:
            img = self.image_cache.get(winner.image_path, box_size)
            if img is not None:
                img = self._apply_rounded_corners(img, self.corner_radius)
                canvas_img.paste(img, (box_x, box_y), img)
            else:
                self._draw_rounded_rect(target, box_x, box_y, box_size, winner.color)
        else:
            self._draw_rounded_rect(target, box_x, box_y, box_size, winner.color)

        bbox = target.textbbox((0, 0), winner.name, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_x = (self.canvas.width - text_width) // 2 + int(box_dx * 0.5)
        text_y = box_y + box_size + 40
        target.text((text_x, text_y), winner.name, fill="white", font=self.font)

    def _create_shadow(self, size: int) -> Image.Image:
        shadow_size = size + 40
        shadow = Image.new('RGBA', (shadow_size, shadow_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow)
        
        margin = 20
        self._draw_rounded_rect_raw(
            draw,
            margin, margin, margin + size, margin + size,
            self.corner_radius,
            (0, 0, 0, 80)
        )
        
        shadow = shadow.filter(ImageFilter.GaussianBlur(10))
        return shadow

    def _draw_rounded_rect(self, target: ImageDraw.Draw, x: int, y: int, size: int, color: str) -> None:
        self._draw_rounded_rect_raw(target, x, y, x + size, y + size, self.corner_radius, color)

    def _draw_rounded_rect_raw(self, draw, x1, y1, x2, y2, radius, fill):
        w, h = x2 - x1, y2 - y1
        radius = min(radius, w // 2, h // 2)

        if radius <= 0:
            draw.rectangle([x1, y1, x2, y2], fill=fill)
            return

        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
        draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
        draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
        draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)

    def _apply_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        if radius <= 0:
            return img

        size = img.size[0]
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        self._draw_rounded_rect_raw(draw, 0, 0, size, size, radius, 255)

        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        result = Image.new('RGBA', img.size, (0, 0, 0, 0))
        result.paste(img, (0, 0), mask)
        return result
