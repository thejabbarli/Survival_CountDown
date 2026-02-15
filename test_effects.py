"""Quick effect test."""

from datetime import datetime
from core import (
    Entity, Simulation, Renderer, Exporter,
    RenderConfig, CanvasConfig, AnimationConfig, CounterDisplayConfig,
    FrameListScheduler
)
from core.idle_animation import IdleAnimator, set_idle_animator

# === SETTINGS ===
ENTITY_COUNT = 4
TRANSPARENT_BG = False    # PNG sequence for editing
GREEN_SCREEN = False      # Green bg for chroma key
ANIMATED_GRADIENT = True  # Colors shift over time

# Test entities
entities = [
    Entity(id="1", name="Red", color="#FF4444"),
    Entity(id="2", name="Blue", color="#4444FF"),
    Entity(id="3", name="Green", color="#44FF44"),
    Entity(id="4", name="Yellow", color="#FFFF44"),
]

# Fixed beats
scheduler = FrameListScheduler([60, 120, 180])

# Run simulation
sim = Simulation(entities, scheduler=scheduler, fps=60)
result = sim.run(seed=42)

# Idle animation
set_idle_animator(IdleAnimator(
    wave_speed=0.08,
    wave_amount=4.0,
    breathe_speed=0.04,
    breathe_amount=0.03
))

# Background config
canvas_cfg = CanvasConfig(
    greenscreen=GREEN_SCREEN,
    transparent=TRANSPARENT_BG,
    gradient_enabled=True,
    animated_gradient=ANIMATED_GRADIENT,
    gradient_top="#1e1e2e",
    gradient_bottom="#0a0a12",
    gradient_top_end="#2e1a3e",     # Shifts to purple
    gradient_bottom_end="#0a1a1f",  # Shifts to teal
    gradient_cycle_speed=2.0,        # 2 full color cycles
    vignette_enabled=True,
    vignette_strength=0.4
)

config = RenderConfig(
    canvas=canvas_cfg,
    animation=AnimationConfig(
        flash_on_elimination=False,
        idle_enabled=True
    ),
    counter=CounterDisplayConfig(
        pulse_on_elimination=True,
        pulse_scale=1.3
    )
)

# Create renderer with total frames
renderer = Renderer(config, total_frames=result.total_frames)
renderer.set_eliminations(result.events)

# Render frames
frames = []
for f in range(result.total_frames):
    if f >= result.total_frames - 60:
        frames.append(renderer.render_winner_frame(result.winner))
    else:
        frames.append(renderer.render_frame(entities, f))

# Generate filename
now = datetime.now()
date_str = now.strftime("%b%d").lower()
time_str = now.strftime("%Hh%Mm")

if GREEN_SCREEN:
    bg_type = "green"
elif TRANSPARENT_BG:
    bg_type = "transparent"
elif ANIMATED_GRADIENT:
    bg_type = "animated"
else:
    bg_type = "static"

filename = f"test_{ENTITY_COUNT}ent_{bg_type}_{date_str}_{time_str}"

# Export
if TRANSPARENT_BG:
    import os
    out_dir = f"output/{filename}"
    os.makedirs(out_dir, exist_ok=True)
    for i, frame in enumerate(frames):
        frame.save(f"{out_dir}/frame_{i:04d}.png")
    print(f"PNG sequence: {out_dir}/")
else:
    exporter = Exporter(fps=60)
    exporter.export(frames, filename)
    print(f"Video: output/{filename}.mp4")

print(f"Winner: {result.winner.name}")
print(f"Frames: {result.total_frames}")
