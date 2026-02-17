"""Elimination strategy implementations."""

from .base import EliminationStrategy
from .random import RandomElimination
from .manual import ManualElimination


def create_elimination_strategy(mode: str = "random", **kwargs) -> EliminationStrategy:
    """Factory function to create elimination strategy.
    
    Args:
        mode: "random" or "manual"
        **kwargs: Strategy-specific arguments
        
    For manual mode:
        order: List[str] - entity IDs in elimination order
        use_names: bool - if True, match by name instead of ID
    
    Examples:
        # Random elimination
        strategy = create_elimination_strategy("random")
        
        # Manual elimination by ID
        strategy = create_elimination_strategy("manual", order=["usa", "uk", "france"])
        
        # Manual elimination by name
        strategy = create_elimination_strategy("manual", order=["USA", "UK"], use_names=True)
    """
    strategies = {
        "random": RandomElimination,
        "manual": ManualElimination,
    }

    strategy_class = strategies.get(mode)
    if strategy_class is None:
        raise ValueError(f"Unknown elimination strategy: {mode}. Available: {list(strategies.keys())}")

    return strategy_class(**kwargs)


__all__ = [
    'EliminationStrategy',
    'RandomElimination',
    'ManualElimination',
    'create_elimination_strategy',
]
