from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QColorDialog

from app.ui.theme.theme_controls import ColorPickerButton

app = QApplication.instance() or QApplication([])


def test_color_picker_button_updates_color(monkeypatch) -> None:
    button = ColorPickerButton("#112233")

    def fake_get_color(*_args, **_kwargs) -> QColor:
        return QColor("#ABCDEF")

    monkeypatch.setattr(QColorDialog, "getColor", staticmethod(fake_get_color))
    button._pick_color()

    assert button.color.lower() == "#abcdef"


def test_color_picker_button_alpha(monkeypatch) -> None:
    button = ColorPickerButton("rgba(0, 0, 0, 0.5)", allow_alpha=True)

    def fake_get_color(*_args, **_kwargs) -> QColor:
        return QColor(10, 20, 30, 128)

    monkeypatch.setattr(QColorDialog, "getColor", staticmethod(fake_get_color))
    button._pick_color()

    assert button.color.startswith("rgba(10, 20, 30,")
