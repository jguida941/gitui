# ui_error_dialog Notes

Purpose
- Show command failures and parsing errors with details.

Key elements
- Summary line plus a detailed stdout/stderr block.
- Handles `CommandFailed` specially to include command + exit code.

Flowchart: ErrorDialog

[error raised] -> [format details] -> [show dialog]
