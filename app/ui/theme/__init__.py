"""
Compatibility layer over ThemeEngine.

This keeps the older theme API stable while delegating to the richer
ThemeEngine used by the editor UI.
"""
from __future__ import annotations

from typing import Any

from .theme_engine import PRESETS, ThemeColors, ThemeMetrics, get_engine

# Legacy constants for modules that still read defaults/presets directly.
DEFAULT_COLORS = ThemeColors().to_dict()
DEFAULT_METRICS = ThemeMetrics().to_dict()
BUILTIN_THEMES = PRESETS


def get_themes() -> list[str]:
    """Get list of all available theme names."""
    engine = get_engine()
    return engine.get_preset_names()


def current_theme() -> str:
    """Get the current theme name."""
    engine = get_engine()
    return engine.current_theme


def get_color(name: str) -> str:
    """Get a color value from the current theme."""
    engine = get_engine()
    return engine.get_color(name)


def get_metric(name: str) -> Any:
    """Get a metric value from the current theme."""
    engine = get_engine()
    return engine.get_metric(name)


def get_colors() -> dict[str, str]:
    """Get all current theme colors."""
    engine = get_engine()
    return engine.get_all_colors()


def get_metrics() -> dict[str, Any]:
    """Get all current theme metrics."""
    engine = get_engine()
    return engine.get_all_metrics()


def apply_theme(
    name: str = "Dark",
    colors: dict[str, str] | None = None,
    metrics: dict[str, Any] | None = None,
    save: bool = True,
) -> None:
    """Apply a theme and optional overrides through ThemeEngine."""
    engine = get_engine()
    engine.apply_theme(name, colors=colors, metrics=metrics, save=save)


def save_custom_theme(name: str, colors: dict[str, str], metrics: dict[str, Any]) -> None:
    """Save a custom theme."""
    engine = get_engine()
    engine.apply_theme(name, colors=colors, metrics=metrics, save=False)
    engine.save_custom_preset(name)


def delete_custom_theme(name: str) -> None:
    """Delete a custom theme."""
    engine = get_engine()
    engine.delete_custom_preset(name)


def load_saved_theme() -> None:
    """Load and apply the user's saved theme preference."""
    engine = get_engine()
    engine.load_saved()
    engine.apply_to_application()
