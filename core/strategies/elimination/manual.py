"""Manual elimination strategy - predetermined order."""

from typing import List, Optional

from .base import EliminationStrategy
from ...entity import Entity


class ManualElimination(EliminationStrategy):
    """Elimination with predetermined order.
    
    The elimination order is set in advance. Each call to select()
    returns the next entity in the order.
    
    Usage:
        # By entity IDs
        strategy = ManualElimination(order=["usa", "uk", "france", "germany"])
        
        # By entity names (set use_names=True)
        strategy = ManualElimination(
            order=["United States", "United Kingdom", "France"],
            use_names=True
        )
    
    For spotlight: The next victim is known before select() is called,
    allowing spotlight animation to scan and land on the predetermined target.
    """

    def __init__(
        self,
        order: List[str],
        use_names: bool = False
    ):
        """
        Args:
            order: List of entity IDs (or names if use_names=True) in elimination order.
                   First item = first to be eliminated.
            use_names: If True, match by entity.name instead of entity.id
        """
        self.order = order
        self.use_names = use_names
        self._current_index = 0
    
    def reset(self) -> None:
        """Reset to beginning of elimination order."""
        self._current_index = 0
    
    def select(self, alive_entities: List[Entity]) -> Entity:
        """Select next entity from predetermined order.
        
        If the next entity in order is already eliminated or not found,
        skips to the next one in the order.
        """
        if not alive_entities:
            raise ValueError("Cannot select from empty list")
        
        # Build lookup
        if self.use_names:
            lookup = {e.name: e for e in alive_entities}
        else:
            lookup = {e.id: e for e in alive_entities}
        
        # Find next valid target from order
        while self._current_index < len(self.order):
            target_key = self.order[self._current_index]
            self._current_index += 1
            
            if target_key in lookup:
                return lookup[target_key]
        
        # Fallback: if order exhausted, return first alive
        return alive_entities[0]
    
    def peek_next(self, alive_entities: List[Entity]) -> Optional[Entity]:
        """Peek at next victim WITHOUT advancing the index.
        
        Used by spotlight to know where to land.
        Returns None if no valid target found.
        """
        if not alive_entities:
            return None
        
        # Build lookup
        if self.use_names:
            lookup = {e.name: e for e in alive_entities}
        else:
            lookup = {e.id: e for e in alive_entities}
        
        # Find next valid target (without advancing)
        temp_index = self._current_index
        while temp_index < len(self.order):
            target_key = self.order[temp_index]
            if target_key in lookup:
                return lookup[target_key]
            temp_index += 1
        
        # Fallback
        return alive_entities[0] if alive_entities else None
    
    @property
    def remaining_order(self) -> List[str]:
        """Get remaining elimination order."""
        return self.order[self._current_index:]
