"""Audio configuration."""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class AudioConfig:
    """Audio settings."""
    enabled: bool = True
    mode: str = "default"
    
    sound_pack: str = "default"
    elimination_sound: str = "pop.mp3"
    
    pitch_start: float = -6.0
    pitch_end: float = 6.0
    
    midi_file: Optional[str] = None
    instrument: str = "piano"
    note_duration: float = 0.3
    
    music_file: Optional[str] = None
    music_path: Optional[str] = None
    beats_file: Optional[str] = None
    beats_fps: int = 60
    use_every_beat: bool = True
    start_offset: float = 0.5
    
    elimination_volume: float = 0.8
    melody_volume: float = 0.8
    countdown_volume: float = 1.0
    winner_volume: float = 1.0
    music_volume: float = 0.3
    
    countdown_enabled: bool = True
    countdown_thresholds: List[int] = field(default_factory=lambda: [10, 5, 3])
    
    winner_sound: str = "fanfare.mp3"
