"""Full theme editor dialog wired to ThemeEngine."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QPlainTextEdit,
    QFontComboBox,
    QSplitter,
)

from app.ui.theme_controls import ColorPickerButton
from app.ui.theme_engine import PRESETS, ThemeEngine, get_engine
from app.ui.theme_preview import ThemePreview


class ThemeEditorDialog(QDialog):
    """Theme editor with presets, live preview, and import/export tools."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Theme Editor")
        self.setMinimumSize(1100, 720)

        self._engine: ThemeEngine = get_engine()
        self._updating_controls = False

        self._color_controls: dict[str, ColorPickerButton] = {}
        self._metric_controls: dict[str, QSpinBox] = {}
        self._effect_controls: dict[str, QWidget] = {}
        self._font_controls: dict[str, QWidget] = {}

        self._setup_ui()
        self._sync_from_engine()

        # Keep the editor in sync with any external theme changes.
        self._engine.theme_changed.connect(self._sync_from_engine)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        # Re-enable live application so the app doesn't get stuck in preview-only mode.
        self._engine.set_apply_enabled(True)
        super().closeEvent(event)

    def _setup_ui(self) -> None:
        """Build the dialog layout and editor tabs."""
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        root.addWidget(self._build_toolbar())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_editor_tabs())
        splitter.addWidget(self._build_preview_panel())
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        root.addWidget(splitter)

    def _build_toolbar(self) -> QWidget:
        """Top toolbar with presets, undo/redo, and live preview toggle."""
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(QLabel("Preset"))
        self._preset_combo = QComboBox()
        self._preset_combo.setToolTip("Load a preset theme")
        self._preset_combo.currentTextChanged.connect(self._on_preset_selected)
        layout.addWidget(self._preset_combo, 2)

        self._save_preset_btn = QPushButton("Save Preset")
        self._save_preset_btn.setToolTip("Save current theme as a custom preset")
        self._save_preset_btn.clicked.connect(self._save_preset)
        layout.addWidget(self._save_preset_btn)

        self._delete_preset_btn = QPushButton("Delete Preset")
        self._delete_preset_btn.setToolTip("Delete a custom preset")
        self._delete_preset_btn.clicked.connect(self._delete_preset)
        layout.addWidget(self._delete_preset_btn)

        layout.addSpacing(10)

        self._undo_btn = QPushButton("Undo")
        self._undo_btn.setToolTip("Undo the last theme change")
        self._undo_btn.clicked.connect(self._undo)
        layout.addWidget(self._undo_btn)

        self._redo_btn = QPushButton("Redo")
        self._redo_btn.setToolTip("Redo the last undone change")
        self._redo_btn.clicked.connect(self._redo)
        layout.addWidget(self._redo_btn)

        layout.addSpacing(10)

        self._live_preview = QCheckBox("Live Preview")
        self._live_preview.setChecked(True)
        self._live_preview.setToolTip("Apply theme changes to the whole app")
        self._live_preview.toggled.connect(self._toggle_live_preview)
        layout.addWidget(self._live_preview)

        layout.addStretch()
        return bar

    def _build_editor_tabs(self) -> QWidget:
        """Create the tabbed editor area."""
        tabs = QTabWidget()
        tabs.addTab(self._build_colors_tab(), "Colors")
        tabs.addTab(self._build_fonts_tab(), "Fonts")
        tabs.addTab(self._build_metrics_tab(), "Metrics")
        tabs.addTab(self._build_effects_tab(), "Effects")
        tabs.addTab(self._build_import_export_tab(), "Import/Export")
        return tabs

    def _build_colors_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)

        categories: dict[str, list[str]] = {
            "Backgrounds": ["background", "background_alt", "surface"],
            "Text": ["text", "text_dim", "text_disabled"],
            "Borders": ["border", "border_focus"],
            "Accent": ["accent", "accent_hover", "accent_pressed"],
            "Status": ["success", "warning", "error", "info"],
            "Diff": ["diff_add", "diff_remove", "diff_header", "diff_hunk"],
            "Selection": ["selection_bg", "selection_text"],
            "Links": ["link", "link_visited"],
        }

        for title, keys in categories.items():
            group = QGroupBox(title)
            group_layout = QFormLayout(group)
            for key in keys:
                btn = ColorPickerButton()
                btn.color_changed.connect(lambda value, name=key: self._on_color_changed(name, value))
                self._color_controls[key] = btn
                group_layout.addRow(QLabel(self._labelize(key)), btn)
            layout.addWidget(group)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def _build_fonts_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        families = QGroupBox("Font Families")
        families_layout = QFormLayout(families)

        font_family = QFontComboBox()
        font_family.currentFontChanged.connect(
            lambda font: self._on_metric_changed("font_family", font.family())
        )
        families_layout.addRow("UI Font", font_family)
        self._font_controls["font_family"] = font_family

        font_mono = QFontComboBox()
        font_mono.currentFontChanged.connect(
            lambda font: self._on_metric_changed("font_family_mono", font.family())
        )
        families_layout.addRow("Mono Font", font_mono)
        self._font_controls["font_family_mono"] = font_mono

        sizes = QGroupBox("Font Sizes")
        sizes_layout = QFormLayout(sizes)
        for key, label, minimum, maximum in [
            ("font_size", "Base", 8, 20),
            ("font_size_small", "Small", 8, 18),
            ("font_size_large", "Large", 10, 28),
            ("font_size_h1", "Heading 1", 14, 36),
            ("font_size_h2", "Heading 2", 12, 32),
            ("font_size_h3", "Heading 3", 10, 28),
        ]:
            spin = self._make_spinbox(minimum, maximum)
            spin.valueChanged.connect(lambda value, name=key: self._on_metric_changed(name, value))
            self._metric_controls[key] = spin
            sizes_layout.addRow(label, spin)

        layout.addWidget(families)
        layout.addWidget(sizes)
        layout.addStretch()
        return widget

    def _build_metrics_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)

        border = QGroupBox("Borders")
        border_layout = QFormLayout(border)
        for key, label, minimum, maximum in [
            ("border_radius", "Radius", 0, 24),
            ("border_radius_small", "Radius (Small)", 0, 16),
            ("border_radius_large", "Radius (Large)", 0, 32),
            ("border_width", "Width", 0, 4),
            ("border_width_focus", "Focus Width", 0, 6),
        ]:
            spin = self._make_spinbox(minimum, maximum)
            spin.valueChanged.connect(lambda value, name=key: self._on_metric_changed(name, value))
            self._metric_controls[key] = spin
            border_layout.addRow(label, spin)

        spacing = QGroupBox("Spacing")
        spacing_layout = QFormLayout(spacing)
        for key, label, minimum, maximum in [
            ("padding", "Padding", 0, 20),
            ("padding_small", "Padding (Small)", 0, 16),
            ("padding_large", "Padding (Large)", 0, 24),
            ("spacing", "Spacing", 0, 16),
            ("margin", "Margin", 0, 20),
        ]:
            spin = self._make_spinbox(minimum, maximum)
            spin.valueChanged.connect(lambda value, name=key: self._on_metric_changed(name, value))
            self._metric_controls[key] = spin
            spacing_layout.addRow(label, spin)

        widgets = QGroupBox("Widgets")
        widgets_layout = QFormLayout(widgets)
        for key, label, minimum, maximum in [
            ("button_min_width", "Button Min Width", 40, 200),
            ("input_height", "Input Height", 20, 60),
            ("toolbar_height", "Toolbar Height", 24, 80),
            ("scrollbar_width", "Scrollbar Width", 6, 20),
        ]:
            spin = self._make_spinbox(minimum, maximum)
            spin.valueChanged.connect(lambda value, name=key: self._on_metric_changed(name, value))
            self._metric_controls[key] = spin
            widgets_layout.addRow(label, spin)

        layout.addWidget(border)
        layout.addWidget(spacing)
        layout.addWidget(widgets)
        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def _build_effects_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        shadow = QGroupBox("Shadow")
        shadow_layout = QFormLayout(shadow)

        shadow_enabled = QCheckBox("Enable")
        shadow_enabled.toggled.connect(
            lambda value, name="shadow_enabled": self._on_effect_changed(name, value)
        )
        shadow_layout.addRow("Enabled", shadow_enabled)
        self._effect_controls["shadow_enabled"] = shadow_enabled

        for key, label, minimum, maximum in [
            ("shadow_x", "Offset X", -20, 20),
            ("shadow_y", "Offset Y", -20, 20),
            ("shadow_blur", "Blur", 0, 60),
            ("shadow_spread", "Spread", -10, 20),
        ]:
            spin = self._make_spinbox(minimum, maximum)
            spin.valueChanged.connect(lambda value, name=key: self._on_effect_changed(name, value))
            self._effect_controls[key] = spin
            shadow_layout.addRow(label, spin)

        shadow_color = ColorPickerButton(allow_alpha=True)
        shadow_color.color_changed.connect(
            lambda value, name="shadow_color": self._on_effect_changed(name, value)
        )
        self._effect_controls["shadow_color"] = shadow_color
        shadow_layout.addRow("Shadow Color", shadow_color)

        transitions = QGroupBox("Transitions")
        transitions_layout = QFormLayout(transitions)
        duration = self._make_spinbox(0, 1000)
        duration.valueChanged.connect(
            lambda value, name="transition_duration": self._on_effect_changed(name, value)
        )
        transitions_layout.addRow("Duration (ms)", duration)
        self._effect_controls["transition_duration"] = duration

        timing = QComboBox()
        timing.addItems(["ease", "ease-in", "ease-out", "linear"])
        timing.currentTextChanged.connect(
            lambda value, name="transition_timing": self._on_effect_changed(name, value)
        )
        transitions_layout.addRow("Timing", timing)
        self._effect_controls["transition_timing"] = timing

        hover = QGroupBox("Hover")
        hover_layout = QFormLayout(hover)
        brighten = QCheckBox("Brighten")
        brighten.toggled.connect(
            lambda value, name="hover_brighten": self._on_effect_changed(name, value)
        )
        hover_layout.addRow("Brighten", brighten)
        self._effect_controls["hover_brighten"] = brighten

        scale = QCheckBox("Scale")
        scale.toggled.connect(
            lambda value, name="hover_scale": self._on_effect_changed(name, value)
        )
        hover_layout.addRow("Scale", scale)
        self._effect_controls["hover_scale"] = scale

        layout.addWidget(shadow)
        layout.addWidget(transitions)
        layout.addWidget(hover)
        layout.addStretch()
        return widget

    def _build_import_export_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        actions = QGroupBox("Actions")
        actions_layout = QHBoxLayout(actions)

        import_json = QPushButton("Import JSON")
        import_json.clicked.connect(self._import_json)
        actions_layout.addWidget(import_json)

        export_json = QPushButton("Export JSON")
        export_json.clicked.connect(self._export_json)
        actions_layout.addWidget(export_json)

        export_qss = QPushButton("Export QSS")
        export_qss.clicked.connect(self._export_qss)
        actions_layout.addWidget(export_qss)

        actions_layout.addStretch()

        layout.addWidget(actions)

        preview = QGroupBox("Generated QSS Preview")
        preview_layout = QVBoxLayout(preview)
        self._export_preview = QPlainTextEdit()
        self._export_preview.setReadOnly(True)
        self._export_preview.setLineWrapMode(QPlainTextEdit.NoWrap)
        preview_layout.addWidget(self._export_preview)
        layout.addWidget(preview, 1)
        return widget

    def _build_preview_panel(self) -> QWidget:
        """Live preview on the right side of the dialog."""
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("Live Preview")
        header.setProperty("heading", True)
        layout.addWidget(header)

        preview_scroll = QScrollArea()
        preview_scroll.setWidgetResizable(True)
        self._preview = ThemePreview()
        preview_scroll.setWidget(self._preview)
        layout.addWidget(preview_scroll, 1)
        return wrapper

    def _make_spinbox(self, minimum: int, maximum: int) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        return spin

    def _labelize(self, name: str) -> str:
        return name.replace("_", " ").title()

    def _toggle_live_preview(self, enabled: bool) -> None:
        # When live preview is off, we style only the preview panel.
        self._engine.set_apply_enabled(enabled)
        if not enabled:
            self._preview.setStyleSheet(self._engine.generate_stylesheet())
        else:
            self._preview.setStyleSheet("")

    def _on_preset_selected(self, name: str) -> None:
        if self._updating_controls:
            return
        self._engine.apply_theme(name, save=True)
        self._engine.save_current()
        self._refresh_preset_combo()

    def _on_color_changed(self, name: str, value: str) -> None:
        if self._updating_controls:
            return
        self._engine.set_color(name, value)
        self._engine.save_current()

    def _on_metric_changed(self, name: str, value: int | str) -> None:
        if self._updating_controls:
            return
        self._engine.set_metric(name, value)
        self._engine.save_current()

    def _on_effect_changed(self, name: str, value: object) -> None:
        if self._updating_controls:
            return
        self._engine.set_effect(name, value)
        self._engine.save_current()

    def _save_preset(self) -> None:
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if not ok or not name.strip():
            return
        self._engine.save_custom_preset(name.strip())
        self._refresh_preset_combo()

    def _delete_preset(self) -> None:
        name = self._preset_combo.currentText()
        if not name:
            return
        if not self._engine.delete_custom_preset(name):
            QMessageBox.information(self, "Cannot Delete", "Built-in presets cannot be deleted.")
            return
        self._refresh_preset_combo()

    def _undo(self) -> None:
        if self._engine.undo():
            self._engine.save_current()

    def _redo(self) -> None:
        if self._engine.redo():
            self._engine.save_current()

    def _import_json(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Theme", "", "JSON Files (*.json);;All Files (*.*)"
        )
        if not filename:
            return
        if not self._engine.import_from_file(filename):
            QMessageBox.warning(self, "Import Failed", "Could not load theme JSON.")
            return
        self._engine.save_current()
        self._refresh_preset_combo()

    def _export_json(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Theme (JSON)", "", "JSON Files (*.json);;All Files (*.*)"
        )
        if not filename:
            return
        self._engine.export_to_file(filename)

    def _export_qss(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Theme (QSS)", "", "Qt Stylesheets (*.qss);;All Files (*.*)"
        )
        if not filename:
            return
        css = self._engine.generate_stylesheet()
        Path(filename).write_text(css, encoding="utf-8")

    def _refresh_preset_combo(self) -> None:
        current = self._engine.current_theme
        presets = self._engine.get_preset_names()
        self._preset_combo.blockSignals(True)
        self._preset_combo.clear()
        self._preset_combo.addItems(presets)
        if current in presets:
            self._preset_combo.setCurrentText(current)
        self._preset_combo.blockSignals(False)
        self._delete_preset_btn.setEnabled(current not in PRESETS)

    def _sync_from_engine(self) -> None:
        """Refresh control values from the ThemeEngine state."""
        self._updating_controls = True
        try:
            state = self._engine.get_state()

            for name, btn in self._color_controls.items():
                btn.color = getattr(state.colors, name, btn.color)

            for name, spin in self._metric_controls.items():
                if hasattr(state.metrics, name):
                    spin.setValue(int(getattr(state.metrics, name)))

            for name, control in self._font_controls.items():
                if name == "font_family":
                    control.setCurrentFont(QFont(state.metrics.font_family))
                if name == "font_family_mono":
                    control.setCurrentFont(QFont(state.metrics.font_family_mono))

            for name, control in self._effect_controls.items():
                value = getattr(state.effects, name, None)
                if isinstance(control, QCheckBox):
                    control.setChecked(bool(value))
                elif isinstance(control, QSpinBox):
                    control.setValue(int(value))
                elif isinstance(control, QComboBox) and isinstance(value, str):
                    control.setCurrentText(value)
                elif isinstance(control, ColorPickerButton) and isinstance(value, str):
                    control.color = value

            self._refresh_preset_combo()
            self._export_preview.setPlainText(self._engine.generate_stylesheet())
            self._undo_btn.setEnabled(self._engine.can_undo())
            self._redo_btn.setEnabled(self._engine.can_redo())

            if not self._live_preview.isChecked():
                self._preview.setStyleSheet(self._engine.generate_stylesheet())
        finally:
            self._updating_controls = False
