"""Layout calculations for entity positioning."""

import math
from dataclasses import dataclass
from typing import List, Tuple
from abc import ABC, abstractmethod


@dataclass
class CellPosition:
    """Position and size of a single cell."""
    x: int
    y: int
    size: int


class BaseLayout(ABC):
    """Abstract base class for layouts."""

    @abstractmethod
    def calculate_positions(self, entity_count: int) -> List[CellPosition]:
        """Calculate positions for all entities."""
        pass


class GridLayout(BaseLayout):
    """Grid-based layout for entities."""

    def __init__(
        self,
        canvas_width: int,
        canvas_height: int,
        padding: int = 8,
        margin: int = 50,
        reserved_top: int = 0,
        reserved_bottom: int = 0
    ):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.padding = padding
        self.margin = margin
        self.reserved_top = reserved_top
        self.reserved_bottom = reserved_bottom

    def _calculate_grid_dimensions(self, entity_count: int) -> Tuple[int, int]:
        """Calculate optimal columns and rows."""
        cols = math.ceil(math.sqrt(entity_count))
        rows = math.ceil(entity_count / cols)
        return cols, rows

    def _calculate_cell_size(self, cols: int, rows: int) -> int:
        """Calculate cell size to fit all entities."""
        usable_height = (
            self.canvas_height
            - self.reserved_top
            - self.reserved_bottom
            - (self.margin * 2)
        )
        usable_width = self.canvas_width - (self.margin * 2)

        max_cell_width = (usable_width - (cols - 1) * self.padding) // cols
        max_cell_height = (usable_height - (rows - 1) * self.padding) // rows

        return min(max_cell_width, max_cell_height)

    def calculate_positions(self, entity_count: int) -> List[CellPosition]:
        """Calculate positions for all entities in a grid."""
        cols, rows = self._calculate_grid_dimensions(entity_count)
        cell_size = self._calculate_cell_size(cols, rows)

        grid_width = cols * cell_size + (cols - 1) * self.padding
        grid_height = rows * cell_size + (rows - 1) * self.padding

        offset_x = (self.canvas_width - grid_width) // 2
        offset_y = self.reserved_top + self.margin + (
            self.canvas_height - self.reserved_top - self.reserved_bottom - (self.margin * 2) - grid_height
        ) // 2

        positions = []
        for idx in range(entity_count):
            col = idx % cols
            row = idx // cols

            x = offset_x + col * (cell_size + self.padding)
            y = offset_y + row * (cell_size + self.padding)

            positions.append(CellPosition(x=x, y=y, size=cell_size))

        return positions
