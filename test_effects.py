"""Quick effect test."""

from datetime import datetime
from core import (
    Entity, Simulation, Renderer, Exporter,
    RenderConfig, CanvasConfig, AnimationConfig, CounterDisplayConfig,
    EntityDisplayConfig, FrameListScheduler, ModernFadeAnimation
)
from core.idle_animation import IdleAnimator, set_idle_animator

# === SETTINGS ===
ENTITY_COUNT = 4
SEED = 42                 # Same seed = same results. Change for different outcome
PREVIEW_MODE = True       # True = 30fps 480p (fast), False = 60fps 1080p
TRANSPARENT_BG = False
GREEN_SCREEN = False
ANIMATED_GRADIENT = True

# Test entities
entities = [
    Entity(id="1", name="Red", color="#FF4444"),
    Entity(id="2", name="Blue", color="#4444FF"),
    Entity(id="3", name="Green", color="#44FF44"),
    Entity(id="4", name="Yellow", color="#FFFF44"),
]

# Fixed beats (adjusted for fps)
fps = 30 if PREVIEW_MODE else 60
scheduler = FrameListScheduler([fps, fps*2, fps*3])  # 1s, 2s, 3s

# Run simulation
sim = Simulation(entities, scheduler=scheduler, fps=fps)
result = sim.run(seed=SEED)

print(f"Seed: {SEED} (use same seed to replay exact simulation)")

# Idle animation
set_idle_animator(IdleAnimator(
    wave_speed=0.08,
    wave_amount=4.0,
    breathe_speed=0.04,
    breathe_amount=0.03
))

# Resolution
if PREVIEW_MODE:
    width, height = 480, 854  # 480p vertical
else:
    width, height = 1080, 1920  # 1080p vertical

# Canvas config
canvas_cfg = CanvasConfig(
    width=width,
    height=height,
    greenscreen=GREEN_SCREEN,
    transparent=TRANSPARENT_BG,
    gradient_enabled=True,
    animated_gradient=ANIMATED_GRADIENT,
    gradient_top="#1e1e2e",
    gradient_bottom="#0a0a12",
    gradient_top_end="#2e1a3e",
    gradient_bottom_end="#0a1a1f",
    gradient_cycle_speed=2.0,
    vignette_enabled=True,
    vignette_strength=0.4
)

# Animation config
anim_cfg = AnimationConfig(
    flash_on_elimination=False,
    idle_enabled=True,
    elimination_duration=int(fps * 0.4)  # 0.4 seconds
)

# Entity config
entity_cfg = EntityDisplayConfig(
    corner_radius=12,
    shadow_enabled=True,
    shadow_blur=10,
    shadow_opacity=100
)

config = RenderConfig(
    canvas=canvas_cfg,
    animation=anim_cfg,
    entity=entity_cfg,
    counter=CounterDisplayConfig(
        pulse_on_elimination=True,
        pulse_scale=1.3
    )
)

# Use modern fade animation (no X)
modern_anim = ModernFadeAnimation(anim_cfg, corner_radius=entity_cfg.corner_radius)

# Create renderer
renderer = Renderer(
    config,
    total_frames=result.total_frames,
    elimination_animation=modern_anim
)
renderer.set_eliminations(result.events)

# Render
print(f"Rendering {result.total_frames} frames at {width}x{height} {fps}fps...")
frames = []
winner_start = result.total_frames - fps  # 1 second winner screen

for f in range(result.total_frames):
    if f % fps == 0:
        print(f"  {f}/{result.total_frames}")

    if f >= winner_start:
        frames.append(renderer.render_winner_frame(result.winner, f))
    else:
        frames.append(renderer.render_frame(entities, f))

# Filename
now = datetime.now()
date_str = now.strftime("%b%d").lower()
time_str = now.strftime("%Hh%Mm")
quality = "preview" if PREVIEW_MODE else "full"

if GREEN_SCREEN:
    bg_type = "green"
elif TRANSPARENT_BG:
    bg_type = "transparent"
elif ANIMATED_GRADIENT:
    bg_type = "animated"
else:
    bg_type = "static"

filename = f"test_{ENTITY_COUNT}ent_{quality}_{bg_type}_seed{SEED}_{date_str}_{time_str}.mp4"

# Export
if TRANSPARENT_BG:
    import os
    out_dir = f"output/{filename}"
    os.makedirs(out_dir, exist_ok=True)
    for i, frame in enumerate(frames):
        frame.save(f"{out_dir}/frame_{i:04d}.png")
    print(f"PNG sequence: {out_dir}/")
else:
    exporter = Exporter(fps=fps)
    exporter.export(frames, filename)
    print(f"Video: output/{filename}.mp4")

print(f"Winner: {result.winner.name}")
