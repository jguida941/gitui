from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from app.ui.theme_engine import ThemeEngine


def test_theme_engine_apply_and_override() -> None:
    engine = ThemeEngine()

    applied = engine.apply_theme(
        "Dark",
        colors={"accent": "#123456"},
        metrics={"padding": 10},
        effects={"hover_scale": True},
        save=False,
    )

    assert applied is True
    assert engine.get_color("accent") == "#123456"
    assert engine.get_metric("padding") == 10
    assert engine.get_effect("hover_scale") is True


def test_theme_engine_undo_redo_round_trip() -> None:
    engine = ThemeEngine()
    original = engine.get_color("accent")

    engine.set_color("accent", "#ABCDEF")
    assert engine.can_undo() is True

    assert engine.undo() is True
    assert engine.get_color("accent") == original

    assert engine.redo() is True
    assert engine.get_color("accent") == "#ABCDEF"


def test_theme_engine_export_import(tmp_path) -> None:
    engine = ThemeEngine()
    path = tmp_path / "theme.json"

    engine.set_color("accent", "#00AAFF")
    engine.export_to_file(path)

    engine.set_color("accent", "#FF00AA")
    assert engine.import_from_file(path) is True
    assert engine.get_color("accent") == "#00AAFF"


def test_theme_engine_custom_preset_round_trip() -> None:
    engine = ThemeEngine()
    engine.apply_theme("Dark", colors={"accent": "#0A0B0C"}, save=False)
    engine.save_custom_preset("CustomTest")

    presets = engine.get_preset_names()
    assert "CustomTest" in presets
