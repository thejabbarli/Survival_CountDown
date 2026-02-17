"""Random elimination strategy."""

import random
from typing import List

from .base import EliminationStrategy
from ...entity import Entity


class RandomElimination(EliminationStrategy):
    """Random elimination - equal probability for all entities."""

    def select(self, alive_entities: List[Entity]) -> Entity:
        """Select a random entity to eliminate."""
        if not alive_entities:
            raise ValueError("Cannot select from empty list")
        return random.choice(alive_entities)
