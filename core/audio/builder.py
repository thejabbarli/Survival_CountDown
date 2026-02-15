"""Audio building - creates audio track from simulation events.

Supports multiple modes:
- DEFAULT: Same sound each elimination
- PROGRESSIVE_PITCH: Pitch rises with each elimination  
- MIDI_MELODY: Play notes from MIDI file
- BEAT_SYNC: Background music (eliminations already synced via scheduler)
- BEAT_SYNC_MIDI: Background music + MIDI melody
"""

import random
from enum import Enum
from pathlib import Path
from typing import List, Optional, Callable
from dataclasses import dataclass

from ..config import AudioConfig
from ..simulation import EliminationEvent


class AudioMode(Enum):
    """Audio mode enumeration."""
    DEFAULT = "default"
    PROGRESSIVE_PITCH = "progressive_pitch"
    MIDI_MELODY = "midi_melody"
    BEAT_SYNC = "beat_sync"
    BEAT_SYNC_MIDI = "beat_sync_midi"


@dataclass
class AudioEvent:
    """Represents a sound event at a specific time."""
    time_seconds: float
    sound_path: Optional[Path] = None
    volume: float = 1.0
    pitch_shift: int = 0  # semitones
    midi_note: Optional[int] = None  # MIDI note number for synthesis


class SoundLoader:
    """Loads sound files from sound packs."""

    def __init__(self, config: AudioConfig):
        self.config = config
        self.pack_path = Path(config.sounds_dir) / config.sound_pack
        self._cache: dict[str, List[Path]] = {}

    def _get_sound_files(self, category: str) -> List[Path]:
        """Get all sound file paths from a category folder."""
        if category in self._cache:
            return self._cache[category]

        folder = self.pack_path / category
        sounds = []

        if folder.exists():
            for file_path in folder.iterdir():
                if file_path.suffix.lower() in ('.mp3', '.wav', '.ogg'):
                    sounds.append(file_path)

        self._cache[category] = sounds
        return sounds

    def get_elimination_sound(self) -> Optional[Path]:
        """Get a random elimination sound path."""
        sounds = self._get_sound_files("elimination")
        return random.choice(sounds) if sounds else None

    def get_countdown_sound(self) -> Optional[Path]:
        """Get a random countdown sound path."""
        sounds = self._get_sound_files("countdown")
        return random.choice(sounds) if sounds else None

    def get_winner_sound(self) -> Optional[Path]:
        """Get a random winner sound path."""
        sounds = self._get_sound_files("winner")
        return random.choice(sounds) if sounds else None

    def get_background_music(self) -> Optional[Path]:
        """Get background music path if configured."""
        if self.config.music_path is None:
            return None

        music_path = Path(self.config.music_path)
        return music_path if music_path.exists() else None


class AudioBuilder:
    """
    Builds audio track from simulation events.
    
    Supports multiple modes with different behaviors.
    """

    def __init__(self, config: AudioConfig, fps: int = 60):
        self.config = config
        self.fps = fps
        self.mode = AudioMode(config.mode)
        self.sound_loader = SoundLoader(config)
        
        # Lazy load optional dependencies
        self._midi_notes: Optional[List[int]] = None

    def _frame_to_seconds(self, frame: int) -> float:
        """Convert frame number to seconds."""
        return frame / self.fps

    def _load_midi_notes(self) -> List[int]:
        """Load MIDI notes if not already loaded."""
        if self._midi_notes is not None:
            return self._midi_notes
        
        if self.config.midi_path is None:
            self._midi_notes = []
            return self._midi_notes
        
        try:
            from .midi_parser import parse_midi
            self._midi_notes = parse_midi(self.config.midi_path)
        except ImportError:
            print("Warning: mido not installed, MIDI features unavailable")
            self._midi_notes = []
        except Exception as e:
            print(f"Warning: Failed to load MIDI: {e}")
            self._midi_notes = []
        
        return self._midi_notes

    def _calculate_pitch_shift(self, elimination_index: int, total_eliminations: int) -> int:
        """Calculate pitch shift for progressive pitch mode."""
        if total_eliminations <= 1:
            return 0
        
        progress = elimination_index / (total_eliminations - 1)
        pitch_range = self.config.pitch_end - self.config.pitch_start
        return int(self.config.pitch_start + (progress * pitch_range))

    def _collect_events(
        self,
        events: List[EliminationEvent],
        winner_frame: int
    ) -> List[AudioEvent]:
        """Collect all audio events with timing."""
        audio_events = []
        total_eliminations = len(events)

        for i, event in enumerate(events):
            time_seconds = self._frame_to_seconds(event.frame)
            
            if self.mode == AudioMode.DEFAULT:
                sound_path = self.sound_loader.get_elimination_sound()
                if sound_path:
                    audio_events.append(AudioEvent(
                        time_seconds=time_seconds,
                        sound_path=sound_path,
                        volume=self.config.elimination_volume
                    ))
            
            elif self.mode == AudioMode.PROGRESSIVE_PITCH:
                sound_path = self.sound_loader.get_elimination_sound()
                if sound_path:
                    pitch = self._calculate_pitch_shift(i, total_eliminations)
                    audio_events.append(AudioEvent(
                        time_seconds=time_seconds,
                        sound_path=sound_path,
                        volume=self.config.elimination_volume,
                        pitch_shift=pitch
                    ))
            
            elif self.mode in (AudioMode.MIDI_MELODY, AudioMode.BEAT_SYNC_MIDI):
                notes = self._load_midi_notes()
                if i < len(notes):
                    audio_events.append(AudioEvent(
                        time_seconds=time_seconds,
                        volume=self.config.melody_volume,
                        midi_note=notes[i]
                    ))
                else:
                    # Fallback to regular sound if we run out of notes
                    sound_path = self.sound_loader.get_elimination_sound()
                    if sound_path:
                        audio_events.append(AudioEvent(
                            time_seconds=time_seconds,
                            sound_path=sound_path,
                            volume=self.config.elimination_volume
                        ))
            
            elif self.mode == AudioMode.BEAT_SYNC:
                # Beat sync mode: just play elimination sounds
                # (timing already handled by BeatSyncScheduler)
                sound_path = self.sound_loader.get_elimination_sound()
                if sound_path:
                    audio_events.append(AudioEvent(
                        time_seconds=time_seconds,
                        sound_path=sound_path,
                        volume=self.config.elimination_volume
                    ))

            # Countdown sounds (all modes)
            if self.config.countdown_enabled:
                if event.entities_remaining in self.config.countdown_thresholds:
                    countdown_path = self.sound_loader.get_countdown_sound()
                    if countdown_path:
                        audio_events.append(AudioEvent(
                            time_seconds=time_seconds,
                            sound_path=countdown_path,
                            volume=self.config.countdown_volume
                        ))

        # Winner sound
        winner_path = self.sound_loader.get_winner_sound()
        if winner_path:
            audio_events.append(AudioEvent(
                time_seconds=self._frame_to_seconds(winner_frame),
                sound_path=winner_path,
                volume=self.config.winner_volume
            ))

        return audio_events

    def build(
        self,
        events: List[EliminationEvent],
        total_frames: int,
        winner_frame: int
    ):
        """
        Build complete audio track.

        Args:
            events: List of elimination events from simulation
            total_frames: Total number of frames in video
            winner_frame: Frame where winner is declared

        Returns:
            CompositeAudioClip with all sounds mixed, or None if no audio
        """
        if not self.config.enabled:
            return None

        try:
            from moviepy import AudioFileClip, CompositeAudioClip, concatenate_audioclips
        except ImportError:
            print("Warning: moviepy not installed, audio disabled")
            return None

        total_duration = self._frame_to_seconds(total_frames)

        # Collect audio events
        audio_events = self._collect_events(events, winner_frame)

        music_path = self.sound_loader.get_background_music()
        
        # For beat sync modes, check if we should use music_path from config
        if self.mode in (AudioMode.BEAT_SYNC, AudioMode.BEAT_SYNC_MIDI):
            if music_path is None and self.config.music_path:
                music_path = Path(self.config.music_path)
                if not music_path.exists():
                    music_path = None

        if not audio_events and not music_path:
            return None

        clips = []

        # Add sound effects
        for event in audio_events:
            if event.sound_path:
                try:
                    clip = AudioFileClip(str(event.sound_path))
                    
                    # Apply pitch shift if needed
                    if event.pitch_shift != 0:
                        clip = self._apply_pitch_shift(clip, event.pitch_shift)
                    
                    clip = clip.with_start(event.time_seconds)
                    clip = clip.with_volume_scaled(event.volume)
                    clips.append(clip)
                except Exception as e:
                    print(f"Warning: Failed to load sound {event.sound_path}: {e}")
                    continue
            
            elif event.midi_note is not None:
                # Synthesize MIDI note
                try:
                    clip = self._synthesize_note(event.midi_note, event.time_seconds)
                    if clip:
                        clip = clip.with_volume_scaled(event.volume)
                        clips.append(clip)
                except Exception as e:
                    print(f"Warning: Failed to synthesize note: {e}")

        # Add background music
        if music_path and music_path.exists():
            try:
                music = AudioFileClip(str(music_path))

                # Loop if needed
                if music.duration < total_duration:
                    loops_needed = int(total_duration / music.duration) + 1
                    music = concatenate_audioclips([music] * loops_needed)

                # Trim to video length
                music = music.subclipped(0, total_duration)
                music = music.with_volume_scaled(self.config.music_volume)
                clips.insert(0, music)  # Music underneath
            except Exception as e:
                print(f"Warning: Failed to load music: {e}")

        if not clips:
            return None

        return CompositeAudioClip(clips)

    def _apply_pitch_shift(self, clip: 'AudioFileClip', semitones: int) -> 'AudioFileClip':
        """Apply pitch shift to audio clip."""
        try:
            import numpy as np
            
            # Simple pitch shift via speed change
            # This changes duration too - for proper pitch shift, use librosa
            factor = 2 ** (semitones / 12)
            
            # For now, just adjust playback speed
            # TODO: Use librosa for proper pitch shifting without speed change
            return clip.with_speed_scaled(factor)
        except Exception:
            return clip

    def _synthesize_note(
        self, 
        midi_note: int, 
        start_time: float
    ) -> Optional['AudioFileClip']:
        """
        Synthesize a MIDI note as audio.
        
        For now, returns None - implement with instrument samples
        or synthesis library later.
        """
        # TODO: Implement note synthesis
        # Options:
        # 1. Load pre-rendered samples from instruments/ folder
        # 2. Use pydub to generate tones
        # 3. Use a synthesis library
        return None


def create_audio_builder(
    config: AudioConfig,
    fps: int = 60
) -> AudioBuilder:
    """Factory function for audio builder."""
    return AudioBuilder(config, fps)
