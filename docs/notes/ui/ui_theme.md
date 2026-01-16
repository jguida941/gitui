# ui_theme Notes

Purpose
- Location: app/ui/theme/__init__.py
- Compatibility wrapper for legacy theme API calls.
- Delegates to ThemeEngine for real work.

Key elements
- `apply_theme()` calls ThemeEngine.apply_theme().
- Exposes defaults/presets aligned with ThemeEngine.

Flowchart: ui_theme

[legacy call] -> [ThemeEngine]
