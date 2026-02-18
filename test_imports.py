"""Test that all imports work after refactoring.

Run this from project root:
    python test_imports.py

If no errors, the refactoring was successful!
"""

print("Testing imports...")

# Core classes
from core import Entity, Project, Simulation, EntityState
print("✓ Core classes")

# Simulation results
from core import EliminationEvent, SimulationResult
print("✓ Simulation results")

# Scheduling
from core import (
    EliminationScheduler,
    IntervalScheduler,
    BeatSyncScheduler,
    FrameListScheduler,
    create_scheduler
)
print("✓ Scheduling")

# Strategies - Elimination
from core import (
    EliminationStrategy,
    RandomElimination,
    create_elimination_strategy
)
print("✓ Elimination strategies")

# Strategies - Animation
from core import (
    EliminationAnimation,
    ModernFadeAnimation,
    ShrinkWithXAnimation,
    create_animation
)
print("✓ Animation strategies")

# Config
from core import (
    RenderConfig,
    CanvasConfig,
    AnimationConfig,
    LayoutConfig,
    CounterDisplayConfig,
    EntityDisplayConfig,
)
print("✓ Config classes")

# Rendering
from core import (
    Renderer,
    GameFrameRenderer,
    WinnerFrameRenderer,
    RendererFactory,
)
print("✓ Rendering classes")

# Test factory functions
strategy = create_elimination_strategy("random")
print(f"✓ Created elimination strategy: {type(strategy).__name__}")

config = AnimationConfig()
anim = create_animation("modern_fade", config, corner_radius=12)
print(f"✓ Created animation: {type(anim).__name__}")

# Test that strategy works
entities = [
    Entity(id="1", name="Test1", color="#FF0000"),
    Entity(id="2", name="Test2", color="#00FF00"),
]
victim = strategy.select(entities)
print(f"✓ Strategy selected: {victim.name}")

print("\n" + "="*50)
print("ALL IMPORTS WORKING! Refactoring successful.")
print("="*50)
