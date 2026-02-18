"""Audio builder for creating sound tracks."""

import random
import math
from enum import Enum
from pathlib import Path
from typing import List, Optional, Set

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
        music_path: Optional[Path] = None,
        spotlight_tick_frames: List[int] = None,
        spotlight_lock_frames: List[int] = None,
        spotlight_tick_sound: str = None,
        spotlight_lock_sound: str = None,
    ) -> Optional[Path]:
        """Build audio track with elimination sounds and music.

        Args:
            events: List of elimination events
            total_frames: Total number of frames in video
            winner_frame: Frame when winner screen starts
            music_path: Optional path to background music
            spotlight_tick_frames: Frames where spotlight moves (tick sound)
            spotlight_lock_frames: Frames where spotlight locks on victim (lock sound)
            spotlight_tick_sound: Filename for tick sound (e.g. 'tick.wav')
            spotlight_lock_sound: Filename for lock sound (e.g. 'lock_sound.mp3')

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

        # Add spotlight tick sounds
        if spotlight_tick_frames:
            audio = self._add_spotlight_sounds(
                audio,
                spotlight_tick_frames,
                spotlight_lock_frames or [],
                spotlight_tick_sound,
                spotlight_lock_sound
            )

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

    def _add_spotlight_sounds(
        self,
        audio,
        tick_frames: List[int],
        lock_frames: List[int],
        tick_filename: str = None,
        lock_filename: str = None
    ):
        """Add spotlight tick/lock sounds to audio.

        Creates a roulette wheel effect:
        - Fast ticks slow down over time
        - Pitch drops as it slows (like real wheel)
        - Lock sound is deeper/longer
        """
        try:
            from pydub import AudioSegment
        except ImportError:
            return audio

        # Try to load custom sounds first
        tick_sound = self._load_spotlight_sound('tick', tick_filename)

        # Only load/generate lock sound if not explicitly disabled
        lock_sound = None
        if lock_filename != "":  # Empty string = disabled
            lock_sound = self._load_spotlight_sound('lock', lock_filename)
            if lock_sound is None:
                lock_sound = self._generate_lock_sound()

        # Generate synthetic tick if not found
        if tick_sound is None:
            tick_sound = self._generate_tick_sound()

        if tick_sound is None:
            return audio

        lock_frame_set = set(lock_frames)

        # Calculate intervals between ticks to detect speed
        intervals = []
        for i in range(1, len(tick_frames)):
            intervals.append(tick_frames[i] - tick_frames[i-1])

        for i, frame in enumerate(tick_frames):
            time_ms = int((frame / self.fps) * 1000)

            # Choose sound type
            if frame in lock_frame_set and lock_sound:
                sound = lock_sound
                volume_db = -6  # Louder lock
            else:
                sound = tick_sound
                volume_db = -12  # Quieter tick

            # Pitch shift based on speed (slower = lower pitch)
            # This creates the "slowing wheel" effect
            if i < len(intervals) and intervals[i] > 0:
                interval = intervals[i]
                # Fast tick (~2 frames apart) = high pitch (1.3x)
                # Slow tick (~15 frames apart) = low pitch (0.6x)
                pitch_factor = 1.3 - (interval / 25.0)
                pitch_factor = max(0.6, min(1.3, pitch_factor))

                if abs(pitch_factor - 1.0) > 0.05:
                    sound = self._pitch_shift(sound, pitch_factor)

            sound = sound + volume_db
            audio = audio.overlay(sound, position=time_ms)

        return audio

    def _pitch_shift(self, sound, factor: float):
        """Shift pitch by changing sample rate.

        factor > 1.0 = higher pitch
        factor < 1.0 = lower pitch
        """
        try:
            new_sample_rate = int(sound.frame_rate * factor)
            shifted = sound._spawn(sound.raw_data, overrides={
                'frame_rate': new_sample_rate
            })
            return shifted.set_frame_rate(sound.frame_rate)
        except Exception:
            return sound

    def _load_spotlight_sound(self, sound_type: str, filename: str = None):
        """Load spotlight sound from pack (tick or lock).

        Args:
            sound_type: 'tick' or 'lock' (fallback search)
            filename: Specific filename from config (e.g. 'lock_sound.mp3')
        """
        try:
            from pydub import AudioSegment
        except ImportError:
            return None

        spotlight_dir = self.sounds_dir / "packs" / self.config.sound_pack / "spotlight"

        if not spotlight_dir.exists():
            return None

        # Try specific filename from config first
        if filename:
            sound_file = spotlight_dir / filename
            if sound_file.exists():
                try:
                    print(f"  Loading spotlight sound: {sound_file}")
                    return AudioSegment.from_file(str(sound_file))
                except Exception as e:
                    print(f"  WARNING: Could not load {sound_file}: {e}")

        # Fallback: search for any file matching sound_type
        for ext in ['.wav', '.mp3', '.ogg']:
            sound_file = spotlight_dir / f"{sound_type}{ext}"
            if sound_file.exists():
                try:
                    return AudioSegment.from_file(str(sound_file))
                except Exception:
                    pass

        # Fallback: any file containing sound_type in name
        for f in spotlight_dir.iterdir():
            if sound_type in f.stem.lower():
                try:
                    return AudioSegment.from_file(str(f))
                except Exception:
                    pass

        return None

    def _generate_tick_sound(self):
        """Generate synthetic roulette tick sound.

        Short click with quick attack and decay.
        Sounds like ball hitting wheel dividers.
        """
        try:
            from pydub import AudioSegment
            from pydub.generators import Sine
        except ImportError:
            return None

        try:
            # Sharp attack tone
            tick = Sine(1200).to_audio_segment(duration=15)

            # Add click transient (higher frequency)
            click = Sine(2400).to_audio_segment(duration=8) - 6
            tick = tick.overlay(click)

            # Quick fade out
            tick = tick.fade_out(12)

            # Reduce volume
            tick = tick - 8

            return tick
        except Exception:
            return None

    def _generate_lock_sound(self):
        """Generate synthetic lock/stop sound.

        Deeper, slightly longer - signals final selection.
        """
        try:
            from pydub import AudioSegment
            from pydub.generators import Sine
        except ImportError:
            return None

        try:
            # Lower base tone
            lock = Sine(600).to_audio_segment(duration=60)

            # Add sub bass
            sub = Sine(300).to_audio_segment(duration=60) - 6
            lock = lock.overlay(sub)

            # Add high click for attack
            click = Sine(1500).to_audio_segment(duration=15) - 3
            lock = lock.overlay(click)

            # Fade out
            lock = lock.fade_in(3).fade_out(40)

            # Volume
            lock = lock - 4

            return lock
        except Exception:
            return None

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
