"""Spotlight visual effect calculations.

Calculates opacity, scale, and glow based on spotlight state.
Used by EntityDrawer to modify entity appearance.
"""

import math
from typing import Tuple, Optional
from dataclasses import dataclass

from .types import SpotlightState
from .config import SpotlightVisualConfig


@dataclass
class SpotlightVisuals:
    """Visual parameters for drawing an entity under spotlight."""
    opacity: float  # 0.0 - 1.0
    scale: float  # 1.0 = normal size
    glow_radius: int  # 0 = no glow
    glow_color: str  # hex color
    glow_opacity: int  # 0-255


def calculate_spotlight_visuals(
        state: SpotlightState,
        config: SpotlightVisualConfig,
        frame: int = 0
) -> SpotlightVisuals:
    """Calculate visual parameters for a spotlight state.

    Args:
        state: Current spotlight state of entity
        config: Visual configuration
        frame: Current frame (for animations like pulse)

    Returns:
        SpotlightVisuals with all parameters
    """
    if state == SpotlightState.NORMAL:
        return SpotlightVisuals(
            opacity=1.0,
            scale=1.0,
            glow_radius=0,
            glow_color=config.glow_color,
            glow_opacity=0
        )

    elif state == SpotlightState.DIMMED:
        return SpotlightVisuals(
            opacity=config.dim_opacity,
            scale=1.0,
            glow_radius=0,
            glow_color=config.glow_color,
            glow_opacity=0
        )

    elif state == SpotlightState.ACTIVE:
        return SpotlightVisuals(
            opacity=1.0,
            scale=config.active_scale,
            glow_radius=config.glow_radius if config.glow_enabled else 0,
            glow_color=config.glow_color,
            glow_opacity=config.glow_opacity
        )

    elif state == SpotlightState.LOCKED:
        # Subtle pulse effect on lock
        pulse = 1.0 + 0.02 * math.sin(frame * 0.3)

        return SpotlightVisuals(
            opacity=1.0,
            scale=config.locked_scale * pulse,
            glow_radius=int(config.glow_radius * 1.3) if config.glow_enabled else 0,
            glow_color=config.glow_color,
            glow_opacity=min(255, int(config.glow_opacity * 1.2))
        )

    # Fallback
    return SpotlightVisuals(
        opacity=1.0,
        scale=1.0,
        glow_radius=0,
        glow_color=config.glow_color,
        glow_opacity=0
    )


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple.

    Args:
        hex_color: Color like "#FFD700" or "FFD700"

    Returns:
        (R, G, B) tuple
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color.

    Args:
        r, g, b: Color components 0-255

    Returns:
        Hex string like "#FFD700"
    """
    return f"#{r:02x}{g:02x}{b:02x}"
