# Repo Structure (Phase 0)

Current tree (placeholder scaffold):

```
.
├── AGENTS.md
├── CHANGELOG.md
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
│   │   ├── fake_command_runner.py
│   │   ├── command_models.py
│   │   ├── command_queue.py
│   │   └── command_runner.py
│   ├── git
│   │   ├── git_runner.py
│   │   ├── git_service.py
│   │   ├── parse_branches.py
│   │   ├── parse_conflicts.py
│   │   ├── parse_diff.py
│   │   ├── parse_log.py
│   │   ├── parse_remotes.py
│   │   ├── parse_status.py
│   │   ├── parse_stash.py
│   │   └── parse_tags.py
│   ├── ui
│   │   ├── branches_panel.py
│   │   ├── commit_panel.py
│   │   ├── console_widget.py
│   │   ├── diff_viewer.py
│   │   ├── git_toolbar.py
│   │   ├── log_panel.py
│   │   ├── main_window.py
│   │   ├── remotes_panel.py
│   │   ├── repo_picker.py
│   │   ├── status_panel.py
│   │   ├── stash_panel.py
│   │   ├── tags_panel.py
│   │   ├── theme
│   │   │   ├── __init__.py
│   │   │   ├── theme_controls.py
│   │   │   ├── theme_editor_dialog.py
│   │   │   ├── theme_engine.py
│   │   │   └── theme_preview.py
│   │   └── dialogs
│   │       ├── confirm_dialog.py
│   │       ├── error_dialog.py
│   │       └── settings_dialog.py
│   └── utils
│       ├── logging.py
│       ├── paths.py
│       ├── qt_compat.py
│       └── settings.py
├── docs
│   ├── README.md
│   ├── adr
│   │   ├── ADR-0001-command-runner.md
│   │   ├── ADR-0002-git-cli-backend.md
│   │   ├── ADR-0003-machine-parsing.md
│   │   ├── ADR-0004-ui-intent-boundary.md
│   │   ├── ADR-0005-scope-and-concurrency.md
│   │   ├── ADR-0006-error-handling.md
│   │   ├── ADR-0007-controller-routing.md
│   │   ├── ADR-0008-testing-strategy.md
│   │   ├── ADR-0009-visualization-library.md
│   │   └── README.md
│   ├── agents.md
│   ├── notes
│   │   ├── README.md
│   │   ├── core
│   │   │   ├── adr_scope.md
│   │   │   ├── errors.md
│   │   │   ├── main_entry.md
│   │   │   ├── models.md
│   │   │   ├── package_app_init.md
│   │   │   ├── repo_controller.md
│   │   │   └── repo_state.md
│   │   ├── exec
│   │   │   ├── command_models.md
│   │   │   ├── command_queue.md
│   │   │   ├── command_runner.md
│   │   │   ├── fake_command_runner.md
│   │   │   └── package_exec_init.md
│   │   ├── git
│   │   │   ├── command_guide.md
│   │   │   ├── core_command_audit.md
│   │   │   ├── git_runner.md
│   │   │   ├── git_service.md
│   │   │   ├── insights.md
│   │   │   ├── parse_branches.md
│   │   │   ├── parse_conflicts.md
│   │   │   ├── parse_diff.md
│   │   │   ├── parse_log.md
│   │   │   ├── parse_remotes.md
│   │   │   ├── parse_status.md
│   │   │   ├── parse_stash.md
│   │   │   └── parse_tags.md
│   │   ├── quality
│   │   │   ├── coverage_check.md
│   │   │   ├── manual_smoke.md
│   │   │   ├── run_gitui.md
│   │   │   ├── run_mutation.md
│   │   │   ├── testing.md
│   │   │   └── testing_checklist.md
│   │   ├── ui
│   │   │   ├── package_ui_init.md
│   │   │   ├── ui_branches_panel.md
│   │   │   ├── ui_commit_panel.md
│   │   │   ├── ui_console_widget.md
│   │   │   ├── ui_confirm_dialog.md
│   │   │   ├── ui_diff_viewer.md
│   │   │   ├── ui_error_dialog.md
│   │   │   ├── ui_git_toolbar.md
│   │   │   ├── ui_log_panel.md
│   │   │   ├── ui_main_window.md
│   │   │   ├── ui_remotes_panel.md
│   │   │   ├── ui_repo_picker.md
│   │   │   ├── ui_status_panel.md
│   │   │   ├── ui_stash_panel.md
│   │   │   ├── ui_tags_panel.md
│   │   │   ├── ui_theme.md
│   │   │   ├── ui_theme_controls.md
│   │   │   ├── ui_theme_editor_dialog.md
│   │   │   ├── ui_theme_engine.md
│   │   │   └── ui_theme_preview.md
│   │   ├── utils
│   │   │   ├── qt_compat.md
│   │   │   ├── utils_logging.md
│   │   │   ├── utils_paths.md
│   │   │   └── utils_settings.md
│   │   └── tests
│   │       ├── README.md
│   │       ├── command_queue.md
│   │       ├── command_runner.md
│   │       ├── conftest.md
│   │       ├── controller.md
│   │       ├── dialogs.md
│   │       ├── errors.md
│   │       ├── git_runner.md
│   │       ├── git_service.md
│   │       ├── main.md
│   │       ├── parse_branches.md
│   │       ├── parse_conflicts.md
│   │       ├── parse_diff.md
│   │       ├── parse_log.md
│   │       ├── parse_remotes.md
│   │       ├── parse_status.md
│   │       ├── parse_stash.md
│   │       ├── parse_tags.md
│   │       ├── parsers_property.md
│   │       ├── qt_compat.md
│   │       ├── repo_state.md
│   │       ├── scripts.md
│   │       ├── theme_controls.md
│   │       ├── theme_editor_dialog.md
│   │       ├── theme_engine.md
│   │       ├── theme_preview.md
│   │       ├── ui_panels.md
│   │       └── ui_placeholders.md
│   ├── roadmap.md
│   └── structure.md
├── pyproject.toml
├── README.md
├── scripts
│   ├── check_coverage.py
│   ├── manual_smoke.py
│   ├── run-mutation.sh
│   └── run_gitui.py
└── tests
    ├── conftest.py
    ├── test_command_runner.py
    ├── test_command_queue.py
    ├── test_controller.py
    ├── test_dialogs.py
    ├── test_errors.py
    ├── test_git_runner.py
    ├── test_git_service.py
    ├── test_main.py
    ├── test_main_window.py
    ├── test_parse_branches.py
    ├── test_parse_conflicts.py
    ├── test_parse_diff.py
    ├── test_parse_log.py
    ├── test_parse_remotes.py
    ├── test_parse_status.py
    ├── test_parse_stash.py
    ├── test_parse_tags.py
    ├── test_parsers_property.py
    ├── test_qt_compat.py
    ├── test_repo_state.py
    ├── test_scripts.py
    ├── test_theme_controls.py
    ├── test_theme_editor_dialog.py
    ├── test_theme_engine.py
    ├── test_theme_preview.py
    ├── test_ui_panels.py
    └── test_ui_placeholders.py
```

Notes
- UI components are wired for core workflows; advanced features remain in progress.
- Placeholder sections remain for future expansion.
