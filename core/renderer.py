"""Frame rendering - composes drawables to create frames."""

from typing import List, Optional

from PIL import Image

from .entity import Entity
from .simulation import EntityState
from .layout import BaseLayout, GridLayout
from .config import RenderConfig
from .fonts import FontLoader
from .canvas import CanvasFactory
from .animations import EliminationAnimation, ShrinkWithXAnimation
from .drawers import CounterDrawer, EntityDrawer, WinnerDrawer


class GameFrameRenderer:
    """Renders game frames."""

    def __init__(
        self,
        canvas_factory: CanvasFactory,
        layout: BaseLayout,
        entity_drawer: EntityDrawer,
        counter_drawer: Optional[CounterDrawer],
        entity_state: EntityState
    ):
        self.canvas_factory = canvas_factory
        self.layout = layout
        self.entity_drawer = entity_drawer
        self.counter_drawer = counter_drawer
        self.entity_state = entity_state
        self._positions_cache: dict[int, list] = {}

    def _get_positions(self, entity_count: int):
        """Get positions, using cache."""
        if entity_count not in self._positions_cache:
            self._positions_cache[entity_count] = self.layout.calculate_positions(entity_count)
        return self._positions_cache[entity_count]

    def render(self, entities: List[Entity], frame_num: int) -> Image.Image:
        """Render a single game frame."""
        img, draw = self.canvas_factory.create()

        # Counter
        if self.counter_drawer is not None:
            alive_count = self.entity_state.count_alive(entities, frame_num)
            self.counter_drawer.draw(draw, count=alive_count)

        # Entities
        positions = self._get_positions(len(entities))

        for entity, position in zip(entities, positions):
            state = self.entity_state.get_state(entity, frame_num)
            progress = self.entity_state.get_elimination_progress(entity, frame_num)

            self.entity_drawer.draw(
                draw,
                entity=entity,
                position=position,
                state=state,
                progress=progress
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

    def render(self, winner: Entity) -> Image.Image:
        """Render winner celebration frame."""
        img, draw = self.canvas_factory.create()
        self.winner_drawer.draw(draw, winner)
        return img


class RendererFactory:
    """Creates configured renderers."""

    def __init__(
        self,
        config: RenderConfig,
        font_loader: FontLoader,
        elimination_animation: Optional[EliminationAnimation] = None
    ):
        self.config = config
        self.font_loader = font_loader
        self.elimination_animation = elimination_animation or ShrinkWithXAnimation(config.animation)
        self._canvas_factory = CanvasFactory(config.canvas)

    def create_entity_state(self) -> EntityState:
        """Create entity state tracker."""
        return EntityState(self.config.animation.elimination_duration)

    def create_layout(self) -> GridLayout:
        """Create layout."""
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
        """Create entity drawer."""
        return EntityDrawer(
            entity_config=self.config.entity,
            font=self.font_loader.get_small(),
            elimination_animation=self.elimination_animation
        )

    def create_counter_drawer(self) -> Optional[CounterDrawer]:
        """Create counter drawer if enabled."""
        if not self.config.counter.enabled:
            return None

        return CounterDrawer(
            canvas=self.config.canvas,
            config=self.config.counter,
            font=self.font_loader.get_large()
        )

    def create_winner_drawer(self) -> WinnerDrawer:
        """Create winner drawer."""
        return WinnerDrawer(
            canvas=self.config.canvas,
            config=self.config.winner,
            font=self.font_loader.get_large()
        )

    def create_game_renderer(self) -> GameFrameRenderer:
        """Create game frame renderer."""
        return GameFrameRenderer(
            canvas_factory=self._canvas_factory,
            layout=self.create_layout(),
            entity_drawer=self.create_entity_drawer(),
            counter_drawer=self.create_counter_drawer(),
            entity_state=self.create_entity_state()
        )

    def create_winner_renderer(self) -> WinnerFrameRenderer:
        """Create winner frame renderer."""
        return WinnerFrameRenderer(
            canvas_factory=self._canvas_factory,
            winner_drawer=self.create_winner_drawer()
        )


class Renderer:
    """
    Facade for easy usage.
    For full control, use RendererFactory directly.
    """

    def __init__(
        self,
        config: RenderConfig = None,
        font_loader: FontLoader = None,
        elimination_animation: EliminationAnimation = None
    ):
        self.config = config or RenderConfig()

        # Allow injection or create default
        self._font_loader = font_loader or FontLoader(self.config.font)

        self._factory = RendererFactory(
            self.config,
            self._font_loader,
            elimination_animation
        )
        self._game_renderer = self._factory.create_game_renderer()
        self._winner_renderer = self._factory.create_winner_renderer()

    def render_frame(self, entities: List[Entity], frame_num: int) -> Image.Image:
        """Render a game frame."""
        return self._game_renderer.render(entities, frame_num)

    def render_winner_frame(self, winner: Entity) -> Image.Image:
        """Render winner frame."""
        return self._winner_renderer.render(winner)
