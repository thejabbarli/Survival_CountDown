"""Font configuration."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FontConfig:
    """Font size settings."""
    size_large: int = 72
    size_small: int = 18
    custom_font_path: Optional[str] = None
