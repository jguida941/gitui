from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QGroupBox

from app.ui.theme_engine import ThemeEffects
from app.ui.theme_preview import ThemePreview

app = QApplication.instance() or QApplication([])


def test_theme_preview_builds_groups() -> None:
    preview = ThemePreview()
    groups = preview.findChildren(QGroupBox)

    titles = {group.title() for group in groups}
    assert "Buttons" in titles
    assert "Inputs" in titles
    assert "Lists" in titles


def test_theme_preview_applies_shadow_effects() -> None:
    preview = ThemePreview()
    effects = ThemeEffects(
        shadow_enabled=True,
        shadow_x=2,
        shadow_y=3,
        shadow_blur=6,
        shadow_spread=2,
        shadow_color="rgba(0, 0, 0, 0.4)",
    )
    preview.apply_effects(effects)

    groups = preview.findChildren(QGroupBox)
    assert groups
    assert all(group.graphicsEffect() is not None for group in groups)

    preview.apply_effects(ThemeEffects(shadow_enabled=False))
    assert all(group.graphicsEffect() is None for group in groups)
