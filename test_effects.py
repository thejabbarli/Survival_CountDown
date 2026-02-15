"""Quick effect test - 4 entities, 2 seconds."""

from core import Entity, Simulation, Renderer, Exporter, RenderConfig, CanvasConfig, FrameListScheduler

# 4 test entities
entities = [
    Entity(id="1", name="Red", color="#FF4444"),
    Entity(id="2", name="Blue", color="#4444FF"),
    Entity(id="3", name="Green", color="#44FF44"),
    Entity(id="4", name="Yellow", color="#FFFF44"),
]

# Fixed beats: frame 30, 60, 90 (3 eliminations = 1 winner)
scheduler = FrameListScheduler([30, 60, 90])

# Run
sim = Simulation(entities, scheduler=scheduler, fps=60)
result = sim.run(seed=42)

# Render
config = RenderConfig(
    canvas=CanvasConfig(
        gradient_enabled=True,
        gradient_top="#1a1a2e",
        gradient_bottom="#0f0f1a",
        vignette_enabled=True,
        vignette_strength=0.3
    )
)
renderer = Renderer(config)

frames = []
for f in range(result.total_frames):
    if f >= result.total_frames - 60:
        frames.append(renderer.render_winner_frame(result.winner))
    else:
        frames.append(renderer.render_frame(entities, f))

# Export
exporter = Exporter(fps=60)
exporter.export(frames, "test_effects")

print(f"Done! Winner: {result.winner.name}")
print("Output: output/test_effects.mp4")
