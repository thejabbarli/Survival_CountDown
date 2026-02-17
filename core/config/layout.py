"""Layout configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LayoutConfig:
    """Grid layout settings."""
    cell_padding: int = 8
    margin: int = 50
