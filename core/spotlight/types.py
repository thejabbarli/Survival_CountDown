"""Spotlight system data types.

Core data structures for the spotlight animation system.
No dependencies on other spotlight modules.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional


class SpotlightState(Enum):
    """Visual state of an entity during spotlight sequence."""

    NORMAL = auto()  # No spotlight active, draw normally
    DIMMED = auto()  # Spotlight is elsewhere, reduce opacity
    ACTIVE = auto()  # Spotlight is on this entity (glow, scale up)
    LOCKED = auto()  # Spotlight locked on victim (stronger glow, about to die)


@dataclass
class SpotlightStop:
    """A single stop in the spotlight sequence.

    Represents the spotlight hovering on one entity for a duration.
    """
    entity_id: str
    start_frame: int
    end_frame: int
    is_victim: bool = False

    @property
    def duration(self) -> int:
        """Duration in frames (inclusive)."""
        return self.end_frame - self.start_frame + 1

    def contains_frame(self, frame: int) -> bool:
        """Check if this stop is active at given frame."""
        return self.start_frame <= frame <= self.end_frame


@dataclass
class SpotlightSequence:
    """Complete spotlight sequence for one elimination.

    Contains all stops (decoys + victim) and provides frame lookups.
    """
    stops: List[SpotlightStop] = field(default_factory=list)

    @property
    def total_frames(self) -> int:
        """Total duration of this sequence in frames."""
        if not self.stops:
            return 0
        return self.stops[-1].end_frame + 1

    @property
    def sound_frames(self) -> List[int]:
        """Frames where spotlight changes entity (for sound triggers)."""
        return [stop.start_frame for stop in self.stops]

    @property
    def victim_id(self) -> Optional[str]:
        """ID of the victim (last stop)."""
        if not self.stops:
            return None
        return self.stops[-1].entity_id

    def get_active_stop(self, frame: int) -> Optional[SpotlightStop]:
        """Get the stop active at given frame, or None."""
        for stop in self.stops:
            if stop.contains_frame(frame):
                return stop
        return None

    def get_active_entity_id(self, frame: int) -> Optional[str]:
        """Get entity ID that spotlight is on at given frame."""
        stop = self.get_active_stop(frame)
        return stop.entity_id if stop else None

    def is_locked(self, frame: int) -> bool:
        """Check if spotlight is locked on victim at this frame."""
        stop = self.get_active_stop(frame)
        return stop.is_victim if stop else False


@dataclass
class SpotlightEvent:
    """Event logged by simulation for renderer/audio.

    Links a spotlight sequence to its start frame in the video.
    """
    start_frame: int
    sequence: SpotlightSequence
    elimination_index: int

    @property
    def end_frame(self) -> int:
        """Frame when spotlight sequence ends (elimination begins)."""
        return self.start_frame + self.sequence.total_frames

    def contains_frame(self, frame: int) -> bool:
        """Check if this event is active at given frame."""
        return self.start_frame <= frame < self.end_frame

    def get_relative_frame(self, absolute_frame: int) -> int:
        """Convert absolute frame to sequence-relative frame."""
        return absolute_frame - self.start_frame
