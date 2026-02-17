"""Simulation logic - runs the survival game.

The simulation handles:
- Entity elimination via pluggable strategy
- Event logging with frame numbers
- Winner determination

Timing is delegated to EliminationScheduler.
Selection is delegated to EliminationStrategy.

This keeps the simulation focused on orchestration, not implementation details.
"""

import random
from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING

from .entity import Entity
from .scheduler import EliminationScheduler, IntervalScheduler, create_scheduler
from .config import SchedulerConfig

# EntityState moved to its own module (it's rendering logic, not game logic)
# Re-export for backward compatibility
from .entity_state import EntityState

if TYPE_CHECKING:
    from .strategies.elimination import EliminationStrategy


@dataclass
class EliminationEvent:
    """Record of a single elimination."""
    frame: int
    entity_id: str
    entity_name: str
    entities_remaining: int


@dataclass
class SimulationResult:
    """Complete results of a simulation run."""
    winner: Entity
    events: List[EliminationEvent]
    total_frames: int
    elimination_frames: List[int]  # for audio sync


class Simulation:
    """
    Runs the survival game logic.

    Timing is handled by an EliminationScheduler, which can be:
    - IntervalScheduler (default, with sudden death)
    - BeatSyncScheduler (sync to music beats)
    - FrameListScheduler (custom frame list)

    Selection is handled by an EliminationStrategy, which can be:
    - RandomElimination (default, equal probability)
    - WeightedElimination (probability based on weight)
    - SeededElimination (guaranteed positions)
    - ManualElimination (full control)
    """

    def __init__(
        self,
        entities: List[Entity],
        scheduler: Optional[EliminationScheduler] = None,
        elimination_strategy: Optional['EliminationStrategy'] = None,
        fps: int = 60,
        winner_celebration_seconds: float = 2.0,
        # Legacy parameters for backward compatibility
        elimination_interval: int = 30,
        sudden_death_enabled: bool = True,
        sudden_death_threshold_1: int = 10,
        sudden_death_multiplier_1: int = 2,
        sudden_death_threshold_2: int = 5,
        sudden_death_multiplier_2: int = 4
    ):
        if len(entities) < 2:
            raise ValueError("Need at least 2 entities for a simulation")

        self.entities = entities
        self.fps = fps
        self.winner_celebration_frames = int(winner_celebration_seconds * fps)

        # Strategy for WHO gets eliminated (defaults to random)
        self._elimination_strategy = elimination_strategy

        # Use provided scheduler or create from legacy params
        if scheduler is not None:
            self.scheduler = scheduler
        else:
            config = SchedulerConfig(
                elimination_interval=elimination_interval,
                sudden_death_enabled=sudden_death_enabled,
                sudden_death_threshold_1=sudden_death_threshold_1,
                sudden_death_multiplier_1=sudden_death_multiplier_1,
                sudden_death_threshold_2=sudden_death_threshold_2,
                sudden_death_multiplier_2=sudden_death_multiplier_2
            )
            self.scheduler = IntervalScheduler(len(entities), config)

    def _get_elimination_strategy(self) -> 'EliminationStrategy':
        """Lazy load default strategy if none provided."""
        if self._elimination_strategy is None:
            # Import here to avoid circular imports
            from .strategies.elimination import RandomElimination
            self._elimination_strategy = RandomElimination()
        return self._elimination_strategy

    def _get_alive(self) -> List[Entity]:
        """Get list of entities still alive."""
        return [e for e in self.entities if e.alive]

    def run(self, seed: Optional[int] = None) -> SimulationResult:
        """
        Run the full simulation.

        Args:
            seed: Random seed for reproducibility

        Returns:
            SimulationResult with winner, events, and frame info
        """
        if seed is not None:
            random.seed(seed)

        # Get strategy and reset its state
        strategy = self._get_elimination_strategy()
        strategy.reset()

        # Get elimination frames from scheduler
        elimination_frames = self.scheduler.get_elimination_frames()

        events: List[EliminationEvent] = []

        for frame in elimination_frames:
            alive = self._get_alive()

            if len(alive) <= 1:
                break

            # Use strategy instead of hardcoded random.choice
            victim = strategy.select(alive)
            victim.eliminate(frame)

            remaining = len(alive) - 1

            # Notify strategy of elimination (for dynamic adjustments)
            strategy.on_elimination(victim, remaining)

            event = EliminationEvent(
                frame=frame,
                entity_id=victim.id,
                entity_name=victim.name,
                entities_remaining=remaining
            )
            events.append(event)

        # Get winner
        winner = self._get_alive()[0]

        # Calculate total frames
        total_frames = self.scheduler.get_total_frames(self.winner_celebration_frames)

        return SimulationResult(
            winner=winner,
            events=events,
            total_frames=total_frames,
            elimination_frames=[e.frame for e in events]
        )


def run_simulation(
    entities: List[Entity],
    scheduler: Optional[EliminationScheduler] = None,
    elimination_strategy: Optional['EliminationStrategy'] = None,
    beat_frames: Optional[List[int]] = None,
    fps: int = 60,
    seed: Optional[int] = None
) -> SimulationResult:
    """
    Convenience function to run a simulation.

    Args:
        entities: List of entities to compete
        scheduler: Optional custom scheduler
        elimination_strategy: Optional custom elimination strategy
        beat_frames: Optional beat frames for beat sync mode
        fps: Frame rate
        seed: Random seed

    Returns:
        SimulationResult
    """
    if scheduler is None and beat_frames is not None:
        scheduler = create_scheduler(
            entity_count=len(entities),
            beat_frames=beat_frames
        )

    sim = Simulation(
        entities,
        scheduler=scheduler,
        elimination_strategy=elimination_strategy,
        fps=fps
    )
    return sim.run(seed=seed)
