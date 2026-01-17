# Testing Notes

Purpose
- Ensure tests can import the `app` package without installing the project.

Config
- pytest uses `pythonpath = ["."]` from pyproject.toml.
- Qt types come from `app/utils/qt_compat.py` so imports work even without PySide6.
- pytest-asyncio uses `asyncio_default_fixture_loop_scope = "function"` to silence warnings.
- Property-based tests skip if Hypothesis is not installed.
- QProcess integration tests are marked `qprocess` and skipped by mutmut.
- QProcess tests are skipped on macOS due to PySide6/pytest-qt instability.

Manual smoke
- `scripts/manual_smoke.py` runs a real git status via QProcess.
- Full checklist lives in `docs/notes/quality/testing_checklist.md`.

Mutation testing
- `scripts/run-mutation.sh` runs mutmut using the parser list in pyproject.toml.
- Mutmut uses `paths_to_mutate` from `pyproject.toml` and pytest args from
  `pytest_add_cli_args`.
- `also_copy = ["app"]` ensures full imports are available in the mutants tree.
- Target mutation kill rate >= 90% (goal 100%) and add focused tests for survivors.

Coverage gate
- `scripts/check_coverage.py` fails the run if any file is below 90%.
- Use `pytest --cov-report=json:coverage.json` before running the gate.

Flowchart: pytest discovery

[pytest starts]
        |
        v
[add repo root to sys.path]
        |
        v
[import app.* modules]
