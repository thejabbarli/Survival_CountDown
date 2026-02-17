"""Scheduler configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SchedulerConfig:
    """Elimination timing settings."""
    elimination_interval: int = 30
    initial_delay: int = 60
    
    sudden_death_enabled: bool = True
    sudden_death_threshold_1: int = 10
    sudden_death_multiplier_1: int = 2
    sudden_death_threshold_2: int = 5
    sudden_death_multiplier_2: int = 4
