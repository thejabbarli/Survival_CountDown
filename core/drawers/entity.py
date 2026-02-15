"""Entity drawer - displays a single entity."""

from PIL import ImageDraw, ImageFont

from ..entity import Entity
from ..layout import CellPosition
from ..config import EntityDisplayConfig
from ..utils import get_contrast_color
from ..animations import EliminationAnimation


class EntityDrawer:
    """Draws a single entity in its cell."""

    def __init__(
        self,
        entity_config: EntityDisplayConfig,
        font: ImageFont.FreeTypeFont,
        elimination_animation: EliminationAnimation
    ):
        self.entity_config = entity_config
        self.font = font
        self.elimination_animation = elimination_animation

    def draw(
        self,
        target: ImageDraw.Draw,
        entity: Entity,
        position: CellPosition,
        state: str,
        progress: float = 0.0
    ) -> None:
        """
        Draw entity based on its state.

        Args:
            target: PIL ImageDraw object to draw on
            entity: The entity to draw
            position: Cell position and size
            state: "alive", "eliminating", or "gone"
            progress: Animation progress (0.0 to 1.0) for eliminating state
        """
        if state == "gone":
            return

        if state == "eliminating":
            self.elimination_animation.draw(target, entity, position, progress)
        else:
            self._draw_alive(target, entity, position)

    def _truncate_name(self, name: str) -> str:
        """Truncate name if too long."""
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
        """Draw alive entity as colored rectangle with name."""
        target.rectangle(
            [pos.x, pos.y, pos.x + pos.size, pos.y + pos.size],
            fill=entity.color
        )

        name = self._truncate_name(entity.name)

        bbox = target.textbbox((0, 0), name, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = pos.x + (pos.size - text_width) // 2
        text_y = pos.y + (pos.size - text_height) // 2

        text_color = get_contrast_color(entity.color)
        target.text((text_x, text_y), name, fill=text_color, font=self.font)
