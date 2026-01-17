from __future__ import annotations

import sys

import pytest

import app.exec.command_runner as command_runner
from app.exec.command_models import CommandSpec, RunHandle
from app.exec.command_runner import CommandRunner
from app.utils import qt_compat

if qt_compat.PYSIDE6_AVAILABLE:
    from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer

IS_DARWIN = sys.platform == "darwin"


def _ensure_qt_app() -> None:
    app = QCoreApplication.instance()
    if app is None:
        QCoreApplication([])


def _wait_for_finished(runner: CommandRunner, timeout_ms: int = 2000) -> dict[str, object]:
    loop = QEventLoop()
    done: dict[str, object] = {}

    def on_finished(handle: object, result: object) -> None:
        done["handle"] = handle
        done["result"] = result
        loop.quit()

    runner.command_finished.connect(on_finished)

    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(loop.quit)
    timer.start(timeout_ms)

    loop.exec()
    runner.command_finished.disconnect(on_finished)
    return done


@pytest.mark.qprocess
@pytest.mark.skipif(
    not qt_compat.PYSIDE6_AVAILABLE or IS_DARWIN,
    reason="PySide6 required for QProcess; macOS QProcess tests are unstable",
)
def test_command_runner_emits_output_and_result(tmp_path) -> None:
    _ensure_qt_app()
    runner = CommandRunner()
    started: list[object] = []
    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []

    runner.command_started.connect(lambda handle: started.append(handle))
    runner.command_stdout.connect(lambda _handle, data: stdout_chunks.append(data))
    runner.command_stderr.connect(lambda _handle, data: stderr_chunks.append(data))

    spec = CommandSpec(
        args=[
            sys.executable,
            "-c",
            "import sys; sys.stdout.write('out'); sys.stderr.write('err')",
        ],
        cwd=str(tmp_path),
        env={"GITUI_TEST": "1"},
    )

    handle = runner.run(spec)
    done = _wait_for_finished(runner)

    assert done, "command_finished did not fire"
    result = done["result"]

    assert started and getattr(started[0], "run_id", None) == handle.run_id
    assert getattr(result, "exit_code", None) == 0
    assert b"out" in getattr(result, "stdout", b"")
    assert b"err" in getattr(result, "stderr", b"")
    assert any(b"out" in chunk for chunk in stdout_chunks)
    assert any(b"err" in chunk for chunk in stderr_chunks)
    assert getattr(result, "duration_ms", 0) >= 0


@pytest.mark.qprocess
@pytest.mark.skipif(
    not qt_compat.PYSIDE6_AVAILABLE or IS_DARWIN,
    reason="PySide6 required for QProcess; macOS QProcess tests are unstable",
)
def test_command_runner_cancel_and_kill(tmp_path) -> None:
    _ensure_qt_app()
    runner = CommandRunner()

    spec = CommandSpec(
        args=[sys.executable, "-c", "import time; time.sleep(5)"],
        cwd=str(tmp_path),
    )
    handle = runner.run(spec)

    assert runner.cancel(handle) is True
    assert runner.kill(handle) is True

    done = _wait_for_finished(runner)
    assert done, "command did not finish after cancel/kill"

    fake = RunHandle(run_id=999, spec=spec, started_at_ms=0)
    assert runner.cancel(fake) is False
    assert runner.kill(fake) is False


def test_command_runner_rejects_empty_args() -> None:
    runner = CommandRunner()

    with pytest.raises(ValueError, match="cannot be empty"):
        runner.run(CommandSpec(args=[]))


def test_command_runner_with_fake_process(monkeypatch: pytest.MonkeyPatch) -> None:
    if qt_compat.PYSIDE6_AVAILABLE:
        pytest.skip("Fallback process test only runs without PySide6")

    class FakeSignal:
        def __init__(self) -> None:
            self._handlers: list = []

        def connect(self, handler) -> None:
            self._handlers.append(handler)

    class FakeByteArray:
        def __init__(self, data: bytes) -> None:
            self._data = data

        def data(self) -> bytes:
            return self._data

    class FakeEnv:
        def __init__(self) -> None:
            self.values: dict[str, str] = {}

        def insert(self, key: str, value: str) -> None:
            self.values[key] = value

    class FakeQProcess:
        def __init__(self, _parent=None) -> None:
            self.readyReadStandardOutput = FakeSignal()
            self.readyReadStandardError = FakeSignal()
            self.finished = FakeSignal()
            self._cwd: str | None = None
            self._program = ""
            self._args: list[str] = []
            self._env = FakeEnv()
            self._stdout = b"stdout"
            self._stderr = b"stderr"
            self.terminated = False
            self.killed = False
            self.deleted = False

        def setWorkingDirectory(self, cwd: str) -> None:
            self._cwd = cwd

        def processEnvironment(self) -> FakeEnv:
            return self._env

        def setProcessEnvironment(self, env: FakeEnv) -> None:
            self._env = env

        def setProgram(self, program: str) -> None:
            self._program = program

        def setArguments(self, args: list[str]) -> None:
            self._args = args

        def start(self) -> None:
            return None

        def terminate(self) -> None:
            self.terminated = True

        def kill(self) -> None:
            self.killed = True

        def readAllStandardOutput(self) -> FakeByteArray:
            return FakeByteArray(self._stdout)

        def readAllStandardError(self) -> FakeByteArray:
            return FakeByteArray(self._stderr)

        def deleteLater(self) -> None:
            self.deleted = True

    monkeypatch.setattr(command_runner, "QProcess", FakeQProcess)

    runner = CommandRunner()
    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []
    finished: list[object] = []

    runner.command_stdout.connect(lambda _handle, data: stdout_chunks.append(data))
    runner.command_stderr.connect(lambda _handle, data: stderr_chunks.append(data))
    runner.command_finished.connect(lambda _handle, result: finished.append(result))

    spec = CommandSpec(args=["git", "status"], cwd="/repo", env={"TEST_ENV": "1"})
    handle = runner.run(spec)

    process = runner._processes[handle.run_id]
    assert runner.cancel(handle) is True
    assert runner.kill(handle) is True
    assert process.terminated is True
    assert process.killed is True
    runner._on_stdout(handle.run_id)
    runner._on_stderr(handle.run_id)
    runner._on_finished(handle.run_id, 0)

    assert process._cwd == "/repo"
    assert process._program == "git"
    assert process._args == ["status"]
    assert process._env.values["TEST_ENV"] == "1"
    assert stdout_chunks and stderr_chunks
    assert finished

    assert runner.cancel(handle) is False
