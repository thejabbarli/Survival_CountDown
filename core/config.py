"""Configuration classes - each focused on one concern."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class CanvasConfig:
    """Canvas/video dimensions and background."""
    width: int = 1080
    height: int = 1920
    background_color: str = "#1a1a2e"

    background_image: str = None

    # Static gradient
    gradient_enabled: bool = True
    gradient_top: str = "#1a1a2e"
    gradient_bottom: str = "#0f0f1a"

    # Animated gradient (overrides static if enabled)
    animated_gradient: bool = False
    gradient_top_end: str = "#2e1a2e"  # Top color shifts to this
    gradient_bottom_end: str = "#1a0f1a"  # Bottom color shifts to this
    gradient_cycle_speed: float = 1.0  # How many full cycles

    # Vignette
    vignette_enabled: bool = True
    vignette_strength: float = 0.3

    # Special modes
    greenscreen: bool = False
    transparent: bool = False


@dataclass(frozen=True)
class FontConfig:
    """Font size settings."""
    size_large: int = 72
    size_small: int = 18
    custom_font_path: str = None


@dataclass(frozen=True)
class LayoutConfig:
    """Grid layout settings."""
    cell_padding: int = 8
    margin: int = 50


@dataclass(frozen=True)
class CounterDisplayConfig:
    """Counter display settings."""
    enabled: bool = True
    position: str = "top"
    color: str = "white"
    format_string: str = "{count} remaining"
    margin_top: int = 30
    margin_bottom: int = 100
    reserved_height: int = 120
    pulse_on_elimination: bool = True
    pulse_scale: float = 1.3


@dataclass(frozen=True)
class AnimationConfig:
    """Animation timing and visuals."""
    elimination_duration: int = 20
    elimination_x_color: str = "#FF0000"
    elimination_x_width_ratio: float = 0.1
    elimination_x_padding_ratio: float = 0.125

    flash_on_elimination: bool = False
    flash_intensity: float = 0.15
    flash_duration: int = 5

    idle_enabled: bool = True
    idle_wave_speed: float = 0.05
    idle_wave_amount: float = 3.0
    idle_breathe_speed: float = 0.03
    idle_breathe_amount: float = 0.02


@dataclass(frozen=True)
class EntityDisplayConfig:
    """Entity display settings."""
    name_max_length: int = 12
    corner_radius: int = 12      # Rounded corners
    shadow_enabled: bool = True
    shadow_blur: int = 10        # Soft shadow
    shadow_opacity: int = 100    # Visible but not harsh

@dataclass(frozen=True)
class WinnerScreenConfig:
    """Winner celebration screen settings."""
    title_text: str = "WINNER!"
    title_color: str = "#FFD700"
    title_y_ratio: float = 0.25
    box_size_ratio: float = 0.33
    name_offset_y: int = -30


@dataclass
class AudioConfig:
    """Audio settings."""
    enabled: bool = True
    mode: str = "default"
    sound_pack: str = "default"
    sounds_dir: str = "sounds/packs"

    elimination_volume: float = 0.8
    countdown_volume: float = 1.0
    winner_volume: float = 1.0
    music_volume: float = 0.3
    melody_volume: float = 0.8

    countdown_enabled: bool = True
    countdown_thresholds: Tuple[int, ...] = (10, 5, 3)

    pitch_start: int = -6
    pitch_end: int = 6

    music_path: Optional[str] = None
    use_every_beat: bool = True
    use_every_nth_beat: int = 1
    beat_start_offset: float = 0.5

    midi_path: Optional[str] = None
    instrument: str = "piano"
    note_duration: float = 0.3


@dataclass
class SchedulerConfig:
    """Elimination timing settings."""
    elimination_interval: int = 30
    initial_delay: int = 60

    sudden_death_enabled: bool = True
    sudden_death_threshold_1: int = 10
    sudden_death_multiplier_1: int = 2
    sudden_death_threshold_2: int = 5
    sudden_death_multiplier_2: int = 4


@dataclass
class RenderConfig:
    """Aggregates all config sections."""
    canvas: CanvasConfig = None
    font: FontConfig = None
    layout: LayoutConfig = None
    counter: CounterDisplayConfig = None
    animation: AnimationConfig = None
    entity: EntityDisplayConfig = None
    winner: WinnerScreenConfig = None
    audio: AudioConfig = None
    scheduler: SchedulerConfig = None

    def __post_init__(self) -> None:
        if self.canvas is None:
            self.canvas = CanvasConfig()
        if self.font is None:
            self.font = FontConfig()
        if self.layout is None:
            self.layout = LayoutConfig()
        if self.counter is None:
            self.counter = CounterDisplayConfig()
        if self.animation is None:
            self.animation = AnimationConfig()
        if self.entity is None:
            self.entity = EntityDisplayConfig()
        if self.winner is None:
            self.winner = WinnerScreenConfig()
        if self.audio is None:
            self.audio = AudioConfig()
        if self.scheduler is None:
            self.scheduler = SchedulerConfig()
