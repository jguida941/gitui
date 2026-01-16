# ui_console_widget Notes

Purpose
- Provide a scrollback console for command stdout/stderr and events.
- Keep output readable with stable prefixes.

Key elements
- `consoleWidget` property lets the theme target monospace styling.
- Appends lines and auto-scrolls to the end.

Flowchart: ConsoleWidget

[command output] -> [append prefixed line] -> [scroll to end]
