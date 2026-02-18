"""Effects tracker for elimination-triggered visual effects."""

from typing import List, Optional, Set

from ..simulation import EliminationEvent
from ..config import RenderConfig


class EffectsTracker:
    """Tracks active effects based on elimination events."""

    def __init__(self, config: RenderConfig):
        self.config = config
        self.elimination_frames: Set[int] = set()
        self.flash_duration = config.animation.flash_duration if config.animation.flash_on_elimination else 0
        self.pulse_duration = 15

    def set_eliminations(self, events: List[EliminationEvent]) -> None:
        self.elimination_frames = {e.frame for e in events}

    def get_flash_progress(self, frame: int) -> Optional[float]:
        if self.flash_duration <= 0:
            return None

        for elim_frame in self.elimination_frames:
            if elim_frame <= frame < elim_frame + self.flash_duration:
                return (frame - elim_frame) / self.flash_duration

        return None

    def get_pulse_progress(self, frame: int) -> Optional[float]:
        for elim_frame in self.elimination_frames:
            if elim_frame <= frame < elim_frame + self.pulse_duration:
                return (frame - elim_frame) / self.pulse_duration

        return None
    
    def is_elimination_frame(self, frame: int) -> bool:
        return frame in self.elimination_frames
