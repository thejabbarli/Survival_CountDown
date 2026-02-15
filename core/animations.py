"""Elimination animation strategies."""

from abc import ABC, abstractmethod
from typing import Optional
from PIL import Image, ImageDraw

from .entity import Entity
from .layout import CellPosition
from .config import AnimationConfig
from .utils import hex_to_grayscale


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


class ShrinkWithXAnimation(EliminationAnimation):
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

        # Try grayscale image
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

        # Fallback: gray rectangle
        gray = hex_to_grayscale(entity.color)
        target.rectangle([x, y, x + new_size, y + new_size], fill=gray)
        self._draw_x(target, x, y, new_size)

    def _draw_x(self, target: ImageDraw.Draw, x: int, y: int, size: int) -> None:
        line_width = max(2, int(size * self.config.elimination_x_width_ratio))
        padding = int(size * self.config.elimination_x_padding_ratio)
        target.line([(x + padding, y + padding), (x + size - padding, y + size - padding)],
                    fill=self.config.elimination_x_color, width=line_width)
        target.line([(x + size - padding, y + padding), (x + padding, y + size - padding)],
                    fill=self.config.elimination_x_color, width=line_width)


class FadeOutAnimation(EliminationAnimation):
    def __init__(self, background_color: str = "#1a1a2e"):
        self.background_color = background_color

    def draw(self, target, entity, position, progress, image_cache=None):
        scale = 1 - progress
        new_size = int(position.size * scale)
        if new_size < 4:
            return
        x = position.x + (position.size - new_size) // 2
        y = position.y + (position.size - new_size) // 2
        gray = hex_to_grayscale(entity.color, darken=0.3 + (0.5 * progress))
        target.rectangle([x, y, x + new_size, y + new_size], fill=gray)


class InstantRemoveAnimation(EliminationAnimation):
    def draw(self, target, entity, position, progress, image_cache=None):
        pass
