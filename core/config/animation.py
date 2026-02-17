"""Animation configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AnimationConfig:
    """Animation timing and visuals."""
    elimination_duration: int = 20
    elimination_x_color: str = "#FF0000"
    elimination_x_width_ratio: float = 0.1
    elimination_x_padding_ratio: float = 0.125

    flash_on_elimination: bool = False
    flash_intensity: float = 0.15
    flash_duration: int = 5

    idle_enabled: bool = True
    idle_wave_speed: float = 0.05
    idle_wave_amount: float = 3.0
    idle_breathe_speed: float = 0.03
    idle_breathe_amount: float = 0.02
