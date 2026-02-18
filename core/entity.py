"""Entity - a single contestant in the survival game."""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class Entity:
    """A single contestant in the survival game."""
    id: str
    name: str
    color: str
    image_path: Optional[Path] = None
    alive: bool = True
    eliminated_at: Optional[int] = None

    def eliminate(self, frame: int) -> None:
        """Mark this entity as eliminated."""
        self.alive = False
        self.eliminated_at = frame

    def __repr__(self) -> str:
        status = "alive" if self.alive else f"eliminated@{self.eliminated_at}"
        return f"Entity({self.id}, {self.name}, {status})"
