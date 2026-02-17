"""Winner screen configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WinnerScreenConfig:
    """Winner celebration screen settings."""
    title_text: str = "WINNER!"
    title_color: str = "#FFD700"
    title_y_ratio: float = 0.25
    box_size_ratio: float = 0.33
    name_offset_y: int = -30
