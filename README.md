# GitUI

A PySide6 desktop UI on top of the git CLI. The backend stays CLI-native for full parity; the UI is a thin, themeable dashboard.

![GitUI Screenshot](docs/images/gitui-screenshot.png)

## Quick start

- Install deps: `pip install .[dev]`
- Run tests: `pytest -q`
- Launch UI: `python -m app.main --repo /path/to/repo`
  - Alternate launcher: `python scripts/run_gitui.py --repo /path/to/repo`

## Features (in progress)

- Status + diff + staging workflow
- Commit panel with templates and amend toggle
- Branch, log, stash, tag, and remote panels
- Git action toolbar (fetch/pull/push)
- Theme editor with presets and export (JSON/QSS)

Status: active development.
