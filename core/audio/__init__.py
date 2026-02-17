"""Audio subsystem for survival countdown."""

from .beat_detector import BeatDetector, BeatDetectionResult, detect_beats
from .builder import AudioBuilder, AudioMode

__all__ = [
    'BeatDetector',
    'BeatDetectionResult',
    'detect_beats',
    'AudioBuilder',
    'AudioMode',
]
