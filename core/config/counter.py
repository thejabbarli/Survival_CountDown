"""Counter display configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CounterDisplayConfig:
    """Counter display settings."""
    enabled: bool = True
    position: str = "top"
    color: str = "white"
    format_string: str = "{count} remaining"
    margin_top: int = 30
    margin_bottom: int = 100
    reserved_height: int = 120
    pulse_on_elimination: bool = True
    pulse_scale: float = 1.3
