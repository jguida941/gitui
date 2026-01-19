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
    QFontComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .theme_controls import ColorPickerButton
from .theme_engine import PRESETS, ThemeEngine, get_engine
from .theme_preview import ThemePreview


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
            group = self._make_editor_group(title)
            group_layout = QFormLayout(group)
            for key in keys:
                btn = ColorPickerButton()
                btn.color_changed.connect(
                    lambda value, name=key: self._on_color_changed(name, value)
                )
                self._color_controls[key] = btn
                group_layout.addRow(QLabel(self._labelize(key)), btn)
            layout.addWidget(group)

        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def _build_fonts_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        families = self._make_editor_group("Font Families")
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

        sizes = self._make_editor_group("Font Sizes")
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
            spin.valueChanged.connect(
                lambda value, name=key: self._on_metric_changed(name, value)
            )
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

        border = self._make_editor_group("Borders")
        border_layout = QFormLayout(border)
        for key, label, minimum, maximum in [
            ("border_radius", "Radius", 0, 24),
            ("border_radius_small", "Radius (Small)", 0, 16),
            ("border_radius_large", "Radius (Large)", 0, 32),
            ("border_width", "Width", 0, 4),
            ("border_width_focus", "Focus Width", 0, 6),
        ]:
            spin = self._make_spinbox(minimum, maximum)
            spin.valueChanged.connect(
                lambda value, name=key: self._on_metric_changed(name, value)
            )
            self._metric_controls[key] = spin
            border_layout.addRow(label, spin)

        spacing = self._make_editor_group("Spacing")
        spacing_layout = QFormLayout(spacing)
        for key, label, minimum, maximum in [
            ("padding", "Padding", 0, 20),
            ("padding_small", "Padding (Small)", 0, 16),
            ("padding_large", "Padding (Large)", 0, 24),
            ("spacing", "Spacing", 0, 16),
            ("margin", "Margin", 0, 20),
        ]:
            spin = self._make_spinbox(minimum, maximum)
            spin.valueChanged.connect(
                lambda value, name=key: self._on_metric_changed(name, value)
            )
            self._metric_controls[key] = spin
            spacing_layout.addRow(label, spin)

        widgets = self._make_editor_group("Widgets")
        widgets_layout = QFormLayout(widgets)
        for key, label, minimum, maximum in [
            ("button_min_width", "Button Min Width", 40, 200),
            ("input_height", "Input Height", 20, 60),
            ("toolbar_height", "Toolbar Height", 24, 80),
            ("scrollbar_width", "Scrollbar Width", 6, 20),
        ]:
            spin = self._make_spinbox(minimum, maximum)
            spin.valueChanged.connect(
                lambda value, name=key: self._on_metric_changed(name, value)
            )
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

        shadow = self._make_editor_group("Shadow")
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
            spin.valueChanged.connect(
                lambda value, name=key: self._on_effect_changed(name, value)
            )
            self._effect_controls[key] = spin
            shadow_layout.addRow(label, spin)

        shadow_color = ColorPickerButton(allow_alpha=True)
        shadow_color.color_changed.connect(
            lambda value, name="shadow_color": self._on_effect_changed(name, value)
        )
        self._effect_controls["shadow_color"] = shadow_color
        shadow_layout.addRow("Shadow Color", shadow_color)

        transitions = self._make_editor_group("Transitions")
        transitions_layout = QFormLayout(transitions)
        duration = self._make_spinbox(0, 1000)
        duration.valueChanged.connect(
            lambda value, name="transition_duration": self._on_effect_changed(
                name, value
            )
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

        hover = self._make_editor_group("Hover")
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

        # File-based actions
        file_actions = self._make_editor_group("File Operations")
        file_actions_layout = QHBoxLayout(file_actions)

        import_json = QPushButton("Import JSON File")
        import_json.clicked.connect(self._import_json)
        file_actions_layout.addWidget(import_json)

        export_json = QPushButton("Export JSON File")
        export_json.clicked.connect(self._export_json)
        file_actions_layout.addWidget(export_json)

        export_qss = QPushButton("Export QSS File")
        export_qss.clicked.connect(self._export_qss)
        file_actions_layout.addWidget(export_qss)

        file_actions_layout.addStretch()
        layout.addWidget(file_actions)

        # Paste JSON section
        json_paste = self._make_editor_group("Paste JSON Theme")
        json_paste_layout = QVBoxLayout(json_paste)
        self._json_paste_input = QPlainTextEdit()
        self._json_paste_input.setPlaceholderText(
            "Paste your JSON theme here...\n\n"
            "Example format:\n"
            "{\n"
            '  "name": "My Theme",\n'
            '  "colors": { "background": "#1e1e1e", ... },\n'
            '  "metrics": { "border_radius": 4, ... },\n'
            '  "effects": { "shadow_enabled": true, ... }\n'
            "}"
        )
        self._json_paste_input.setLineWrapMode(QPlainTextEdit.NoWrap)
        json_paste_layout.addWidget(self._json_paste_input)

        json_btn_layout = QHBoxLayout()
        apply_json_btn = QPushButton("Apply JSON")
        apply_json_btn.clicked.connect(self._apply_pasted_json)
        json_btn_layout.addWidget(apply_json_btn)
        clear_json_btn = QPushButton("Clear")
        clear_json_btn.clicked.connect(lambda: self._json_paste_input.clear())
        json_btn_layout.addWidget(clear_json_btn)
        json_btn_layout.addStretch()
        json_paste_layout.addLayout(json_btn_layout)
        layout.addWidget(json_paste)

        # Paste QSS section
        qss_paste = self._make_editor_group("Paste QSS Stylesheet")
        qss_paste_layout = QVBoxLayout(qss_paste)
        self._qss_paste_input = QPlainTextEdit()
        self._qss_paste_input.setPlaceholderText(
            "Paste your QSS stylesheet here...\n\n"
            "The QSS will be parsed and converted to an editable theme.\n"
            "Colors and metrics will be extracted and can be modified."
        )
        self._qss_paste_input.setLineWrapMode(QPlainTextEdit.NoWrap)
        qss_paste_layout.addWidget(self._qss_paste_input)

        qss_btn_layout = QHBoxLayout()
        apply_qss_btn = QPushButton("Import QSS")
        apply_qss_btn.setToolTip("Parse QSS and import as editable theme")
        apply_qss_btn.clicked.connect(self._apply_pasted_qss)
        qss_btn_layout.addWidget(apply_qss_btn)
        save_qss_preset_btn = QPushButton("Import && Save as Preset")
        save_qss_preset_btn.setToolTip("Parse QSS and save as a named editable preset")
        save_qss_preset_btn.clicked.connect(self._save_qss_as_preset)
        qss_btn_layout.addWidget(save_qss_preset_btn)
        clear_qss_btn = QPushButton("Clear")
        clear_qss_btn.clicked.connect(lambda: self._qss_paste_input.clear())
        qss_btn_layout.addWidget(clear_qss_btn)
        qss_btn_layout.addStretch()
        qss_paste_layout.addLayout(qss_btn_layout)
        layout.addWidget(qss_paste)

        # Generated QSS preview
        preview = self._make_editor_group("Generated QSS Preview")
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

    def _make_editor_group(self, title: str) -> QGroupBox:
        group = QGroupBox(title)
        group.setProperty("editorSection", True)
        return group

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
            QMessageBox.information(
                self, "Cannot Delete", "Built-in presets cannot be deleted."
            )
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

    def _apply_pasted_json(self) -> None:
        """Apply JSON theme pasted into the text area."""
        json_text = self._json_paste_input.toPlainText().strip()
        if not json_text:
            QMessageBox.warning(self, "Empty Input", "Please paste a JSON theme first.")
            return
        if not self._engine.import_from_json(json_text):
            QMessageBox.warning(
                self,
                "Invalid JSON",
                "Could not parse the JSON theme.\n\n"
                "Make sure it contains valid JSON with 'colors', 'metrics', "
                "and 'effects' sections.",
            )
            return
        self._engine.save_current()
        self._refresh_preset_combo()
        QMessageBox.information(self, "Success", "JSON theme applied successfully.")

    def _apply_pasted_qss(self) -> None:
        """Parse QSS and apply as editable theme."""
        qss_text = self._qss_paste_input.toPlainText().strip()
        if not qss_text:
            QMessageBox.warning(
                self, "Empty Input", "Please paste a QSS stylesheet first."
            )
            return
        if not self._engine.import_from_qss(qss_text):
            QMessageBox.warning(
                self,
                "Parse Failed",
                "Could not parse the QSS stylesheet.",
            )
            return
        self._engine.save_current()
        self._refresh_preset_combo()
        QMessageBox.information(
            self,
            "QSS Imported",
            "QSS parsed and imported as editable theme.\n\n"
            "You can now modify colors and metrics with the editor.",
        )

    def _save_qss_as_preset(self) -> None:
        """Parse QSS and save as a named editable preset."""
        qss_text = self._qss_paste_input.toPlainText().strip()
        if not qss_text:
            QMessageBox.warning(
                self, "Empty Input", "Please paste a QSS stylesheet first."
            )
            return
        name, ok = QInputDialog.getText(self, "Save QSS as Preset", "Preset name:")
        if not ok or not name.strip():
            return
        # Parse QSS and save as regular editable preset
        if not self._engine.import_from_qss(qss_text, name.strip()):
            QMessageBox.warning(
                self, "Parse Failed", "Could not parse the QSS stylesheet."
            )
            return
        self._engine.save_custom_preset(name.strip())
        self._engine.save_current()
        self._refresh_preset_combo()
        QMessageBox.information(
            self,
            "Saved",
            f"QSS parsed and saved as editable preset '{name.strip()}'.",
        )

    def _reset_to_engine_stylesheet(self) -> None:
        """Reset to the theme engine's managed stylesheet and clear saved raw QSS."""
        self._engine.clear_raw_stylesheet()
        QMessageBox.information(self, "Reset", "Theme engine stylesheet restored.")

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
            self._preview.apply_effects(state.effects)

            if not self._live_preview.isChecked():
                self._preview.setStyleSheet(self._engine.generate_stylesheet())
        finally:
            self._updating_controls = False
