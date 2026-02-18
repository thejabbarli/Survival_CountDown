"""Canvas/video configuration."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CanvasConfig:
    """Canvas/video dimensions and background."""
    width: int = 1080
    height: int = 1920
    background_color: str = "#1a1a2e"

    background_image: Optional[str] = None

    # Static gradient
    gradient_enabled: bool = True
    gradient_top: str = "#1a1a2e"
    gradient_bottom: str = "#0f0f1a"

    # Animated gradient (overrides static if enabled)
    animated_gradient: bool = False
    gradient_top_end: str = "#2e1a2e"
    gradient_bottom_end: str = "#1a0f1a"
    gradient_cycle_speed: float = 1.0

    # Vignette
    vignette_enabled: bool = True
    vignette_strength: float = 0.3

    # Special modes
    greenscreen: bool = False
    transparent: bool = False
