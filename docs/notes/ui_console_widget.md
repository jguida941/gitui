# ui_console_widget Notes

Purpose
- Display command output and lifecycle events for transparency.
- Keep a simple scrollback log the user can read.

Flowchart: append_stdout

[stdout bytes]
        |
        v
[decode + prefix lines]
        |
        v
[append to QPlainTextEdit]

Flowchart: append_event

[command start/finish]
        |
        v
[format event line]
        |
        v
[append to QPlainTextEdit]
