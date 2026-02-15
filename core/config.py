"""Configuration classes - each focused on one concern."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CanvasConfig:
    """Canvas/video dimensions and background."""
    width: int = 1080
    height: int = 1920
    background_color: str = "#1a1a2e"


@dataclass(frozen=True)
class FontConfig:
    """Font size settings."""
    size_large: int = 72
    size_small: int = 18


@dataclass(frozen=True)
class LayoutConfig:
    """Grid layout settings."""
    cell_padding: int = 8
    margin: int = 50


@dataclass(frozen=True)
class CounterDisplayConfig:
    """Counter display settings."""
    enabled: bool = True
    position: str = "top"  # "top" or "bottom"
    color: str = "white"
    format_string: str = "{count} remaining"
    margin_top: int = 30
    margin_bottom: int = 100
    reserved_height: int = 120


@dataclass(frozen=True)
class AnimationConfig:
    """Animation timing and visuals."""
    elimination_duration: int = 20  # frames
    elimination_x_color: str = "#FF0000"
    elimination_x_width_ratio: float = 0.1
    elimination_x_padding_ratio: float = 0.125


@dataclass(frozen=True)
class EntityDisplayConfig:
    """Entity display settings."""
    name_max_length: int = 12


@dataclass(frozen=True)
class WinnerScreenConfig:
    """Winner celebration screen settings."""
    title_text: str = "WINNER!"
    title_color: str = "#FFD700"
    title_y_ratio: float = 0.25
    box_size_ratio: float = 0.33
    name_offset_y: int = -30


@dataclass
class RenderConfig:
    """
    Aggregates all config sections.
    Use this as the single entry point for configuration.
    """
    canvas: CanvasConfig = None
    font: FontConfig = None
    layout: LayoutConfig = None
    counter: CounterDisplayConfig = None
    animation: AnimationConfig = None
    entity: EntityDisplayConfig = None
    winner: WinnerScreenConfig = None

    def __post_init__(self) -> None:
        """Initialize with defaults if not provided."""
        if self.canvas is None:
            self.canvas = CanvasConfig()
        if self.font is None:
            self.font = FontConfig()
        if self.layout is None:
            self.layout = LayoutConfig()
        if self.counter is None:
            self.counter = CounterDisplayConfig()
        if self.animation is None:
            self.animation = AnimationConfig()
        if self.entity is None:
            self.entity = EntityDisplayConfig()
        if self.winner is None:
            self.winner = WinnerScreenConfig()
