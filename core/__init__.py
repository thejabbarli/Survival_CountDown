"""Core module for Survival Countdown.

This module provides all the building blocks for generating
survival countdown videos.

Main classes:
- Entity: A single contestant
- Project: A themed collection of entities
- Simulation: Runs the survival game logic
- Renderer: Generates video frames
- Exporter: Saves frames to MP4
- AudioBuilder: Creates audio track

Scheduling (flexible timing):
- EliminationScheduler: Base class for timing strategies
- IntervalScheduler: Default interval-based timing
- BeatSyncScheduler: Sync eliminations to music beats
- FrameListScheduler: Custom frame list

Configuration:
- RenderConfig: Aggregates all settings
- AudioConfig: Audio mode and settings
- SchedulerConfig: Timing settings
"""

from .entity import Entity
from .project import Project
from .simulation import Simulation, EliminationEvent, SimulationResult, EntityState
from .scheduler import (
    EliminationScheduler,
    IntervalScheduler,
    BeatSyncScheduler,
    FrameListScheduler,
    create_scheduler
)
from .layout import GridLayout, BaseLayout, CellPosition
from .config import (
    RenderConfig,
    CanvasConfig,
    FontConfig,
    LayoutConfig,
    CounterDisplayConfig,
    AnimationConfig,
    EntityDisplayConfig,
    WinnerScreenConfig,
    AudioConfig,
    SchedulerConfig
)
from .fonts import FontLoader
from .canvas import CanvasFactory
from .animations import (
    EliminationAnimation,
    ShrinkWithXAnimation,
    FadeOutAnimation,
    InstantRemoveAnimation
)
from .drawers import EntityDrawer, CounterDrawer, WinnerDrawer
from .renderer import Renderer, GameFrameRenderer, WinnerFrameRenderer, RendererFactory
from .exporter import Exporter
from .image_cache import ImageCache, get_image_cache

# Audio subsystem
from .audio import (
    BeatDetector,
    BeatDetectionResult,
    detect_beats,
    AudioBuilder,
    AudioMode
)

__all__ = [
    # Core
    'Entity',
    'Project',
    'Simulation',
    'EliminationEvent',
    'SimulationResult',
    'EntityState',
    
    # Scheduling
    'EliminationScheduler',
    'IntervalScheduler',
    'BeatSyncScheduler',
    'FrameListScheduler',
    'create_scheduler',
    
    # Layout
    'GridLayout',
    'BaseLayout',
    'CellPosition',
    
    # Config
    'RenderConfig',
    'CanvasConfig',
    'FontConfig',
    'LayoutConfig',
    'CounterDisplayConfig',
    'AnimationConfig',
    'EntityDisplayConfig',
    'WinnerScreenConfig',
    'AudioConfig',
    'SchedulerConfig',
    
    # Rendering
    'FontLoader',
    'CanvasFactory',
    'EliminationAnimation',
    'ShrinkWithXAnimation',
    'FadeOutAnimation',
    'InstantRemoveAnimation',
    'EntityDrawer',
    'CounterDrawer',
    'WinnerDrawer',
    'Renderer',
    'GameFrameRenderer',
    'WinnerFrameRenderer',
    'RendererFactory',
    'Exporter',
    'ImageCache',
    'get_image_cache',
    
    # Audio
    'BeatDetector',
    'BeatDetectionResult',
    'detect_beats',
    'AudioBuilder',
    'AudioMode',
]
