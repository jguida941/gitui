"""Live preview widget for the theme editor."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QProgressBar,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QPushButton,
    QGraphicsDropShadowEffect,
)

from app.ui.theme_engine import ThemeEffects

class ThemePreview(QWidget):
    """Compact preview gallery that exercises common widgets."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(self._build_button_group())
        layout.addWidget(self._build_input_group())
        layout.addWidget(self._build_list_group())
        layout.addWidget(self._build_progress_group())
        layout.addWidget(self._build_misc_group())
        layout.addStretch()

    def _build_button_group(self) -> QGroupBox:
        group = QGroupBox("Buttons")
        row = QHBoxLayout(group)

        primary = QPushButton("Primary")
        primary.setProperty("primary", True)

        danger = QPushButton("Danger")
        danger.setProperty("danger", True)

        tool = QToolButton()
        tool.setText("Tool")

        row.addWidget(QPushButton("Default"))
        row.addWidget(primary)
        row.addWidget(danger)
        row.addWidget(tool)
        row.addStretch()
        return group

    def _build_input_group(self) -> QGroupBox:
        group = QGroupBox("Inputs")
        layout = QVBoxLayout(group)

        line = QLineEdit()
        line.setPlaceholderText("Search or type here")

        combo = QComboBox()
        combo.addItems(["Option A", "Option B", "Option C"])

        spin = QSpinBox()
        spin.setRange(0, 99)
        spin.setValue(42)

        text = QTextEdit()
        text.setPlainText("Multi-line\ntext input")
        text.setFixedHeight(60)

        layout.addWidget(line)
        layout.addWidget(combo)
        layout.addWidget(spin)
        layout.addWidget(text)
        return group

    def _build_list_group(self) -> QGroupBox:
        group = QGroupBox("Lists")
        layout = QHBoxLayout(group)

        staged = QListWidget()
        staged.setProperty("gitStatus", "staged")
        staged.addItem(QListWidgetItem("staged_file.py"))

        unstaged = QListWidget()
        unstaged.setProperty("gitStatus", "unstaged")
        unstaged.addItem(QListWidgetItem("changed_file.py"))

        untracked = QListWidget()
        untracked.setProperty("gitStatus", "untracked")
        untracked.addItem(QListWidgetItem("new_file.py"))

        layout.addWidget(staged)
        layout.addWidget(unstaged)
        layout.addWidget(untracked)
        return group

    def _build_progress_group(self) -> QGroupBox:
        group = QGroupBox("Progress")
        layout = QVBoxLayout(group)

        progress = QProgressBar()
        progress.setValue(60)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setValue(30)

        layout.addWidget(progress)
        layout.addWidget(slider)
        return group

    def _build_misc_group(self) -> QGroupBox:
        group = QGroupBox("Misc")
        layout = QHBoxLayout(group)

        checkbox = QCheckBox("Checkbox")
        checkbox.setChecked(True)

        radio = QRadioButton("Radio")
        radio.setChecked(True)

        table = QTableWidget(2, 2)
        table.setHorizontalHeaderLabels(["Col A", "Col B"])
        table.setItem(0, 0, QTableWidgetItem("A1"))
        table.setItem(0, 1, QTableWidgetItem("B1"))
        table.setItem(1, 0, QTableWidgetItem("A2"))
        table.setItem(1, 1, QTableWidgetItem("B2"))
        table.setMaximumHeight(110)

        diff = QPlainTextEdit()
        diff.setProperty("diffViewer", True)
        diff.setPlainText("--- a/file.py\n+++ b/file.py\n@@\n+added line")
        diff.setMaximumHeight(90)

        layout.addWidget(checkbox)
        layout.addWidget(radio)
        layout.addWidget(table)
        layout.addWidget(diff)
        return group

    def apply_effects(self, effects: ThemeEffects) -> None:
        """Apply effect settings to the preview widgets."""
        groups = self.findChildren(QGroupBox)
        if not effects.shadow_enabled:
            for group in groups:
                group.setGraphicsEffect(None)
            return

        for group in groups:
            group.setGraphicsEffect(self._build_shadow_effect(effects))

    def _build_shadow_effect(self, effects: ThemeEffects) -> QGraphicsDropShadowEffect:
        effect = QGraphicsDropShadowEffect(self)
        effect.setOffset(effects.shadow_x, effects.shadow_y)
        # Qt drop shadows do not support spread; fold it into blur.
        blur = max(0, effects.shadow_blur + effects.shadow_spread)
        effect.setBlurRadius(blur)
        effect.setColor(self._parse_shadow_color(effects.shadow_color))
        return effect

    def _parse_shadow_color(self, value: str) -> QColor:
        color = QColor(value)
        if color.isValid():
            return color

        text = value.strip().lower()
        if text.startswith("rgba(") and text.endswith(")"):
            parts = [p.strip() for p in text[5:-1].split(",")]
            if len(parts) >= 4:
                try:
                    red = int(float(parts[0]))
                    green = int(float(parts[1]))
                    blue = int(float(parts[2]))
                    alpha_raw = float(parts[3])
                except ValueError:
                    return QColor(0, 0, 0, 120)
                alpha = int(alpha_raw * 255) if alpha_raw <= 1 else int(alpha_raw)
                return QColor(red, green, blue, max(0, min(alpha, 255)))

        return QColor(0, 0, 0, 120)
