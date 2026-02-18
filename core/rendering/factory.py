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

# Import base class - concrete animations imported where needed
from ..animations import EliminationAnimation, ShrinkWithXAnimation

# Spotlight imports
from ..spotlight import SpotlightVisualConfig, SpotlightTracker


class RendererFactory:
    """Factory for creating configured renderer components.

    Centralizes creation of all rendering-related objects:
    - Layout
    - Drawers (entity, counter, winner)
    - Renderers (game, winner)
    - IdleAnimator
    - SpotlightTracker

    This follows the Factory pattern - clients don't need to know
    how to construct complex renderer hierarchies.

    Usage:
        factory = RendererFactory(config, font_loader)
        game_renderer = factory.create_game_renderer()
        winner_renderer = factory.create_winner_renderer()

    With custom idle animator:
        animator = IdleAnimator(wave_speed=0.1)
        factory = RendererFactory(config, font_loader, idle_animator=animator)

    With spotlight:
        spot_config = SpotlightVisualConfig(glow_color="#FFD700")
        factory = RendererFactory(config, font_loader, spotlight_visual_config=spot_config)
    """

    def __init__(
        self,
        config: RenderConfig,
        font_loader: FontLoader,
        elimination_animation: Optional[EliminationAnimation] = None,
        idle_animator: Optional[IdleAnimator] = None,
        spotlight_visual_config: Optional[SpotlightVisualConfig] = None,
        total_frames: int = 1
    ):
        self.config = config
        self.font_loader = font_loader
        self.elimination_animation = elimination_animation or ShrinkWithXAnimation(config.animation)
        self.total_frames = total_frames
        self._canvas_factory = CanvasFactory(config.canvas, total_frames)
        self.spotlight_visual_config = spotlight_visual_config

        # Create or use provided idle animator
        if idle_animator is not None:
            self._idle_animator = idle_animator
        else:
            # Create from config
            anim_cfg = config.animation
            self._idle_animator = IdleAnimator(
                wave_speed=anim_cfg.idle_wave_speed,
                wave_amount=anim_cfg.idle_wave_amount,
                breathe_speed=anim_cfg.idle_breathe_speed,
                breathe_amount=anim_cfg.idle_breathe_amount
            )

        # Create spotlight tracker
        self._spotlight_tracker = SpotlightTracker()

    @property
    def idle_animator(self) -> IdleAnimator:
        """Get the idle animator used by this factory."""
        return self._idle_animator

    @property
    def spotlight_tracker(self) -> SpotlightTracker:
        """Get the spotlight tracker used by this factory."""
        return self._spotlight_tracker

    def create_entity_state(self) -> EntityState:
        """Create EntityState with configured animation duration."""
        return EntityState(self.config.animation.elimination_duration)

    def create_layout(self) -> GridLayout:
        """Create GridLayout with counter space reserved."""
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
        """Create EntityDrawer with elimination animation and spotlight."""
        return EntityDrawer(
            entity_config=self.config.entity,
            font=self.font_loader.get_small(),
            elimination_animation=self.elimination_animation,
            spotlight_visual_config=self.spotlight_visual_config,
        )

    def create_counter_drawer(self) -> Optional[CounterDrawer]:
        """Create CounterDrawer if enabled in config."""
        if not self.config.counter.enabled:
            return None
        return CounterDrawer(
            canvas=self.config.canvas,
            config=self.config.counter,
            font=self.font_loader.get_large()
        )

    def create_winner_drawer(self) -> WinnerDrawer:
        """Create WinnerDrawer for celebration screen."""
        return WinnerDrawer(
            canvas=self.config.canvas,
            config=self.config.winner,
            font=self.font_loader.get_large(),
            corner_radius=self.config.entity.corner_radius,
            shadow_enabled=self.config.entity.shadow_enabled
        )

    def create_game_renderer(self) -> GameFrameRenderer:
        """Create fully configured GameFrameRenderer."""
        return GameFrameRenderer(
            canvas_factory=self._canvas_factory,
            layout=self.create_layout(),
            entity_drawer=self.create_entity_drawer(),
            counter_drawer=self.create_counter_drawer(),
            entity_state=self.create_entity_state(),
            config=self.config,
            spotlight_tracker=self._spotlight_tracker,
        )

    def create_winner_renderer(self) -> WinnerFrameRenderer:
        """Create WinnerFrameRenderer for victory screen."""
        return WinnerFrameRenderer(
            canvas_factory=self._canvas_factory,
            winner_drawer=self.create_winner_drawer()
        )
