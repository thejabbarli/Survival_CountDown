"""Strategy pattern implementations for swappable behaviors.

This package contains all strategy interfaces and implementations:
- elimination: WHO gets eliminated (random, weighted, seeded, manual)
- animation: HOW elimination looks visually
- spotlight: HOW selection is shown (future)
"""

from .elimination import (
    EliminationStrategy,
    RandomElimination,
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
