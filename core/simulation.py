"""Simulation logic - runs the survival game.

The simulation handles:
- Random entity selection for elimination
- Event logging with frame numbers
- Winner determination

Timing is delegated to EliminationScheduler, making the simulation
agnostic to HOW timing is determined (intervals, beats, custom).
"""

import random
from dataclasses import dataclass
from typing import List, Optional

from .entity import Entity
from .scheduler import EliminationScheduler, IntervalScheduler, create_scheduler
from .config import SchedulerConfig


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


class EntityState:
    """Determines entity state at a given frame. This is game logic."""

    ALIVE = "alive"
    ELIMINATING = "eliminating"
    GONE = "gone"

    def __init__(self, animation_duration: int = 20):
        self.animation_duration = animation_duration

    def get_state(self, entity: Entity, frame_num: int) -> str:
        """Determine entity state at a specific frame."""
        if entity.eliminated_at is None:
            return self.ALIVE

        if frame_num < entity.eliminated_at:
            return self.ALIVE

        frames_since = frame_num - entity.eliminated_at
        if frames_since < self.animation_duration:
            return self.ELIMINATING

        return self.GONE

    def get_elimination_progress(self, entity: Entity, frame_num: int) -> float:
        """Get animation progress (0.0 to 1.0) for eliminating entity."""
        if entity.eliminated_at is None or frame_num < entity.eliminated_at:
            return 0.0

        frames_since = frame_num - entity.eliminated_at
        return min(1.0, frames_since / self.animation_duration)

    def count_alive(self, entities: List[Entity], frame_num: int) -> int:
        """Count entities alive at a specific frame."""
        return sum(
            1 for e in entities
            if self.get_state(e, frame_num) == self.ALIVE
        )


class Simulation:
    """
    Runs the survival game logic.
    
    Timing is handled by an EliminationScheduler, which can be:
    - IntervalScheduler (default, with sudden death)
    - BeatSyncScheduler (sync to music beats)
    - FrameListScheduler (custom frame list)
    """

    def __init__(
        self,
        entities: List[Entity],
        scheduler: Optional[EliminationScheduler] = None,
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

        # Get elimination frames from scheduler
        elimination_frames = self.scheduler.get_elimination_frames()
        
        events: List[EliminationEvent] = []

        for frame in elimination_frames:
            alive = self._get_alive()

            if len(alive) <= 1:
                break

            victim = random.choice(alive)
            victim.eliminate(frame)

            event = EliminationEvent(
                frame=frame,
                entity_id=victim.id,
                entity_name=victim.name,
                entities_remaining=len(alive) - 1
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
    beat_frames: Optional[List[int]] = None,
    fps: int = 60,
    seed: Optional[int] = None
) -> SimulationResult:
    """
    Convenience function to run a simulation.
    
    Args:
        entities: List of entities to compete
        scheduler: Optional custom scheduler
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
    
    sim = Simulation(entities, scheduler=scheduler, fps=fps)
    return sim.run(seed=seed)
