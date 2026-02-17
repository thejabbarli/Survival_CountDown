"""Entity state management for rendering.

EntityState determines the visual state of entities based on frame numbers.
This is rendering logic, separate from game logic in Simulation.
"""

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .entity import Entity


class EntityState:
    """Determines entity visual state based on frame timing.
    
    States:
    - ALIVE: Normal, interactive
    - ELIMINATING: Playing death animation
    - GONE: Fully removed from view
    """
    
    ALIVE = "alive"
    ELIMINATING = "eliminating"
    GONE = "gone"
    
    def __init__(self, elimination_duration: int = 20):
        """
        Args:
            elimination_duration: Frames for elimination animation
        """
        self.elimination_duration = elimination_duration
    
    def get_state(self, entity: 'Entity', frame_num: int) -> str:
        """Get entity's visual state at given frame.
        
        Args:
            entity: The entity to check
            frame_num: Current frame number
            
        Returns:
            One of: ALIVE, ELIMINATING, GONE
        """
        if entity.alive:
            return self.ALIVE
            
        if entity.eliminated_at is None:
            return self.GONE
            
        frames_since = frame_num - entity.eliminated_at
        
        if frames_since < 0:
            return self.ALIVE
        elif frames_since < self.elimination_duration:
            return self.ELIMINATING
        else:
            return self.GONE
    
    def get_elimination_progress(self, entity: 'Entity', frame_num: int) -> float:
        """Get elimination animation progress (0.0 to 1.0).
        
        Args:
            entity: The entity to check
            frame_num: Current frame number
            
        Returns:
            Progress from 0.0 (just eliminated) to 1.0 (animation complete)
        """
        if entity.alive or entity.eliminated_at is None:
            return 0.0
            
        frames_since = frame_num - entity.eliminated_at
        
        if frames_since < 0:
            return 0.0
        elif frames_since >= self.elimination_duration:
            return 1.0
        else:
            return frames_since / self.elimination_duration
    
    def count_alive(self, entities: List['Entity'], frame_num: int) -> int:
        """Count entities that appear alive at given frame.
        
        Args:
            entities: List of all entities
            frame_num: Current frame number
            
        Returns:
            Number of entities in ALIVE state (not eliminating, not gone)
        """
        return sum(
            1 for e in entities
            if self.get_state(e, frame_num) == self.ALIVE
        )
    
    def is_any_eliminating(self, entities: List['Entity'], frame_num: int) -> bool:
        """Check if any entity is currently being eliminated.
        
        Args:
            entities: List of all entities
            frame_num: Current frame number
            
        Returns:
            True if any entity is in ELIMINATING state
        """
        return any(
            self.get_state(e, frame_num) == self.ELIMINATING
            for e in entities
        )
