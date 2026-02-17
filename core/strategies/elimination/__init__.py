"""Elimination strategy implementations."""

from .base import EliminationStrategy
from .random import RandomElimination


def create_elimination_strategy(mode: str = "random", **kwargs) -> EliminationStrategy:
    """Factory function to create elimination strategy."""
    strategies = {
        "random": RandomElimination,
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
