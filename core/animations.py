"""Elimination animation strategies."""

from abc import ABC, abstractmethod
from typing import Optional
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

from .entity import Entity
from .layout import CellPosition
from .config import AnimationConfig
from .utils import hex_to_rgb


class EliminationAnimation(ABC):
    @abstractmethod
    def draw(
        self,
        target: ImageDraw.Draw,
        entity: Entity,
        position: CellPosition,
        progress: float,
        image_cache: Optional['ImageCache'] = None
    ) -> None:
        pass


class ModernFadeAnimation(EliminationAnimation):
    """Modern fade + shrink. No X. Keeps rounded corners."""

    def __init__(self, config: AnimationConfig, corner_radius: int = 12):
        self.config = config
        self.corner_radius = corner_radius

    def draw(
        self,
        target: ImageDraw.Draw,
        entity: Entity,
        position: CellPosition,
        progress: float,
        image_cache: Optional['ImageCache'] = None
    ) -> None:
        # Shrink
        scale = 1 - (progress * 0.5)  # Shrink to 50%
        new_size = int(position.size * scale)

        if new_size < 4:
            return

        # Center the shrunk entity
        x = position.x + (position.size - new_size) // 2
        y = position.y + (position.size - new_size) // 2

        # Fade opacity
        opacity = int(255 * (1 - progress))

        canvas = target._image

        # Get image or create colored square
        if entity.image_path is not None and image_cache is not None:
            img = image_cache.get(entity.image_path, position.size)
            if img is not None:
                # Desaturate
                img = self._desaturate(img, progress)
                # Resize
                if new_size != position.size:
                    img = img.resize((new_size, new_size), Image.Resampling.LANCZOS)
                # Apply rounded corners
                img = self._apply_rounded_corners(img, self.corner_radius)
                # Apply opacity
                img = self._apply_opacity(img, opacity)
                # Paste
                canvas.paste(img, (x, y), img)
                return

        # Fallback: colored rectangle
        color = hex_to_rgb(entity.color)
        # Desaturate color
        gray = int(0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2])
        faded_color = (
            int(color[0] + (gray - color[0]) * progress),
            int(color[1] + (gray - color[1]) * progress),
            int(color[2] + (gray - color[2]) * progress),
            opacity
        )

        # Create temp image for rounded rect with alpha
        temp = Image.new('RGBA', (new_size, new_size), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        self._draw_rounded_rect(temp_draw, 0, 0, new_size, new_size, self.corner_radius, faded_color)

        canvas.paste(temp, (x, y), temp)

    def _desaturate(self, img: Image.Image, amount: float) -> Image.Image:
        """Gradually remove color."""
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Split into RGB and A
        r, g, b, a = img.split()

        # Create grayscale
        gray = img.convert('L')

        # Blend RGB with gray based on amount
        from PIL import Image as PILImage
        gray_rgb = PILImage.merge('RGB', (gray, gray, gray))
        rgb = PILImage.merge('RGB', (r, g, b))

        blended = PILImage.blend(rgb, gray_rgb, amount)

        # Add alpha back
        r, g, b = blended.split()
        return PILImage.merge('RGBA', (r, g, b, a))

    def _apply_opacity(self, img: Image.Image, opacity: int) -> Image.Image:
        """Apply opacity to image."""
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        r, g, b, a = img.split()
        a = a.point(lambda x: int(x * opacity / 255))
        return Image.merge('RGBA', (r, g, b, a))

    def _apply_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        """Apply rounded corners."""
        if radius <= 0:
            return img

        size = img.size[0]
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        self._draw_rounded_rect(draw, 0, 0, size, size, radius, 255)

        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Apply mask to alpha
        r, g, b, a = img.split()
        a = Image.composite(a, Image.new('L', (size, size), 0), mask)
        return Image.merge('RGBA', (r, g, b, a))

    def _draw_rounded_rect(self, draw, x1, y1, x2, y2, radius, fill):
        """Draw rounded rectangle."""
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


class RedPulseFadeAnimation(EliminationAnimation):
    """Flash red, then fade out."""

    def __init__(self, config: AnimationConfig, corner_radius: int = 12):
        self.config = config
        self.corner_radius = corner_radius

    def draw(
        self,
        target: ImageDraw.Draw,
        entity: Entity,
        position: CellPosition,
        progress: float,
        image_cache: Optional['ImageCache'] = None
    ) -> None:
        # Phase 1 (0-0.3): Red tint
        # Phase 2 (0.3-1.0): Fade + shrink

        if progress < 0.3:
            red_amount = progress / 0.3
            scale = 1.0
            opacity = 255
        else:
            red_amount = 1 - ((progress - 0.3) / 0.7)
            scale = 1 - ((progress - 0.3) / 0.7) * 0.5
            opacity = int(255 * (1 - (progress - 0.3) / 0.7))

        new_size = int(position.size * scale)
        if new_size < 4:
            return

        x = position.x + (position.size - new_size) // 2
        y = position.y + (position.size - new_size) // 2

        canvas = target._image

        if entity.image_path is not None and image_cache is not None:
            img = image_cache.get(entity.image_path, position.size)
            if img is not None:
                # Apply red tint
                img = self._apply_red_tint(img, red_amount * 0.5)
                # Resize
                if new_size != position.size:
                    img = img.resize((new_size, new_size), Image.Resampling.LANCZOS)
                # Rounded corners
                img = self._apply_rounded_corners(img, self.corner_radius)
                # Opacity
                img = self._apply_opacity(img, opacity)
                canvas.paste(img, (x, y), img)
                return

        # Fallback
        color = hex_to_rgb(entity.color)
        tinted = (
            min(255, int(color[0] + (255 - color[0]) * red_amount * 0.5)),
            int(color[1] * (1 - red_amount * 0.3)),
            int(color[2] * (1 - red_amount * 0.3)),
            opacity
        )

        temp = Image.new('RGBA', (new_size, new_size), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        self._draw_rounded_rect(temp_draw, 0, 0, new_size, new_size, self.corner_radius, tinted)
        canvas.paste(temp, (x, y), temp)

    def _apply_red_tint(self, img: Image.Image, amount: float) -> Image.Image:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        r, g, b, a = img.split()
        r = r.point(lambda x: min(255, int(x + (255 - x) * amount)))
        g = g.point(lambda x: int(x * (1 - amount * 0.5)))
        b = b.point(lambda x: int(x * (1 - amount * 0.5)))

        return Image.merge('RGBA', (r, g, b, a))

    def _apply_opacity(self, img: Image.Image, opacity: int) -> Image.Image:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        r, g, b, a = img.split()
        a = a.point(lambda x: int(x * opacity / 255))
        return Image.merge('RGBA', (r, g, b, a))

    def _apply_rounded_corners(self, img: Image.Image, radius: int) -> Image.Image:
        if radius <= 0:
            return img
        size = img.size[0]
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        self._draw_rounded_rect(draw, 0, 0, size, size, radius, 255)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        r, g, b, a = img.split()
        a = Image.composite(a, Image.new('L', (size, size), 0), mask)
        return Image.merge('RGBA', (r, g, b, a))

    def _draw_rounded_rect(self, draw, x1, y1, x2, y2, radius, fill):
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


# Keep old one for compatibility
class ShrinkWithXAnimation(EliminationAnimation):
    """Old style - shrink with red X."""

    def __init__(self, config: AnimationConfig):
        self.config = config

    def draw(
        self,
        target: ImageDraw.Draw,
        entity: Entity,
        position: CellPosition,
        progress: float,
        image_cache: Optional['ImageCache'] = None
    ) -> None:
        scale = 1 - progress
        new_size = int(position.size * scale)

        if new_size < 4:
            return

        x = position.x + (position.size - new_size) // 2
        y = position.y + (position.size - new_size) // 2

        if entity.image_path is not None and image_cache is not None:
            gray_img = image_cache.get_grayscale(entity.image_path, position.size)
            if gray_img is not None:
                if new_size != position.size:
                    resized = gray_img.resize((new_size, new_size), Image.Resampling.LANCZOS)
                else:
                    resized = gray_img
                canvas = target._image
                canvas.paste(resized, (x, y), resized)
                self._draw_x(target, x, y, new_size)
                return

        # Fallback
        r, g, b = hex_to_rgb(entity.color)
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        gray_color = f"#{gray:02x}{gray:02x}{gray:02x}"
        target.rectangle([x, y, x + new_size, y + new_size], fill=gray_color)
        self._draw_x(target, x, y, new_size)

    def _draw_x(self, target: ImageDraw.Draw, x: int, y: int, size: int) -> None:
        line_width = max(2, int(size * self.config.elimination_x_width_ratio))
        padding = int(size * self.config.elimination_x_padding_ratio)
        target.line([(x + padding, y + padding), (x + size - padding, y + size - padding)],
                    fill=self.config.elimination_x_color, width=line_width)
        target.line([(x + size - padding, y + padding), (x + padding, y + size - padding)],
                    fill=self.config.elimination_x_color, width=line_width)


class FadeOutAnimation(EliminationAnimation):
    """Simple fade out."""

    def __init__(self, background_color: str = "#1a1a2e"):
        self.background_color = background_color

    def draw(self, target, entity, position, progress, image_cache=None):
        scale = 1 - progress
        new_size = int(position.size * scale)
        if new_size < 4:
            return
        x = position.x + (position.size - new_size) // 2
        y = position.y + (position.size - new_size) // 2

        r, g, b = hex_to_rgb(entity.color)
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        darken = 0.3 + (0.5 * progress)
        gray = int(gray * darken)
        gray_color = f"#{gray:02x}{gray:02x}{gray:02x}"
        target.rectangle([x, y, x + new_size, y + new_size], fill=gray_color)


class InstantRemoveAnimation(EliminationAnimation):
    """Just disappear."""
    def draw(self, target, entity, position, progress, image_cache=None):
        pass
