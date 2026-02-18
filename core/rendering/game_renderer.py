"""Game frame renderer - FIXED VERSION"""

from typing import List, Optional

from PIL import Image

from ..entity import Entity
from ..entity_state import EntityState
from ..simulation import EliminationEvent
from ..layout import GridLayout
from ..config import RenderConfig
from ..canvas import CanvasFactory
from ..drawers import EntityDrawer, CounterDrawer
from ..effects import apply_flash
from .effects_tracker import EffectsTracker
from ..spotlight import SpotlightTracker, SpotlightState, SpotlightEvent


class GameFrameRenderer:
    """Renders game frames with entities, counter, effects, and spotlight."""

    def __init__(
        self,
        canvas_factory: CanvasFactory,
        layout: GridLayout,
        entity_drawer: EntityDrawer,
        counter_drawer: Optional[CounterDrawer],
        entity_state: EntityState,
        config: RenderConfig,
        spotlight_tracker: Optional[SpotlightTracker] = None,
    ):
        self.canvas_factory = canvas_factory
        self.layout = layout
        self.entity_drawer = entity_drawer
        self.counter_drawer = counter_drawer
        self.entity_state = entity_state
        self.config = config
        self.effects_tracker = EffectsTracker(config)
        self.spotlight_tracker = spotlight_tracker or SpotlightTracker()
        self._positions_cache: dict[int, list] = {}

    def set_eliminations(self, events: List[EliminationEvent]) -> None:
        """Register elimination events for effect timing."""
        self.effects_tracker.set_eliminations(events)

    def set_spotlight_events(self, events: List[SpotlightEvent]) -> None:
        """Register spotlight events for state tracking."""
        self.spotlight_tracker.set_events(events)

    def _get_positions(self, entity_count: int):
        """Get cached positions for entity count."""
        if entity_count not in self._positions_cache:
            self._positions_cache[entity_count] = self.layout.calculate_positions(entity_count)
        return self._positions_cache[entity_count]

    def _get_alive_ids_at_frame(self, entities: List[Entity], frame_num: int) -> List[str]:
        """Get entity IDs that are alive at the given frame.

        An entity is alive if:
        - It was never eliminated (eliminated_at is None), OR
        - It will be eliminated at a FUTURE frame (eliminated_at > frame_num)
        """
        alive_ids = []
        for e in entities:
            if e.eliminated_at is None or e.eliminated_at > frame_num:
                alive_ids.append(e.id)
        return alive_ids

    def render(self, entities: List[Entity], frame_num: int) -> Image.Image:
        """Render a single game frame."""
        # Create canvas with background
        img, draw = self.canvas_factory.create(frame=frame_num)

        # Counter with pulse (draw BEFORE entities)
        if self.counter_drawer is not None:
            alive_count = self.entity_state.count_alive(entities, frame_num)
            pulse_progress = self.effects_tracker.get_pulse_progress(frame_num)
            self.counter_drawer.draw(draw, count=alive_count, pulse_progress=pulse_progress)

        # Get spotlight states for all entities ALIVE AT THIS FRAME
        alive_ids = self._get_alive_ids_at_frame(entities, frame_num)
        spotlight_states = self.spotlight_tracker.get_all_states(frame_num, alive_ids)

        # DEBUG: print spotlight states
        if frame_num % 30 == 0:
            non_normal = {eid: str(state).split('.')[-1] for eid, state in spotlight_states.items()
                         if state != SpotlightState.NORMAL}
            if non_normal:
                print(f"[DEBUG] Frame {frame_num}: {non_normal}")

        # Entities (with cached positions)
        positions = self._get_positions(len(entities))

        for idx, (entity, pos) in enumerate(zip(entities, positions)):
            state = self.entity_state.get_state(entity, frame_num)
            progress = self.entity_state.get_elimination_progress(entity, frame_num)

            # Get spotlight state for this entity
            spot_state = spotlight_states.get(entity.id, SpotlightState.NORMAL)

            self.entity_drawer.draw(
                target=draw,
                entity=entity,
                position=pos,
                state=state,
                progress=progress,
                frame_num=frame_num,
                entity_index=idx,
                total_entities=len(entities),
                spotlight_state=spot_state,
            )

        # Apply screen flash effect
        flash_progress = self.effects_tracker.get_flash_progress(frame_num)
        if flash_progress is not None:
            img = apply_flash(img, flash_progress, self.config.animation.flash_intensity)

        return img
