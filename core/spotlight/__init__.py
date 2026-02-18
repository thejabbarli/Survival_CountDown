"""Spotlight animation system.

Creates the "gambling psychology" effect by highlighting entities
in sequence before elimination, creating near-misses and tension.

Main components:
- SpotlightGenerator: Creates spotlight paths
- SpotlightTracker: Frame-to-state lookups for renderer
- SpotlightConfig: Configuration settings

Usage:
    from core.spotlight import (
        SpotlightConfig,
        SpotlightGenerator,
        SpotlightTracker,
        SpotlightState
    )

    # Setup
    config = SpotlightConfig()
    generator = SpotlightGenerator(config, total_entities=64)
    tracker = SpotlightTracker()

    # In simulation: generate sequences
    sequence = generator.generate(victim_id, alive_ids, remaining)
    events.append(SpotlightEvent(start_frame, sequence, index))

    # After simulation: register events with tracker
    tracker.set_events(spotlight_events)

    # In renderer: get state per entity
    state = tracker.get_entity_state(entity_id, frame, is_alive)
"""

from .types import (
    SpotlightState,
    SpotlightStop,
    SpotlightSequence,
    SpotlightEvent,
)

from .config import (
    SpotlightConfig,
    SpotlightVisualConfig,
    SpotlightSoundConfig,
    PhaseConfig,
)

from .phase import (
    Phase,
    PhaseController,
)

from .generator import (
    SpotlightGenerator,
    NoSpotlightGenerator,
    create_spotlight_generator,
)

from .tracker import (
    SpotlightTracker,
)

from .effects import (
    SpotlightVisuals,
    calculate_spotlight_visuals,
    hex_to_rgb,
)

__all__ = [
    # Types
    'SpotlightState',
    'SpotlightStop',
    'SpotlightSequence',
    'SpotlightEvent',

    # Config
    'SpotlightConfig',
    'SpotlightVisualConfig',
    'SpotlightSoundConfig',
    'PhaseConfig',

    # Phase
    'Phase',
    'PhaseController',

    # Generator
    'SpotlightGenerator',
    'NoSpotlightGenerator',
    'create_spotlight_generator',

    # Tracker
    'SpotlightTracker',

    # Effects
    'SpotlightVisuals',
    'calculate_spotlight_visuals',
    'hex_to_rgb',
]
