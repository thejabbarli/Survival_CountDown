"""Idle animations - makes entities feel alive."""

import math
from typing import Tuple


class IdleAnimator:
    """
    Generates gentle movement for entities.
    Each entity sways slightly, offset by position for wave effect.
    """

    def __init__(
            self,
            wave_speed: float = 0.05,  # How fast the wave moves
            wave_amount: float = 3.0,  # Pixels of movement
            breathe_speed: float = 0.03,  # How fast breathing cycle
            breathe_amount: float = 0.02,  # Scale change (0.02 = 2%)
    ):
        self.wave_speed = wave_speed
        self.wave_amount = wave_amount
        self.breathe_speed = breathe_speed
        self.breathe_amount = breathe_amount

    def get_offset(self, frame: int, entity_index: int, total_entities: int) -> Tuple[float, float]:
        """
        Get x, y offset for an entity at this frame.
        Returns (dx, dy) in pixels.
        """
        # Phase offset based on position (creates wave rolling across grid)
        phase = entity_index / max(1, total_entities) * math.pi * 2

        # Horizontal sway
        dx = math.sin(frame * self.wave_speed + phase) * self.wave_amount

        # Vertical bob (different frequency for organic feel)
        dy = math.sin(frame * self.wave_speed * 0.7 + phase * 1.3) * self.wave_amount * 0.5

        return dx, dy

    def get_scale(self, frame: int, entity_index: int, total_entities: int) -> float:
        """
        Get scale multiplier for breathing effect.
        Returns scale (1.0 = normal, 1.02 = 2% bigger).
        """
        phase = entity_index / max(1, total_entities) * math.pi * 2

        # Breathing - slow pulse
        breath = math.sin(frame * self.breathe_speed + phase) * self.breathe_amount

        return 1.0 + breath


# Global instance with defaults
_idle_animator = None


def get_idle_animator() -> IdleAnimator:
    global _idle_animator
    if _idle_animator is None:
        _idle_animator = IdleAnimator()
    return _idle_animator


def set_idle_animator(animator: IdleAnimator) -> None:
    global _idle_animator
    _idle_animator = animator
