# ui_theme_engine Notes

Purpose
- Central theme state (colors/metrics/effects) with presets + undo/redo.
- Generates the Qt stylesheet and applies it to the app.
- Persists current theme and custom presets in QSettings.

Key elements
- `apply_theme()` merges preset + overrides in one undoable step.
- `set_apply_enabled()` toggles live application vs preview-only.
- Emits `theme_changed` for UI refresh.
- `hover_brighten` influences hover colors in generated styles.
- Transition settings are injected into button/tool styles when enabled.
- `editorSection` group boxes get lighter styling in the stylesheet.

Flowchart: ThemeEngine

[apply_theme/set_color] -> [update state] -> [emit theme_changed]
                              |
                              v
                     [apply stylesheet if enabled]
