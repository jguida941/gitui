from __future__ import annotations

import pytest

from app.exec.fake_command_runner import FakeCommandRunner
from app.git.git_runner import GitRunner


def test_git_runner_builds_command_spec_with_defaults() -> None:
    runner = FakeCommandRunner()
    git = GitRunner(runner, git_executable="git-test")

    handle = git.run(["status"], cwd="/repo", env={"LANG": "C"})

    spec = runner.calls[-1]
    assert spec.args == ["git-test", "status"]
    assert spec.cwd == "/repo"
    assert spec.env is not None
    assert spec.env["GIT_PAGER"] == "cat"
    assert spec.env["GIT_TERMINAL_PROMPT"] == "0"
    assert spec.env["LANG"] == "C"
    assert handle == runner.handles[-1]


def test_git_runner_exposes_runner() -> None:
    runner = FakeCommandRunner()
    git = GitRunner(runner)

    assert git.runner is runner


def test_git_runner_requires_args() -> None:
    runner = FakeCommandRunner()
    git = GitRunner(runner)

    with pytest.raises(ValueError, match="at least one arg"):
        git.run([])
