"""Spotlight state tracker. DEBUG VERSION"""

from typing import Dict, List, Optional, Set

from .types import SpotlightState, SpotlightSequence, SpotlightEvent


class SpotlightTracker:
    """Tracks spotlight state across all frames."""

    def __init__(self):
        self._events: List[SpotlightEvent] = []
        self._sound_frames: Set[int] = set()
        self._lock_frames: Set[int] = set()
        print(f"[DEBUG TRACKER] SpotlightTracker created")

    def set_events(self, events: List[SpotlightEvent]) -> None:
        """Register spotlight events from simulation."""
        self._events = events
        print(f"[DEBUG TRACKER] set_events called with {len(events)} events")
        for i, ev in enumerate(events[:3]):  # Print first 3
            print(f"[DEBUG TRACKER]   event {i}: start={ev.start_frame}, end={ev.end_frame}")
        if len(events) > 3:
            print(f"[DEBUG TRACKER]   ... and {len(events) - 3} more")
        self._build_sound_cache()

    def _build_sound_cache(self) -> None:
        """Pre-compute frames that need sound triggers."""
        self._sound_frames.clear()
        self._lock_frames.clear()

        for event in self._events:
            for stop in event.sequence.stops:
                absolute_frame = event.start_frame + stop.start_frame
                self._sound_frames.add(absolute_frame)

                if stop.is_victim:
                    self._lock_frames.add(absolute_frame)

    def get_active_event(self, frame: int) -> Optional[SpotlightEvent]:
        """Get the spotlight event active at given frame."""
        for event in self._events:
            if event.contains_frame(frame):
                return event
        return None

    def get_spotlit_entity(self, frame: int) -> Optional[str]:
        """Get entity ID currently under spotlight."""
        event = self.get_active_event(frame)
        if event is None:
            return None

        relative_frame = event.get_relative_frame(frame)
        return event.sequence.get_active_entity_id(relative_frame)

    def is_locked(self, frame: int) -> bool:
        """Check if spotlight is locked on victim at this frame."""
        event = self.get_active_event(frame)
        if event is None:
            return False

        relative_frame = event.get_relative_frame(frame)
        return event.sequence.is_locked(relative_frame)

    def get_entity_state(self, entity_id: str, frame: int, is_alive: bool) -> SpotlightState:
        """Get spotlight state for a specific entity."""
        if not is_alive:
            return SpotlightState.NORMAL

        event = self.get_active_event(frame)

        if event is None:
            return SpotlightState.NORMAL

        relative_frame = event.get_relative_frame(frame)
        active_id = event.sequence.get_active_entity_id(relative_frame)

        if active_id is None:
            return SpotlightState.NORMAL

        if active_id == entity_id:
            if event.sequence.is_locked(relative_frame):
                return SpotlightState.LOCKED
            else:
                return SpotlightState.ACTIVE

        return SpotlightState.DIMMED

    def get_all_states(
        self,
        frame: int,
        alive_ids: List[str]
    ) -> Dict[str, SpotlightState]:
        """Get spotlight state for all entities at once."""
        event = self.get_active_event(frame)

        # No spotlight active - everyone normal
        if event is None:
            return {eid: SpotlightState.NORMAL for eid in alive_ids}

        relative_frame = event.get_relative_frame(frame)
        active_id = event.sequence.get_active_entity_id(relative_frame)

        # Spotlight sequence ended
        if active_id is None:
            return {eid: SpotlightState.NORMAL for eid in alive_ids}

        is_locked = event.sequence.is_locked(relative_frame)

        states = {}
        for eid in alive_ids:
            if eid == active_id:
                states[eid] = SpotlightState.LOCKED if is_locked else SpotlightState.ACTIVE
            else:
                states[eid] = SpotlightState.DIMMED

        return states

    def should_play_sound(self, frame: int) -> bool:
        """Check if spotlight transition sound should play."""
        return frame in self._sound_frames

    def should_play_lock_sound(self, frame: int) -> bool:
        """Check if this is a lock sound (vs regular tick)."""
        return frame in self._lock_frames

    def get_sound_frames(self) -> List[int]:
        """Get all frames that need spotlight sounds."""
        return sorted(self._sound_frames)
