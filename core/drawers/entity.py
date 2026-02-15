"""Entity drawer with modern card styling."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from ..entity import Entity
from ..layout import CellPosition
from ..config import EntityDisplayConfig
from ..utils import get_contrast_color
from ..animations import EliminationAnimation
from ..image_cache import get_image_cache
from ..idle_animation import get_idle_animator


class EntityDrawer:
    """Draws a single entity with modern card styling."""

    def __init__(
        self,
        entity_config: EntityDisplayConfig,
        font: ImageFont.FreeTypeFont,
        elimination_animation: EliminationAnimation,
        idle_enabled: bool = True
    ):
        self.entity_config = entity_config
        self.font = font
        self.elimination_animation = elimination_animation
        self.image_cache = get_image_cache()
        self.idle_enabled = idle_enabled
        self._shadow_cache = {}

    def _create_shadow(self, size: int) -> Image.Image:
        """Create cached drop shadow."""
        if size in self._shadow_cache:
            return self._shadow_cache[size]

        cfg = self.entity_config
        blur = cfg.shadow_blur
        opacity = cfg.shadow_opacity
        radius = cfg.corner_radius

        # Shadow needs extra space for blur
        shadow_size = size + blur * 4
        shadow = Image.new('RGBA', (shadow_size, shadow_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(shadow)

        # Draw rounded rect for shadow
        margin = blur * 2
        self._draw_rounded_rect(
            draw,
            margin, margin, margin + size, margin + size,
            radius,
            (0, 0, 0, opacity)
        )

        # Blur it
        shadow = shadow.filter(ImageFilter.GaussianBlur(blur))

        self._shadow_cache[size] = shadow
        return shadow

    def _draw_rounded_rect(self, draw, x1, y1, x2, y2, radius, fill):
        """Draw a rounded rectangle."""
        if radius <= 0:
            draw.rectangle([x1, y1, x2, y2], fill=fill)
            return

        radius = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)

        # Main rectangles
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)

        # Corners
        draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
        draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
        draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
        draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)

    def _create_rounded_mask(self, size: int, radius: int) -> Image.Image:
        """Create a rounded corner mask."""
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        self._draw_rounded_rect(draw, 0, 0, size, size, radius, 255)
        return mask

    def _apply_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        """Apply rounded corners to an image."""
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
            # Apply idle animation
            if self.idle_enabled:
                animator = get_idle_animator()
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
                self._draw_alive(target, entity, animated_pos)
            else:
                self._draw_alive(target, entity, position)

    def _truncate_name(self, name: str) -> str:
        max_len = self.entity_config.name_max_length
        if len(name) > max_len:
            return name[:max_len - 1] + "…"
        return name

    def _draw_alive(
        self,
        target: ImageDraw.Draw,
        entity: Entity,
        pos: CellPosition
    ) -> None:
        cfg = self.entity_config
        canvas = target._image

        # Draw shadow first (behind everything)
        if cfg.shadow_enabled:
            shadow = self._create_shadow(pos.size)
            shadow_offset = cfg.shadow_blur
            # Resize shadow if needed
            expected_shadow_size = pos.size + cfg.shadow_blur * 4
            if shadow.size[0] != expected_shadow_size:
                shadow = self._create_shadow(pos.size)

            shadow_x = pos.x - cfg.shadow_blur * 2 + 2  # Slight offset down-right
            shadow_y = pos.y - cfg.shadow_blur * 2 + 4
            canvas.paste(shadow, (shadow_x, shadow_y), shadow)


        # FOR ROUND CORNERS
        # Try image first
        # if entity.image_path is not None:
        #     img = self.image_cache.get(entity.image_path, pos.size)
        #     if img is not None:
        #         # Apply rounded corners
        #         if cfg.corner_radius > 0:
        #             img = self._apply_rounded_corners(img, cfg.corner_radius)
        #
        #         canvas.paste(img, (pos.x, pos.y), img)
        #
        #         # Draw subtle border
        #         self._draw_border(target, pos, cfg.corner_radius)
        #         return

        if entity.image_path is not None:
            img = self.image_cache.get(entity.image_path, pos.size)
            if img is not None:
                # Keep original flag shape - no rounding
                canvas.paste(img, (pos.x, pos.y), img)
                return

        # Fallback: colored rounded rectangle with name
        self._draw_rounded_rect(
            target,
            pos.x, pos.y, pos.x + pos.size, pos.y + pos.size,
            cfg.corner_radius,
            entity.color
        )

        # Draw border
        self._draw_border(target, pos, cfg.corner_radius)

        # Draw name
        name = self._truncate_name(entity.name)
        bbox = target.textbbox((0, 0), name, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = pos.x + (pos.size - text_width) // 2
        text_y = pos.y + (pos.size - text_height) // 2
        text_color = get_contrast_color(entity.color)
        target.text((text_x, text_y), name, fill=text_color, font=self.font)

    def _draw_border(self, target: ImageDraw.Draw, pos: CellPosition, radius: int) -> None:
        """Draw subtle border around entity."""
        # Thin white border with low opacity for definition
        border_color = (255, 255, 255, 40)  # Semi-transparent white

        if radius > 0:
            # Draw rounded border (just the outline)
            # We'll draw 4 arcs and 4 lines
            x1, y1 = pos.x, pos.y
            x2, y2 = pos.x + pos.size, pos.y + pos.size
            r = min(radius, pos.size // 2)

            # For simplicity, just draw a thin rounded rect on top
            # This creates subtle edge definition
            pass  # Skip complex border for now, shadow is enough
