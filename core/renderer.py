import math
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
from .entity import Entity


class Renderer:
    """Renders frames of the survival game."""

    def __init__(
            self,
            width: int = 1080,
            height: int = 1920,
            background_color: str = "#1a1a2e",
            cell_padding: int = 8,
            show_counter: bool = True,
            counter_position: str = "top"
    ):
        self.width = width
        self.height = height
        self.background_color = background_color
        self.cell_padding = cell_padding
        self.show_counter = show_counter
        self.counter_position = counter_position
        self.animation_duration = 20  # frames for elimination animation

        self.font_large = None
        self.font_small = None
        self._load_fonts()

    def _load_fonts(self) -> None:
        """Load fonts for text rendering."""
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]

        for path in font_paths:
            try:
                self.font_large = ImageFont.truetype(path, 72)
                self.font_small = ImageFont.truetype(path, 18)
                return
            except (OSError, IOError):
                continue

        self.font_large = ImageFont.load_default()
        self.font_small = ImageFont.load_default()

    def _calculate_grid(self, entity_count: int) -> Tuple[int, int]:
        """Calculate grid dimensions."""
        cols = math.ceil(math.sqrt(entity_count))
        rows = math.ceil(entity_count / cols)
        return cols, rows

    def _get_cell_size(self, cols: int, rows: int) -> int:
        """Calculate cell size to fit all entities."""
        counter_height = 120 if self.show_counter else 0
        margin = 50

        usable_height = self.height - counter_height - (margin * 2)
        usable_width = self.width - (margin * 2)

        max_cell_width = (usable_width - (cols - 1) * self.cell_padding) // cols
        max_cell_height = (usable_height - (rows - 1) * self.cell_padding) // rows

        cell_size = min(max_cell_width, max_cell_height)
        return cell_size

    def _hex_to_gray(self, hex_color: str) -> str:
        """Convert hex color to grayscale."""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        gray = int(gray * 0.4)
        return f"#{gray:02x}{gray:02x}{gray:02x}"

    def _get_contrast_color(self, hex_color: str) -> str:
        """Return black or white depending on background brightness."""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return "black" if luminance > 0.5 else "white"

    def _get_entity_state(self, entity: Entity, frame_num: int) -> str:
        """
        Determine entity state at a specific frame.
        Returns: 'alive', 'eliminating', or 'gone'
        """
        # If entity was never eliminated, it's alive
        if entity.eliminated_at is None:
            return 'alive'

        # If current frame is before elimination, entity is still alive
        if frame_num < entity.eliminated_at:
            return 'alive'

        # If we're within the animation window after elimination
        frames_since = frame_num - entity.eliminated_at
        if frames_since < self.animation_duration:
            return 'eliminating'

        # Animation complete, entity is gone
        return 'gone'

    def _count_alive_at_frame(self, entities: List[Entity], frame_num: int) -> int:
        """Count how many entities are alive at a specific frame."""
        count = 0
        for entity in entities:
            state = self._get_entity_state(entity, frame_num)
            if state == 'alive':
                count += 1
        return count

    def render_frame(
            self,
            entities: List[Entity],
            frame_num: int
    ) -> Image.Image:
        """Render a single frame."""
        img = Image.new('RGB', (self.width, self.height), self.background_color)
        draw = ImageDraw.Draw(img)

        # Calculate grid layout
        cols, rows = self._calculate_grid(len(entities))
        cell_size = self._get_cell_size(cols, rows)

        # Calculate grid total size
        grid_width = cols * cell_size + (cols - 1) * self.cell_padding
        grid_height = rows * cell_size + (rows - 1) * self.cell_padding

        # Center the grid
        counter_height = 120 if self.show_counter else 0
        offset_x = (self.width - grid_width) // 2

        if self.counter_position == "top":
            offset_y = counter_height + (self.height - counter_height - grid_height) // 2
        else:
            offset_y = (self.height - counter_height - grid_height) // 2

        # Draw counter
        if self.show_counter:
            alive_count = self._count_alive_at_frame(entities, frame_num)
            counter_text = f"{alive_count} remaining"

            counter_y = 30 if self.counter_position == "top" else self.height - 100

            bbox = draw.textbbox((0, 0), counter_text, font=self.font_large)
            text_width = bbox[2] - bbox[0]
            text_x = (self.width - text_width) // 2

            draw.text((text_x, counter_y), counter_text, fill="white", font=self.font_large)

        # Draw each entity in its grid position
        for idx, entity in enumerate(entities):
            col = idx % cols
            row = idx // cols

            cell_x = offset_x + col * (cell_size + self.cell_padding)
            cell_y = offset_y + row * (cell_size + self.cell_padding)

            self._draw_entity(draw, entity, cell_x, cell_y, cell_size, frame_num)

        return img

    def _draw_entity(
            self,
            draw: ImageDraw.Draw,
            entity: Entity,
            cell_x: int,
            cell_y: int,
            cell_size: int,
            frame_num: int
    ) -> None:
        """Draw a single entity in its cell."""

        state = self._get_entity_state(entity, frame_num)

        if state == 'gone':
            # Don't draw anything
            return

        if state == 'eliminating':
            # Calculate animation progress
            frames_since = frame_num - entity.eliminated_at
            progress = frames_since / self.animation_duration  # 0 to 1

            # Shrink from 100% to 0%
            scale = 1 - progress
            new_size = int(cell_size * scale)

            if new_size < 4:
                return

            # Center the shrinking box in the cell
            x = cell_x + (cell_size - new_size) // 2
            y = cell_y + (cell_size - new_size) // 2

            # Draw grayed out rectangle
            gray = self._hex_to_gray(entity.color)
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

        else:  # state == 'alive'
            # Draw colored rectangle
            draw.rectangle(
                [cell_x, cell_y, cell_x + cell_size, cell_y + cell_size],
                fill=entity.color
            )

            # Draw entity name
            name = entity.name
            if len(name) > 12:
                name = name[:11] + "…"

            bbox = draw.textbbox((0, 0), name, font=self.font_small)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            text_x = cell_x + (cell_size - text_width) // 2
            text_y = cell_y + (cell_size - text_height) // 2

            text_color = self._get_contrast_color(entity.color)
            draw.text((text_x, text_y), name, fill=text_color, font=self.font_small)

    def render_winner_frame(self, winner: Entity) -> Image.Image:
        """Render the winner celebration frame."""
        img = Image.new('RGB', (self.width, self.height), self.background_color)
        draw = ImageDraw.Draw(img)

        # "WINNER!" text
        winner_text = "WINNER!"
        bbox = draw.textbbox((0, 0), winner_text, font=self.font_large)
        text_width = bbox[2] - bbox[0]
        text_x = (self.width - text_width) // 2
        draw.text((text_x, self.height // 4), winner_text, fill="#FFD700", font=self.font_large)

        # Winner box
        box_size = min(self.width, self.height) // 3
        box_x = (self.width - box_size) // 2
        box_y = (self.height - box_size) // 2

        draw.rectangle(
            [box_x, box_y, box_x + box_size, box_y + box_size],
            fill=winner.color
        )

        # Winner name inside box
        bbox = draw.textbbox((0, 0), winner.name, font=self.font_large)
        text_width = bbox[2] - bbox[0]
        text_x = (self.width - text_width) // 2
        text_y = box_y + (box_size // 2) - 30

        text_color = self._get_contrast_color(winner.color)
        draw.text((text_x, text_y), winner.name, fill=text_color, font=self.font_large)

        return img
