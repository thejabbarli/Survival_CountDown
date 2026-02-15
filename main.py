import yaml
from pathlib import Path
from datetime import datetime

from core import Project, Simulation, Renderer, RenderConfig, Exporter


def load_config(config_path: Path = Path("config.yaml")) -> dict:
    """Load configuration from YAML file."""
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def main():
    # Load config
    config = load_config()
    video_cfg = config.get('video', {})
    sim_cfg = config.get('simulation', {})
    vis_cfg = config.get('visuals', {})
    out_cfg = config.get('output', {})
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

    # Create simulation
    simulation = Simulation(
        entities=entities,
        elimination_interval=sim_cfg.get('elimination_interval', 30),
        sudden_death_enabled=sudden_death_cfg.get('enabled', True),
        sudden_death_threshold_1=sudden_death_cfg.get('threshold_1', 10),
        sudden_death_multiplier_1=sudden_death_cfg.get('multiplier_1', 2),
        sudden_death_threshold_2=sudden_death_cfg.get('threshold_2', 5),
        sudden_death_multiplier_2=sudden_death_cfg.get('multiplier_2', 4),
        fps=video_cfg.get('fps', 60)
    )

    # Run simulation
    print("Running simulation...")
    result = simulation.run()
    print(f"Winner: {result.winner.name}")
    print(f"Total eliminations: {len(result.events)}")
    print(f"Total frames: {result.total_frames}")

    # Create renderer with config
    render_config = RenderConfig(
        width=video_cfg.get('width', 1080),
        height=video_cfg.get('height', 1920),
        background_color=vis_cfg.get('background_color', '#1a1a2e'),
        cell_padding=vis_cfg.get('cell_padding', 8),
        show_counter=vis_cfg.get('show_counter', True),
        counter_position=vis_cfg.get('counter_position', 'top')
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

    # Export video
    print("Exporting video...")
    exporter = Exporter(
        fps=video_cfg.get('fps', 60),
        output_dir=Path(out_cfg.get('directory', 'output'))
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{project.name}_{timestamp}"

    output_path = exporter.export(frames, filename)
    print(f"Done! Video saved to: {output_path}")


if __name__ == "__main__":
    main()
