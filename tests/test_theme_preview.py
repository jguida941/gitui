from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QGroupBox

from app.ui.theme_preview import ThemePreview

app = QApplication.instance() or QApplication([])


def test_theme_preview_builds_groups() -> None:
    preview = ThemePreview()
    groups = preview.findChildren(QGroupBox)

    titles = {group.title() for group in groups}
    assert "Buttons" in titles
    assert "Inputs" in titles
    assert "Lists" in titles
