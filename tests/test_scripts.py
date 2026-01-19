from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import scripts.check_coverage as check_coverage
import scripts.manual_smoke as manual_smoke


def test_check_coverage_passes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {"files": {"app/x.py": {"summary": {"percent_covered": 95.0}}}}
    coverage_path = tmp_path / "coverage.json"
    coverage_path.write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["check_coverage.py", str(coverage_path)])
    assert check_coverage.main() == 0


def test_check_coverage_fails_below_threshold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = {"files": {"app/x.py": {"summary": {"percent_covered": 50.0}}}}
    coverage_path = tmp_path / "coverage.json"
    coverage_path.write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["check_coverage.py", str(coverage_path)])
    assert check_coverage.main() == 1


def test_check_coverage_missing_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    coverage_path = tmp_path / "missing.json"
    monkeypatch.setattr(sys, "argv", ["check_coverage.py", str(coverage_path)])
    assert check_coverage.main() == 2


def test_manual_smoke_main_uses_fake_runner(
    monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    class DummySignal:
        def __init__(self) -> None:
            self._handlers: list = []

        def connect(self, handler) -> None:
            self._handlers.append(handler)

        def emit(self, *args, **kwargs) -> None:
            for handler in list(self._handlers):
                handler(*args, **kwargs)

    class DummyRunner:
        def __init__(self) -> None:
            self.command_stdout = DummySignal()
            self.command_stderr = DummySignal()
            self.command_finished = DummySignal()

    class DummyResult:
        exit_code = 0
        duration_ms = 1

    class DummyGitRunner:
        def __init__(self, runner: DummyRunner) -> None:
            self._runner = runner

        def run(self, _args, cwd=None) -> None:
            self._runner.command_stdout.emit(None, b"status")
            self._runner.command_stderr.emit(None, b"")
            self._runner.command_finished.emit(None, DummyResult())

    class DummyApp:
        def __init__(self, _argv) -> None:
            self.quit_called = False

        def exec(self) -> int:
            return 0

        def quit(self) -> None:
            self.quit_called = True

    monkeypatch.setattr(manual_smoke, "CommandRunner", DummyRunner)
    monkeypatch.setattr(manual_smoke, "GitRunner", DummyGitRunner)
    monkeypatch.setattr(manual_smoke, "QCoreApplication", DummyApp)
    monkeypatch.setattr(sys, "argv", ["manual_smoke.py", "--repo", "/tmp"])

    assert manual_smoke.main() == 0
    output = capsys.readouterr().out
    assert "exit=0" in output
