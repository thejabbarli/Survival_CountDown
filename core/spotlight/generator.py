"""Spotlight path generator - slot machine with smooth deceleration."""

import random
import math
from typing import List, Optional, TYPE_CHECKING

from .types import SpotlightStop, SpotlightSequence
from .phase import Phase, PhaseController

if TYPE_CHECKING:
    from .config import SpotlightConfig, PhaseConfig


class SpotlightGenerator:
    """Generates spotlight paths with realistic deceleration.

    Like a real slot machine:
    - Starts fast
    - Gradually slows down
    - Almost stops before landing on victim
    """

    def __init__(self, config: 'SpotlightConfig', total_entities: int):
        self.config = config
        self.phase_controller = PhaseController(total_entities, config)
        self._initial_entity_count = total_entities

    def generate(
        self,
        victim_id: str,
        alive_ids: List[str],
        remaining_count: int,
        seed: Optional[int] = None
    ) -> SpotlightSequence:
        """Generate spotlight sequence with deceleration."""
        if seed is not None:
            random.seed(seed)

        if remaining_count <= 1 or victim_id not in alive_ids:
            return self._create_direct_sequence(victim_id)

        phase = self.phase_controller.get_phase(remaining_count)
        phase_config = self.phase_controller.get_phase_config(phase)

        try:
            victim_idx = alive_ids.index(victim_id)
        except ValueError:
            return self._create_direct_sequence(victim_id)

        # Calculate how far into the game we are (0.0 = start, 1.0 = end)
        game_progress = 1.0 - (remaining_count / self._initial_entity_count)

        path = self._build_scan_path(alive_ids, victim_idx, phase, remaining_count)

        return self._build_sequence_with_deceleration(
            path, victim_id, phase_config, phase, game_progress
        )

    def _build_scan_path(
        self,
        alive_ids: List[str],
        victim_idx: int,
        phase: Phase,
        remaining_count: int
    ) -> List[str]:
        """Build path scanning through entities."""
        total = len(alive_ids)

        if phase == Phase.CHAOS:
            # Quick: half rotation
            scan_count = max(3, total // 2)

        elif phase == Phase.GRIND:
            # Full rotation + extra
            scan_count = total + random.randint(total // 3, total)

        else:  # DUEL
            if total <= 3:
                # Final few: 2-3 full rotations
                scan_count = total * random.randint(2, 3)
            else:
                scan_count = total * 2 + random.randint(0, total // 2)

        # Random start
        start_idx = random.randint(0, total - 1)

        # Calculate steps to end on victim
        steps_to_victim = (victim_idx - start_idx) % total
        full_rotations = max(0, (scan_count - steps_to_victim) // total)
        total_steps = full_rotations * total + steps_to_victim

        while total_steps < scan_count:
            total_steps += total

        total_steps = max(2, total_steps)

        # Build path
        path = []
        for i in range(total_steps):
            idx = (start_idx + i) % total
            path.append(alive_ids[idx])

        if path[-1] != alive_ids[victim_idx]:
            path.append(alive_ids[victim_idx])

        return path

    def _build_sequence_with_deceleration(
        self,
        path: List[str],
        victim_id: str,
        phase_config: 'PhaseConfig',
        phase: Phase,
        game_progress: float
    ) -> SpotlightSequence:
        """Build sequence with smooth deceleration curve.

        Uses easing function so cursor visibly slows down.
        """
        stops = []
        current_frame = 0
        path_len = len(path)

        min_frames, max_frames = phase_config.frames_per_stop_range

        # Game progress affects overall speed
        # Early game (progress=0): faster
        # Late game (progress=1): slower
        speed_multiplier = 1.0 + game_progress * 1.5  # 1.0x to 2.5x slower

        for i, entity_id in enumerate(path):
            is_victim = (entity_id == victim_id and i == path_len - 1)

            if is_victim:
                duration = phase_config.lock_frames
            else:
                # Progress through this scan (0.0 = start, 1.0 = end)
                scan_progress = i / max(1, path_len - 1)

                # Easing function: slow at end
                # Using ease-out-quad: 1 - (1-t)^2
                # This makes it start fast and slow down toward the end
                ease = 1.0 - math.pow(1.0 - scan_progress, 2)

                # Interpolate between min and max frames based on easing
                base_duration = min_frames + (max_frames - min_frames) * ease

                # Apply game progress multiplier
                duration = int(base_duration * speed_multiplier)

                # Ensure minimum of 1 frame
                duration = max(1, duration)

            stop = SpotlightStop(
                entity_id=entity_id,
                start_frame=current_frame,
                end_frame=current_frame + duration - 1,
                is_victim=is_victim
            )
            stops.append(stop)
            current_frame += duration

        return SpotlightSequence(stops=stops)

    def _create_direct_sequence(self, victim_id: str) -> SpotlightSequence:
        """Create minimal sequence for edge cases."""
        lock_frames = self.config.duel.lock_frames

        stop = SpotlightStop(
            entity_id=victim_id,
            start_frame=0,
            end_frame=lock_frames - 1,
            is_victim=True
        )

        return SpotlightSequence(stops=[stop])


class NoSpotlightGenerator:
    """Null generator for when spotlight is disabled."""

    def generate(
        self,
        victim_id: str,
        alive_ids: List[str],
        remaining_count: int,
        seed: Optional[int] = None
    ) -> SpotlightSequence:
        return SpotlightSequence(stops=[])


def create_spotlight_generator(
    config: 'SpotlightConfig',
    total_entities: int
) -> 'SpotlightGenerator | NoSpotlightGenerator':
    if config.enabled:
        return SpotlightGenerator(config, total_entities)
    else:
        return NoSpotlightGenerator()
