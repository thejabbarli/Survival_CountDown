"""Beat detection using librosa."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Union


@dataclass
class BeatDetectionResult:
    """Results from beat detection."""
    tempo: float
    beat_times: List[float]
    beat_frames: List[int]
    duration: float
    sample_rate: int
    
    @property
    def beat_count(self) -> int:
        return len(self.beat_frames)
    
    @property
    def average_interval_frames(self) -> float:
        """Average frames between beats."""
        if len(self.beat_frames) < 2:
            return 30  # Default fallback
        intervals = [
            self.beat_frames[i+1] - self.beat_frames[i] 
            for i in range(len(self.beat_frames) - 1)
        ]
        return sum(intervals) / len(intervals)


class BeatDetector:
    """Beat detector using librosa."""
    
    def __init__(self, fps: int = 60):
        self.fps = fps
    
    def detect(self, audio_path: Union[str, Path]) -> BeatDetectionResult:
        """Detect beats in audio file."""
        try:
            import librosa
        except ImportError:
            raise ImportError("librosa is required for beat detection")

        y, sr = librosa.load(str(audio_path))
        tempo, beat_frames_audio = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames_audio, sr=sr)
        beat_frames_video = [int(t * self.fps) for t in beat_times]
        duration = librosa.get_duration(y=y, sr=sr)

        return BeatDetectionResult(
            tempo=float(tempo),
            beat_times=list(beat_times),
            beat_frames=beat_frames_video,
            duration=duration,
            sample_rate=sr
        )


def detect_beats(audio_path: Union[str, Path], fps: int = 60) -> BeatDetectionResult:
    """Convenience function for beat detection."""
    detector = BeatDetector(fps=fps)
    return detector.detect(audio_path)
