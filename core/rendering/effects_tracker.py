"""Effects tracker for elimination-triggered visual effects."""

from typing import List, Optional, Set

from ..simulation import EliminationEvent
from ..config import RenderConfig


class EffectsTracker:
    """Tracks active effects based on elimination events.

    Manages timing for:
    - Screen flash on elimination
    - Counter pulse on elimination

    Usage:
        tracker = EffectsTracker(config)
        tracker.set_eliminations(events)

        # Each frame:
        flash = tracker.get_flash_progress(frame)
        pulse = tracker.get_pulse_progress(frame)
    """

    def __init__(self, config: RenderConfig):
        self.config = config
        self.elimination_frames: Set[int] = set()
        self.flash_duration = config.animation.flash_duration if config.animation.flash_on_elimination else 0
        self.pulse_duration = 15

    def set_eliminations(self, events: List[EliminationEvent]) -> None:
        """Register elimination events for effect timing."""
        self.elimination_frames = {e.frame for e in events}

    def get_flash_progress(self, frame: int) -> Optional[float]:
        """Get flash effect progress (0.0-1.0) or None if not flashing.

        Args:
            frame: Current frame number

        Returns:
            Progress from 0.0 (flash start) to 1.0 (flash end), or None
        """
        if self.flash_duration <= 0:
            return None

        for elim_frame in self.elimination_frames:
            if elim_frame <= frame < elim_frame + self.flash_duration:
                return (frame - elim_frame) / self.flash_duration

        return None

    def get_pulse_progress(self, frame: int) -> Optional[float]:
        """Get counter pulse progress (0.0-1.0) or None if not pulsing.

        Args:
            frame: Current frame number

        Returns:
            Progress from 0.0 (pulse start) to 1.0 (pulse end), or None
        """
        for elim_frame in self.elimination_frames:
            if elim_frame <= frame < elim_frame + self.pulse_duration:
                return (frame - elim_frame) / self.pulse_duration

        return None

    def is_elimination_frame(self, frame: int) -> bool:
        """Check if this exact frame is an elimination frame."""
        return frame in self.elimination_frames
