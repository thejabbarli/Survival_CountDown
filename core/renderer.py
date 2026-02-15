"""Frame rendering for survival game."""

from dataclasses import dataclass
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont

from .entity import Entity
from .layout import GridLayout, CellPosition
from .utils import hex_to_grayscale, get_contrast_color


@dataclass
class RenderConfig:
    """Configuration for rendering."""
    width: int = 1080
    height: int = 1920
    background_color: str = "#1a1a2e"
    cell_padding: int = 8
    show_counter: bool = True
    counter_position: str = "top"  # "top" or "bottom"
    animation_duration: int = 20  # frames for elimination animation
    font_size_large: int = 72
    font_size_small: int = 18


class FontLoader:
    """Handles font loading with fallbacks."""

    FONT_PATHS = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]

    @classmethod
    def load(cls, size: int) -> ImageFont.FreeTypeFont:
        """Load font with given size, falling back to default if needed."""
        for path in cls.FONT_PATHS:
            try:
                return ImageFont.truetype(path, size)
            except (OSError, IOError):
                continue
        return ImageFont.load_default()


class EntityState:
    """Determines entity visual state at a given frame."""

    ALIVE = "alive"
    ELIMINATING = "eliminating"
    GONE = "gone"

    @staticmethod
    def get_state(entity: Entity, frame_num: int, animation_duration: int) -> str:
        """Determine entity state at a specific frame."""
        if entity.eliminated_at is None:
            return EntityState.ALIVE

        if frame_num < entity.eliminated_at:
            return EntityState.ALIVE

        frames_since = frame_num - entity.eliminated_at
        if frames_since < animation_duration:
            return EntityState.ELIMINATING

        return EntityState.GONE

    @staticmethod
    def count_alive(entities: List[Entity], frame_num: int, animation_duration: int) -> int:
        """Count entities alive at a specific frame."""
        return sum(
            1 for e in entities
            if EntityState.get_state(e, frame_num, animation_duration) == EntityState.ALIVE
        )


class EntityDrawer:
    """Draws individual entities."""

    def __init__(self, font: ImageFont.FreeTypeFont, animation_duration: int):
        self.font = font
        self.animation_duration = animation_duration

    def draw(
        self,
        draw: ImageDraw.Draw,
        entity: Entity,
        position: CellPosition,
        frame_num: int
    ) -> None:
        """Draw an entity at the given position."""
        state = EntityState.get_state(entity, frame_num, self.animation_duration)

        if state == EntityState.GONE:
            return

        if state == EntityState.ELIMINATING:
            self._draw_eliminating(draw, entity, position, frame_num)
        else:
            self._draw_alive(draw, entity, position)

    def _draw_alive(
        self,
        draw: ImageDraw.Draw,
        entity: Entity,
        pos: CellPosition
    ) -> None:
        """Draw an alive entity."""
        # Draw colored rectangle
        draw.rectangle(
            [pos.x, pos.y, pos.x + pos.size, pos.y + pos.size],
            fill=entity.color
        )

        # Draw name
        name = entity.name[:11] + "…" if len(entity.name) > 12 else entity.name

        bbox = draw.textbbox((0, 0), name, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = pos.x + (pos.size - text_width) // 2
        text_y = pos.y + (pos.size - text_height) // 2

        text_color = get_contrast_color(entity.color)
        draw.text((text_x, text_y), name, fill=text_color, font=self.font)

    def _draw_eliminating(
        self,
        draw: ImageDraw.Draw,
        entity: Entity,
        pos: CellPosition,
        frame_num: int
    ) -> None:
        """Draw an entity being eliminated (shrinking with X)."""
        frames_since = frame_num - entity.eliminated_at
        progress = frames_since / self.animation_duration

        # Shrink
        scale = 1 - progress
        new_size = int(pos.size * scale)

        if new_size < 4:
            return

        # Center in cell
        x = pos.x + (pos.size - new_size) // 2
        y = pos.y + (pos.size - new_size) // 2

        # Draw gray rectangle
        gray = hex_to_grayscale(entity.color)
        draw.rectangle([x, y, x + new_size, y + new_size], fill=gray)

        # Draw red X
        line_width = max(2, new_size // 10)
        padding = new_size // 8
        draw.line(
            [(x + padding, y + padding), (x + new_size - padding, y + new_size - padding)],
            fill="#FF0000",
            width=line_width
        )
        draw.line(
            [(x + new_size - padding, y + padding), (x + padding, y + new_size - padding)],
            fill="#FF0000",
            width=line_width
        )


class Renderer:
    """Main renderer - composes frames."""

    def __init__(self, config: RenderConfig = None):
        self.config = config or RenderConfig()

        # Load fonts
        self.font_large = FontLoader.load(self.config.font_size_large)
        self.font_small = FontLoader.load(self.config.font_size_small)

        # Create entity drawer
        self.entity_drawer = EntityDrawer(
            font=self.font_small,
            animation_duration=self.config.animation_duration
        )

        # Calculate reserved space for counter
        self._counter_height = 120 if self.config.show_counter else 0

    def _create_layout(self, entity_count: int) -> GridLayout:
        """Create layout for the given entity count."""
        reserved_top = self._counter_height if self.config.counter_position == "top" else 0
        reserved_bottom = self._counter_height if self.config.counter_position == "bottom" else 0

        return GridLayout(
            canvas_width=self.config.width,
            canvas_height=self.config.height,
            padding=self.config.cell_padding,
            reserved_top=reserved_top,
            reserved_bottom=reserved_bottom
        )

    def _draw_counter(self, draw: ImageDraw.Draw, count: int) -> None:
        """Draw the remaining counter."""
        if not self.config.show_counter:
            return

        text = f"{count} remaining"

        bbox = draw.textbbox((0, 0), text, font=self.font_large)
        text_width = bbox[2] - bbox[0]
        text_x = (self.config.width - text_width) // 2

        if self.config.counter_position == "top":
            text_y = 30
        else:
            text_y = self.config.height - 100

        draw.text((text_x, text_y), text, fill="white", font=self.font_large)

    def render_frame(self, entities: List[Entity], frame_num: int) -> Image.Image:
        """Render a single game frame."""
        # Create canvas
        img = Image.new('RGB', (self.config.width, self.config.height), self.config.background_color)
        draw = ImageDraw.Draw(img)

        # Draw counter
        alive_count = EntityState.count_alive(
            entities, frame_num, self.config.animation_duration
        )
        self._draw_counter(draw, alive_count)

        # Calculate positions
        layout = self._create_layout(len(entities))
        positions = layout.calculate_positions(len(entities))

        # Draw entities
        for entity, position in zip(entities, positions):
            self.entity_drawer.draw(draw, entity, position, frame_num)

        return img

    def render_winner_frame(self, winner: Entity) -> Image.Image:
        """Render the winner celebration frame."""
        img = Image.new('RGB', (self.config.width, self.config.height), self.config.background_color)
        draw = ImageDraw.Draw(img)

        # "WINNER!" text
        winner_text = "WINNER!"
        bbox = draw.textbbox((0, 0), winner_text, font=self.font_large)
        text_width = bbox[2] - bbox[0]
        text_x = (self.config.width - text_width) // 2
        draw.text((text_x, self.config.height // 4), winner_text, fill="#FFD700", font=self.font_large)

        # Winner box
        box_size = min(self.config.width, self.config.height) // 3
        box_x = (self.config.width - box_size) // 2
        box_y = (self.config.height - box_size) // 2

        draw.rectangle(
            [box_x, box_y, box_x + box_size, box_y + box_size],
            fill=winner.color
        )

        # Winner name
        bbox = draw.textbbox((0, 0), winner.name, font=self.font_large)
        text_width = bbox[2] - bbox[0]
        text_x = (self.config.width - text_width) // 2
        text_y = box_y + (box_size // 2) - 30

        text_color = get_contrast_color(winner.color)
        draw.text((text_x, text_y), winner.name, fill=text_color, font=self.font_large)

        return img
