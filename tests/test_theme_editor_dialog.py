from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QInputDialog

from app.ui.theme.theme_editor_dialog import ThemeEditorDialog

app = QApplication.instance() or QApplication([])


def test_theme_editor_dialog_constructs() -> None:
    dialog = ThemeEditorDialog()
    assert dialog.windowTitle() == "Theme Editor"
    dialog.close()


def test_theme_editor_dialog_live_preview_toggle() -> None:
    dialog = ThemeEditorDialog()
    dialog._toggle_live_preview(False)
    dialog._toggle_live_preview(True)
    dialog._on_color_changed("accent", "#112233")
    dialog._on_metric_changed("padding", 12)
    dialog._on_effect_changed("hover_scale", True)
    dialog._on_preset_selected("Dark")
    dialog._undo()
    dialog._redo()
    dialog.close()


def test_theme_editor_dialog_save_and_delete_preset(monkeypatch) -> None:
    dialog = ThemeEditorDialog()

    monkeypatch.setattr(
        QInputDialog,
        "getText",
        staticmethod(lambda *_args, **_kwargs: ("CustomTest", True)),
    )
    dialog._save_preset()
    dialog._preset_combo.setCurrentText("CustomTest")
    dialog._delete_preset()
    dialog.close()


def test_theme_editor_dialog_import_export(monkeypatch, tmp_path) -> None:
    dialog = ThemeEditorDialog()

    # Silence message boxes in tests.
    monkeypatch.setattr(QMessageBox, "information", staticmethod(lambda *_args, **_kwargs: None))
    monkeypatch.setattr(QMessageBox, "warning", staticmethod(lambda *_args, **_kwargs: None))

    export_json = tmp_path / "theme.json"
    export_qss = tmp_path / "theme.qss"

    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        staticmethod(lambda *_args, **_kwargs: (str(export_json), "")),
    )
    dialog._export_json()
    assert export_json.exists()

    monkeypatch.setattr(
        QFileDialog,
        "getSaveFileName",
        staticmethod(lambda *_args, **_kwargs: (str(export_qss), "")),
    )
    dialog._export_qss()
    assert export_qss.exists()

    monkeypatch.setattr(
        QFileDialog,
        "getOpenFileName",
        staticmethod(lambda *_args, **_kwargs: (str(export_json), "")),
    )
    dialog._import_json()
    dialog.close()
