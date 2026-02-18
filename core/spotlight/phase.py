"""Spotlight phase logic.

Determines which phase (CHAOS/GRIND/DUEL) based on remaining entities.
"""

from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import SpotlightConfig, PhaseConfig


class Phase(Enum):
    """Spotlight behavior phases.

    CHAOS: Many entities, fast movement, many decoys
    GRIND: Getting tense, medium speed, fewer decoys
    DUEL: Final few, slow and dramatic
    """
    CHAOS = auto()
    GRIND = auto()
    DUEL = auto()


class PhaseController:
    """Determines spotlight phase based on remaining entity count.

    Usage:
        controller = PhaseController(total_entities=64, config=spotlight_config)
        phase = controller.get_phase(remaining=40)  # -> Phase.CHAOS
        phase_config = controller.get_phase_config(phase)
    """

    def __init__(self, total_entities: int, config: 'SpotlightConfig'):
        """
        Args:
            total_entities: Starting number of entities
            config: Spotlight configuration with phase thresholds
        """
        self.total_entities = total_entities
        self.config = config

        # Pre-calculate thresholds as absolute counts
        self._chaos_threshold = int(total_entities * config.chaos.until_remaining_percent / 100)
        self._grind_threshold = int(total_entities * config.grind.until_remaining_percent / 100)

    def get_phase(self, remaining: int) -> Phase:
        """Get phase based on remaining entity count.

        Args:
            remaining: Number of entities still alive

        Returns:
            Current phase
        """
        # Calculate what percentage remaining represents
        # Phase transitions: CHAOS -> GRIND -> DUEL as count decreases

        if remaining > self._chaos_threshold:
            return Phase.CHAOS
        elif remaining > self._grind_threshold:
            return Phase.GRIND
        else:
            return Phase.DUEL

    def get_phase_config(self, phase: Phase) -> 'PhaseConfig':
        """Get configuration for a specific phase.

        Args:
            phase: The phase to get config for

        Returns:
            PhaseConfig for that phase
        """
        if phase == Phase.CHAOS:
            return self.config.chaos
        elif phase == Phase.GRIND:
            return self.config.grind
        else:
            return self.config.duel

    def get_current_config(self, remaining: int) -> 'PhaseConfig':
        """Convenience: get config for current remaining count.

        Args:
            remaining: Number of entities still alive

        Returns:
            PhaseConfig for current phase
        """
        phase = self.get_phase(remaining)
        return self.get_phase_config(phase)
