"""Render configuration - aggregates all visual configs."""

from dataclasses import dataclass, field

from .canvas import CanvasConfig
from .font import FontConfig
from .layout import LayoutConfig
from .counter import CounterDisplayConfig
from .animation import AnimationConfig
from .entity import EntityDisplayConfig
from .winner import WinnerScreenConfig


@dataclass
class RenderConfig:
    """Aggregates all rendering configuration."""
    canvas: CanvasConfig = field(default_factory=CanvasConfig)
    font: FontConfig = field(default_factory=FontConfig)
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    counter: CounterDisplayConfig = field(default_factory=CounterDisplayConfig)
    animation: AnimationConfig = field(default_factory=AnimationConfig)
    entity: EntityDisplayConfig = field(default_factory=EntityDisplayConfig)
    winner: WinnerScreenConfig = field(default_factory=WinnerScreenConfig)
