# ui_theme_editor_dialog Notes

Purpose
- Location: app/ui/theme/theme_editor_dialog.py
- Full theme editor UI with presets, controls, and live preview.
- Emits no git commands; it only drives ThemeEngine state.

Key elements
- Toolbar for presets, undo/redo, and live-preview toggle.
- Tabs for Colors, Fonts, Metrics, Effects, Import/Export.
- Live preview panel with a widget gallery.
- Editor groups mark `editorSection` for lighter styling.

Flowchart: ThemeEditorDialog

[preset select] -> [ThemeEngine.apply_theme]
        |
        v
[control change] -> [ThemeEngine.set_*] -> [theme_changed]
        |
        v
[sync controls] -> [ThemePreview.apply_effects] -> [preview + export updated]
