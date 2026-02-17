"""Idle animations - makes entities feel alive."""

import math
from typing import Tuple, Optional


class IdleAnimator:
    """Generates gentle movement for entities."""

    def __init__(
            self,
            wave_speed: float = 0.05,
            wave_amount: float = 3.0,
            breathe_speed: float = 0.03,
            breathe_amount: float = 0.02,
    ):
        self.wave_speed = wave_speed
        self.wave_amount = wave_amount
        self.breathe_speed = breathe_speed
        self.breathe_amount = breathe_amount

    def get_offset(self, frame: int, entity_index: int, total_entities: int) -> Tuple[float, float]:
        """Get x, y offset for an entity at this frame."""
        phase = entity_index / max(1, total_entities) * math.pi * 2
        dx = math.sin(frame * self.wave_speed + phase) * self.wave_amount
        dy = math.sin(frame * self.wave_speed * 0.7 + phase * 1.3) * self.wave_amount * 0.5
        return dx, dy

    def get_scale(self, frame: int, entity_index: int, total_entities: int) -> float:
        """Get scale multiplier for breathing effect."""
        phase = entity_index / max(1, total_entities) * math.pi * 2
        breath = math.sin(frame * self.breathe_speed + phase) * self.breathe_amount
        return 1.0 + breath


# Global instance (legacy support)
_idle_animator: Optional[IdleAnimator] = None


def get_idle_animator() -> IdleAnimator:
    """Get the global IdleAnimator instance."""
    global _idle_animator
    if _idle_animator is None:
        _idle_animator = IdleAnimator()
    return _idle_animator


def set_idle_animator(animator: IdleAnimator) -> None:
    """Set the global IdleAnimator instance."""
    global _idle_animator
    _idle_animator = animator
