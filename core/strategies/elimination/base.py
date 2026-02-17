"""Base class for elimination strategies."""

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...entity import Entity


class EliminationStrategy(ABC):
    """Abstract base class for elimination selection strategies."""
    
    @abstractmethod
    def select(self, alive_entities: List['Entity']) -> 'Entity':
        """Select one entity to eliminate."""
        pass
    
    def reset(self) -> None:
        """Reset any internal state for a new simulation."""
        pass
    
    def on_elimination(self, eliminated: 'Entity', remaining: int) -> None:
        """Called after an elimination occurs."""
        pass
