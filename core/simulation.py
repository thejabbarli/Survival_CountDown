"""Simulation - game logic for eliminations."""

import random
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from .entity import Entity
from .entity_state import EntityState

from .spotlight import (
    SpotlightConfig,
    SpotlightEvent,
    create_spotlight_generator,
)

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
    spotlight_events: List[SpotlightEvent] = field(default_factory=list)


class Simulation:
    """Runs the survival game logic."""

    def __init__(
        self,
        entities: List[Entity],
        scheduler: 'EliminationScheduler' = None,
        fps: int = 60,
        elimination_strategy: Optional['EliminationStrategy'] = None,
        spotlight_config: Optional[SpotlightConfig] = None,
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
        self.winner_celebration_frames = fps * 2

        if scheduler is None:
            from .scheduler import IntervalScheduler
            from .config import SchedulerConfig

            config = SchedulerConfig(
                elimination_interval=elimination_interval,
                initial_delay=fps,
                sudden_death_enabled=sudden_death_enabled,
                sudden_death_threshold_1=sudden_death_threshold_1,
                sudden_death_multiplier_1=sudden_death_multiplier_1,
                sudden_death_threshold_2=sudden_death_threshold_2,
                sudden_death_multiplier_2=sudden_death_multiplier_2,
            )
            scheduler = IntervalScheduler(len(entities), config)

        self.scheduler = scheduler

        if elimination_strategy is None:
            from .strategies.elimination import RandomElimination
            elimination_strategy = RandomElimination()
        self._elimination_strategy = elimination_strategy

        self._spotlight_config = spotlight_config or SpotlightConfig(enabled=False)
        self._spotlight_generator = create_spotlight_generator(
            self._spotlight_config,
            len(entities)
        )

    def run(self, seed: Optional[int] = None) -> SimulationResult:
        """Run the simulation and return results."""
        if seed is not None:
            random.seed(seed)

        self._elimination_strategy.reset()

        for entity in self.entities:
            entity.alive = True
            entity.eliminated_at = None

        events = []
        spotlight_events = []

        spotlight_enabled = self._spotlight_config.enabled

        if spotlight_enabled:
            current_frame = self.fps
            elimination_duration = int(self.fps * 0.5)
            elimination_index = 0

            while True:
                alive = [e for e in self.entities if e.alive]

                if len(alive) <= 1:
                    break

                remaining = len(alive)

                victim = self._elimination_strategy.select(alive)
                alive_ids = [e.id for e in alive]

                spotlight_seq = self._spotlight_generator.generate(
                    victim_id=victim.id,
                    alive_ids=alive_ids,
                    remaining_count=remaining
                )

                if spotlight_seq.total_frames > 0:
                    spotlight_events.append(SpotlightEvent(
                        start_frame=current_frame,
                        sequence=spotlight_seq,
                        elimination_index=elimination_index
                    ))

                elim_frame = current_frame + spotlight_seq.total_frames
                victim.eliminate(elim_frame)

                events.append(EliminationEvent(
                    entity=victim,
                    frame=elim_frame,
                    remaining=remaining - 1
                ))

                self._elimination_strategy.on_elimination(victim, remaining - 1)

                current_frame = elim_frame + elimination_duration
                elimination_index += 1

            total_frames = current_frame + self.winner_celebration_frames

        else:
            elimination_frames = self.scheduler.get_elimination_frames()

            for frame in elimination_frames:
                alive = [e for e in self.entities if e.alive]

                if len(alive) <= 1:
                    break

                victim = self._elimination_strategy.select(alive)
                victim.eliminate(frame)

                remaining = len(alive) - 1
                events.append(EliminationEvent(
                    entity=victim,
                    frame=frame,
                    remaining=remaining
                ))

                self._elimination_strategy.on_elimination(victim, remaining)

            total_frames = self.scheduler.get_total_frames(self.winner_celebration_frames)

        winner = next(e for e in self.entities if e.alive)

        return SimulationResult(
            events=events,
            winner=winner,
            total_frames=total_frames,
            seed=seed,
            spotlight_events=spotlight_events
        )
