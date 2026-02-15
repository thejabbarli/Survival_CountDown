"""Beat detection using librosa.

Detects beats in audio files and converts to video frame numbers.
Used for beat-synced elimination timing.

Usage:
    detector = BeatDetector(fps=60)
    result = detector.detect("song.mp3")
    
    print(f"Tempo: {result.tempo} BPM")
    print(f"Beats: {len(result.beat_frames)} at frames {result.beat_frames[:5]}...")
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union
from abc import ABC, abstractmethod


@dataclass
class BeatDetectionResult:
    """Results from beat detection."""
    tempo: float                    # BPM
    beat_times: List[float]         # seconds
    beat_frames: List[int]          # video frame numbers
    duration: float                 # audio duration in seconds
    sample_rate: int                # audio sample rate
    
    @property
    def beat_count(self) -> int:
        return len(self.beat_frames)
    
    @property
    def average_interval_frames(self) -> float:
        """Average frames between beats."""
        if len(self.beat_frames) < 2:
            return 0.0
        return (self.beat_frames[-1] - self.beat_frames[0]) / (len(self.beat_frames) - 1)


class BaseBeatDetector(ABC):
    """Abstract base for beat detection strategies."""
    
    @abstractmethod
    def detect(self, audio_path: Union[str, Path]) -> BeatDetectionResult:
        """Detect beats in audio file."""
        pass


class BeatDetector(BaseBeatDetector):
    """
    Beat detector using librosa.
    
    Librosa's beat_track uses a dynamic programming approach
    to find beat positions that maximize onset strength.
    """
    
    def __init__(self, fps: int = 60):
        self.fps = fps
    
    def detect(self, audio_path: Union[str, Path]) -> BeatDetectionResult:
        """
        Detect beats in audio file.
        
        Args:
            audio_path: Path to audio file (mp3, wav, etc.)
            
        Returns:
            BeatDetectionResult with tempo, beat times, and frame numbers
        """
        try:
            import librosa
        except ImportError:
            raise ImportError(
                "librosa is required for beat detection. "
                "Install with: pip install librosa"
            )
        
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load audio
        y, sr = librosa.load(str(audio_path))
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Detect tempo and beats
        tempo, beat_frames_librosa = librosa.beat.beat_track(y=y, sr=sr)
        
        # Handle tempo being an array (librosa returns ndarray)
        if hasattr(tempo, '__len__'):
            tempo = float(tempo[0]) if len(tempo) > 0 else 120.0
        else:
            tempo = float(tempo)
        
        # Convert librosa frames to time
        beat_times = librosa.frames_to_time(beat_frames_librosa, sr=sr)
        beat_times = [float(t) for t in beat_times]
        
        # Convert to video frames
        beat_video_frames = [int(t * self.fps) for t in beat_times]
        
        return BeatDetectionResult(
            tempo=tempo,
            beat_times=beat_times,
            beat_frames=beat_video_frames,
            duration=duration,
            sample_rate=sr
        )
    
    def detect_with_options(
        self,
        audio_path: Union[str, Path],
        start_time: float = 0.0,
        end_time: Optional[float] = None,
        hop_length: int = 512
    ) -> BeatDetectionResult:
        """
        Detect beats with more control over the process.
        
        Args:
            audio_path: Path to audio file
            start_time: Start analysis at this time (seconds)
            end_time: End analysis at this time (seconds), None for full track
            hop_length: Hop length for beat tracking (affects precision)
        """
        try:
            import librosa
        except ImportError:
            raise ImportError("librosa is required for beat detection.")
        
        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load with duration/offset if specified
        y, sr = librosa.load(
            str(audio_path),
            offset=start_time,
            duration=(end_time - start_time) if end_time else None
        )
        
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Detect with custom hop length
        tempo, beat_frames_librosa = librosa.beat.beat_track(
            y=y, sr=sr, hop_length=hop_length
        )
        
        if hasattr(tempo, '__len__'):
            tempo = float(tempo[0]) if len(tempo) > 0 else 120.0
        else:
            tempo = float(tempo)
        
        # Convert to time (adjusted for start_time offset)
        beat_times = librosa.frames_to_time(beat_frames_librosa, sr=sr, hop_length=hop_length)
        beat_times = [float(t) + start_time for t in beat_times]
        
        # Convert to video frames
        beat_video_frames = [int(t * self.fps) for t in beat_times]
        
        return BeatDetectionResult(
            tempo=tempo,
            beat_times=beat_times,
            beat_frames=beat_video_frames,
            duration=duration + start_time,
            sample_rate=sr
        )


class ManualBeatDetector(BaseBeatDetector):
    """
    Manual beat detector for testing or when tempo is known.
    Generates evenly-spaced beats based on BPM.
    """
    
    def __init__(self, fps: int = 60, tempo: float = 120.0, offset: float = 0.0):
        """
        Args:
            fps: Video frame rate
            tempo: Beats per minute
            offset: Time offset for first beat (seconds)
        """
        self.fps = fps
        self.tempo = tempo
        self.offset = offset
    
    def detect(self, audio_path: Union[str, Path]) -> BeatDetectionResult:
        """Generate beats based on known tempo."""
        try:
            import librosa
            y, sr = librosa.load(str(audio_path))
            duration = librosa.get_duration(y=y, sr=sr)
        except ImportError:
            # Fallback: estimate duration or use a default
            import wave
            try:
                with wave.open(str(audio_path), 'rb') as w:
                    frames = w.getnframes()
                    sr = w.getframerate()
                    duration = frames / sr
            except Exception:
                duration = 180.0  # 3 minute default
                sr = 44100
        
        # Calculate beat times
        beat_interval = 60.0 / self.tempo
        beat_times = []
        t = self.offset
        while t < duration:
            beat_times.append(t)
            t += beat_interval
        
        beat_frames = [int(t * self.fps) for t in beat_times]
        
        return BeatDetectionResult(
            tempo=self.tempo,
            beat_times=beat_times,
            beat_frames=beat_frames,
            duration=duration,
            sample_rate=sr
        )


def detect_beats(
    audio_path: Union[str, Path],
    fps: int = 60
) -> BeatDetectionResult:
    """
    Convenience function for simple beat detection.
    
    Args:
        audio_path: Path to audio file
        fps: Video frame rate
        
    Returns:
        BeatDetectionResult
    """
    detector = BeatDetector(fps=fps)
    return detector.detect(audio_path)
