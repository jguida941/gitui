# Notes Index

UI notes (docs/notes/ui/)
- ui/package_ui_init.md: ui package marker.
- ui/ui_branches_panel.md: Branch list panel.
- ui/ui_commit_panel.md: Commit message panel.
- ui/ui_console_widget.md: Console widget for command output.
- ui/ui_diff_viewer.md: Diff viewer panel.
- ui/ui_log_panel.md: Commit history panel.
- ui/ui_main_window.md: Main window layout + wiring.
- ui/ui_repo_picker.md: Repo picker component.
- ui/ui_status_panel.md: Status lists + context menu actions.
- ui/ui_stash_panel.md: Stash list + actions.
- ui/ui_tags_panel.md: Tag list + actions.
- ui/ui_remotes_panel.md: Remote list + actions.
- ui/ui_confirm_dialog.md: Confirmation dialog.
- ui/ui_error_dialog.md: Error dialog.
- ui/ui_git_toolbar.md: Quick git action toolbar.
- ui/ui_theme_engine.md: Theme engine and presets.
- ui/ui_theme_editor_dialog.md: Theme editor dialog.
- ui/ui_theme_controls.md: Theme editor controls.
- ui/ui_theme_preview.md: Theme preview widget gallery.
- ui/ui_theme.md: Theme API compatibility layer.

Execution notes (docs/notes/exec/)
- exec/package_exec_init.md: exec package marker.
- exec/command_models.md: CommandSpec/RunHandle/CommandResult data models.
- exec/command_runner.md: CommandRunner flow + signal lifecycle.
- exec/command_queue.md: CommandQueue rules and flow.
- exec/fake_command_runner.md: Fake runner purpose and flow.

Git notes (docs/notes/git/)
- git/command_guide.md: Verified git command reference.
- git/core_command_audit.md: Manual audit order for core commands.
- git/git_runner.md: GitRunner defaults and delegation.
- git/git_service.md: Intent layer overview.
- git/insights.md: Git+ analytics plan and data flow.
- git/parse_branches.md: Branch list parsing plan.
- git/parse_conflicts.md: Conflict list parsing plan.
- git/parse_diff.md: Diff parsing scope (raw for now).
- git/parse_log.md: Log parsing plan with separators.
- git/parse_remotes.md: Remote list parsing plan.
- git/parse_remote_branches.md: Remote branch parsing plan.
- git/parse_status.md: Status parsing plan for porcelain v2.
- git/parse_stash.md: Stash list parsing plan with separators.
- git/parse_tags.md: Tag list parsing plan.

Core notes (docs/notes/core/)
- core/package_app_init.md: app package marker.
- core/main_entry.md: app/main.py launch flow.
- core/models.md: Shared dataclasses for parsing and UI.
- core/repo_controller.md: Controller intent flow.
- core/repo_state.md: Repo state fields and signals.
- core/errors.md: Typed error meanings and flow.
- core/adr_scope.md: Summary of added ADRs.

Utils notes (docs/notes/utils/)
- utils/qt_compat.md: Qt import fallback for tests without PySide6.
- utils/utils_logging.md: Logging setup helper.
- utils/utils_paths.md: Path normalization helper.
- utils/utils_settings.md: In-memory settings store.

Quality notes (docs/notes/quality/)
- quality/run_gitui.md: Launcher script for GitUI.
- quality/run_mutation.md: Mutmut wrapper script.
- quality/manual_smoke.md: CLI smoke test script for CommandRunner.
- quality/coverage_check.md: Per-file coverage gate script.
- quality/testing_checklist.md: Manual test checklist for CLI + GUI.
- quality/testing.md: Test configuration and import path.

Test notes (docs/notes/tests/)
- tests/README.md: Index for test notes.
- tests/command_queue.md: What CommandQueue tests assert.
- tests/command_runner.md: What CommandRunner tests assert.
- tests/conftest.md: Shared fixtures used by tests.
- tests/parse_branches.md: What parse_branches tests assert.
- tests/parse_conflicts.md: What parse_conflicts tests assert.
- tests/parse_diff.md: What parse_diff tests assert.
- tests/parse_log.md: What parse_log tests assert.
- tests/parse_status.md: What parse_status tests assert.
- tests/parse_stash.md: What parse_stash tests assert.
- tests/parse_tags.md: What parse_tags tests assert.
- tests/parse_remotes.md: What parse_remotes tests assert.
- tests/parse_remote_branches.md: What parse_remote_branches tests assert.
- tests/parsers_property.md: Property tests for parsers.
- tests/git_service.md: What GitService tests assert.
- tests/git_runner.md: What GitRunner tests assert.
- tests/controller.md: What RepoController tests assert.
- tests/command_queue.md: What CommandQueue tests assert.
- tests/errors.md: What error class tests assert.
- tests/main.md: What app.main tests assert.
- tests/qt_compat.md: Qt compatibility tests.
- tests/repo_state.md: RepoState setter tests.
- tests/scripts.md: Script tests (coverage + smoke).
- tests/ui_placeholders.md: UI placeholder tests.
- tests/ui_panels.md: UI panel behavior tests.
- tests/theme_engine.md: ThemeEngine state tests.
- tests/theme_controls.md: Theme control widgets tests.
- tests/theme_preview.md: Theme preview widget tests.
- tests/theme_editor_dialog.md: Theme editor dialog tests.
- tests/dialogs.md: Confirm/Error dialog tests.
