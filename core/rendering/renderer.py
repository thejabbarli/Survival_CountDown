"""Renderer facade - simple interface for frame rendering."""

from typing import List, Optional

from PIL import Image

from ..entity import Entity
from ..simulation import EliminationEvent
from ..config import RenderConfig
from ..fonts import FontLoader
from ..animations import EliminationAnimation
from ..idle_animation import IdleAnimator
from .factory import RendererFactory


class Renderer:
    """Facade for easy frame rendering."""

    def __init__(
        self,
        config: RenderConfig = None,
        font_loader: FontLoader = None,
        elimination_animation: EliminationAnimation = None,
        idle_animator: IdleAnimator = None,
        total_frames: int = 1
    ):
        self.config = config or RenderConfig()
        self._font_loader = font_loader or FontLoader(self.config.font)
        self._total_frames = total_frames
        self._factory = RendererFactory(
            self.config,
            self._font_loader,
            elimination_animation,
            idle_animator=idle_animator,
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
