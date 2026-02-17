"""Winner frame renderer - renders the victory screen."""

from PIL import Image

from ..entity import Entity
from ..canvas import CanvasFactory
from ..drawers import WinnerDrawer


class WinnerFrameRenderer:
    """Renders the winner celebration screen.

    Shows the winning entity prominently with celebration text.

    Usage:
        renderer = WinnerFrameRenderer(canvas_factory, winner_drawer)
        img = renderer.render(winner, frame_num)
    """

    def __init__(
            self,
            canvas_factory: CanvasFactory,
            winner_drawer: WinnerDrawer
    ):
        self.canvas_factory = canvas_factory
        self.winner_drawer = winner_drawer

    def render(self, winner: Entity, frame_num: int = 0) -> Image.Image:
        """Render the winner celebration frame.

        Args:
            winner: The winning entity
            frame_num: Frame number (for animated backgrounds)

        Returns:
            Rendered frame as PIL Image
        """
        img, draw = self.canvas_factory.create(frame=frame_num)
        self.winner_drawer.draw(draw, winner)
        return img
