import random
from dataclasses import dataclass
from typing import List, Optional

from .entity import Entity


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
    """Runs the survival game logic."""

    def __init__(
            self,
            entities: List[Entity],
            elimination_interval: int = 30,
            sudden_death_enabled: bool = True,
            sudden_death_threshold_1: int = 10,
            sudden_death_multiplier_1: int = 2,
            sudden_death_threshold_2: int = 5,
            sudden_death_multiplier_2: int = 4,
            fps: int = 60,
            winner_celebration_seconds: float = 2.0
    ):
        if len(entities) < 2:
            raise ValueError("Need at least 2 entities for a simulation")

        self.entities = entities
        self.base_interval = elimination_interval
        self.sudden_death_enabled = sudden_death_enabled
        self.sd_threshold_1 = sudden_death_threshold_1
        self.sd_multiplier_1 = sudden_death_multiplier_1
        self.sd_threshold_2 = sudden_death_threshold_2
        self.sd_multiplier_2 = sudden_death_multiplier_2
        self.fps = fps
        self.winner_celebration_frames = int(winner_celebration_seconds * fps)

    def _get_current_interval(self, remaining: int) -> int:
        """
        Calculate elimination interval based on remaining entities.
        Fewer remaining = longer interval (slower, more dramatic).
        """
        if not self.sudden_death_enabled:
            return self.base_interval

        # Invert the logic: multiply instead of divide
        if remaining <= self.sd_threshold_2:
            return self.base_interval * self.sd_multiplier_2
        elif remaining <= self.sd_threshold_1:
            return self.base_interval * self.sd_multiplier_1
        else:
            return self.base_interval

    def _get_alive(self) -> List[Entity]:
        """Get list of entities still alive."""
        return [e for e in self.entities if e.alive]

    def run(self, seed: Optional[int] = None) -> SimulationResult:
        """Run the full simulation."""
        if seed is not None:
            random.seed(seed)

        events: List[EliminationEvent] = []
        frame = 0

        # Initial pause before first elimination
        frame += self.fps

        while True:
            alive = self._get_alive()

            if len(alive) == 1:
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

            interval = self._get_current_interval(len(alive) - 1)
            frame += interval

        total_frames = frame + self.winner_celebration_frames
        winner = self._get_alive()[0]

        return SimulationResult(
            winner=winner,
            events=events,
            total_frames=total_frames
        )
