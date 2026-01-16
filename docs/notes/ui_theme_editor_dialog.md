# ui_theme_editor_dialog Notes

Purpose
- Full theme editor UI with presets, controls, and live preview.
- Emits no git commands; it only drives ThemeEngine state.

Key elements
- Toolbar for presets, undo/redo, and live-preview toggle.
- Tabs for Colors, Fonts, Metrics, Effects, Import/Export.
- Live preview panel with a widget gallery.

Flowchart: ThemeEditorDialog

[preset select] -> [ThemeEngine.apply_theme]
        |
        v
[control change] -> [ThemeEngine.set_*] -> [theme_changed]
        |
        v
[preview + export updated]
