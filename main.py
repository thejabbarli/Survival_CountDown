"""Main entry point for Survival Countdown.

Supports multiple audio modes:
- default: Same sound each elimination
- progressive_pitch: Pitch rises with each elimination
- beat_sync: Sync eliminations to music beats
- midi_melody: Play notes from MIDI file
- beat_sync_midi: Combined beat sync + MIDI

Usage:
    # Basic (interval-based)
    python main.py
    
    # Beat sync mode
    python main.py --mode beat_sync --music path/to/song.mp3
    
    # MIDI melody mode
    python main.py --mode midi_melody --midi path/to/melody.mid
"""

import argparse
import yaml
from pathlib import Path
from datetime import datetime

from core import (
    Project,
    Simulation,
    Renderer,
    Exporter,
    AudioBuilder,
    RenderConfig,
    CanvasConfig,
    LayoutConfig,
    CounterDisplayConfig,
    AudioConfig,
    SchedulerConfig,
    IntervalScheduler,
    BeatSyncScheduler,
    detect_beats
)


def load_config(config_path: Path = Path("config.yaml")) -> dict:
    """Load configuration from YAML file."""
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Survival Countdown Video Generator")
    
    parser.add_argument(
        "--project", "-p",
        default="assets/countries",
        help="Path to project folder"
    )
    parser.add_argument(
        "--count", "-c",
        type=int,
        default=None,
        help="Number of entities to use (default: from config or 16)"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["default", "progressive_pitch", "beat_sync", "midi_melody", "beat_sync_midi"],
        default=None,
        help="Audio mode"
    )
    parser.add_argument(
        "--music",
        type=str,
        default=None,
        help="Path to music file for beat sync"
    )
    parser.add_argument(
        "--midi",
        type=str,
        default=None,
        help="Path to MIDI file for melody mode"
    )
    parser.add_argument(
        "--beats",
        type=str,
        default=None,
        help="Path to beats.txt from tap_beats.py"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output filename (without extension)"
    )
    
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    # Load config
    config = load_config()
    video_cfg = config.get('video', {})
    sim_cfg = config.get('simulation', {})
    vis_cfg = config.get('visuals', {})
    out_cfg = config.get('output', {})
    audio_cfg = config.get('audio', {})
    sudden_death_cfg = sim_cfg.get('sudden_death', {})

    # Load project
    project_path = Path(args.project)
    project = Project(project_path)
    print(f"Loaded project: {project.name} ({len(project.entities)} entities)")

    # Get entities
    entity_count = args.count or sim_cfg.get('entity_count', 16)
    if entity_count == "all":
        entity_count = None
    entities = project.get_entities(count=entity_count)
    print(f"Using {len(entities)} entities")

    # Setup fps
    fps = video_cfg.get('fps', 60)
    
    # Determine audio mode
    audio_mode = args.mode or audio_cfg.get('mode', 'default')
    music_path = args.music or audio_cfg.get('music_path')
    midi_path = args.midi or audio_cfg.get('midi_path')

    # Load manual beats if provided
    manual_frames = None
    if args.beats:
        print(f"Loading manual beats from: {args.beats}")
        manual_frames = []
        with open(args.beats, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    manual_frames.append(int(line))
        print(f"  Loaded {len(manual_frames)} beat frames")

    # Create scheduler based on mode
    scheduler = None
    beat_info = None

    if manual_frames:
        # Manual beats from tap_beats.py
        from core import FrameListScheduler
        scheduler = FrameListScheduler(manual_frames)
        print(f"Using manual beat scheduler")

    elif audio_mode in ('beat_sync', 'beat_sync_midi'):
        if music_path is None:
            print("Error: Beat sync mode requires --music path")
            return

        print(f"Detecting beats in: {music_path}")
        beat_result = detect_beats(music_path, fps=fps)
        print(f"  Tempo: {beat_result.tempo:.1f} BPM")
        print(f"  Beats detected: {beat_result.beat_count}")

        scheduler = BeatSyncScheduler(
            beat_frames=beat_result.beat_frames,
            entity_count=len(entities),
            start_offset_frames=int(0.5 * fps)
        )
        beat_info = beat_result

        print(f"  Usable beats: {scheduler.usable_beat_count}")
        print(f"  Eliminations needed: {len(entities) - 1}")

    else:
        # Interval-based scheduler
        scheduler_config = SchedulerConfig(
            elimination_interval=sim_cfg.get('elimination_interval', 30),
            initial_delay=fps,
            sudden_death_enabled=sudden_death_cfg.get('enabled', True),
            sudden_death_threshold_1=sudden_death_cfg.get('threshold_1', 10),
            sudden_death_multiplier_1=sudden_death_cfg.get('multiplier_1', 2),
            sudden_death_threshold_2=sudden_death_cfg.get('threshold_2', 5),
            sudden_death_multiplier_2=sudden_death_cfg.get('multiplier_2', 4)
        )
        scheduler = IntervalScheduler(len(entities), scheduler_config)

    # Create simulation
    simulation = Simulation(
        entities=entities,
        scheduler=scheduler,
        fps=fps
    )

    # Run simulation
    print("Running simulation...")
    result = simulation.run(seed=args.seed)
    print(f"Winner: {result.winner.name}")
    print(f"Total eliminations: {len(result.events)}")
    print(f"Total frames: {result.total_frames}")

    # Create render config
    render_config = RenderConfig(
        canvas=CanvasConfig(
            width=video_cfg.get('width', 1080),
            height=video_cfg.get('height', 1920),
            background_color=vis_cfg.get('background_color', '#1a1a2e')
        ),
        layout=LayoutConfig(
            cell_padding=vis_cfg.get('cell_padding', 8)
        ),
        counter=CounterDisplayConfig(
            enabled=vis_cfg.get('show_counter', True),
            position=vis_cfg.get('counter_position', 'top')
        )
    )
    renderer = Renderer(render_config)

    # Render all frames
    print(f"Rendering {result.total_frames} frames...")
    frames = []

    winner_start_frame = result.total_frames - simulation.winner_celebration_frames

    for frame_num in range(result.total_frames):
        if frame_num % 60 == 0:
            print(f"  Frame {frame_num}/{result.total_frames}")

        if frame_num >= winner_start_frame:
            frame = renderer.render_winner_frame(result.winner)
        else:
            frame = renderer.render_frame(entities, frame_num)

        frames.append(frame)

    # Build audio
    audio = None
    if audio_cfg.get('enabled', True):
        print(f"Building audio (mode: {audio_mode})...")
        
        audio_config = AudioConfig(
            enabled=True,
            mode=audio_mode,
            sound_pack=audio_cfg.get('sound_pack', 'default'),
            elimination_volume=audio_cfg.get('volume', {}).get('elimination', 0.8),
            countdown_volume=audio_cfg.get('volume', {}).get('countdown', 1.0),
            winner_volume=audio_cfg.get('volume', {}).get('winner', 1.0),
            music_volume=audio_cfg.get('volume', {}).get('music', 0.3),
            melody_volume=audio_cfg.get('volume', {}).get('melody', 0.8),
            countdown_enabled=audio_cfg.get('countdown_enabled', True),
            countdown_thresholds=tuple(audio_cfg.get('countdown_thresholds', [10, 5, 3])),
            music_path=music_path,
            midi_path=midi_path,
            pitch_start=audio_cfg.get('pitch_start', -6),
            pitch_end=audio_cfg.get('pitch_end', 6)
        )

        audio_builder = AudioBuilder(audio_config, fps=fps)
        audio = audio_builder.build(
            events=result.events,
            total_frames=result.total_frames,
            winner_frame=winner_start_frame
        )

        if audio:
            print("  Audio track created")
        else:
            print("  No sounds found, video will be silent")

    # Export video
    print("Exporting video...")
    exporter = Exporter(
        fps=fps,
        output_dir=Path(out_cfg.get('directory', 'output'))
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = args.output or f"{project.name}_{timestamp}"

    output_path = exporter.export(frames, filename, audio=audio)
    print(f"Done! Video saved to: {output_path}")


if __name__ == "__main__":
    main()
