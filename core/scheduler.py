"""Elimination scheduling strategies."""

from abc import ABC, abstractmethod
from typing import List, Optional
from .config import SchedulerConfig


class EliminationScheduler(ABC):
    """Abstract base class for elimination timing strategies."""
    
    @abstractmethod
    def get_elimination_frames(self) -> List[int]:
        """Return list of frame numbers when eliminations should occur."""
        pass
    
    @abstractmethod
    def get_total_frames(self, winner_celebration_frames: int = 120) -> int:
        """Return total frame count including winner celebration."""
        pass


class IntervalScheduler(EliminationScheduler):
    """Default interval-based scheduler."""
    
    def __init__(
        self,
        entity_count: int,
        config: Optional[SchedulerConfig] = None
    ):
        self.entity_count = entity_count
        self.config = config or SchedulerConfig()
        self._cached_frames: Optional[List[int]] = None
    
    def _calculate_interval(self, remaining: int) -> int:
        cfg = self.config
        base = cfg.elimination_interval
        
        if not cfg.sudden_death_enabled:
            return base
        
        if remaining <= cfg.sudden_death_threshold_2:
            return base * cfg.sudden_death_multiplier_2
        elif remaining <= cfg.sudden_death_threshold_1:
            return base * cfg.sudden_death_multiplier_1
        else:
            return base
    
    def get_elimination_frames(self) -> List[int]:
        if self._cached_frames is not None:
            return self._cached_frames
        
        frames = []
        current_frame = self.config.initial_delay
        remaining = self.entity_count
        
        for _ in range(self.entity_count - 1):
            frames.append(current_frame)
            remaining -= 1
            interval = self._calculate_interval(remaining)
            current_frame += interval
        
        self._cached_frames = frames
        return frames
    
    def get_total_frames(self, winner_celebration_frames: int = 120) -> int:
        frames = self.get_elimination_frames()
        if not frames:
            return winner_celebration_frames
        return frames[-1] + winner_celebration_frames


class BeatSyncScheduler(EliminationScheduler):
    """Sync eliminations to music beats."""
    
    def __init__(
        self,
        beat_frames: List[int],
        entity_count: int
    ):
        self.beat_frames = beat_frames
        self.entity_count = entity_count
    
    def get_elimination_frames(self) -> List[int]:
        needed = self.entity_count - 1
        return self.beat_frames[:needed]
    
    def get_total_frames(self, winner_celebration_frames: int = 120) -> int:
        frames = self.get_elimination_frames()
        if not frames:
            return winner_celebration_frames
        return frames[-1] + winner_celebration_frames


class FrameListScheduler(EliminationScheduler):
    """Custom frame list scheduler."""
    
    def __init__(self, frames: List[int]):
        self.frames = frames
    
    def get_elimination_frames(self) -> List[int]:
        return self.frames
    
    def get_total_frames(self, winner_celebration_frames: int = 120) -> int:
        if not self.frames:
            return winner_celebration_frames
        return self.frames[-1] + winner_celebration_frames


def create_scheduler(
    mode: str,
    entity_count: int,
    config: Optional[SchedulerConfig] = None,
    beat_frames: Optional[List[int]] = None,
    custom_frames: Optional[List[int]] = None
) -> EliminationScheduler:
    """Factory function to create scheduler."""
    if mode == "beat_sync" and beat_frames:
        return BeatSyncScheduler(beat_frames, entity_count)
    elif mode == "custom" and custom_frames:
        return FrameListScheduler(custom_frames)
    else:
        return IntervalScheduler(entity_count, config)
