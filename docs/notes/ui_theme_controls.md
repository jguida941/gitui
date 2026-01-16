# ui_theme_controls Notes

Purpose
- Reusable controls for the theme editor (color picker button).

Key elements
- Button renders the color swatch + hex/rgba label.
- Optional alpha channel support for shadow colors.

Flowchart: ColorPickerButton

[click] -> [QColorDialog] -> [emit color_changed]
