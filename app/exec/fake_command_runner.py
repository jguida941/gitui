from __future__ import annotations

from app.exec.command_models import CommandSpec, RunHandle


class FakeCommandRunner:
    """Test double that records CommandSpec inputs and returns handles."""

    def __init__(self) -> None:
        # Store all CommandSpec inputs for assertions in tests.
        self.calls: list[CommandSpec] = []
        self.handles: list[RunHandle] = []
        self._next_run_id = 1

    def run(self, spec: CommandSpec) -> RunHandle:
        """Record the spec and return a stable RunHandle."""
        self.calls.append(spec)

        # We do not execute a real process; this is a deterministic handle.
        handle = RunHandle(run_id=self._next_run_id, spec=spec, started_at_ms=0)
        self._next_run_id += 1
        self.handles.append(handle)
        return handle
