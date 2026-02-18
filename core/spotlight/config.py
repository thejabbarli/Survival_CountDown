"""Spotlight configuration.

All spotlight settings as dataclasses.
Designed to be loaded from YAML config.
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class PhaseConfig:
    """Configuration for a single spotlight phase.

    Attributes:
        until_remaining_percent: Phase active until this % of entities remain
        decoy_count_range: (min, max) number of decoys to visit
        frames_per_stop_range: (min, max) frames to stay on each decoy
        lock_frames: Frames to stay on victim before elimination
    """
    until_remaining_percent: int
    decoy_count_range: Tuple[int, int]
    frames_per_stop_range: Tuple[int, int]
    lock_frames: int


@dataclass
class SpotlightVisualConfig:
    """Visual settings for spotlight effects.

    Attributes:
        dim_opacity: Opacity for non-spotlit entities (0.0-1.0)
        active_scale: Scale multiplier when spotlight is on entity
        locked_scale: Scale multiplier when locked on victim
        glow_enabled: Whether to draw glow effect
        glow_radius: Blur radius for glow effect
        glow_color: Color of glow (hex string)
        glow_opacity: Opacity of glow effect (0-255)
    """
    dim_opacity: float = 0.6
    active_scale: float = 1.08
    locked_scale: float = 1.10
    glow_enabled: bool = True
    glow_radius: int = 15
    glow_color: str = "#FFD700"  # Gold
    glow_opacity: int = 180


@dataclass
class SpotlightSoundConfig:
    """Sound settings for spotlight.

    Attributes:
        enabled: Whether spotlight makes sounds
        tick_sound: Sound file for passing through entities
        lock_sound: Sound file for locking on victim (optional)
    """
    enabled: bool = True
    tick_sound: str = "spotlight_tick.wav"
    lock_sound: str = "spotlight_lock.wav"


@dataclass
class SpotlightConfig:
    """Main spotlight configuration.

    Attributes:
        enabled: Master toggle for spotlight system
        visual: Visual effect settings
        sound: Sound settings
        phases: Phase configurations (chaos, grind, duel)
    """
    enabled: bool = True

    visual: SpotlightVisualConfig = field(default_factory=SpotlightVisualConfig)
    sound: SpotlightSoundConfig = field(default_factory=SpotlightSoundConfig)

    # Phase configs with sensible defaults
    chaos: PhaseConfig = field(default_factory=lambda: PhaseConfig(
        until_remaining_percent=60,
        decoy_count_range=(2, 4),
        frames_per_stop_range=(5, 10),
        lock_frames=5
    ))

    grind: PhaseConfig = field(default_factory=lambda: PhaseConfig(
        until_remaining_percent=20,
        decoy_count_range=(1, 2),
        frames_per_stop_range=(15, 25),
        lock_frames=10
    ))

    duel: PhaseConfig = field(default_factory=lambda: PhaseConfig(
        until_remaining_percent=0,
        decoy_count_range=(0, 1),
        frames_per_stop_range=(25, 40),
        lock_frames=15
    ))

    @classmethod
    def from_dict(cls, data: dict) -> 'SpotlightConfig':
        """Create config from dictionary (e.g., loaded from YAML)."""
        if not data:
            return cls()

        visual_data = data.get('visual', {})
        visual = SpotlightVisualConfig(
            dim_opacity=visual_data.get('dim_opacity', 0.6),
            active_scale=visual_data.get('active_scale', 1.08),
            locked_scale=visual_data.get('locked_scale', 1.10),
            glow_enabled=visual_data.get('glow_enabled', True),
            glow_radius=visual_data.get('glow_radius', 15),
            glow_color=visual_data.get('glow_color', '#FFD700'),
            glow_opacity=visual_data.get('glow_opacity', 180),
        )

        sound_data = data.get('sound', {})
        sound = SpotlightSoundConfig(
            enabled=sound_data.get('enabled', True),
            tick_sound=sound_data.get('tick_sound', 'spotlight_tick.wav'),
            lock_sound=sound_data.get('lock_sound', 'spotlight_lock.wav'),
        )

        def parse_phase(phase_data: dict, defaults: PhaseConfig) -> PhaseConfig:
            if not phase_data:
                return defaults

            # Handle range as list [min, max] from YAML
            decoy = phase_data.get('decoy_count', list(defaults.decoy_count_range))
            frames = phase_data.get('frames_per_stop', list(defaults.frames_per_stop_range))

            return PhaseConfig(
                until_remaining_percent=phase_data.get('until_remaining_percent', defaults.until_remaining_percent),
                decoy_count_range=tuple(decoy) if isinstance(decoy, list) else decoy,
                frames_per_stop_range=tuple(frames) if isinstance(frames, list) else frames,
                lock_frames=phase_data.get('lock_frames', defaults.lock_frames),
            )

        default = cls()
        phases_data = data.get('phases', {})

        return cls(
            enabled=data.get('enabled', True),
            visual=visual,
            sound=sound,
            chaos=parse_phase(phases_data.get('chaos', {}), default.chaos),
            grind=parse_phase(phases_data.get('grind', {}), default.grind),
            duel=parse_phase(phases_data.get('duel', {}), default.duel),
        )
