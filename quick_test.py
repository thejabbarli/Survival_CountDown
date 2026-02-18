# test_imports.py
from core import (
    Entity,
    Simulation,
    Renderer,
    EliminationStrategy,
    RandomElimination,
    ModernFadeAnimation,
    create_animation,
    create_elimination_strategy,
)

print("✓ All imports work!")

# Test factory functions
strategy = create_elimination_strategy("random")
print(f"✓ Created strategy: {type(strategy).__name__}")

# If you have AnimationConfig:
from core import AnimationConfig
config = AnimationConfig()
anim = create_animation("modern_fade", config, corner_radius=12)
print(f"✓ Created animation: {type(anim).__name__}")
