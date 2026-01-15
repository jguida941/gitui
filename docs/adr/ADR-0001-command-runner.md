# ADR-0001: Single CommandRunner using QProcess

Status: accepted

Context
- We need a single execution path for git and other commands.
- PySide6 provides QProcess with async signals for stdout/stderr.

Decision
- All process execution goes through CommandRunner built on QProcess.
- UI and services must not spawn processes directly.

Consequences
- CommandRunner becomes the primary boundary for execution, logging, and cancellation.
- Tests can use a FakeCommandRunner to isolate parsing and intent logic.
