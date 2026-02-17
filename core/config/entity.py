"""Entity display configuration.

NOTE: This is EntityDisplayConfig (how entities LOOK).
      This is NOT the same as core/entity.py (Entity class).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EntityDisplayConfig:
    """Entity display settings."""
    name_max_length: int = 12
    corner_radius: int = 12
    shadow_enabled: bool = True
    shadow_blur: int = 10
    shadow_opacity: int = 100
