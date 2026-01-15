# Repo Structure (Phase 0)

Current tree (placeholder scaffold):

```
.
├── .github
│   └── workflows
│       └── ci.yml
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── core
│   │   ├── controller.py
│   │   ├── errors.py
│   │   ├── models.py
│   │   └── repo_state.py
│   ├── exec
│   │   ├── __init__.py
│   │   ├── command_models.py
│   │   ├── command_queue.py
│   │   └── command_runner.py
│   ├── git
│   │   ├── git_runner.py
│   │   ├── git_service.py
│   │   ├── parse_diff.py
│   │   ├── parse_log.py
│   │   └── parse_status.py
│   ├── ui
│   │   ├── branches_panel.py
│   │   ├── commit_panel.py
│   │   ├── console_widget.py
│   │   ├── diff_viewer.py
│   │   ├── log_panel.py
│   │   ├── main_window.py
│   │   ├── repo_picker.py
│   │   ├── status_panel.py
│   │   └── dialogs
│   │       ├── confirm_dialog.py
│   │       └── error_dialog.py
│   └── utils
│       ├── logging.py
│       ├── paths.py
│       └── settings.py
├── docs
│   ├── README.md
│   ├── adr
│   │   ├── ADR-0001-command-runner.md
│   │   ├── ADR-0002-git-cli-backend.md
│   │   ├── ADR-0003-machine-parsing.md
│   │   └── ADR-0004-ui-intent-boundary.md
│   ├── agents.md
│   ├── roadmap.md
│   └── structure.md
├── pyproject.toml
├── README.md
└── tests
    ├── test_controller.py
    ├── test_git_service.py
    ├── test_parse_log.py
    └── test_parse_status.py
```

Notes
- Many files are placeholders for tracking and modularization.
- UI logic still starts only after Phase 0 backend is in place.
