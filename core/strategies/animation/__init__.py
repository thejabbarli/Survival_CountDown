"""Elimination animation strategies."""

from ...animations import (
    EliminationAnimation,
    ShrinkWithXAnimation,
    FadeOutAnimation,
    InstantRemoveAnimation,
    ModernFadeAnimation,
    RedPulseFadeAnimation
)


def create_animation(style: str, config, **kwargs) -> EliminationAnimation:
    """Factory function to create animation from config."""
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
    'EliminationAnimation',
    'ShrinkWithXAnimation',
    'FadeOutAnimation',
    'InstantRemoveAnimation',
    'ModernFadeAnimation',
    'RedPulseFadeAnimation',
    'create_animation',
]
