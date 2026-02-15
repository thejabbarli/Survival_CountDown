"""Frame rendering with effects."""

from typing import List, Optional, Set

from PIL import Image

from .entity import Entity
from .simulation import EntityState, EliminationEvent
from .layout import BaseLayout, GridLayout
from .config import RenderConfig
from .fonts import FontLoader
from .canvas import CanvasFactory
from .animations import EliminationAnimation, ShrinkWithXAnimation
from .drawers import CounterDrawer, EntityDrawer, WinnerDrawer
from .effects import apply_flash


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


class GameFrameRenderer:
    """Renders game frames with effects."""

    def __init__(
        self,
        canvas_factory: CanvasFactory,
        layout: BaseLayout,
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
        self.effects = EffectsTracker(config)
        self._positions_cache: dict[int, list] = {}

    def set_eliminations(self, events: List[EliminationEvent]) -> None:
        self.effects.set_eliminations(events)

    def _get_positions(self, entity_count: int):
        if entity_count not in self._positions_cache:
            self._positions_cache[entity_count] = self.layout.calculate_positions(entity_count)
        return self._positions_cache[entity_count]

    def render(self, entities: List[Entity], frame_num: int) -> Image.Image:
        # Pass frame number for animated gradient
        img, draw = self.canvas_factory.create(frame=frame_num)

        # Counter with pulse
        if self.counter_drawer is not None:
            alive_count = self.entity_state.count_alive(entities, frame_num)
            pulse_progress = self.effects.get_pulse_progress(frame_num)
            self.counter_drawer.draw(draw, count=alive_count, pulse_progress=pulse_progress)

        # Entities
        positions = self._get_positions(len(entities))

        for idx, (entity, position) in enumerate(zip(entities, positions)):
            state = self.entity_state.get_state(entity, frame_num)
            progress = self.entity_state.get_elimination_progress(entity, frame_num)

            self.entity_drawer.draw(
                draw,
                entity=entity,
                position=position,
                state=state,
                progress=progress,
                frame_num=frame_num,
                entity_index=idx,
                total_entities=len(entities)
            )

        # Apply flash effect
        flash_progress = self.effects.get_flash_progress(frame_num)
        if flash_progress is not None:
            img = apply_flash(
                img,
                flash_progress,
                intensity=self.config.animation.flash_intensity
            )

        return img


class WinnerFrameRenderer:
    """Renders winner celebration frames."""

    def __init__(
        self,
        canvas_factory: CanvasFactory,
        winner_drawer: WinnerDrawer
    ):
        self.canvas_factory = canvas_factory
        self.winner_drawer = winner_drawer

    def render(self, winner: Entity, frame_num: int = 0) -> Image.Image:
        img, draw = self.canvas_factory.create(frame=frame_num)
        self.winner_drawer.draw(draw, winner)
        return img


class RendererFactory:
    """Creates configured renderers."""

    def __init__(
        self,
        config: RenderConfig,
        font_loader: FontLoader,
        elimination_animation: Optional[EliminationAnimation] = None,
        total_frames: int = 1
    ):
        self.config = config
        self.font_loader = font_loader
        self.elimination_animation = elimination_animation or ShrinkWithXAnimation(config.animation)
        self.total_frames = total_frames
        self._canvas_factory = CanvasFactory(config.canvas, total_frames)

    def create_entity_state(self) -> EntityState:
        return EntityState(self.config.animation.elimination_duration)

    def create_layout(self) -> GridLayout:
        counter = self.config.counter
        layout = self.config.layout
        canvas = self.config.canvas

        reserved_top = counter.reserved_height if (
            counter.enabled and counter.position == "top"
        ) else 0
        reserved_bottom = counter.reserved_height if (
            counter.enabled and counter.position == "bottom"
        ) else 0

        return GridLayout(
            canvas_width=canvas.width,
            canvas_height=canvas.height,
            padding=layout.cell_padding,
            margin=layout.margin,
            reserved_top=reserved_top,
            reserved_bottom=reserved_bottom
        )

    def create_entity_drawer(self) -> EntityDrawer:
        return EntityDrawer(
            entity_config=self.config.entity,
            font=self.font_loader.get_small(),
            elimination_animation=self.elimination_animation
        )

    def create_counter_drawer(self) -> Optional[CounterDrawer]:
        if not self.config.counter.enabled:
            return None
        return CounterDrawer(
            canvas=self.config.canvas,
            config=self.config.counter,
            font=self.font_loader.get_large()
        )

    def create_winner_drawer(self) -> WinnerDrawer:
        return WinnerDrawer(
            canvas=self.config.canvas,
            config=self.config.winner,
            font=self.font_loader.get_large(),
            corner_radius=self.config.entity.corner_radius,
            shadow_enabled=self.config.entity.shadow_enabled
        )

    def create_game_renderer(self) -> GameFrameRenderer:
        return GameFrameRenderer(
            canvas_factory=self._canvas_factory,
            layout=self.create_layout(),
            entity_drawer=self.create_entity_drawer(),
            counter_drawer=self.create_counter_drawer(),
            entity_state=self.create_entity_state(),
            config=self.config
        )

    def create_winner_renderer(self) -> WinnerFrameRenderer:
        return WinnerFrameRenderer(
            canvas_factory=self._canvas_factory,
            winner_drawer=self.create_winner_drawer()
        )


class Renderer:
    """Facade for easy usage."""

    def __init__(
        self,
        config: RenderConfig = None,
        font_loader: FontLoader = None,
        elimination_animation: EliminationAnimation = None,
        total_frames: int = 1
    ):
        self.config = config or RenderConfig()
        self._font_loader = font_loader or FontLoader(self.config.font)
        self._total_frames = total_frames
        self._factory = RendererFactory(
            self.config,
            self._font_loader,
            elimination_animation,
            total_frames=total_frames
        )
        self._game_renderer = self._factory.create_game_renderer()
        self._winner_renderer = self._factory.create_winner_renderer()

    def set_eliminations(self, events: List[EliminationEvent]) -> None:
        self._game_renderer.set_eliminations(events)

    def render_frame(self, entities: List[Entity], frame_num: int) -> Image.Image:
        return self._game_renderer.render(entities, frame_num)

    def render_winner_frame(self, winner: Entity, frame_num: int = 0) -> Image.Image:
        return self._winner_renderer.render(winner, frame_num)
