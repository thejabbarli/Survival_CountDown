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

Strategies (swappable behaviors):
- EliminationStrategy: WHO gets eliminated
- EliminationAnimation: HOW elimination looks

Configuration:
- RenderConfig: Aggregates all settings
- AudioConfig: Audio mode and settings
- SchedulerConfig: Timing settings
"""

# Core classes
from .entity import Entity
from .project import Project
from .entity_state import EntityState
from .simulation import Simulation, EliminationEvent, SimulationResult

# Scheduling
from .scheduler import (
    EliminationScheduler,
    IntervalScheduler,
    BeatSyncScheduler,
    FrameListScheduler,
    create_scheduler
)

# Strategies
from .strategies import (
    # Elimination
    EliminationStrategy,
    RandomElimination,
    create_elimination_strategy,
    # Animation
    EliminationAnimation,
    create_animation,
)

# Layout
from .layout import GridLayout, BaseLayout, CellPosition

# Config
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

# Rendering infrastructure
from .fonts import FontLoader
from .canvas import CanvasFactory

# Animation implementations (also available via strategies.animation)
from .animations import (
    ShrinkWithXAnimation,
    FadeOutAnimation,
    InstantRemoveAnimation,
    ModernFadeAnimation,
    RedPulseFadeAnimation
)

# Drawers
from .drawers import EntityDrawer, CounterDrawer, WinnerDrawer

# Rendering
from .rendering import (
    Renderer,
    GameFrameRenderer,
    WinnerFrameRenderer,
    RendererFactory,
    EffectsTracker
)

# Export
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

    # Strategies - Elimination
    'EliminationStrategy',
    'RandomElimination',
    'create_elimination_strategy',

    # Strategies - Animation
    'EliminationAnimation',
    'create_animation',
    'ShrinkWithXAnimation',
    'FadeOutAnimation',
    'InstantRemoveAnimation',
    'ModernFadeAnimation',
    'RedPulseFadeAnimation',

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
    'EntityDrawer',
    'CounterDrawer',
    'WinnerDrawer',
    'Renderer',
    'GameFrameRenderer',
    'WinnerFrameRenderer',
    'RendererFactory',
    'EffectsTracker',
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
