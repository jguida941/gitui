"""
Modular Theme Engine for GitUI.

A complete theming system extracted and adapted from WebHookCliEditor.
Supports real-time preview, undo/redo, presets, and full visual customization.

Usage:
    from app.ui.theme.theme_engine import ThemeEngine, get_engine

    engine = get_engine()
    engine.apply_preset("Cyberpunk")
    engine.set_color("accent", "#FF00FF")
    css = engine.generate_stylesheet()
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QSettings, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QApplication

# ---------------------------------------------------------------------------
# Theme Data Structures
# ---------------------------------------------------------------------------


@dataclass
class ThemeColors:
    """All customizable colors in the theme."""

    # Backgrounds
    background: str = "#121212"
    background_alt: str = "#1E1E1E"
    surface: str = "#1F1F1F"

    # Text
    text: str = "#EEEEEE"
    text_dim: str = "#888888"
    text_disabled: str = "#555555"

    # Borders
    border: str = "#2D2D2D"
    border_focus: str = "#00FFAA"

    # Accent
    accent: str = "#00FFAA"
    accent_hover: str = "#00CC88"
    accent_pressed: str = "#009966"

    # Status
    success: str = "#00FF7F"
    warning: str = "#FFAA00"
    error: str = "#FF5555"
    info: str = "#00AAFF"

    # Git-specific
    diff_add: str = "#00FF7F"
    diff_remove: str = "#FF5555"
    diff_header: str = "#00AAFF"
    diff_hunk: str = "#CC66FF"

    # Selection
    selection_bg: str = "#00FFAA"
    selection_text: str = "#000000"

    # Links
    link: str = "#00FFFF"
    link_visited: str = "#CC66FF"

    def to_dict(self) -> dict[str, str]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> ThemeColors:
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class ThemeMetrics:
    """All customizable metrics/dimensions in the theme."""

    # Border radius
    border_radius: int = 6
    border_radius_small: int = 4
    border_radius_large: int = 10

    # Border width
    border_width: int = 1
    border_width_focus: int = 2

    # Spacing
    padding: int = 8
    padding_small: int = 4
    padding_large: int = 12
    spacing: int = 6
    margin: int = 8

    # Typography
    font_size: int = 13
    font_size_small: int = 11
    font_size_large: int = 15
    font_size_h1: int = 24
    font_size_h2: int = 20
    font_size_h3: int = 16
    font_family: str = "SF Pro Display, Segoe UI, system-ui, sans-serif"
    font_family_mono: str = "SF Mono, Consolas, Monaco, monospace"

    # Widgets
    button_min_width: int = 80
    input_height: int = 32
    toolbar_height: int = 40
    scrollbar_width: int = 12

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ThemeMetrics:
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class ThemeEffects:
    """Visual effects configuration."""

    # Shadows
    shadow_enabled: bool = True
    shadow_x: int = 0
    shadow_y: int = 4
    shadow_blur: int = 12
    shadow_spread: int = 0
    shadow_color: str = "rgba(0, 0, 0, 0.3)"

    # Transitions
    transition_duration: int = 150
    transition_timing: str = "ease-out"

    # Hover effects
    hover_brighten: bool = True
    hover_scale: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ThemeEffects:
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


@dataclass
class ThemeState:
    """Complete theme state for undo/redo."""

    name: str = "Custom"
    colors: ThemeColors = field(default_factory=ThemeColors)
    metrics: ThemeMetrics = field(default_factory=ThemeMetrics)
    effects: ThemeEffects = field(default_factory=ThemeEffects)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "colors": self.colors.to_dict(),
            "metrics": self.metrics.to_dict(),
            "effects": self.effects.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ThemeState:
        return cls(
            name=data.get("name", "Custom"),
            colors=ThemeColors.from_dict(data.get("colors", {})),
            metrics=ThemeMetrics.from_dict(data.get("metrics", {})),
            effects=ThemeEffects.from_dict(data.get("effects", {})),
        )

    def copy(self) -> ThemeState:
        return ThemeState.from_dict(self.to_dict())


def _adjust_color(value: str, factor: float) -> str:
    color = QColor(value)
    if not color.isValid():
        return value

    if factor >= 1:
        color = color.lighter(int(factor * 100))
    else:
        color = color.darker(int(100 / max(factor, 0.01)))

    if color.alpha() < 255:
        return f"rgba({color.red()}, {color.green()}, {color.blue()}, {color.alphaF():.2f})"
    return color.name()


def parse_qss_to_theme(qss: str) -> dict[str, Any]:
    """
    Parse a QSS stylesheet and extract theme values.
    Returns a dict suitable for ThemeState.from_dict().
    """
    colors: dict[str, str] = {}
    metrics: dict[str, Any] = {}

    # Color pattern: matches #hex, rgb(), rgba()
    color_pattern = r"(#[0-9A-Fa-f]{3,8}|rgba?\s*\([^)]+\))"

    # Property-to-theme-color mappings
    color_mappings = {
        "background-color": ["background", "background_alt", "surface"],
        "background": ["background", "background_alt", "surface"],
        "color": ["text", "text_dim", "text_disabled"],
        "border-color": ["border", "border_focus"],
        "border": ["border"],
        "selection-background-color": ["selection_bg"],
        "selection-color": ["selection_text"],
    }

    # Track colors we've seen for each category
    seen_colors: dict[str, list[str]] = {k: [] for k in color_mappings}

    # Parse QSS rules
    # Match property: value; patterns
    prop_pattern = r"([a-zA-Z-]+)\s*:\s*([^;{}]+);"

    for match in re.finditer(prop_pattern, qss):
        prop_name = match.group(1).strip().lower()
        prop_value = match.group(2).strip()

        # Extract colors
        if prop_name in color_mappings:
            color_match = re.search(color_pattern, prop_value)
            if color_match:
                color_val = color_match.group(1)
                # Normalize the color
                qcolor = QColor(color_val)
                if qcolor.isValid():
                    if qcolor.alpha() == 255:
                        normalized = qcolor.name()
                    else:
                        r, g, b = qcolor.red(), qcolor.green(), qcolor.blue()
                        a = qcolor.alphaF()
                        normalized = f"rgba({r}, {g}, {b}, {a:.2f})"
                    if normalized not in seen_colors[prop_name]:
                        seen_colors[prop_name].append(normalized)

        # Extract metrics
        if prop_name == "border-radius":
            px_match = re.search(r"(\d+)(?:px)?", prop_value)
            if px_match:
                metrics["border_radius"] = int(px_match.group(1))

        elif prop_name == "padding":
            px_match = re.search(r"(\d+)(?:px)?", prop_value)
            if px_match:
                metrics["padding"] = int(px_match.group(1))

        elif prop_name == "border-width":
            px_match = re.search(r"(\d+)(?:px)?", prop_value)
            if px_match:
                metrics["border_width"] = int(px_match.group(1))

        elif prop_name == "font-size":
            px_match = re.search(r"(\d+)(?:px)?", prop_value)
            if px_match:
                metrics["font_size"] = int(px_match.group(1))

        elif prop_name == "font-family":
            # Extract first font family
            font = prop_value.split(",")[0].strip().strip("\"'")
            if font:
                metrics["font_family"] = font

    # Assign colors based on what we found
    # Background colors (first = main, second = alt, third = surface)
    bg_colors = seen_colors.get("background-color", []) + seen_colors.get(
        "background", []
    )
    bg_colors = list(dict.fromkeys(bg_colors))  # Remove duplicates, preserve order
    if len(bg_colors) >= 1:
        colors["background"] = bg_colors[0]
    if len(bg_colors) >= 2:
        colors["background_alt"] = bg_colors[1]
    if len(bg_colors) >= 3:
        colors["surface"] = bg_colors[2]

    # Text colors
    text_colors = seen_colors.get("color", [])
    if len(text_colors) >= 1:
        colors["text"] = text_colors[0]
    if len(text_colors) >= 2:
        colors["text_dim"] = text_colors[1]

    # Border colors
    border_colors = seen_colors.get("border-color", []) + seen_colors.get("border", [])
    border_colors = list(dict.fromkeys(border_colors))
    if len(border_colors) >= 1:
        colors["border"] = border_colors[0]
    if len(border_colors) >= 2:
        colors["border_focus"] = border_colors[1]

    # Selection colors
    sel_bg = seen_colors.get("selection-background-color", [])
    if sel_bg:
        colors["selection_bg"] = sel_bg[0]
    sel_text = seen_colors.get("selection-color", [])
    if sel_text:
        colors["selection_text"] = sel_text[0]

    # Try to detect accent color (often used in :hover, QPushButton, etc.)
    # Look for colors that aren't the main bg/text colors
    all_colors_in_qss = re.findall(color_pattern, qss)
    unique_colors = []
    for c in all_colors_in_qss:
        qc = QColor(c)
        if qc.isValid():
            norm = qc.name()
            if norm not in unique_colors:
                unique_colors.append(norm)

    # Filter out already-assigned colors to find potential accent
    assigned = set(colors.values())
    potential_accents = [c for c in unique_colors if c not in assigned]

    # Pick a vibrant color as accent (high saturation)
    for c in potential_accents:
        qc = QColor(c)
        if qc.saturation() > 100:  # Reasonably saturated
            colors["accent"] = c
            break

    return {"name": "Imported QSS", "colors": colors, "metrics": metrics, "effects": {}}


# ---------------------------------------------------------------------------
# Built-in Presets
# ---------------------------------------------------------------------------

PRESETS: dict[str, dict[str, Any]] = {
    "Dark": {"colors": {}},  # Uses all defaults
    "Dark Sci-Fi": {
        "colors": {
            "accent": "#00FFAA",
            "accent_hover": "#00CC88",
            "border_focus": "#00FFAA",
            "selection_bg": "#00FFAA",
        }
    },
    "Cyberpunk": {
        "colors": {
            "background": "#0A0A0F",
            "background_alt": "#12121A",
            "surface": "#1A1A25",
            "border": "#FF00FF",
            "border_focus": "#00FFFF",
            "accent": "#00FFFF",
            "accent_hover": "#00CCCC",
            "accent_pressed": "#009999",
            "selection_bg": "#FF00FF",
            "link": "#FF00FF",
        },
        "metrics": {
            "border_width": 2,
            "border_radius": 4,
        },
    },
    "Midnight Blue": {
        "colors": {
            "background": "#0D1117",
            "background_alt": "#161B22",
            "surface": "#21262D",
            "border": "#30363D",
            "accent": "#58A6FF",
            "accent_hover": "#388BFD",
            "accent_pressed": "#1F6FEB",
            "selection_bg": "#58A6FF",
            "link": "#58A6FF",
        }
    },
    "Dracula": {
        "colors": {
            "background": "#282A36",
            "background_alt": "#21222C",
            "surface": "#343746",
            "border": "#44475A",
            "text": "#F8F8F2",
            "accent": "#BD93F9",
            "accent_hover": "#A77BF3",
            "accent_pressed": "#9166E8",
            "success": "#50FA7B",
            "warning": "#FFB86C",
            "error": "#FF5555",
            "selection_bg": "#BD93F9",
            "link": "#8BE9FD",
            "diff_add": "#50FA7B",
            "diff_remove": "#FF5555",
            "diff_header": "#8BE9FD",
        }
    },
    "Nord": {
        "colors": {
            "background": "#2E3440",
            "background_alt": "#3B4252",
            "surface": "#434C5E",
            "border": "#4C566A",
            "text": "#ECEFF4",
            "text_dim": "#D8DEE9",
            "accent": "#88C0D0",
            "accent_hover": "#81A1C1",
            "accent_pressed": "#5E81AC",
            "success": "#A3BE8C",
            "warning": "#EBCB8B",
            "error": "#BF616A",
            "selection_bg": "#88C0D0",
            "link": "#88C0D0",
        }
    },
    "Forest": {
        "colors": {
            "background": "#1A1F16",
            "background_alt": "#232A1E",
            "surface": "#2D3626",
            "border": "#3D4A34",
            "accent": "#7CB342",
            "accent_hover": "#689F38",
            "accent_pressed": "#558B2F",
            "success": "#8BC34A",
            "selection_bg": "#7CB342",
        }
    },
    "Material Dark": {
        "colors": {
            "background": "#121212",
            "background_alt": "#1E1E1E",
            "surface": "#2D2D2D",
            "border": "#424242",
            "accent": "#BB86FC",
            "accent_hover": "#A66FF2",
            "accent_pressed": "#9155E8",
            "success": "#03DAC6",
            "error": "#CF6679",
            "selection_bg": "#BB86FC",
        }
    },
    "Material Light": {
        "colors": {
            "background": "#FAFAFA",
            "background_alt": "#F0F0F0",
            "surface": "#FFFFFF",
            "border": "#DDDDDD",
            "text": "#212121",
            "text_dim": "#5F5F5F",
            "accent": "#6200EE",
            "accent_hover": "#7B2FF2",
            "accent_pressed": "#4B00B5",
            "selection_bg": "#6200EE",
            "selection_text": "#FFFFFF",
        }
    },
    "Light Modern": {
        "colors": {
            "background": "#FFFFFF",
            "background_alt": "#F5F7FA",
            "surface": "#FFFFFF",
            "border": "#E0E0E0",
            "text": "#333333",
            "text_dim": "#666666",
            "accent": "#2196F3",
            "accent_hover": "#1976D2",
            "accent_pressed": "#0D47A1",
            "selection_bg": "#2196F3",
            "selection_text": "#FFFFFF",
            "success": "#4CAF50",
        }
    },
    "Minimalist": {
        "colors": {
            "background": "#F5F5F5",
            "background_alt": "#EEEEEE",
            "surface": "#FFFFFF",
            "border": "#CCCCCC",
            "text": "#333333",
            "text_dim": "#666666",
            "accent": "#000000",
            "accent_hover": "#444444",
            "accent_pressed": "#222222",
            "selection_bg": "#E0E0E0",
            "selection_text": "#000000",
        }
    },
    "Corporate Blue": {
        "colors": {
            "background": "#F0F4F8",
            "background_alt": "#E2E8F0",
            "surface": "#FFFFFF",
            "border": "#CBD5E0",
            "text": "#1A365D",
            "text_dim": "#4A5568",
            "accent": "#2B6CB0",
            "accent_hover": "#2C5282",
            "accent_pressed": "#1A365D",
            "selection_bg": "#2B6CB0",
            "selection_text": "#FFFFFF",
            "warning": "#ED8936",
        }
    },
    "Nature Green": {
        "colors": {
            "background": "#F7FAFC",
            "background_alt": "#EDF2F7",
            "surface": "#FFFFFF",
            "border": "#C6F6D5",
            "text": "#22543D",
            "text_dim": "#4A5568",
            "accent": "#48BB78",
            "accent_hover": "#38A169",
            "accent_pressed": "#2F855A",
            "selection_bg": "#48BB78",
            "selection_text": "#FFFFFF",
            "warning": "#F6E05E",
        }
    },
    "Light": {
        "colors": {
            "background": "#FFFFFF",
            "background_alt": "#F5F5F5",
            "surface": "#EEEEEE",
            "border": "#DDDDDD",
            "border_focus": "#0066CC",
            "text": "#333333",
            "text_dim": "#666666",
            "text_disabled": "#999999",
            "accent": "#0066CC",
            "accent_hover": "#0055AA",
            "accent_pressed": "#004488",
            "selection_bg": "#0066CC",
            "selection_text": "#FFFFFF",
            "diff_add": "#22863A",
            "diff_remove": "#CB2431",
            "diff_header": "#0366D6",
        }
    },
    "High Contrast": {
        "colors": {
            "background": "#000000",
            "background_alt": "#0A0A0A",
            "surface": "#1A1A1A",
            "border": "#FFFFFF",
            "border_focus": "#FFFF00",
            "text": "#FFFFFF",
            "text_dim": "#CCCCCC",
            "accent": "#FFFF00",
            "accent_hover": "#FFFF66",
            "accent_pressed": "#CCCC00",
            "selection_bg": "#FFFF00",
            "selection_text": "#000000",
        },
        "metrics": {
            "border_width": 2,
        },
    },
}


# ---------------------------------------------------------------------------
# Theme Engine
# ---------------------------------------------------------------------------


class ThemeEngine(QObject):
    """
    Central theme management engine.

    Features:
    - Real-time stylesheet generation
    - Undo/redo support (50 levels)
    - Preset management
    - Custom theme save/load
    - Signal emission on changes
    """

    theme_changed = Signal()
    colors_changed = Signal(str, str)  # (color_name, new_value)
    metrics_changed = Signal(str, object)  # (metric_name, new_value)
    effects_changed = Signal(str, object)  # (effect_name, new_value)

    MAX_UNDO_LEVELS = 50

    def __init__(self) -> None:
        super().__init__()
        self._state = ThemeState()
        self._undo_stack: list[ThemeState] = []
        self._redo_stack: list[ThemeState] = []
        self._settings = QSettings("GitUI", "Theme")
        self._suppress_signals = False
        self._apply_enabled = True

    # ─────────────────────────────────────────────────────────────────────
    # Properties
    # ─────────────────────────────────────────────────────────────────────

    @property
    def current_theme(self) -> str:
        return self._state.name

    @property
    def colors(self) -> ThemeColors:
        return self._state.colors

    @property
    def metrics(self) -> ThemeMetrics:
        return self._state.metrics

    @property
    def effects(self) -> ThemeEffects:
        return self._state.effects

    # ─────────────────────────────────────────────────────────────────────
    # Color Operations
    # ─────────────────────────────────────────────────────────────────────

    def get_color(self, name: str) -> str:
        """Get a color value by name."""
        return getattr(self._state.colors, name, "#FF00FF")

    def set_color(self, name: str, value: str, record_undo: bool = True) -> None:
        """Set a color value by name."""
        if not hasattr(self._state.colors, name):
            return
        # Clear raw QSS mode when user edits via controls
        self._clear_raw_qss_mode()
        if record_undo:
            self._push_undo()
        setattr(self._state.colors, name, value)
        self._emit_change()
        if not self._suppress_signals:
            self.colors_changed.emit(name, value)

    def get_all_colors(self) -> dict[str, str]:
        """Get all colors as a dictionary."""
        return self._state.colors.to_dict()

    # ─────────────────────────────────────────────────────────────────────
    # Metric Operations
    # ─────────────────────────────────────────────────────────────────────

    def get_metric(self, name: str) -> Any:
        """Get a metric value by name."""
        return getattr(self._state.metrics, name, 0)

    def set_metric(self, name: str, value: Any, record_undo: bool = True) -> None:
        """Set a metric value by name."""
        if not hasattr(self._state.metrics, name):
            return
        # Clear raw QSS mode when user edits via controls
        self._clear_raw_qss_mode()
        if record_undo:
            self._push_undo()
        setattr(self._state.metrics, name, value)
        self._emit_change()
        if not self._suppress_signals:
            self.metrics_changed.emit(name, value)

    def get_all_metrics(self) -> dict[str, Any]:
        """Get all metrics as a dictionary."""
        return self._state.metrics.to_dict()

    # ─────────────────────────────────────────────────────────────────────
    # Effect Operations
    # ─────────────────────────────────────────────────────────────────────

    def get_effect(self, name: str) -> Any:
        """Get an effect value by name."""
        return getattr(self._state.effects, name, None)

    def set_effect(self, name: str, value: Any, record_undo: bool = True) -> None:
        """Set an effect value by name."""
        if not hasattr(self._state.effects, name):
            return
        # Clear raw QSS mode when user edits via controls
        self._clear_raw_qss_mode()
        if record_undo:
            self._push_undo()
        setattr(self._state.effects, name, value)
        self._emit_change()
        if not self._suppress_signals:
            self.effects_changed.emit(name, value)

    def get_all_effects(self) -> dict[str, Any]:
        """Get all effects as a dictionary."""
        return self._state.effects.to_dict()

    # ─────────────────────────────────────────────────────────────────────
    # Preset Operations
    # ─────────────────────────────────────────────────────────────────────

    def get_preset_names(self) -> list[str]:
        """Get list of all available preset names (JSON and QSS presets)."""
        presets = list(PRESETS.keys())

        # Add custom JSON presets from settings
        self._settings.beginGroup("custom_themes")
        for key in self._settings.childKeys():
            if key not in presets:
                presets.append(key)
        self._settings.endGroup()

        # Add custom QSS presets from settings
        self._settings.beginGroup("qss_themes")
        for key in self._settings.childKeys():
            if key not in presets:
                presets.append(f"[QSS] {key}")
        self._settings.endGroup()

        return sorted(presets)

    def is_qss_preset(self, name: str) -> bool:
        """Check if a preset name refers to a QSS preset."""
        return name.startswith("[QSS] ")

    def get_qss_preset_name(self, display_name: str) -> str:
        """Get the actual QSS preset name from display name."""
        if display_name.startswith("[QSS] "):
            return display_name[6:]
        return display_name

    def apply_preset(self, name: str, record_undo: bool = True) -> bool:
        """Apply a preset theme by name."""
        if record_undo:
            self._push_undo()

        # Check if this is a QSS preset
        if self.is_qss_preset(name):
            qss_name = self.get_qss_preset_name(name)
            self._settings.beginGroup("qss_themes")
            qss = self._settings.value(qss_name)
            self._settings.endGroup()
            if qss:
                self._state = ThemeState(name=name)
                self.apply_raw_stylesheet(qss, save=True)
                self._emit_change()
                return True
            return False

        # Start with defaults
        self._state = ThemeState(name=name)

        # Clear any raw QSS override when switching to a regular preset
        self._settings.setValue("use_raw_qss", False)

        # Apply preset overrides
        if name in PRESETS:
            preset = PRESETS[name]
            if "colors" in preset:
                for k, v in preset["colors"].items():
                    if hasattr(self._state.colors, k):
                        setattr(self._state.colors, k, v)
            if "metrics" in preset:
                for k, v in preset["metrics"].items():
                    if hasattr(self._state.metrics, k):
                        setattr(self._state.metrics, k, v)
            if "effects" in preset:
                for k, v in preset["effects"].items():
                    if hasattr(self._state.effects, k):
                        setattr(self._state.effects, k, v)
        else:
            # Try loading custom preset
            self._settings.beginGroup("custom_themes")
            data = self._settings.value(name)
            self._settings.endGroup()
            if data:
                try:
                    theme_data = json.loads(data)
                    self._state = ThemeState.from_dict(theme_data)
                    self._state.name = name
                except (json.JSONDecodeError, TypeError):
                    return False

        self._emit_change()
        return True

    def apply_theme(
        self,
        name: str,
        colors: dict[str, str] | None = None,
        metrics: dict[str, Any] | None = None,
        effects: dict[str, Any] | None = None,
        save: bool = True,
    ) -> bool:
        """
        Apply a preset plus optional overrides in one undoable step.

        This is used by the editor so a preset load + tweaks doesn't spam
        the undo stack or emit partial theme changes.
        """
        self._push_undo()
        self._suppress_signals = True
        applied = self.apply_preset(name, record_undo=False)

        if colors:
            for key, value in colors.items():
                if hasattr(self._state.colors, key):
                    setattr(self._state.colors, key, value)
        if metrics:
            for key, value in metrics.items():
                if hasattr(self._state.metrics, key):
                    setattr(self._state.metrics, key, value)
        if effects:
            for key, value in effects.items():
                if hasattr(self._state.effects, key):
                    setattr(self._state.effects, key, value)

        self._suppress_signals = False
        self._emit_change()

        if save:
            self.save_current()
        return applied

    def save_custom_preset(self, name: str) -> None:
        """Save current theme as a custom preset."""
        self._state.name = name
        self._settings.beginGroup("custom_themes")
        self._settings.setValue(name, json.dumps(self._state.to_dict()))
        self._settings.endGroup()

    def save_qss_preset(self, name: str, qss: str) -> None:
        """Save a raw QSS stylesheet as a named preset."""
        self._settings.beginGroup("qss_themes")
        self._settings.setValue(name, qss)
        self._settings.endGroup()
        # Also apply it immediately
        self.apply_raw_stylesheet(qss, save=True)
        self._state.name = f"[QSS] {name}"
        self.save_current()

    def get_qss_preset(self, name: str) -> str | None:
        """Get a saved QSS preset by name."""
        actual_name = self.get_qss_preset_name(name)
        self._settings.beginGroup("qss_themes")
        qss = self._settings.value(actual_name)
        self._settings.endGroup()
        return qss

    def delete_custom_preset(self, name: str) -> bool:
        """Delete a custom preset (cannot delete built-in)."""
        if name in PRESETS:
            return False

        # Check if it's a QSS preset
        if self.is_qss_preset(name):
            qss_name = self.get_qss_preset_name(name)
            self._settings.beginGroup("qss_themes")
            self._settings.remove(qss_name)
            self._settings.endGroup()
            return True

        # Regular custom preset
        self._settings.beginGroup("custom_themes")
        self._settings.remove(name)
        self._settings.endGroup()
        return True

    # ─────────────────────────────────────────────────────────────────────
    # State Management
    # ─────────────────────────────────────────────────────────────────────

    def get_state(self) -> ThemeState:
        """Get a copy of the current theme state."""
        return self._state.copy()

    def set_state(self, state: ThemeState, record_undo: bool = True) -> None:
        """Set the complete theme state."""
        if record_undo:
            self._push_undo()
        self._state = state.copy()
        self._emit_change()

    def _push_undo(self) -> None:
        """Push current state to undo stack."""
        self._undo_stack.append(self._state.copy())
        if len(self._undo_stack) > self.MAX_UNDO_LEVELS:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> bool:
        """Undo last change."""
        if not self._undo_stack:
            return False
        self._redo_stack.append(self._state.copy())
        self._state = self._undo_stack.pop()
        self._emit_change()
        return True

    def redo(self) -> bool:
        """Redo last undone change."""
        if not self._redo_stack:
            return False
        self._undo_stack.append(self._state.copy())
        self._state = self._redo_stack.pop()
        self._emit_change()
        return True

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    # ─────────────────────────────────────────────────────────────────────
    # Persistence
    # ─────────────────────────────────────────────────────────────────────

    def save_current(self) -> None:
        """Save current theme as the default."""
        self._settings.setValue("current_theme", json.dumps(self._state.to_dict()))

    def load_saved(self) -> None:
        """Load the saved default theme."""
        data = self._settings.value("current_theme")
        if data:
            try:
                self._state = ThemeState.from_dict(json.loads(data))
            except (json.JSONDecodeError, TypeError):
                self.apply_preset("Dark", record_undo=False)
        else:
            self.apply_preset("Dark", record_undo=False)

    def has_raw_qss(self) -> bool:
        """Check if a raw QSS stylesheet is saved."""
        return self._settings.value("use_raw_qss", False, type=bool)

    def get_saved_raw_qss(self) -> str | None:
        """Get the saved raw QSS stylesheet if any."""
        if self.has_raw_qss():
            return self._settings.value("raw_qss", None)
        return None

    def _clear_raw_qss_mode(self) -> None:
        """Clear raw QSS mode silently (used when user edits via controls)."""
        if self.has_raw_qss():
            self._settings.remove("raw_qss")
            self._settings.setValue("use_raw_qss", False)

    def export_to_file(self, path: str | Path) -> None:
        """Export current theme to JSON file."""
        with open(path, "w") as f:
            json.dump(self._state.to_dict(), f, indent=2)

    def import_from_file(self, path: str | Path) -> bool:
        """Import theme from JSON file."""
        try:
            with open(path) as f:
                data = json.load(f)
            self._push_undo()
            self._state = ThemeState.from_dict(data)
            self._emit_change()
            return True
        except (json.JSONDecodeError, FileNotFoundError, TypeError):
            return False

    def import_from_json(self, json_text: str) -> bool:
        """Import theme from JSON string (for paste functionality)."""
        try:
            data = json.loads(json_text)
            self._push_undo()
            self._state = ThemeState.from_dict(data)
            self._emit_change()
            return True
        except (json.JSONDecodeError, TypeError, KeyError):
            return False

    def import_from_qss(self, qss: str, name: str = "Imported QSS") -> bool:
        """Import theme by parsing QSS stylesheet.

        Extracts colors and metrics from QSS and creates an editable theme.
        The theme can then be modified with the editor controls.
        """
        try:
            data = parse_qss_to_theme(qss)
            data["name"] = name
            self._push_undo()
            self._state = ThemeState.from_dict(data)
            self._emit_change()
            return True
        except Exception:
            return False

    def apply_raw_stylesheet(self, qss: str, save: bool = True) -> None:
        """Apply raw QSS stylesheet directly to the application.

        Note: This bypasses the theme engine's color/metric system.
        The controls won't reflect the applied styles.

        Args:
            qss: The QSS stylesheet string to apply.
            save: If True, saves the QSS to settings for persistence.
        """
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app:
            app.setStyleSheet(qss)
        if save:
            self._settings.setValue("raw_qss", qss)
            self._settings.setValue("use_raw_qss", True)

    def clear_raw_stylesheet(self) -> None:
        """Clear any saved raw QSS and restore theme engine control."""
        self._settings.remove("raw_qss")
        self._settings.setValue("use_raw_qss", False)
        self.apply_to_application()

    # ─────────────────────────────────────────────────────────────────────
    # Stylesheet Generation
    # ─────────────────────────────────────────────────────────────────────

    def generate_stylesheet(self) -> str:
        """Generate complete Qt stylesheet from current theme."""
        c = self._state.colors
        m = self._state.metrics
        e = self._state.effects
        button_hover = (
            _adjust_color(c.surface, 1.08) if e.hover_brighten else c.background_alt
        )
        tool_hover = (
            _adjust_color(c.surface, 1.06) if e.hover_brighten else c.background_alt
        )

        return f"""
/* ═══════════════════════════════════════════════════════════════════════
   GitUI Theme: {self._state.name}
   Generated by ThemeEngine
   ═══════════════════════════════════════════════════════════════════════ */

/* ===== Base Styles ===== */
QWidget {{
    background-color: {c.background};
    color: {c.text};
    font-family: {m.font_family};
    font-size: {m.font_size}px;
    selection-background-color: {c.selection_bg};
    selection-color: {c.selection_text};
}}

QMainWindow {{
    background-color: {c.background};
}}

QDialog {{
    background-color: {c.background};
}}

/* ===== Labels ===== */
QLabel {{
    background-color: transparent;
    padding: {m.padding_small}px;
}}

QLabel[heading="true"] {{
    font-size: {m.font_size_h2}px;
    font-weight: bold;
    color: {c.accent};
}}

/* ===== Buttons ===== */
QPushButton {{
    background-color: {c.surface};
    color: {c.text};
    border: {m.border_width}px solid {c.border};
    border-radius: {m.border_radius}px;
    padding: {m.padding}px {m.padding_large}px;
    min-width: {m.button_min_width}px;
    min-height: {m.input_height}px;
}}

QPushButton:hover {{
    background-color: {button_hover};
    border-color: {c.accent};
}}

QPushButton:pressed {{
    background-color: {c.accent_pressed};
    border-color: {c.accent};
}}

QPushButton:disabled {{
    color: {c.text_disabled};
    border-color: {c.border};
    background-color: {c.background_alt};
}}

QPushButton:focus {{
    border-color: {c.border_focus};
    border-width: {m.border_width_focus}px;
}}

/* Primary Button */
QPushButton[primary="true"] {{
    background-color: {c.accent};
    color: {c.selection_text};
    border: none;
    font-weight: bold;
}}

QPushButton[primary="true"]:hover {{
    background-color: {c.accent_hover};
}}

QPushButton[primary="true"]:pressed {{
    background-color: {c.accent_pressed};
}}

/* Danger Button */
QPushButton[danger="true"] {{
    background-color: {c.error};
    color: {c.selection_text};
    border: none;
}}

QPushButton[danger="true"]:hover {{
    background-color: #FF7777;
}}

/* ===== Tool Buttons ===== */
QToolButton {{
    background-color: {c.surface};
    border: {m.border_width}px solid {c.border};
    border-radius: {m.border_radius_small}px;
    padding: {m.padding_small}px;
    min-width: 28px;
    min-height: 28px;
}}

QToolButton:hover {{
    background-color: {tool_hover};
    border-color: {c.accent};
}}

QToolButton:pressed {{
    background-color: {c.accent_pressed};
}}

QToolButton:checked {{
    background-color: {c.accent};
    color: {c.selection_text};
}}

QToolButton::menu-indicator {{
    image: none;
}}

/* ===== Inputs ===== */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {{
    background-color: {c.background_alt};
    color: {c.text};
    border: {m.border_width}px solid {c.border};
    border-radius: {m.border_radius_small}px;
    padding: {m.padding}px;
    min-height: {m.input_height}px;
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {c.border_focus};
    border-width: {m.border_width_focus}px;
}}

QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
    background-color: {c.surface};
    color: {c.text_disabled};
}}

QLineEdit::placeholder {{
    color: {c.text_dim};
}}

/* ===== Combo Box ===== */
QComboBox {{
    background-color: {c.surface};
    color: {c.text};
    border: {m.border_width}px solid {c.border};
    border-radius: {m.border_radius_small}px;
    padding: {m.padding}px {m.padding_large}px {m.padding}px {m.padding}px;
    min-width: 100px;
    min-height: {m.input_height}px;
}}

QComboBox:hover {{
    border-color: {c.accent};
}}

QComboBox:focus {{
    border-color: {c.border_focus};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {c.text_dim};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {c.surface};
    color: {c.text};
    border: {m.border_width}px solid {c.border};
    selection-background-color: {c.accent};
    selection-color: {c.selection_text};
    outline: none;
}}

QComboBox QAbstractItemView::item {{
    padding: {m.padding}px;
    min-height: 28px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: {c.background_alt};
}}

/* ===== Lists ===== */
QListWidget, QListView {{
    background-color: {c.background_alt};
    border: {m.border_width}px solid {c.border};
    border-radius: {m.border_radius_small}px;
    outline: none;
}}

QListWidget::item, QListView::item {{
    padding: {m.padding_small}px {m.padding}px;
    border-radius: {m.border_radius_small}px;
    margin: 1px {m.padding_small}px;
}}

QListWidget::item:hover, QListView::item:hover {{
    background-color: {c.surface};
}}

QListWidget::item:selected, QListView::item:selected {{
    background-color: {c.accent};
    color: {c.selection_text};
}}

/* ===== Tree Widget ===== */
QTreeWidget, QTreeView {{
    background-color: {c.background_alt};
    border: {m.border_width}px solid {c.border};
    border-radius: {m.border_radius_small}px;
    outline: none;
}}

QTreeWidget::item, QTreeView::item {{
    padding: {m.padding_small}px;
    border-radius: {m.border_radius_small}px;
}}

QTreeWidget::item:hover, QTreeView::item:hover {{
    background-color: {c.surface};
}}

QTreeWidget::item:selected, QTreeView::item:selected {{
    background-color: {c.accent};
    color: {c.selection_text};
}}

QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {{
    border-image: none;
    image: none;
}}

QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings {{
    border-image: none;
    image: none;
}}

/* ===== Table Widget ===== */
QTableWidget, QTableView {{
    background-color: {c.background_alt};
    border: {m.border_width}px solid {c.border};
    border-radius: {m.border_radius_small}px;
    gridline-color: {c.border};
    outline: none;
}}

QTableWidget::item, QTableView::item {{
    padding: {m.padding_small}px;
}}

QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {c.accent};
    color: {c.selection_text};
}}

QHeaderView::section {{
    background-color: {c.surface};
    color: {c.text};
    padding: {m.padding}px;
    border: none;
    border-right: {m.border_width}px solid {c.border};
    border-bottom: {m.border_width}px solid {c.border};
    font-weight: bold;
}}

QHeaderView::section:hover {{
    background-color: {c.background_alt};
}}

/* ===== Group Box ===== */
QGroupBox {{
    background-color: {c.background_alt};
    border: {m.border_width}px solid {c.border};
    border-radius: {m.border_radius}px;
    margin-top: 16px;
    padding-top: 12px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: {m.padding}px;
    padding: 0 {m.padding}px;
    color: {c.accent};
    background-color: {c.background_alt};
}}

QGroupBox[editorSection="true"] {{
    background-color: transparent;
    border: none;
    margin-top: 10px;
    padding-top: 8px;
}}

QGroupBox[editorSection="true"]::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 0;
    padding: 0 {m.padding}px;
    color: {c.text_dim};
    background-color: transparent;
}}

/* ===== Tabs ===== */
QTabWidget::pane {{
    background-color: {c.background_alt};
    border: {m.border_width}px solid {c.border};
    border-radius: {m.border_radius}px;
    border-top-left-radius: 0;
}}

QTabBar::tab {{
    background-color: {c.surface};
    color: {c.text_dim};
    border: {m.border_width}px solid {c.border};
    border-bottom: none;
    border-top-left-radius: {m.border_radius}px;
    border-top-right-radius: {m.border_radius}px;
    padding: {m.padding}px {m.padding_large}px;
    margin-right: 2px;
}}

QTabBar::tab:selected {{
    background-color: {c.background_alt};
    color: {c.text};
    border-bottom: 2px solid {c.accent};
}}

QTabBar::tab:hover:!selected {{
    background-color: {c.background_alt};
    color: {c.text};
}}

/* ===== Splitter ===== */
QSplitter::handle {{
    background-color: {c.border};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

QSplitter::handle:hover {{
    background-color: {c.accent};
}}

/* ===== Scrollbars ===== */
QScrollBar:vertical {{
    background-color: {c.background_alt};
    width: {m.scrollbar_width}px;
    border-radius: {m.scrollbar_width // 2}px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background-color: {c.border};
    min-height: 30px;
    border-radius: {m.scrollbar_width // 2 - 1}px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {c.accent};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {c.background_alt};
    height: {m.scrollbar_width}px;
    border-radius: {m.scrollbar_width // 2}px;
    margin: 2px;
}}

QScrollBar::handle:horizontal {{
    background-color: {c.border};
    min-width: 30px;
    border-radius: {m.scrollbar_width // 2 - 1}px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {c.accent};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
    width: 0;
}}

/* ===== Menus ===== */
QMenuBar {{
    background-color: {c.surface};
    color: {c.text};
    border-bottom: {m.border_width}px solid {c.border};
    padding: 2px;
}}

QMenuBar::item {{
    padding: {m.padding}px {m.padding_large}px;
    border-radius: {m.border_radius_small}px;
}}

QMenuBar::item:selected {{
    background-color: {c.background_alt};
}}

QMenu {{
    background-color: {c.surface};
    color: {c.text};
    border: {m.border_width}px solid {c.border};
    border-radius: {m.border_radius}px;
    padding: {m.padding_small}px;
}}

QMenu::item {{
    padding: {m.padding}px {m.padding_large}px;
    border-radius: {m.border_radius_small}px;
}}

QMenu::item:selected {{
    background-color: {c.accent};
    color: {c.selection_text};
}}

QMenu::separator {{
    height: 1px;
    background-color: {c.border};
    margin: {m.spacing}px {m.padding}px;
}}

QMenu::indicator {{
    width: 16px;
    height: 16px;
    margin-left: {m.padding}px;
}}

/* ===== Toolbar ===== */
QToolBar {{
    background-color: {c.surface};
    border: none;
    border-bottom: {m.border_width}px solid {c.border};
    padding: {m.padding_small}px;
    spacing: {m.spacing}px;
}}

QToolBar::separator {{
    width: 1px;
    background-color: {c.border};
    margin: {m.padding_small}px {m.padding}px;
}}

/* ===== Status Bar ===== */
QStatusBar {{
    background-color: {c.surface};
    color: {c.text_dim};
    border-top: {m.border_width}px solid {c.border};
}}

QStatusBar::item {{
    border: none;
}}

/* ===== Progress Bar ===== */
QProgressBar {{
    background-color: {c.background_alt};
    border: {m.border_width}px solid {c.border};
    border-radius: {m.border_radius_small}px;
    text-align: center;
    color: {c.text};
}}

QProgressBar::chunk {{
    background-color: {c.accent};
    border-radius: {m.border_radius_small - 1}px;
}}

/* ===== Slider ===== */
QSlider::groove:horizontal {{
    border: none;
    height: 4px;
    background-color: {c.border};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background-color: {c.accent};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background-color: {c.accent_hover};
}}

QSlider::groove:vertical {{
    border: none;
    width: 4px;
    background-color: {c.border};
    border-radius: 2px;
}}

QSlider::handle:vertical {{
    background-color: {c.accent};
    width: 16px;
    height: 16px;
    margin: 0 -6px;
    border-radius: 8px;
}}

/* ===== Checkbox & Radio ===== */
QCheckBox, QRadioButton {{
    spacing: {m.spacing}px;
    color: {c.text};
}}

QCheckBox::indicator, QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: {m.border_width}px solid {c.border};
    border-radius: 4px;
    background-color: {c.background_alt};
}}

QRadioButton::indicator {{
    border-radius: 9px;
}}

QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background-color: {c.accent};
    border-color: {c.accent};
}}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
    border-color: {c.accent};
}}

QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {{
    background-color: {c.surface};
    border-color: {c.border};
}}

/* ===== Tooltips ===== */
QToolTip {{
    background-color: {c.surface};
    color: {c.text};
    border: {m.border_width}px solid {c.accent};
    border-radius: {m.border_radius_small}px;
    padding: {m.padding}px;
}}

/* ===== Dock Widget ===== */
QDockWidget {{
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}}

QDockWidget::title {{
    background-color: {c.surface};
    padding: {m.padding}px;
    border-bottom: {m.border_width}px solid {c.border};
}}

/* ===== Dialog Buttons ===== */
QDialogButtonBox QPushButton {{
    min-width: 80px;
}}

/* ===== Font Combo Box ===== */
QFontComboBox {{
    background-color: {c.surface};
    border: {m.border_width}px solid {c.border};
    border-radius: {m.border_radius_small}px;
    padding: {m.padding}px;
}}

/* ===== Color Dialog ===== */
QColorDialog {{
    background-color: {c.background};
}}

/* ===== Git-specific Styles ===== */

/* Staged files - green accent */
QListWidget[gitStatus="staged"]::item {{
    border-left: 3px solid {c.success};
}}

/* Unstaged files - yellow accent */
QListWidget[gitStatus="unstaged"]::item {{
    border-left: 3px solid {c.warning};
}}

/* Untracked files - blue accent */
QListWidget[gitStatus="untracked"]::item {{
    border-left: 3px solid {c.info};
}}

/* Conflicted files - red accent */
QListWidget[gitStatus="conflicted"]::item {{
    border-left: 3px solid {c.error};
}}

/* Diff viewer */
QPlainTextEdit[diffViewer="true"] {{
    font-family: {m.font_family_mono};
    font-size: {m.font_size}px;
    background-color: {c.background};
}}

/* Console widget */
QPlainTextEdit[consoleWidget="true"] {{
    font-family: {m.font_family_mono};
    font-size: {m.font_size_small}px;
    background-color: #0D0D0D;
}}
"""

    def apply_to_application(self) -> None:
        """Apply the current theme to the application."""
        app = QApplication.instance()
        if not app:
            return

        # Check if we should use raw QSS instead
        raw_qss = self.get_saved_raw_qss()
        if raw_qss:
            app.setStyleSheet(raw_qss)
        else:
            css = self.generate_stylesheet()
            app.setStyleSheet(css)

        # Set application font
        font = QFont(
            self._state.metrics.font_family.split(",")[0].strip(),
            self._state.metrics.font_size,
        )
        app.setFont(font)

    def set_apply_enabled(self, enabled: bool) -> None:
        """Control whether theme changes apply to QApplication immediately."""
        self._apply_enabled = enabled
        if enabled:
            # Apply current state immediately when re-enabled.
            self.apply_to_application()

    def _emit_change(self) -> None:
        """Emit theme changed signal and apply to app."""
        if not self._suppress_signals:
            if self._apply_enabled:
                self.apply_to_application()
            self.theme_changed.emit()


# ---------------------------------------------------------------------------
# Singleton Instance
# ---------------------------------------------------------------------------

_engine_instance: ThemeEngine | None = None


def get_engine() -> ThemeEngine:
    """Get the singleton ThemeEngine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = ThemeEngine()
    return _engine_instance


def init_theme() -> None:
    """Initialize the theme system and load saved preferences."""
    engine = get_engine()
    engine.load_saved()
    # Check for raw QSS override
    raw_qss = engine.get_saved_raw_qss()
    if raw_qss:
        engine.apply_raw_stylesheet(raw_qss, save=False)
    else:
        engine.apply_to_application()
