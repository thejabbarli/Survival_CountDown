"""Elimination animation strategies."""

from abc import ABC, abstractmethod
from PIL import ImageDraw

from .entity import Entity
from .layout import CellPosition
from .config import AnimationConfig
from .utils import hex_to_grayscale


class EliminationAnimation(ABC):
    """Base class for elimination animations."""

    @abstractmethod
    def draw(
            self,
            target: ImageDraw.Draw,
            entity: Entity,
            position: CellPosition,
            progress: float
    ) -> None:
        """
        Draw elimination animation.

        Args:
            target: PIL ImageDraw object
            entity: Entity being eliminated
            position: Cell position and size
            progress: Animation progress (0.0 to 1.0)
        """
        pass


class ShrinkWithXAnimation(EliminationAnimation):
    """Shrink and show red X animation."""

    def __init__(self, config: AnimationConfig):
        self.config = config

    def draw(
            self,
            target: ImageDraw.Draw,
            entity: Entity,
            position: CellPosition,
            progress: float
    ) -> None:
        scale = 1 - progress
        new_size = int(position.size * scale)

        if new_size < 4:
            return

        x = position.x + (position.size - new_size) // 2
        y = position.y + (position.size - new_size) // 2

        # Gray rectangle
        gray = hex_to_grayscale(entity.color)
        target.rectangle([x, y, x + new_size, y + new_size], fill=gray)

        # Red X
        line_width = max(2, int(new_size * self.config.elimination_x_width_ratio))
        padding = int(new_size * self.config.elimination_x_padding_ratio)

        target.line(
            [(x + padding, y + padding), (x + new_size - padding, y + new_size - padding)],
            fill=self.config.elimination_x_color,
            width=line_width
        )
        target.line(
            [(x + new_size - padding, y + padding), (x + padding, y + new_size - padding)],
            fill=self.config.elimination_x_color,
            width=line_width
        )


class FadeOutAnimation(EliminationAnimation):
    """Fade to background animation (alternative)."""

    def __init__(self, background_color: str = "#1a1a2e"):
        self.background_color = background_color

    def draw(
            self,
            target: ImageDraw.Draw,
            entity: Entity,
            position: CellPosition,
            progress: float
    ) -> None:
        # Blend entity color toward background
        # For simplicity, just reduce size without X
        scale = 1 - progress
        new_size = int(position.size * scale)

        if new_size < 4:
            return

        x = position.x + (position.size - new_size) // 2
        y = position.y + (position.size - new_size) // 2

        gray = hex_to_grayscale(entity.color, darken=0.3 + (0.5 * progress))
        target.rectangle([x, y, x + new_size, y + new_size], fill=gray)


class InstantRemoveAnimation(EliminationAnimation):
    """Instant removal, no animation."""

    def draw(
            self,
            target: ImageDraw.Draw,
            entity: Entity,
            position: CellPosition,
            progress: float
    ) -> None:
        # Draw nothing - instant removal
        pass
