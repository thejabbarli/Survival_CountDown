"""Entity drawer with modern card styling.

NOTE: This draws Entity objects.
      This is different from core/config/entity.py (EntityDisplayConfig).
"""

from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from ..entity import Entity
from ..layout import CellPosition
from ..config import EntityDisplayConfig
from ..utils import get_contrast_color
from ..animations import EliminationAnimation
from ..image_cache import get_image_cache
from ..idle_animation import get_idle_animator, IdleAnimator


class EntityDrawer:
    """Draws a single entity with modern card styling."""

    def __init__(
        self,
        entity_config: EntityDisplayConfig,
        font: ImageFont.FreeTypeFont,
        elimination_animation: EliminationAnimation,
        idle_animator: Optional[IdleAnimator] = None,
        idle_enabled: bool = True
    ):
        self.entity_config = entity_config
        self.font = font
        self.elimination_animation = elimination_animation
        self.image_cache = get_image_cache()
        self.idle_enabled = idle_enabled
        self._shadow_cache = {}
        self._idle_animator = idle_animator

    def _get_idle_animator(self) -> IdleAnimator:
        if self._idle_animator is not None:
            return self._idle_animator
        return get_idle_animator()

    def _create_shadow(self, size: int) -> Image.Image:
        if size in self._shadow_cache:
            return self._shadow_cache[size]

        cfg = self.entity_config
        blur = cfg.shadow_blur
        opacity = cfg.shadow_opacity
        radius = cfg.corner_radius

        shadow_size = size + blur * 4
        shadow = Image.new('RGBA', (shadow_size, shadow_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow)

        margin = blur * 2
        self._draw_rounded_rect(
            draw,
            margin, margin, margin + size, margin + size,
            radius,
            (0, 0, 0, opacity)
        )

        shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
        self._shadow_cache[size] = shadow
        return shadow

    def _draw_rounded_rect(self, draw, x1, y1, x2, y2, radius, fill):
        if radius <= 0:
            draw.rectangle([x1, y1, x2, y2], fill=fill)
            return

        radius = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)

        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
        draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
        draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
        draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)

    def _create_rounded_mask(self, size: int, radius: int) -> Image.Image:
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        self._draw_rounded_rect(draw, 0, 0, size, size, radius, 255)
        return mask

    def _apply_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        if radius <= 0:
            return img

        size = img.size[0]
        mask = self._create_rounded_mask(size, radius)

        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        result = Image.new('RGBA', img.size, (0, 0, 0, 0))
        result.paste(img, (0, 0), mask)
        return result

    def draw(
        self,
        target: ImageDraw.Draw,
        entity: Entity,
        position: CellPosition,
        state: str,
        progress: float = 0.0,
        frame_num: int = 0,
        entity_index: int = 0,
        total_entities: int = 1
    ) -> None:
        if state == "gone":
            return

        if state == "eliminating":
            self.elimination_animation.draw(
                target, entity, position, progress, self.image_cache
            )
        else:
            if self.idle_enabled:
                animator = self._get_idle_animator()
                dx, dy = animator.get_offset(frame_num, entity_index, total_entities)
                scale = animator.get_scale(frame_num, entity_index, total_entities)

                new_size = int(position.size * scale)
                offset_x = (position.size - new_size) // 2
                offset_y = (position.size - new_size) // 2

                animated_pos = CellPosition(
                    x=int(position.x + dx + offset_x),
                    y=int(position.y + dy + offset_y),
                    size=new_size
                )
                self._draw_entity_card(target, entity, animated_pos)
            else:
                self._draw_entity_card(target, entity, position)

    def _draw_entity_card(self, target: ImageDraw.Draw, entity: Entity, pos: CellPosition) -> None:
        cfg = self.entity_config
        canvas = target._image

        if cfg.shadow_enabled:
            shadow = self._create_shadow(pos.size)
            shadow_x = pos.x - cfg.shadow_blur * 2
            shadow_y = pos.y - cfg.shadow_blur * 2 + 4
            canvas.paste(shadow, (shadow_x, shadow_y), shadow)

        if entity.image_path is not None:
            img = self.image_cache.get(entity.image_path, pos.size)
            if img is not None:
                img = self._apply_rounded_corners(img, cfg.corner_radius)
                canvas.paste(img, (pos.x, pos.y), img)
                return

        self._draw_rounded_rect(
            target,
            pos.x, pos.y, pos.x + pos.size, pos.y + pos.size,
            cfg.corner_radius,
            entity.color
        )

        name = entity.name[:cfg.name_max_length]
        text_color = get_contrast_color(entity.color)
        bbox = target.textbbox((0, 0), name, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = pos.x + (pos.size - text_width) // 2
        text_y = pos.y + (pos.size - text_height) // 2
        target.text((text_x, text_y), name, fill=text_color, font=self.font)
