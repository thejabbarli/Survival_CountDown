"""Core module for Survival Countdown.

This module provides all the building blocks for generating
survival countdown videos.
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
    EliminationStrategy,
    RandomElimination,
    create_elimination_strategy,
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

# Animation implementations
from .animations import (
    ShrinkWithXAnimation,
    FadeOutAnimation,
    InstantRemoveAnimation,
    ModernFadeAnimation,
    RedPulseFadeAnimation
)

# Idle animation
from .idle_animation import IdleAnimator, get_idle_animator, set_idle_animator

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

# Audio
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

    # Strategies
    'EliminationStrategy',
    'RandomElimination',
    'create_elimination_strategy',
    'EliminationAnimation',
    'create_animation',
    'ShrinkWithXAnimation',
    'FadeOutAnimation',
    'InstantRemoveAnimation',
    'ModernFadeAnimation',
    'RedPulseFadeAnimation',

    # Idle Animation
    'IdleAnimator',
    'get_idle_animator',
    'set_idle_animator',

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
