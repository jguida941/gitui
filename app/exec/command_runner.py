from __future__ import annotations

from time import monotonic_ns

from app.exec.command_models import CommandResult, CommandSpec, RunHandle
from app.utils.qt_compat import QObject, QProcess, Signal


class CommandRunner(QObject):
    """Runs external commands via QProcess."""

    # Signals for lifecycle + streaming output (handle first, payload second).
    # We use object types to avoid PySide6 type registration friction.
    command_started = Signal(object)
    command_stdout = Signal(object, bytes)
    command_stderr = Signal(object, bytes)
    command_finished = Signal(object, object)

    def __init__(self) -> None:
        """Initialize runner state and buffers."""
        super().__init__()
        self._next_run_id = 1  # Unique ID generator for each run.

        # Keep QProcess alive and accessible by run_id.
        self._processes: dict[int, QProcess] = {}
        self._handles: dict[int, RunHandle] = {}

        # Accumulate output so we can build CommandResult later.
        self._stdout_buffers: dict[int, bytearray] = {}
        self._stderr_buffers: dict[int, bytearray] = {}

    def _new_handle(self, spec: CommandSpec) -> RunHandle:
        """Create and register a new handle for a command run."""
        run_id = self._next_run_id
        self._next_run_id += 1
        # Monotonic time only moves forward, which is safe for durations.
        started_at_ms = monotonic_ns() // 1_000_000
        handle = RunHandle(run_id=run_id, spec=spec, started_at_ms=started_at_ms)
        self._handles[run_id] = handle
        return handle

    def run(self, spec: CommandSpec) -> RunHandle:
        """Start a command and return its handle."""
        # Fail fast if no program was provided.
        if not spec.args:
            raise ValueError("CommandSpec.args cannot be empty")

        handle = self._new_handle(spec)

        # Create and store the QProcess so it stays alive.
        process = QProcess(self)
        self._processes[handle.run_id] = process

        # Create output buffers for this run.
        self._stdout_buffers[handle.run_id] = bytearray()
        self._stderr_buffers[handle.run_id] = bytearray()

        # Set working directory if provided (so git runs in the repo).
        if spec.cwd:
            process.setWorkingDirectory(spec.cwd)

        # Apply environment overrides if provided.
        if spec.env:
            env = process.processEnvironment()
            for key, value in spec.env.items():
                env.insert(key, value)
            process.setProcessEnvironment(env)

        # QProcess expects program and args split, while CommandSpec keeps argv together.
        process.setProgram(spec.args[0])
        process.setArguments(list(spec.args[1:]))

        # Wire output and completion signals for this run.
        # The lambda captures run_id so signals map back to the right handle.
        process.readyReadStandardOutput.connect(
            lambda rid=handle.run_id: self._on_stdout(rid)
        )
        process.readyReadStandardError.connect(
            lambda rid=handle.run_id: self._on_stderr(rid)
        )
        process.finished.connect(
            lambda exit_code, _status, rid=handle.run_id: self._on_finished(
                rid, exit_code
            )
        )

        # Kick off the process and announce it started.
        process.start()
        self.command_started.emit(handle)
        return handle

    def cancel(self, handle: RunHandle) -> bool:
        """Request a graceful stop for a running command."""
        process = self._processes.get(handle.run_id)
        if not process:
            return False

        # Terminate asks the process to exit cleanly.
        process.terminate()
        return True

    def kill(self, handle: RunHandle) -> bool:
        """Force-kill a running command."""
        process = self._processes.get(handle.run_id)
        if not process:
            return False

        # Kill is immediate and does not allow cleanup.
        process.kill()
        return True

    def _on_stdout(self, run_id: int) -> None:
        """Read and emit stdout for a running command."""
        # Look up the process/handle for this run.
        process = self._processes.get(run_id)
        handle = self._handles.get(run_id)
        if not process or not handle:
            return

        # Read bytes, buffer them, and emit streaming output.
        data = process.readAllStandardOutput().data()
        if data:
            self._stdout_buffers[run_id].extend(data)
            self.command_stdout.emit(handle, data)

    def _on_stderr(self, run_id: int) -> None:
        """Read and emit stderr for a running command."""
        # Look up the process/handle for this run.
        process = self._processes.get(run_id)
        handle = self._handles.get(run_id)
        if not process or not handle:
            return

        # Read bytes, buffer them, and emit streaming output.
        data = process.readAllStandardError().data()
        if data:
            self._stderr_buffers[run_id].extend(data)
            self.command_stderr.emit(handle, data)

    def _on_finished(self, run_id: int, exit_code: int) -> None:
        """Assemble the CommandResult and emit completion."""
        # Build the final result from buffers and emit completion.
        handle = self._handles.get(run_id)
        process = self._processes.get(run_id)
        if not handle:
            return

        # Compute duration from monotonic timestamp.
        duration_ms = monotonic_ns() // 1_000_000 - handle.started_at_ms
        stdout = bytes(self._stdout_buffers.pop(run_id, bytearray()))
        stderr = bytes(self._stderr_buffers.pop(run_id, bytearray()))
        result = CommandResult(
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
        )
        self.command_finished.emit(handle, result)

        # Cleanup process and handle to avoid leaks.
        if process:
            process.deleteLater()
        self._processes.pop(run_id, None)
        self._handles.pop(run_id, None)
