"""Main entry point for Survival Countdown."""

import time
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
    AnimationConfig,
    EntityDisplayConfig,
    AudioConfig,
    FrameListScheduler,
    ModernFadeAnimation
)
from core.audio import BeatDetector
from core.idle_animation import IdleAnimator, set_idle_animator


def load_config(config_path: Path = Path("config.yaml")) -> dict:
    """Load configuration from YAML file."""
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def main() -> None:
    # Load config
    config = load_config()
    video_cfg = config.get('video', {})
    sim_cfg = config.get('simulation', {})
    vis_cfg = config.get('visuals', {})
    out_cfg = config.get('output', {})
    audio_cfg = config.get('audio', {})
    sudden_death_cfg = sim_cfg.get('sudden_death', {})

    # Load project
    project_path = Path("assets/countries")
    project = Project(project_path)
    print(f"Loaded project: {project.name} ({len(project.entities)} entities)")

    # Get entities
    entity_count = sim_cfg.get('entity_count', 16)
    if entity_count == "all":
        entity_count = None
    entities = project.get_entities(count=entity_count)
    print(f"Using {len(entities)} entities")

    # FPS and resolution
    fps = video_cfg.get('fps', 60)
    width = video_cfg.get('width', 1080)
    height = video_cfg.get('height', 1920)

    # ========================================
    # SCHEDULER (manual beats, beat sync, or interval)
    # ========================================

    audio_mode = audio_cfg.get('mode', 'default')
    music_path = audio_cfg.get('music_path')
    beats_file = audio_cfg.get('beats_file')
    scheduler = None

    # Option 1: Manual beats file
    if beats_file:
        beats_path = Path(beats_file)
        if beats_path.exists():
            print(f"\nLoading manual beats from: {beats_path.name}")
            with open(beats_path, 'r') as f:
                all_beats = [int(line.strip()) for line in f if line.strip().isdigit()]

            # Convert FPS if needed
            beats_fps = audio_cfg.get('beats_fps', fps)
            if beats_fps != fps:
                all_beats = [int(b * fps / beats_fps) for b in all_beats]
                print(f"Converted beats from {beats_fps}fps to {fps}fps")

            # Only use as many beats as we need
            num_eliminations = len(entities) - 1
            elimination_frames = all_beats[:num_eliminations]
            print(f"Using {len(elimination_frames)} of {len(all_beats)} beats")

            scheduler = FrameListScheduler(elimination_frames)
        else:
            print(f"WARNING: Beats file not found: {beats_file}")

    # Option 2: Auto beat detection
    elif audio_mode == 'beat_sync' and music_path:
        music_file = Path(music_path)
        if music_file.exists():
            print(f"\nDetecting beats in: {music_file.name}")
            detector = BeatDetector(fps=fps)
            beat_result = detector.detect(music_file)

            num_eliminations = len(entities) - 1

            if len(beat_result.beat_frames) >= num_eliminations:
                elimination_frames = beat_result.beat_frames[:num_eliminations]
            else:
                elimination_frames = list(beat_result.beat_frames)
                avg_interval = int(beat_result.average_interval_frames)
                while len(elimination_frames) < num_eliminations:
                    elimination_frames.append(elimination_frames[-1] + avg_interval)

            print(f"BPM: {beat_result.tempo:.1f}")
            print(f"Beats found: {len(beat_result.beat_frames)}")
            print(f"Using {num_eliminations} beats for eliminations")

            scheduler = FrameListScheduler(elimination_frames)
        else:
            print(f"WARNING: Music file not found: {music_path}")

    # ========================================
    # SIMULATION
    # ========================================

    print("\nRunning simulation...")

    if scheduler:
        simulation = Simulation(
            entities=entities,
            scheduler=scheduler,
            fps=fps
        )
    else:
        simulation = Simulation(
            entities=entities,
            elimination_interval=sim_cfg.get('elimination_interval', 30),
            sudden_death_enabled=sudden_death_cfg.get('enabled', True),
            sudden_death_threshold_1=sudden_death_cfg.get('threshold_1', 10),
            sudden_death_multiplier_1=sudden_death_cfg.get('multiplier_1', 2),
            sudden_death_threshold_2=sudden_death_cfg.get('threshold_2', 5),
            sudden_death_multiplier_2=sudden_death_cfg.get('multiplier_2', 4),
            fps=fps
        )

    seed = sim_cfg.get('seed')
    result = simulation.run(seed=seed)

    print(f"Winner: {result.winner.name}")
    print(f"Total eliminations: {len(result.events)}")
    print(f"Total frames: {result.total_frames}")
    print(f"Duration: {result.total_frames / fps:.1f} seconds")
    if seed:
        print(f"Seed: {seed} (use same seed to replay)")

    # ========================================
    # RENDER CONFIG (with all new features)
    # ========================================

    # Setup idle animation
    set_idle_animator(IdleAnimator(
        wave_speed=vis_cfg.get('idle_wave_speed', 0.08),
        wave_amount=vis_cfg.get('idle_wave_amount', 4.0),
        breathe_speed=vis_cfg.get('idle_breathe_speed', 0.04),
        breathe_amount=vis_cfg.get('idle_breathe_amount', 0.03)
    ))

    # Canvas with gradient
    canvas_config = CanvasConfig(
        width=width,
        height=height,
        background_color=vis_cfg.get('background_color', '#1a1a2e'),
        gradient_enabled=vis_cfg.get('gradient_enabled', True),
        gradient_top=vis_cfg.get('gradient_top', '#1e1e2e'),
        gradient_bottom=vis_cfg.get('gradient_bottom', '#0a0a12'),
        animated_gradient=vis_cfg.get('animated_gradient', True),
        gradient_top_end=vis_cfg.get('gradient_top_end', '#2e1a3e'),
        gradient_bottom_end=vis_cfg.get('gradient_bottom_end', '#0a1a1f'),
        gradient_cycle_speed=vis_cfg.get('gradient_cycle_speed', 2.0),
        vignette_enabled=vis_cfg.get('vignette_enabled', True),
        vignette_strength=vis_cfg.get('vignette_strength', 0.4),
        greenscreen=vis_cfg.get('greenscreen', False),
        transparent=vis_cfg.get('transparent', False)
    )

    # Animation config
    animation_config = AnimationConfig(
        elimination_duration=int(fps * 0.5),
        flash_on_elimination=vis_cfg.get('flash_on_elimination', False),
        idle_enabled=vis_cfg.get('idle_enabled', True)
    )

    # Entity display (rounded corners, shadows)
    entity_config = EntityDisplayConfig(
        corner_radius=vis_cfg.get('corner_radius', 12),
        shadow_enabled=vis_cfg.get('shadow_enabled', True),
        shadow_blur=vis_cfg.get('shadow_blur', 10),
        shadow_opacity=vis_cfg.get('shadow_opacity', 100)
    )

    render_config = RenderConfig(
        canvas=canvas_config,
        layout=LayoutConfig(
            cell_padding=vis_cfg.get('cell_padding', 10)
        ),
        counter=CounterDisplayConfig(
            enabled=vis_cfg.get('show_counter', True),
            position=vis_cfg.get('counter_position', 'top'),
            format_string=vis_cfg.get('counter_format', '{count}'),
            pulse_on_elimination=True,
            pulse_scale=1.3
        ),
        animation=animation_config,
        entity=entity_config
    )

    # Modern animation (no ugly X)
    modern_animation = ModernFadeAnimation(
        animation_config,
        corner_radius=entity_config.corner_radius
    )

    renderer = Renderer(
        render_config,
        total_frames=result.total_frames,
        elimination_animation=modern_animation
    )
    renderer.set_eliminations(result.events)

    # ========================================
    # RENDER FRAMES (memory efficient - writes to disk)
    # ========================================

    print(f"\nRendering {result.total_frames} frames at {width}x{height} {fps}fps...")
    render_start = time.time()

    # Create temp directory for frames
    temp_frames_dir = Path(out_cfg.get('directory', 'output')) / "_temp_frames"
    if temp_frames_dir.exists():
        import shutil
        shutil.rmtree(temp_frames_dir)
    temp_frames_dir.mkdir(parents=True)

    # Add extra frames for last elimination animation to finish
    animation_buffer = int(fps * 0.5)  # 0.5 seconds
    winner_start_frame = result.total_frames - simulation.winner_celebration_frames + animation_buffer

    frame_paths = []
    for frame_num in range(result.total_frames):
        # Progress every 60 frames
        if frame_num % 60 == 0:
            elapsed = time.time() - render_start
            progress = (frame_num + 1) / result.total_frames
            if progress > 0.01:
                remaining = (elapsed / progress) - elapsed
                print(f"  Frame {frame_num}/{result.total_frames} | "
                      f"Elapsed: {int(elapsed)}s | Remaining: ~{int(remaining)}s")

        if frame_num >= winner_start_frame:
            frame = renderer.render_winner_frame(result.winner, frame_num)
        else:
            frame = renderer.render_frame(entities, frame_num)

        # Save to disk immediately (don't store in memory)
        frame_path = temp_frames_dir / f"frame_{frame_num:06d}.jpg"
        frame.convert('RGB').save(frame_path, "JPEG", quality=95)
        frame_paths.append(str(frame_path))

    render_time = time.time() - render_start
    print(f"Render done in {int(render_time // 60)}m {int(render_time % 60)}s")

    # ========================================
    # AUDIO
    # ========================================

    audio = None
    if audio_cfg.get('enabled', True):
        print(f"\nBuilding audio (mode: {audio_mode})...")

        audio_config = AudioConfig(
            enabled=True,
            mode=audio_mode,
            sound_pack=audio_cfg.get('sound_pack', 'default'),
            music_path=music_path,
            elimination_volume=audio_cfg.get('volume', {}).get('elimination', 0.8),
            countdown_volume=audio_cfg.get('volume', {}).get('countdown', 1.0),
            winner_volume=audio_cfg.get('volume', {}).get('winner', 1.0),
            music_volume=audio_cfg.get('volume', {}).get('music', 0.4),
            countdown_enabled=audio_cfg.get('countdown_enabled', False),
            countdown_thresholds=tuple(audio_cfg.get('countdown_thresholds', [10, 5, 3]))
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

        # ========================================
        # EXPORT
        # ========================================

        print("\nExporting video...")
        export_start = time.time()

        try:
            from moviepy import ImageSequenceClip, AudioFileClip
        except ImportError:
            from moviepy.editor import ImageSequenceClip, AudioFileClip

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        seed_str = f"_seed{seed}" if seed else ""
        filename = f"{project.name}_{len(entities)}ent{seed_str}_{timestamp}.mp4"
        output_path = Path(out_cfg.get('directory', 'output')) / filename

        # Create clip from saved frames
        clip = ImageSequenceClip(frame_paths, fps=fps)

        # Add audio
        if audio and Path(audio).exists():
            audio_clip = AudioFileClip(str(audio))
            if audio_clip.duration > clip.duration:
                try:
                    audio_clip = audio_clip.subclipped(0, clip.duration)
                except AttributeError:
                    audio_clip = audio_clip.subclip(0, clip.duration)
            try:
                clip = clip.with_audio(audio_clip)
            except AttributeError:
                clip = clip.set_audio(audio_clip)

        clip.write_videofile(
            str(output_path),
            codec='libx264',
            audio_codec='aac' if audio else None,
            fps=fps,
            preset='fast',
            threads=4,
            logger='bar'
        )
        clip.close()

        # Clean up temp frames
        import shutil
        shutil.rmtree(temp_frames_dir)

        export_time = time.time() - export_start


if __name__ == "__main__":
    main()
