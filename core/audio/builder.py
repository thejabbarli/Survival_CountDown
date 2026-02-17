"""Audio builder for creating sound tracks."""

import random
from enum import Enum
from pathlib import Path
from typing import List, Optional

from ..config import AudioConfig
from ..simulation import EliminationEvent


class AudioMode(Enum):
    """Audio generation modes."""
    DEFAULT = "default"
    PROGRESSIVE_PITCH = "progressive_pitch"
    MIDI_MELODY = "midi_melody"
    BEAT_SYNC = "beat_sync"


class AudioBuilder:
    """Builds audio tracks for videos."""

    def __init__(
        self,
        config: AudioConfig,
        fps: int = 60
    ):
        self.config = config
        self.fps = fps
        self.sounds_dir = Path("sounds")

    def build(
        self,
        events: List[EliminationEvent],
        total_frames: int,
        winner_frame: int = None,
        music_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Build audio track with elimination sounds and music.

        Args:
            events: List of elimination events
            total_frames: Total number of frames in video
            winner_frame: Frame when winner screen starts
            music_path: Optional path to background music

        Returns:
            Path to generated audio file, or None if no audio
        """
        if not self.config.enabled:
            return None

        try:
            from pydub import AudioSegment
        except ImportError:
            print("  WARNING: pydub not installed. No sound effects.")
            # Fall back to just music
            if music_path is None and self.config.music_path:
                music_path = Path(self.config.music_path)
            if music_path and music_path.exists():
                return music_path
            return None

        # Calculate total duration in milliseconds
        duration_ms = int((total_frames / self.fps) * 1000)

        # Create silent base track
        audio = AudioSegment.silent(duration=duration_ms)

        # Load elimination sounds
        elim_sounds = self._load_elimination_sounds()

        # Add elimination sounds at event times
        for event in events:
            time_ms = int((event.frame / self.fps) * 1000)

            if elim_sounds:
                sound = random.choice(elim_sounds)
                # Apply volume
                sound = sound + (20 * (self.config.elimination_volume - 1))
                audio = audio.overlay(sound, position=time_ms)

        # Add winner sound
        if winner_frame is not None:
            winner_sound = self._load_winner_sound()
            if winner_sound:
                time_ms = int((winner_frame / self.fps) * 1000)
                winner_sound = winner_sound + (20 * (self.config.winner_volume - 1))
                audio = audio.overlay(winner_sound, position=time_ms)

        # Mix with background music
        if music_path is None and self.config.music_path:
            music_path = Path(self.config.music_path)

        if music_path and music_path.exists():
            try:
                music = AudioSegment.from_file(str(music_path))
                # Adjust music volume
                music = music + (20 * (self.config.music_volume - 1))
                # Trim or loop music to match duration
                if len(music) < duration_ms:
                    # Loop music
                    loops_needed = (duration_ms // len(music)) + 1
                    music = music * loops_needed
                music = music[:duration_ms]
                # Mix music with effects
                audio = music.overlay(audio)
            except Exception as e:
                print(f"  WARNING: Could not load music: {e}")

        # Export to temp file
        output_path = Path("output") / "_temp_audio.mp3"
        output_path.parent.mkdir(exist_ok=True)
        audio.export(str(output_path), format="mp3")

        return output_path

    def _load_elimination_sounds(self) -> List:
        """Load elimination sound effects from sound pack."""
        try:
            from pydub import AudioSegment
        except ImportError:
            return []

        sounds = []
        pack_dir = self.sounds_dir / "packs" / self.config.sound_pack / "elimination"

        if pack_dir.exists():
            for ext in ['*.wav', '*.mp3', '*.ogg']:
                for sound_file in pack_dir.glob(ext):
                    try:
                        sound = AudioSegment.from_file(str(sound_file))
                        sounds.append(sound)
                    except Exception:
                        pass

        # Try single file
        if not sounds:
            single_file = self.sounds_dir / "packs" / self.config.sound_pack / self.config.elimination_sound
            if single_file.exists():
                try:
                    sounds.append(AudioSegment.from_file(str(single_file)))
                except Exception:
                    pass

        return sounds

    def _load_winner_sound(self):
        """Load winner celebration sound."""
        try:
            from pydub import AudioSegment
        except ImportError:
            return None

        winner_file = self.sounds_dir / "packs" / self.config.sound_pack / "winner" / self.config.winner_sound
        if not winner_file.exists():
            winner_file = self.sounds_dir / "packs" / self.config.sound_pack / self.config.winner_sound

        if winner_file.exists():
            try:
                return AudioSegment.from_file(str(winner_file))
            except Exception:
                pass

        return None
