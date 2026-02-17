"""Renderer factory - creates configured renderer components."""

from typing import Optional

from ..entity_state import EntityState
from ..layout import GridLayout
from ..config import RenderConfig
from ..fonts import FontLoader
from ..canvas import CanvasFactory
from ..drawers import EntityDrawer, CounterDrawer, WinnerDrawer
from ..idle_animation import IdleAnimator
from .game_renderer import GameFrameRenderer
from .winner_renderer import WinnerFrameRenderer

from ..animations import EliminationAnimation, ShrinkWithXAnimation


class RendererFactory:
    """Factory for creating configured renderer components."""

    def __init__(
        self,
        config: RenderConfig,
        font_loader: FontLoader,
        elimination_animation: Optional[EliminationAnimation] = None,
        idle_animator: Optional[IdleAnimator] = None,
        total_frames: int = 1
    ):
        self.config = config
        self.font_loader = font_loader
        self.elimination_animation = elimination_animation or ShrinkWithXAnimation(config.animation)
        self.total_frames = total_frames
        self._canvas_factory = CanvasFactory(config.canvas, total_frames)
        
        if idle_animator is not None:
            self._idle_animator = idle_animator
        else:
            anim_cfg = config.animation
            self._idle_animator = IdleAnimator(
                wave_speed=anim_cfg.idle_wave_speed,
                wave_amount=anim_cfg.idle_wave_amount,
                breathe_speed=anim_cfg.idle_breathe_speed,
                breathe_amount=anim_cfg.idle_breathe_amount
            )

    @property
    def idle_animator(self) -> IdleAnimator:
        return self._idle_animator

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
            elimination_animation=self.elimination_animation,
            idle_animator=self._idle_animator,
            idle_enabled=self.config.animation.idle_enabled
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
            shadow_enabled=self.config.entity.shadow_enabled,
            idle_animator=self._idle_animator
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
