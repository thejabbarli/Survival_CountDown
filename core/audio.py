"""Audio building - creates audio track from simulation events."""

import random
from pathlib import Path
from typing import List, Optional

from moviepy import AudioFileClip, CompositeAudioClip, concatenate_audioclips

from .config import AudioConfig
from .simulation import EliminationEvent


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


class AudioEvent:
    """Represents a sound event at a specific time."""

    def __init__(self, time_seconds: float, sound_path: Path, volume: float = 1.0):
        self.time_seconds = time_seconds
        self.sound_path = sound_path
        self.volume = volume


class AudioBuilder:
    """Builds audio track from simulation events."""

    def __init__(self, config: AudioConfig, fps: int = 60):
        self.config = config
        self.fps = fps
        self.sound_loader = SoundLoader(config)

    def _frame_to_seconds(self, frame: int) -> float:
        """Convert frame number to seconds."""
        return frame / self.fps

    def _collect_events(
        self,
        events: List[EliminationEvent],
        winner_frame: int
    ) -> List[AudioEvent]:
        """Collect all audio events with timing."""
        audio_events = []

        # Elimination sounds
        for event in events:
            sound_path = self.sound_loader.get_elimination_sound()
            if sound_path:
                audio_events.append(AudioEvent(
                    time_seconds=self._frame_to_seconds(event.frame),
                    sound_path=sound_path,
                    volume=self.config.elimination_volume
                ))

            # Countdown sounds
            if self.config.countdown_enabled:
                if event.entities_remaining in self.config.countdown_thresholds:
                    countdown_path = self.sound_loader.get_countdown_sound()
                    if countdown_path:
                        audio_events.append(AudioEvent(
                            time_seconds=self._frame_to_seconds(event.frame),
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
    ) -> Optional[CompositeAudioClip]:
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

        total_duration = self._frame_to_seconds(total_frames)

        # Collect audio events
        audio_events = self._collect_events(events, winner_frame)

        if not audio_events and not self.sound_loader.get_background_music():
            return None

        clips = []

        # Add sound effects
        for event in audio_events:
            try:
                clip = AudioFileClip(str(event.sound_path))
                clip = clip.with_start(event.time_seconds)
                clip = clip.with_volume_scaled(event.volume)
                clips.append(clip)
            except Exception:
                continue

        # Add background music
        music_path = self.sound_loader.get_background_music()
        if music_path:
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
            except Exception:
                pass

        if not clips:
            return None

        return CompositeAudioClip(clips)
