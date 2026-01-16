# utils_logging Notes

Purpose
- Provide a safe, idempotent logging setup for CLI/debug runs.

Flowchart: setup_logging

[call setup_logging]
        |
        v
[if handlers exist -> no-op]
        |
        v
[else configure basic logging]
