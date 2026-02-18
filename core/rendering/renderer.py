"""Renderer facade - simple interface for frame rendering."""

from typing import List, Optional

from PIL import Image

from ..entity import Entity
from ..simulation import EliminationEvent
from ..config import RenderConfig
from ..fonts import FontLoader
from ..animations import EliminationAnimation
from .factory import RendererFactory
from .game_renderer import GameFrameRenderer
from .winner_renderer import WinnerFrameRenderer
from ..spotlight import SpotlightVisualConfig, SpotlightEvent


class Renderer:
    """Facade for easy frame rendering.

    Provides a simple interface hiding the complexity of:
    - RendererFactory
    - GameFrameRenderer
    - WinnerFrameRenderer
    - SpotlightTracker

    Usage:
        renderer = Renderer(config, total_frames=result.total_frames)
        renderer.set_eliminations(result.events)
        renderer.set_spotlight_events(result.spotlight_events)

        # Game frames
        for frame in game_frames:
            img = renderer.render_frame(entities, frame)

        # Winner frames
        for frame in winner_frames:
            img = renderer.render_winner_frame(winner, frame)
    """

    def __init__(
            self,
            config: RenderConfig = None,
            font_loader: FontLoader = None,
            elimination_animation: EliminationAnimation = None,
            spotlight_visual_config: Optional[SpotlightVisualConfig] = None,
            total_frames: int = 1
    ):
        self.config = config or RenderConfig()
        self._font_loader = font_loader or FontLoader(self.config.font)
        self._total_frames = total_frames
        self._factory = RendererFactory(
            self.config,
            self._font_loader,
            elimination_animation,
            spotlight_visual_config=spotlight_visual_config,
            total_frames=total_frames
        )
        self._game_renderer = self._factory.create_game_renderer()
        self._winner_renderer = self._factory.create_winner_renderer()

    def set_eliminations(self, events: List[EliminationEvent]) -> None:
        """Register elimination events for effects timing."""
        self._game_renderer.set_eliminations(events)

    def set_spotlight_events(self, events: List[SpotlightEvent]) -> None:
        """Register spotlight events for state tracking."""
        self._game_renderer.set_spotlight_events(events)

    def render_frame(self, entities: List[Entity], frame_num: int) -> Image.Image:
        """Render a game frame.

        Args:
            entities: All entities in the simulation
            frame_num: Current frame number

        Returns:
            Rendered frame as PIL Image
        """
        return self._game_renderer.render(entities, frame_num)

    def render_winner_frame(self, winner: Entity, frame_num: int = 0) -> Image.Image:
        """Render a winner celebration frame.

        Args:
            winner: The winning entity
            frame_num: Frame number (for animated backgrounds)

        Returns:
            Rendered frame as PIL Image
        """
        return self._winner_renderer.render(winner, frame_num)
