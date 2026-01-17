# ADR-0008: Testing Strategy and Quality Gates

Status: accepted

Context
- This codebase will grow into a large CLI-driven Git UI, so regressions must be
  caught early.
- We need confidence in parsing logic, command orchestration, and controller
  behavior before UI wiring grows.
- Mutation testing should drive targeted tests rather than blanket assertions.

Decision
- Use a layered test strategy:
  - Unit tests for parsers and pure logic.
  - Integration-style tests for controller/service flows with fakes.
  - Scripted checks for CLI-oriented flows (manual_smoke, check_coverage).
  - Property-based tests (Hypothesis) for parser robustness.
  - Mutation testing (mutmut) to validate that tests detect meaningful changes.
  - Manual smoke tests for real git/QProcess execution.
- Skip QProcess integration tests on macOS where PySide6/pytest-qt is unstable; rely on Linux/Windows runs plus manual smoke.
- Enforce per-file line coverage >= 90% on backend and script code.
- Keep a manual test checklist with expected results for CLI/GUI steps.
- Prefer targeted tests for risky or complex logic instead of broad, shallow tests.
- Target mutation kill rate >= 90% (goal 100%) by adding focused tests for survivors.

Consequences
- CI will gate on per-file coverage thresholds.
- Mutation testing becomes a routine regression signal; survivors must be triaged
  with targeted tests or deliberate exclusions.
- Tests must evolve with architecture changes to keep coverage and mutation goals.
