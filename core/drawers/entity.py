"""Entity drawer - CLEAN BORDER instead of ugly glow."""

from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from ..entity import Entity
from ..layout import CellPosition
from ..config import EntityDisplayConfig
from ..utils import get_contrast_color
from ..animations import EliminationAnimation
from ..image_cache import get_image_cache
from ..idle_animation import get_idle_animator, IdleAnimator
from ..spotlight import (
    SpotlightState,
    SpotlightVisualConfig,
    hex_to_rgb,
)


class EntityDrawer:
    """Draws entities with spotlight as a clean bright border."""

    def __init__(
        self,
        entity_config: EntityDisplayConfig,
        font: ImageFont.FreeTypeFont,
        elimination_animation: EliminationAnimation,
        idle_animator: Optional[IdleAnimator] = None,
        idle_enabled: bool = True,
        spotlight_visual_config: Optional[SpotlightVisualConfig] = None,
    ):
        self.entity_config = entity_config
        self.font = font
        self.elimination_animation = elimination_animation
        self.image_cache = get_image_cache()
        self.idle_enabled = idle_enabled
        self._shadow_cache = {}
        self._idle_animator = idle_animator
        self.spotlight_config = spotlight_visual_config or SpotlightVisualConfig()

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

    def _apply_opacity(self, img: Image.Image, opacity: float) -> Image.Image:
        """Apply opacity to an RGBA image."""
        if opacity >= 1.0:
            return img

        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        r, g, b, a = img.split()
        a = a.point(lambda x: int(x * opacity))
        return Image.merge('RGBA', (r, g, b, a))

    def _draw_spotlight_border(
        self,
        canvas: Image.Image,
        pos: CellPosition,
        is_locked: bool
    ) -> None:
        """Draw a clean bright border around the spotlit entity."""
        # Border settings
        border_width = 4 if is_locked else 3
        r, g, b = hex_to_rgb(self.spotlight_config.glow_color)

        # For locked state, make it brighter/whiter
        if is_locked:
            # Blend toward white
            r = min(255, r + 50)
            g = min(255, g + 50)
            b = min(255, b + 50)

        radius = self.entity_config.corner_radius

        # Create border by drawing a larger rounded rect behind
        border_size = pos.size + border_width * 2
        border_img = Image.new('RGBA', (border_size, border_size), (0, 0, 0, 0))
        border_draw = ImageDraw.Draw(border_img)

        # Draw outer (border color)
        self._draw_rounded_rect(
            border_draw,
            0, 0, border_size, border_size,
            radius + border_width,
            (r, g, b, 255)
        )

        # Cut out inner (transparent hole where entity goes)
        inner_mask = Image.new('L', (border_size, border_size), 255)
        mask_draw = ImageDraw.Draw(inner_mask)
        self._draw_rounded_rect(
            mask_draw,
            border_width, border_width,
            border_width + pos.size, border_width + pos.size,
            radius,
            0  # Black = transparent in mask
        )

        # Apply mask to create border ring
        border_img.putalpha(inner_mask)

        # Paste onto canvas
        border_x = pos.x - border_width
        border_y = pos.y - border_width
        canvas.paste(border_img, (border_x, border_y), border_img)

    def _get_spotlight_params(self, spotlight_state: SpotlightState, frame_num: int):
        """Get visual parameters based on spotlight state."""
        if spotlight_state == SpotlightState.NORMAL:
            return 1.0, 1.0, False, False  # opacity, scale, show_border, is_locked

        elif spotlight_state == SpotlightState.DIMMED:
            return self.spotlight_config.dim_opacity, 1.0, False, False

        elif spotlight_state == SpotlightState.ACTIVE:
            return 1.0, self.spotlight_config.active_scale, True, False

        elif spotlight_state == SpotlightState.LOCKED:
            # Subtle pulse
            import math
            pulse = 1.0 + 0.02 * math.sin(frame_num * 0.4)
            scale = self.spotlight_config.locked_scale * pulse
            return 1.0, scale, True, True

        return 1.0, 1.0, False, False

    def draw(
        self,
        target: ImageDraw.Draw,
        entity: Entity,
        position: CellPosition,
        state: str,
        progress: float = 0.0,
        frame_num: int = 0,
        entity_index: int = 0,
        total_entities: int = 1,
        spotlight_state: SpotlightState = SpotlightState.NORMAL,
    ) -> None:
        if state == "gone":
            return

        if state == "eliminating":
            self.elimination_animation.draw(
                target, entity, position, progress, self.image_cache
            )
            return

        # Get spotlight parameters
        opacity, spot_scale, show_border, is_locked = self._get_spotlight_params(
            spotlight_state, frame_num
        )

        # ALWAYS apply idle animation
        if self.idle_enabled:
            animator = self._get_idle_animator()
            dx, dy = animator.get_offset(frame_num, entity_index, total_entities)
            idle_scale = animator.get_scale(frame_num, entity_index, total_entities)
        else:
            dx, dy = 0, 0
            idle_scale = 1.0

        # Combine scales
        total_scale = idle_scale * spot_scale

        # Calculate final position
        new_size = int(position.size * total_scale)
        offset_x = (position.size - new_size) // 2
        offset_y = (position.size - new_size) // 2

        final_pos = CellPosition(
            x=int(position.x + dx + offset_x),
            y=int(position.y + dy + offset_y),
            size=new_size
        )

        # Draw spotlight border BEHIND entity
        canvas = target._image
        if show_border:
            self._draw_spotlight_border(canvas, final_pos, is_locked)

        # Draw the entity card
        self._draw_entity_card(target, entity, final_pos, opacity)

    def _draw_entity_card(
        self,
        target: ImageDraw.Draw,
        entity: Entity,
        pos: CellPosition,
        opacity: float = 1.0
    ) -> None:
        cfg = self.entity_config
        canvas = target._image

        # Shadow
        if cfg.shadow_enabled:
            shadow = self._create_shadow(pos.size)
            shadow_x = pos.x - cfg.shadow_blur * 2
            shadow_y = pos.y - cfg.shadow_blur * 2 + 4

            if opacity < 1.0:
                shadow = self._apply_opacity(shadow, opacity)

            canvas.paste(shadow, (shadow_x, shadow_y), shadow)

        # Entity image
        if entity.image_path is not None:
            img = self.image_cache.get(entity.image_path, pos.size)
            if img is not None:
                img = self._apply_rounded_corners(img, cfg.corner_radius)

                if opacity < 1.0:
                    img = self._apply_opacity(img, opacity)

                canvas.paste(img, (pos.x, pos.y), img)
                return

        # Fallback: colored rectangle with name
        if opacity < 1.0:
            card = Image.new('RGBA', (pos.size, pos.size), (0, 0, 0, 0))
            card_draw = ImageDraw.Draw(card)

            self._draw_rounded_rect(
                card_draw,
                0, 0, pos.size, pos.size,
                cfg.corner_radius,
                entity.color
            )

            name = entity.name[:cfg.name_max_length]
            text_color = get_contrast_color(entity.color)
            bbox = card_draw.textbbox((0, 0), name, font=self.font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = (pos.size - text_width) // 2
            text_y = (pos.size - text_height) // 2
            card_draw.text((text_x, text_y), name, fill=text_color, font=self.font)

            card = self._apply_opacity(card, opacity)
            canvas.paste(card, (pos.x, pos.y), card)
        else:
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
