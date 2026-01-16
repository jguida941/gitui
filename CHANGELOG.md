# Changelog

All notable changes to this project will be documented here.

## [Unreleased]

### Added
- CommandRunner (QProcess) with lifecycle signals and streaming output.
- GitRunner wrapper with safe git defaults.
- GitService intents (status/diff/stage/commit/fetch/pull/push/log/branches).
- GitService parse helpers (status/log/diff).
- FakeCommandRunner for tests.
- Core models for status and log parsing (RepoStatus, FileChange, Commit).
- Branch model for branch list parsing.
- Notes and flowcharts for backend components.
- Porcelain v2 status parser with tests.
- Structured log parser with tests.
- Raw diff parser (bytes -> text).
- RepoState and RepoController skeletons.
- RepoState fields for log/branches/diff text.
- RepoController actions for status/log/branches/diff and mutations.
- Typed errors for command and parsing failures.
- Expanded GitService intent tests.
- ADRs for scope/concurrency, error handling, and controller routing.
- Branch list parser with tests.
- RepoController tests for basic flows.
- CommandQueue for coalesced background refreshes with tests.
- Qt compatibility shim for importing backend modules without PySide6 installed.
- RepoController tests for log/branches refresh and stage-triggered status refresh.
- Porcelain status test covering paths with spaces and newlines.
- Stash, tag, and remote models + parsers.
- Stash/tag/remote intents in GitService with tests.
- RepoState fields for stashes/tags/remotes.
- RepoController refresh + actions for stashes/tags/remotes.
- Parsing tests for stashes, tags, and remotes.
- RepoController tests for fetch/pull/push and error handling.
- Conflict detection parser + intents with tests.
- RepoState conflict list and RepoController refresh for conflicts.
- UI placeholder panels for stashes, tags, and remotes.
- CLI manual smoke test script for CommandRunner + GitRunner.
- Manual testing checklist for CLI + GUI steps.
- Conflict parsing smoke tests are now runnable via mutmut.
- CommandRunner integration tests covering stdout/stderr and cancel/kill.
- GitRunner tests verifying env defaults and arg handling.
- UI placeholder tests to keep per-file coverage gates green.
- Script tests for coverage gate + manual smoke harness.
- Qt compatibility tests for fallback and PySide6 branches.
- Additional parse_branches and parse_remotes test cases.
- Notes for new test files and flowcharts.
- ADR-0009 for visualization library (PyQtGraph + QGraphicsView).
- Core command audit note + checklist entry before advanced features.
- Tests for edge cases: malformed branch headers, non-numeric ahead/behind values.
- Tests for empty line handling in remote parsing.
- Tests for stash records with missing fields (padding logic).
- Tests for GitService push() ValueError when set_upstream missing args.
- Tests for GitService runner property accessor.
- Initial GUI wiring: MainWindow, RepoPicker, StatusPanel, DiffViewer, ConsoleWidget.
- `--no-gui` option for the main entrypoint to keep tests headless.
- ThemeEngine with presets, undo/redo, and QSS generation.
- Theme editor dialog with live preview and import/export tooling.
- Theme preview widget gallery and reusable theme controls.
- Git toolbar with common action shortcuts.
- Commit/branches/log/stash/tags/remotes panels wired to controller intents.
- Confirm and error dialogs for destructive actions and failures.
- Launcher script (`scripts/run_gitui.py`) for clean app startup.
- New UI/theme/dialog tests to keep per-file coverage green.
- Push failure prompt for missing upstreams with automatic retry.

### Changed
- Docs structure and agent contract for learning workflow.
- Reformatted docs/roadmap.md into standard Markdown and locked key decisions.
- Core Qt imports now flow through the compatibility helper.
- Pytest config silences pytest-asyncio loop scope warnings.
- Notes directory now separates test notes under `docs/notes/tests/`.
- Test note filenames dropped the `tests_` prefix under `docs/notes/tests/`.
- Notes are now grouped under `docs/notes/{ui,exec,git,core,utils,quality}/`.
- Mutmut config now uses list syntax and copies full `app/` into `mutants/`.
- Mutation runner script now relies on pyproject config.
- Manual smoke script ensures repo root is on `sys.path`.
- ADR-0008 now codifies per-file coverage and mutation kill targets.
- Agents contract now includes coverage + mutation goals.
- Testing checklist includes the coverage JSON step.
- Manual smoke script now exits cleanly when PySide6 is missing.
- Roadmap includes Phase 2.5 graphs and Phase 3.5 power CLI tools.
- Roadmap now gates advanced phases on completing the core command audit.
- Mutmut now skips `qprocess` tests to avoid Qt/QProcess crashes.
- Core command audit completed: all CLI commands produce expected machine-readable output.
- Test coverage improved to 91% (above 90% threshold) for non-UI modules.
- UI notes updated to document wiring and diff selection behavior.
- MainWindow now uses tabbed panels and a toolbar layout.
- Theme initialization moved to ThemeEngine.
- Discard actions now prompt for confirmation and error dialogs show command details.
- Theme modules now live under `app/ui/theme/` with updated imports.

### Fixed
- Ruff import cleanup in command models.
- Removed stray non-ASCII character in core models.
- Pytest import path for `app` package.
- CommandQueue tests now simulate mark_idle lifecycle.
- Test collection without PySide6 installed.
- Property-based tests now skip cleanly when Hypothesis is missing.
- Ignore Hypothesis cache directory in git.
- Ignore mutmut output directories in git.
- Commit template cursor movement now uses QTextCursor.End.
- Branch upstream signal now accepts an optional branch name.
- Theme editor sections render without heavy group box panels.
- Theme preview now applies shadow effects from the theme engine.
