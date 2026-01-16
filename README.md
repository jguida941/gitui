# GitUI

A PySide6 desktop UI on top of the git CLI. The backend stays CLI-native for full parity; the UI is a thin, themeable dashboard.

![GitUI Screenshot](docs/images/gitui-screenshot.png)

## Quick start

- Install deps: `pip install .[dev]`
- Run tests: `pytest -q`
- Launch UI: `python -m app.main --repo /path/to/repo`
  - Alternate launcher: `python scripts/run_gitui.py --repo /path/to/repo`

## Features

Implemented
- CLI-native backend (CommandRunner + GitRunner) with machine-parseable output.
- Status + diff + stage/unstage/discard workflow.
- Commit panel (message + amend toggle).
- Branch/log/stash/tag/remote panels (listing + selection).
- Git action toolbar (fetch/pull/push).
- Theme engine + editor (presets, undo/redo, JSON/QSS import/export, live preview).

Planned
- Branch management actions (create/rename/delete/checkout, upstream tooling).
- Rich history views (commit details, per-commit diffs).
- Stash/tag/remote actions beyond listing.
- Insights/graphs (activity, churn, contributors).
- Power tools (blame, grep, file history, stat views).

Status: active development.
