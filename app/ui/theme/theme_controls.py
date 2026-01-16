"""Shared UI controls for the theme editor."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton, QWidget


class ColorPickerButton(QPushButton):
    """Button that shows a color swatch and emits when it changes."""

    color_changed = Signal(str)

    def __init__(
        self,
        color: str = "#FFFFFF",
        parent: QWidget | None = None,
        allow_alpha: bool = False,
    ) -> None:
        super().__init__(parent)
        self._color = color
        self._allow_alpha = allow_alpha
        self.setFixedSize(70, 28)
        self._update_style()
        self.clicked.connect(self._pick_color)

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        self._color = value
        self._update_style()

    def _update_style(self) -> None:
        # Pick a readable label color so the hex stays visible.
        qc = QColor(self._color)
        luminance = 0.299 * qc.red() + 0.587 * qc.green() + 0.114 * qc.blue()
        text_color = "#000000" if luminance > 128 else "#FFFFFF"

        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self._color};
                color: {text_color};
                border: 1px solid #555;
                border-radius: 4px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                border: 2px solid #00FFAA;
            }}
        """
        )
        self.setText(self._color.upper())

    def _pick_color(self) -> None:
        options = QColorDialog.ColorDialogOption.ShowAlphaChannel if self._allow_alpha else QColorDialog.ColorDialogOption(0)
        color = QColorDialog.getColor(QColor(self._color), self, "Pick Color", options)
        if color.isValid():
            if self._allow_alpha:
                alpha = color.alphaF()
                self._color = f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha:.2f})"
            else:
                self._color = color.name()
            self._update_style()
            self.color_changed.emit(self._color)
