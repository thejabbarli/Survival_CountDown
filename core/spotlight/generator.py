"""Spotlight path generator - REAL SLOT MACHINE STYLE.

Scans through ALL entities (sometimes multiple rotations) before landing.
Early game = quick scan. Late game = multiple full rotations.
"""

import random
from typing import List, Optional, TYPE_CHECKING

from .types import SpotlightStop, SpotlightSequence
from .phase import Phase, PhaseController

if TYPE_CHECKING:
    from .config import SpotlightConfig, PhaseConfig


class SpotlightGenerator:
    """Generates spotlight paths with full rotations like a slot machine.

    The spotlight scans through ALL entities, potentially multiple times,
    before landing on the victim. Creates real gambling tension.
    """

    def __init__(self, config: 'SpotlightConfig', total_entities: int):
        self.config = config
        self.phase_controller = PhaseController(total_entities, config)

    def generate(
        self,
        victim_id: str,
        alive_ids: List[str],
        remaining_count: int,
        seed: Optional[int] = None
    ) -> SpotlightSequence:
        """Generate spotlight sequence with full rotations.

        Args:
            victim_id: Entity that will be eliminated
            alive_ids: All currently alive entity IDs (IN GRID ORDER)
            remaining_count: Number of entities alive
            seed: Optional random seed

        Returns:
            SpotlightSequence scanning through entities
        """
        if seed is not None:
            random.seed(seed)

        if remaining_count <= 1 or victim_id not in alive_ids:
            return self._create_direct_sequence(victim_id)

        # Get phase
        phase = self.phase_controller.get_phase(remaining_count)
        phase_config = self.phase_controller.get_phase_config(phase)

        # Find victim's position
        try:
            victim_idx = alive_ids.index(victim_id)
        except ValueError:
            return self._create_direct_sequence(victim_id)

        # Build scan path based on phase
        path = self._build_scan_path(alive_ids, victim_idx, phase, remaining_count)

        # Generate stops with timing
        return self._build_sequence(path, victim_id, phase_config, phase)

    def _build_scan_path(
        self,
        alive_ids: List[str],
        victim_idx: int,
        phase: Phase,
        remaining_count: int
    ) -> List[str]:
        """Build path that scans through entities like slot machine.

        CHAOS: Quick scan, ~1/2 rotation
        GRIND: Full rotation + some extra
        DUEL: Multiple rotations, dramatic
        """
        total = len(alive_ids)

        if phase == Phase.CHAOS:
            # Quick scan: half the entities or so
            scan_count = max(3, total // 2)

        elif phase == Phase.GRIND:
            # Full rotation plus random extra
            scan_count = total + random.randint(total // 3, total // 2)

        else:  # DUEL
            # Multiple rotations for drama
            if total <= 3:
                # Final few: 2-3 full rotations
                scan_count = total * random.randint(2, 3)
            else:
                scan_count = total + random.randint(total // 2, total)

        # Random starting position (adds unpredictability)
        start_idx = random.randint(0, total - 1)

        # We need to end on victim, so calculate how many steps to get there
        # from start position, plus full rotations

        # Steps from start to victim (going forward/clockwise)
        steps_to_victim = (victim_idx - start_idx) % total

        # Add full rotations to reach our target scan_count
        full_rotations = (scan_count - steps_to_victim) // total
        if full_rotations < 0:
            full_rotations = 0

        # Total steps = rotations * total + steps to victim
        # But we want at least scan_count steps total
        total_steps = full_rotations * total + steps_to_victim

        # Make sure we have at least the minimum scan count
        while total_steps < scan_count:
            total_steps += total

        # Ensure at least 2 steps (1 decoy + victim)
        total_steps = max(2, total_steps)

        # Build the path
        path = []
        for i in range(total_steps):
            idx = (start_idx + i) % total
            path.append(alive_ids[idx])

        # Make sure we end on victim
        if path[-1] != alive_ids[victim_idx]:
            path.append(alive_ids[victim_idx])

        return path

    def _build_sequence(
        self,
        path: List[str],
        victim_id: str,
        phase_config: 'PhaseConfig',
        phase: Phase
    ) -> SpotlightSequence:
        """Build timed sequence from path.

        Timing varies by phase:
        - CHAOS: Very fast, consistent
        - GRIND: Medium, slight slowdown at end
        - DUEL: Slow with dramatic deceleration
        """
        stops = []
        current_frame = 0
        path_len = len(path)

        for i, entity_id in enumerate(path):
            is_victim = (entity_id == victim_id and i == path_len - 1)

            if is_victim:
                # Lock on victim
                duration = phase_config.lock_frames
            else:
                # Calculate duration based on position in path
                min_frames, max_frames = phase_config.frames_per_stop_range

                if phase == Phase.CHAOS:
                    # Fast and consistent
                    duration = min_frames

                elif phase == Phase.GRIND:
                    # Slight slowdown toward end
                    progress = i / path_len
                    if progress > 0.7:
                        duration = max_frames
                    elif progress > 0.5:
                        duration = (min_frames + max_frames) // 2
                    else:
                        duration = min_frames

                else:  # DUEL
                    # Dramatic deceleration
                    progress = i / path_len
                    if progress > 0.85:
                        # Very slow at end
                        duration = max_frames + 5
                    elif progress > 0.6:
                        duration = max_frames
                    elif progress > 0.3:
                        duration = (min_frames + max_frames) // 2
                    else:
                        duration = min_frames

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
