"""Random elimination strategy.

This is the default strategy - pure random selection with equal probability
for all alive entities. This extracts the current hardcoded behavior from
simulation.py into a swappable strategy.
"""

import random
from typing import List, Optional, TYPE_CHECKING

from .base import EliminationStrategy

if TYPE_CHECKING:
    from ...entity import Entity


class RandomElimination(EliminationStrategy):
    """Random elimination with equal probability.

    Every alive entity has an equal chance of being eliminated.
    This is the default, "fair" mode.

    Args:
        seed: Optional random seed for reproducibility.
              Note: Seed is typically set at simulation level,
              but can be set here for strategy-specific randomness.
    """

    def __init__(self, seed: Optional[int] = None):
        self._seed = seed
        if seed is not None:
            random.seed(seed)

    def select(self, alive_entities: List['Entity']) -> 'Entity':
        """Randomly select one entity to eliminate.

        Args:
            alive_entities: List of entities still alive

        Returns:
            Randomly chosen entity

        Raises:
            ValueError: If alive_entities is empty
        """
        if not alive_entities:
            raise ValueError("Cannot select from empty list")

        return random.choice(alive_entities)

    def reset(self) -> None:
        """Reset random seed if one was provided."""
        if self._seed is not None:
            random.seed(self._seed)
