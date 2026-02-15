"""Audio subsystem for survival countdown.

Supports multiple audio modes:
- default: Same sound each elimination
- progressive_pitch: Pitch rises with each elimination
- midi_melody: Play notes from MIDI file
- beat_sync: Sync eliminations to music beats
- beat_sync_midi: Combine beat sync with MIDI melody
"""

from .beat_detector import (
    BeatDetector,
    BeatDetectionResult,
    ManualBeatDetector,
    detect_beats
)
from .builder import AudioBuilder, AudioMode

__all__ = [
    'BeatDetector',
    'BeatDetectionResult', 
    'ManualBeatDetector',
    'detect_beats',
    'AudioBuilder',
    'AudioMode'
]
