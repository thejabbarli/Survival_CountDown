"""Elimination animation strategies.

Animations control HOW an entity visually disappears after being eliminated.

Available animations:
- ModernFadeAnimation: Smooth fade + shrink, modern look (no X)
- ShrinkWithXAnimation: Classic shrink with red X overlay
- FadeOutAnimation: Simple fade to transparent
- InstantRemoveAnimation: Immediate disappearance (no animation)
- RedPulseFadeAnimation: Red pulse effect then fade

Usage:
    from core.strategies.animation import ModernFadeAnimation, create_animation

    # Direct instantiation
    animation = ModernFadeAnimation(config, corner_radius=12)

    # Or via factory
    animation = create_animation("modern_fade", config)
"""

# Import EVERYTHING from the original animations.py
# This includes the base class AND all implementations
from ...animations import (
    EliminationAnimation,  # Base class
    ShrinkWithXAnimation,
    FadeOutAnimation,
    InstantRemoveAnimation,
    ModernFadeAnimation,
    RedPulseFadeAnimation
)


def create_animation(style: str, config, **kwargs) -> EliminationAnimation:
    """Factory function to create animation from config.

    Args:
        style: Animation style name
        config: AnimationConfig instance
        **kwargs: Additional parameters (e.g., corner_radius)

    Returns:
        Configured EliminationAnimation instance
    """
    animations = {
        "modern_fade": ModernFadeAnimation,
        "shrink_x": ShrinkWithXAnimation,
        "fade_out": FadeOutAnimation,
        "instant": InstantRemoveAnimation,
        "red_pulse": RedPulseFadeAnimation,
    }

    animation_class = animations.get(style)
    if animation_class is None:
        raise ValueError(f"Unknown animation style: {style}. Available: {list(animations.keys())}")

    return animation_class(config, **kwargs)


__all__ = [
    # Base
    'EliminationAnimation',

    # Implementations
    'ShrinkWithXAnimation',
    'FadeOutAnimation',
    'InstantRemoveAnimation',
    'ModernFadeAnimation',
    'RedPulseFadeAnimation',

    # Factory
    'create_animation',
]
