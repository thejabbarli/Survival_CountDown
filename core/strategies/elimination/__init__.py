"""Elimination strategy implementations.

Strategies decide WHO gets eliminated. This is separate from:
- Spotlight (HOW selection is shown visually)
- Animation (HOW the entity disappears)

Available strategies:
- RandomElimination: Equal probability for all (default, current behavior)
- WeightedElimination: Probability based on weight (future)
- SeededElimination: Guaranteed positions for specific entities (future)
- ManualElimination: Full control of elimination order (future)
"""

from .base import EliminationStrategy
from .random import RandomElimination


def create_elimination_strategy(mode: str = "random", **kwargs) -> EliminationStrategy:
    """Factory function to create elimination strategy from config.

    Args:
        mode: Strategy type ("random", "weighted", "seeded", "manual")
        **kwargs: Strategy-specific parameters

    Returns:
        Configured EliminationStrategy instance
    """
    strategies = {
        "random": RandomElimination,
        # Future:
        # "weighted": WeightedElimination,
        # "seeded": SeededElimination,
        # "manual": ManualElimination,
    }

    strategy_class = strategies.get(mode)
    if strategy_class is None:
        raise ValueError(f"Unknown elimination strategy: {mode}. Available: {list(strategies.keys())}")

    return strategy_class(**kwargs)


__all__ = [
    'EliminationStrategy',
    'RandomElimination',
    'create_elimination_strategy',
]
