# manual_smoke Notes

Purpose
- Provide a CLI-driven smoke test for CommandRunner + GitRunner.
- Adds repo root to `sys.path` so `app` imports resolve.

Usage
- `python scripts/manual_smoke.py --repo /path/to/repo`

Notes
- Qt may emit a locale warning if your shell locale is not UTF-8.
- Script exits with an error if PySide6 is not installed.

Flowchart: manual_smoke.py

[start Qt event loop]
        |
        v
[wire runner stdout/stderr/finished]
        |
        v
[run git status porcelain v2]
        |
        v
[print output + exit code]
