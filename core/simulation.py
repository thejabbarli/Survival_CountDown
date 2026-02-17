"""Simulation - game logic for eliminations."""

import random
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

from .entity import Entity
from .entity_state import EntityState

if TYPE_CHECKING:
    from .scheduler import EliminationScheduler
    from .strategies.elimination import EliminationStrategy


@dataclass
class EliminationEvent:
    """Record of a single elimination."""
    entity: Entity
    frame: int
    remaining: int


@dataclass
class SimulationResult:
    """Results of running a simulation."""
    events: List[EliminationEvent]
    winner: Entity
    total_frames: int
    seed: Optional[int]


class Simulation:
    """Runs the survival game logic."""

    def __init__(
        self,
        entities: List[Entity],
        scheduler: 'EliminationScheduler' = None,
        fps: int = 60,
        elimination_strategy: Optional['EliminationStrategy'] = None,
        # Legacy parameters (used if scheduler is None)
        elimination_interval: int = 30,
        sudden_death_enabled: bool = True,
        sudden_death_threshold_1: int = 10,
        sudden_death_multiplier_1: int = 2,
        sudden_death_threshold_2: int = 5,
        sudden_death_multiplier_2: int = 4,
    ):
        self.entities = entities
        self.fps = fps
        self.winner_celebration_frames = fps * 2  # 2 seconds
        
        # Create scheduler if not provided (backward compatibility)
        if scheduler is None:
            from .scheduler import IntervalScheduler
            from .config import SchedulerConfig
            
            config = SchedulerConfig(
                elimination_interval=elimination_interval,
                initial_delay=fps,  # 1 second delay
                sudden_death_enabled=sudden_death_enabled,
                sudden_death_threshold_1=sudden_death_threshold_1,
                sudden_death_multiplier_1=sudden_death_multiplier_1,
                sudden_death_threshold_2=sudden_death_threshold_2,
                sudden_death_multiplier_2=sudden_death_multiplier_2,
            )
            scheduler = IntervalScheduler(len(entities), config)
        
        self.scheduler = scheduler
        
        # Elimination strategy (defaults to random)
        if elimination_strategy is None:
            from .strategies.elimination import RandomElimination
            elimination_strategy = RandomElimination()
        self._elimination_strategy = elimination_strategy

    def run(self, seed: Optional[int] = None) -> SimulationResult:
        """Run the simulation and return results."""
        if seed is not None:
            random.seed(seed)
        
        # Reset strategy
        self._elimination_strategy.reset()
        
        # Reset entities
        for entity in self.entities:
            entity.alive = True
            entity.eliminated_at = None

        events = []
        elimination_frames = self.scheduler.get_elimination_frames()

        for frame in elimination_frames:
            alive = [e for e in self.entities if e.alive]
            
            if len(alive) <= 1:
                break

            # Use strategy to select victim
            victim = self._elimination_strategy.select(alive)
            victim.eliminate(frame)
            
            remaining = len(alive) - 1
            events.append(EliminationEvent(
                entity=victim,
                frame=frame,
                remaining=remaining
            ))
            
            # Notify strategy
            self._elimination_strategy.on_elimination(victim, remaining)

        # Find winner
        winner = next(e for e in self.entities if e.alive)

        # Calculate total frames
        total_frames = self.scheduler.get_total_frames(self.winner_celebration_frames)

        return SimulationResult(
            events=events,
            winner=winner,
            total_frames=total_frames,
            seed=seed
        )
