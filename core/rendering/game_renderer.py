"""Game frame renderer - renders the main game grid."""

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


class GameFrameRenderer:
    """Renders game frames with entities, counter, and effects."""

    def __init__(
        self,
        canvas_factory: CanvasFactory,
        layout: GridLayout,
        entity_drawer: EntityDrawer,
        counter_drawer: Optional[CounterDrawer],
        entity_state: EntityState,
        config: RenderConfig
    ):
        self.canvas_factory = canvas_factory
        self.layout = layout
        self.entity_drawer = entity_drawer
        self.counter_drawer = counter_drawer
        self.entity_state = entity_state
        self.config = config
        self.effects_tracker = EffectsTracker(config)

    def set_eliminations(self, events: List[EliminationEvent]) -> None:
        self.effects_tracker.set_eliminations(events)

    def render(self, entities: List[Entity], frame_num: int) -> Image.Image:
        img, draw = self.canvas_factory.create(frame=frame_num)

        alive_count = self.entity_state.count_alive(entities, frame_num)
        positions = self.layout.calculate_positions(len(entities))

        for idx, (entity, pos) in enumerate(zip(entities, positions)):
            state = self.entity_state.get_state(entity, frame_num)
            progress = self.entity_state.get_elimination_progress(entity, frame_num)

            self.entity_drawer.draw(
                target=draw,
                entity=entity,
                position=pos,
                state=state,
                progress=progress,
                frame_num=frame_num,
                entity_index=idx,
                total_entities=len(entities)
            )

        if self.counter_drawer:
            pulse_progress = self.effects_tracker.get_pulse_progress(frame_num)
            self.counter_drawer.draw(draw, alive_count, pulse_progress)

        flash_progress = self.effects_tracker.get_flash_progress(frame_num)
        if flash_progress is not None:
            img = apply_flash(img, flash_progress, self.config.animation.flash_intensity)

        return img
