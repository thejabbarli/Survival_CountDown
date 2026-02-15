"""Elimination scheduling strategies.

This module provides flexible timing for eliminations.
Instead of hardcoding timing logic, we have pluggable schedulers.

Usage:
    # Interval-based (default)
    scheduler = IntervalScheduler(config, entity_count=64)
    
    # Beat-synced
    scheduler = BeatSyncScheduler(beat_frames=[60, 90, 120, ...])
    
    # Custom frames
    scheduler = FrameListScheduler(frames=[30, 60, 90, ...])
    
    # Get elimination frames
    frames = scheduler.get_elimination_frames()
"""

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
    """
    Default interval-based scheduler.
    Supports sudden death mode (slower intervals when fewer remain).
    """
    
    def __init__(
        self,
        entity_count: int,
        config: Optional[SchedulerConfig] = None
    ):
        self.entity_count = entity_count
        self.config = config or SchedulerConfig()
        self._cached_frames: Optional[List[int]] = None
    
    def _calculate_interval(self, remaining: int) -> int:
        """
        Calculate elimination interval based on remaining entities.
        Fewer remaining = longer interval (slower, more dramatic).
        """
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
        """Calculate all elimination frame numbers."""
        if self._cached_frames is not None:
            return self._cached_frames
        
        frames = []
        current_frame = self.config.initial_delay
        remaining = self.entity_count
        
        # We need (entity_count - 1) eliminations to get to 1 winner
        for _ in range(self.entity_count - 1):
            frames.append(current_frame)
            remaining -= 1
            interval = self._calculate_interval(remaining)
            current_frame += interval
        
        self._cached_frames = frames
        return frames
    
    def get_total_frames(self, winner_celebration_frames: int = 120) -> int:
        """Total frames = last elimination + winner celebration."""
        frames = self.get_elimination_frames()
        if not frames:
            return winner_celebration_frames
        return frames[-1] + winner_celebration_frames


class FrameListScheduler(EliminationScheduler):
    """
    Scheduler that uses a pre-defined list of frames.
    Useful for beat sync, custom timing, or testing.
    """
    
    def __init__(self, frames: List[int]):
        if not frames:
            raise ValueError("Frame list cannot be empty")
        self.frames = sorted(frames)
    
    def get_elimination_frames(self) -> List[int]:
        return self.frames.copy()
    
    def get_total_frames(self, winner_celebration_frames: int = 120) -> int:
        return self.frames[-1] + winner_celebration_frames


class BeatSyncScheduler(EliminationScheduler):
    """
    Scheduler that syncs eliminations to detected beats.
    Wraps beat detection results into a scheduler.
    """
    
    def __init__(
        self,
        beat_frames: List[int],
        entity_count: int,
        use_every_nth: int = 1,
        start_offset_frames: int = 0
    ):
        """
        Args:
            beat_frames: Frame numbers where beats occur
            entity_count: Number of entities (determines how many beats to use)
            use_every_nth: Use every Nth beat (1 = all, 2 = every other)
            start_offset_frames: Skip this many frames before first beat
        """
        self.raw_beats = beat_frames
        self.entity_count = entity_count
        self.use_every_nth = max(1, use_every_nth)
        self.start_offset_frames = start_offset_frames
        self._cached_frames: Optional[List[int]] = None
    
    def get_elimination_frames(self) -> List[int]:
        if self._cached_frames is not None:
            return self._cached_frames
        
        # Filter beats after start offset
        beats = [b for b in self.raw_beats if b >= self.start_offset_frames]
        
        # Take every Nth beat
        if self.use_every_nth > 1:
            beats = beats[::self.use_every_nth]
        
        # We need exactly (entity_count - 1) elimination frames
        needed = self.entity_count - 1
        
        if len(beats) >= needed:
            # Enough beats — use first N
            frames = beats[:needed]
        else:
            # Not enough beats — we need to handle this
            # Option 1: Loop the beat pattern
            # Option 2: Extend with estimated interval
            # Going with Option 2 for now (more predictable)
            frames = beats.copy()
            
            if len(beats) >= 2:
                # Estimate interval from existing beats
                avg_interval = (beats[-1] - beats[0]) / (len(beats) - 1)
            else:
                avg_interval = 30  # fallback
            
            last_frame = beats[-1] if beats else self.start_offset_frames
            while len(frames) < needed:
                last_frame += int(avg_interval)
                frames.append(last_frame)
        
        self._cached_frames = frames
        return frames
    
    def get_total_frames(self, winner_celebration_frames: int = 120) -> int:
        frames = self.get_elimination_frames()
        if not frames:
            return winner_celebration_frames
        return frames[-1] + winner_celebration_frames
    
    @property
    def beat_count(self) -> int:
        """Number of raw beats detected."""
        return len(self.raw_beats)
    
    @property
    def usable_beat_count(self) -> int:
        """Number of beats after filtering."""
        beats = [b for b in self.raw_beats if b >= self.start_offset_frames]
        if self.use_every_nth > 1:
            beats = beats[::self.use_every_nth]
        return len(beats)


def create_scheduler(
    entity_count: int,
    config: Optional[SchedulerConfig] = None,
    beat_frames: Optional[List[int]] = None,
    custom_frames: Optional[List[int]] = None
) -> EliminationScheduler:
    """
    Factory function to create appropriate scheduler.
    
    Priority:
    1. custom_frames — if provided, use FrameListScheduler
    2. beat_frames — if provided, use BeatSyncScheduler  
    3. Default to IntervalScheduler
    """
    if custom_frames is not None:
        return FrameListScheduler(custom_frames)
    
    if beat_frames is not None:
        cfg = config or SchedulerConfig()
        return BeatSyncScheduler(
            beat_frames=beat_frames,
            entity_count=entity_count,
            start_offset_frames=cfg.initial_delay
        )
    
    return IntervalScheduler(entity_count, config)
