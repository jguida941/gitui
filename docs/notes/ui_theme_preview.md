# ui_theme_preview Notes

Purpose
- Provide a gallery of widgets to validate theme changes.

Key elements
- Buttons, inputs, lists, progress, and misc widgets.
- Uses `gitStatus` and `diffViewer` properties for targeted styles.
- Applies shadow effects from ThemeEngine for visual checks.

Flowchart: ThemePreview

[ThemeEngine update] -> [ThemePreview.apply_effects] -> [preview widgets restyled]
