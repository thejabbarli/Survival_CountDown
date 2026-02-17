"""Easing functions for smooth animations."""

import math


def linear(t: float) -> float:
    """Linear (no easing)."""
    return t


def ease_out_cubic(t: float) -> float:
    """Fast start, slow end. Good for exits."""
    return 1 - pow(1 - t, 3)


def ease_in_cubic(t: float) -> float:
    """Slow start, fast end. Good for entries."""
    return t * t * t


def ease_in_out_cubic(t: float) -> float:
    """Slow start, fast middle, slow end. Smooth."""
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def ease_out_back(t: float, overshoot: float = 1.7) -> float:
    """Overshoot then settle. Bouncy feel."""
    c1 = overshoot
    c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)


def ease_out_elastic(t: float) -> float:
    """Spring/elastic effect."""
    if t == 0 or t == 1:
        return t
    c4 = (2 * math.pi) / 3
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def pulse(t: float, intensity: float = 0.3) -> float:
    """Heartbeat pulse. Returns scale multiplier."""
    if t < 0.2:
        return 1 + intensity * ease_out_cubic(t / 0.2)
    else:
        return 1 + intensity * (1 - ease_out_cubic((t - 0.2) / 0.8))


def flash_fade(t: float) -> float:
    """Flash that fades quickly. Returns opacity 0-1."""
    return 1 - ease_out_cubic(t)
