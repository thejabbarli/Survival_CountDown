"""Entity state tracking for rendering.

This module determines the visual state of entities at any given frame.
It's used by the renderer to know HOW to draw each entity.

This is rendering/display logic, separate from game logic (Simulation).
The simulation marks entities as eliminated; this interprets that for display.
"""

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .entity import Entity


class EntityState:
    """Determines entity visual state at a given frame.

    States:
    - ALIVE: Entity is active, draw normally
    - ELIMINATING: Entity is in elimination animation
    - GONE: Entity has finished animating, don't draw

    Usage:
        state = EntityState(animation_duration=20)

        for entity in entities:
            visual_state = state.get_state(entity, current_frame)
            if visual_state == EntityState.ALIVE:
                draw_normal(entity)
            elif visual_state == EntityState.ELIMINATING:
                progress = state.get_elimination_progress(entity, current_frame)
                draw_eliminating(entity, progress)
            # GONE = don't draw
    """

    ALIVE = "alive"
    ELIMINATING = "eliminating"
    GONE = "gone"

    def __init__(self, animation_duration: int = 20):
        """
        Args:
            animation_duration: Frames for elimination animation to complete
        """
        self.animation_duration = animation_duration

    def get_state(self, entity: 'Entity', frame_num: int) -> str:
        """Determine entity visual state at a specific frame.

        Args:
            entity: The entity to check
            frame_num: Current frame number

        Returns:
            One of ALIVE, ELIMINATING, or GONE
        """
        if entity.eliminated_at is None:
            return self.ALIVE

        if frame_num < entity.eliminated_at:
            return self.ALIVE

        frames_since = frame_num - entity.eliminated_at
        if frames_since < self.animation_duration:
            return self.ELIMINATING

        return self.GONE

    def get_elimination_progress(self, entity: 'Entity', frame_num: int) -> float:
        """Get animation progress (0.0 to 1.0) for eliminating entity.

        Args:
            entity: The entity being eliminated
            frame_num: Current frame number

        Returns:
            0.0 at start of animation, 1.0 when complete
        """
        if entity.eliminated_at is None or frame_num < entity.eliminated_at:
            return 0.0

        frames_since = frame_num - entity.eliminated_at
        return min(1.0, frames_since / self.animation_duration)

    def count_alive(self, entities: List['Entity'], frame_num: int) -> int:
        """Count entities visually alive at a specific frame.

        Note: This counts entities that APPEAR alive (not yet animating out),
        which may differ from entities that ARE alive in game logic during
        the animation period.

        Args:
            entities: List of all entities
            frame_num: Current frame number

        Returns:
            Number of entities in ALIVE state
        """
        return sum(
            1 for e in entities
            if self.get_state(e, frame_num) == self.ALIVE
        )

    def is_any_eliminating(self, entities: List['Entity'], frame_num: int) -> bool:
        """Check if any entity is currently in elimination animation.

        Useful for effects that trigger during eliminations.

        Args:
            entities: List of all entities
            frame_num: Current frame number

        Returns:
            True if at least one entity is ELIMINATING
        """
        return any(
            self.get_state(e, frame_num) == self.ELIMINATING
            for e in entities
        )
