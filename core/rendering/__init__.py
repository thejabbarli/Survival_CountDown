"""Rendering subsystem for survival countdown.

This package handles all visual rendering:
- GameFrameRenderer: Main game grid with entities
- WinnerFrameRenderer: Victory celebration screen
- RendererFactory: Creates configured renderers
- Renderer: Simple facade for common usage
- EffectsTracker: Manages effect timing

The rendering system is separate from:
- Simulation (game logic)
- Animation strategies (how eliminations look)
- Audio (sound generation)
"""

from .effects_tracker import EffectsTracker
from .game_renderer import GameFrameRenderer
from .winner_renderer import WinnerFrameRenderer
from .factory import RendererFactory
from .renderer import Renderer


__all__ = [
    'EffectsTracker',
    'GameFrameRenderer',
    'WinnerFrameRenderer',
    'RendererFactory',
    'Renderer',
]
