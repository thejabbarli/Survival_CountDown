"""Base class for elimination strategies.

This defines the interface that all elimination strategies must implement.
The strategy pattern allows swapping WHO gets eliminated without changing
the simulation or rendering code.
"""

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...entity import Entity


class EliminationStrategy(ABC):
    """Abstract base class for elimination selection strategies.

    Implementations decide which entity to eliminate from a list of
    alive entities. This is pure selection logic - no rendering,
    no animation, just "who dies next?"

    Example usage:
        strategy = RandomElimination()
        victim = strategy.select(alive_entities)
        victim.eliminate(frame)
    """

    @abstractmethod
    def select(self, alive_entities: List['Entity']) -> 'Entity':
        """Select one entity to eliminate.

        Args:
            alive_entities: List of entities still alive (len >= 1)

        Returns:
            The entity to eliminate

        Raises:
            ValueError: If alive_entities is empty
        """
        pass

    def reset(self) -> None:
        """Reset any internal state for a new simulation.

        Override this if your strategy maintains state across eliminations
        (e.g., SeededStrategy tracking which seeds have been used).
        """
        pass

    def on_elimination(self, eliminated: 'Entity', remaining: int) -> None:
        """Called after an elimination occurs.

        Override this if your strategy needs to react to eliminations
        (e.g., adjusting weights dynamically).

        Args:
            eliminated: The entity that was just eliminated
            remaining: Number of entities still alive after this elimination
        """
        pass
