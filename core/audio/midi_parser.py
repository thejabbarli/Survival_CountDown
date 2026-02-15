"""MIDI file parsing.

Extracts note sequence from MIDI files for melody playback.

Usage:
    notes = parse_midi("melody.mid")
    # Returns list of MIDI note numbers [60, 62, 64, ...]
    
    # Or use the class for more control
    parser = MidiParser()
    result = parser.parse("melody.mid")
    for note in result.notes:
        print(f"{note.name} (MIDI {note.pitch})")
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union


@dataclass
class Note:
    """Represents a single MIDI note."""
    pitch: int           # MIDI note number (60 = C4)
    velocity: int        # 0-127 (loudness)
    name: str            # Human readable: "C4", "D#5", etc.
    duration_ticks: int = 0  # Duration in MIDI ticks


@dataclass
class MidiParseResult:
    """Result of parsing a MIDI file."""
    notes: List[Note]
    tempo: float         # BPM (first tempo found)
    ticks_per_beat: int
    track_count: int
    
    @property
    def note_count(self) -> int:
        return len(self.notes)
    
    @property
    def pitches(self) -> List[int]:
        """Just the pitch values."""
        return [n.pitch for n in self.notes]


NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def pitch_to_name(pitch: int) -> str:
    """Convert MIDI pitch to note name."""
    octave = (pitch // 12) - 1
    note = NOTE_NAMES[pitch % 12]
    return f"{note}{octave}"


def name_to_pitch(name: str) -> int:
    """Convert note name to MIDI pitch."""
    # Parse name like "C4", "D#5", "Eb3"
    name = name.strip()
    
    if len(name) < 2:
        raise ValueError(f"Invalid note name: {name}")
    
    # Handle sharps and flats
    if len(name) >= 3 and name[1] in '#b':
        note_part = name[:2]
        octave_part = name[2:]
    else:
        note_part = name[0]
        octave_part = name[1:]
    
    # Normalize flats to sharps
    flat_to_sharp = {
        'Db': 'C#', 'Eb': 'D#', 'Fb': 'E', 'Gb': 'F#',
        'Ab': 'G#', 'Bb': 'A#', 'Cb': 'B'
    }
    note_part = flat_to_sharp.get(note_part, note_part)
    
    try:
        note_index = NOTE_NAMES.index(note_part.upper())
        octave = int(octave_part)
    except (ValueError, IndexError):
        raise ValueError(f"Invalid note name: {name}")
    
    return (octave + 1) * 12 + note_index


class MidiParser:
    """Parses MIDI files to extract note sequences."""
    
    def __init__(self, track_index: Optional[int] = None):
        """
        Args:
            track_index: Specific track to parse (None = all tracks)
        """
        self.track_index = track_index
    
    def parse(self, midi_path: Union[str, Path]) -> MidiParseResult:
        """
        Parse MIDI file and extract notes.
        
        Args:
            midi_path: Path to .mid file
            
        Returns:
            MidiParseResult with notes and metadata
        """
        try:
            import mido
        except ImportError:
            raise ImportError(
                "mido is required for MIDI parsing. "
                "Install with: pip install mido"
            )
        
        midi_path = Path(midi_path)
        if not midi_path.exists():
            raise FileNotFoundError(f"MIDI file not found: {midi_path}")
        
        mid = mido.MidiFile(str(midi_path))
        
        notes = []
        tempo = 120.0  # default BPM
        
        # Determine which tracks to process
        if self.track_index is not None:
            if self.track_index >= len(mid.tracks):
                raise ValueError(f"Track {self.track_index} not found (file has {len(mid.tracks)} tracks)")
            tracks_to_process = [mid.tracks[self.track_index]]
        else:
            tracks_to_process = mid.tracks
        
        # Parse tracks
        for track in tracks_to_process:
            for msg in track:
                # Get tempo
                if msg.type == 'set_tempo':
                    tempo = mido.tempo2bpm(msg.tempo)
                
                # Get notes
                if msg.type == 'note_on' and msg.velocity > 0:
                    note = Note(
                        pitch=msg.note,
                        velocity=msg.velocity,
                        name=pitch_to_name(msg.note)
                    )
                    notes.append(note)
        
        return MidiParseResult(
            notes=notes,
            tempo=tempo,
            ticks_per_beat=mid.ticks_per_beat,
            track_count=len(mid.tracks)
        )
    
    def parse_with_timing(self, midi_path: Union[str, Path]) -> List[tuple]:
        """
        Parse MIDI with absolute timing.
        
        Returns:
            List of (time_seconds, Note) tuples
        """
        try:
            import mido
        except ImportError:
            raise ImportError("mido is required for MIDI parsing.")
        
        midi_path = Path(midi_path)
        mid = mido.MidiFile(str(midi_path))
        
        timed_notes = []
        
        for track in mid.tracks:
            absolute_time = 0
            for msg in track:
                absolute_time += msg.time
                
                if msg.type == 'note_on' and msg.velocity > 0:
                    time_seconds = mido.tick2second(
                        absolute_time, 
                        mid.ticks_per_beat, 
                        500000  # default tempo (120 BPM)
                    )
                    note = Note(
                        pitch=msg.note,
                        velocity=msg.velocity,
                        name=pitch_to_name(msg.note)
                    )
                    timed_notes.append((time_seconds, note))
        
        # Sort by time
        timed_notes.sort(key=lambda x: x[0])
        return timed_notes


def parse_midi(midi_path: Union[str, Path]) -> List[int]:
    """
    Simple function to extract note pitches from MIDI.
    
    Args:
        midi_path: Path to .mid file
        
    Returns:
        List of MIDI note numbers
    """
    parser = MidiParser()
    result = parser.parse(midi_path)
    return result.pitches


def create_test_midi(
    output_path: Union[str, Path],
    notes: List[str] = None,
    tempo: int = 120
) -> Path:
    """
    Create a simple test MIDI file.
    
    Args:
        output_path: Where to save the file
        notes: List of note names ["C4", "E4", "G4", ...]
        tempo: BPM
        
    Returns:
        Path to created file
    """
    try:
        import mido
    except ImportError:
        raise ImportError("mido is required to create MIDI files.")
    
    if notes is None:
        # Default: C major scale
        notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
    
    output_path = Path(output_path)
    
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Set tempo
    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo)))
    
    # Add notes
    ticks_per_note = 480  # quarter note
    
    for note_name in notes:
        pitch = name_to_pitch(note_name)
        track.append(mido.Message('note_on', note=pitch, velocity=100, time=0))
        track.append(mido.Message('note_off', note=pitch, velocity=0, time=ticks_per_note))
    
    mid.save(str(output_path))
    return output_path
