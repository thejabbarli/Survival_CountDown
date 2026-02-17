"""Winner frame renderer - renders the victory screen."""

from PIL import Image

from ..entity import Entity
from ..canvas import CanvasFactory
from ..drawers import WinnerDrawer


class WinnerFrameRenderer:
    """Renders the winner celebration screen."""

    def __init__(
            self,
            canvas_factory: CanvasFactory,
            winner_drawer: WinnerDrawer
    ):
        self.canvas_factory = canvas_factory
        self.winner_drawer = winner_drawer

    def render(self, winner: Entity, frame_num: int = 0) -> Image.Image:
        img, draw = self.canvas_factory.create(frame=frame_num)
        self.winner_drawer.draw(draw, winner, frame_num)
        return img
