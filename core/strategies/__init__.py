"""Strategy pattern implementations for swappable behaviors."""

from .elimination import (
    EliminationStrategy,
    RandomElimination,
    ManualElimination,
    create_elimination_strategy
)

from .animation import (
    EliminationAnimation,
    ShrinkWithXAnimation,
    FadeOutAnimation,
    InstantRemoveAnimation,
    ModernFadeAnimation,
    RedPulseFadeAnimation,
    create_animation
)

__all__ = [
    # Elimination
    'EliminationStrategy',
    'RandomElimination',
    'ManualElimination',
    'create_elimination_strategy',
    
    # Animation
    'EliminationAnimation',
    'ShrinkWithXAnimation',
    'FadeOutAnimation',
    'InstantRemoveAnimation',
    'ModernFadeAnimation',
    'RedPulseFadeAnimation',
    'create_animation',
]
