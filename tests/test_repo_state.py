from __future__ import annotations

from app.core.models import Branch, BranchInfo, Commit, RepoStatus
from app.core.repo_state import RepoState


def test_initial_state_is_empty() -> None:
    state = RepoState()
    assert state.repo_path is None
    assert state.status is None
    assert state.log is None
    assert state.branches is None
    assert state.diff_text is None
    assert state.last_error is None
    assert state.busy is False


def test_set_repo_path_emits_signal() -> None:
    state = RepoState()
    emissions: list[str] = []
    state.state_changed.connect(lambda: emissions.append("changed"))

    state.set_repo_path("/path/to/repo")

    assert state.repo_path == "/path/to/repo"
    assert len(emissions) == 1


def test_set_status_emits_signal() -> None:
    state = RepoState()
    emissions: list[str] = []
    state.state_changed.connect(lambda: emissions.append("changed"))

    status = RepoStatus(
        branch=BranchInfo(name="main", head_oid=None, upstream=None, ahead=0, behind=0),
        staged=[],
        unstaged=[],
        untracked=[],
        conflicted=[],
    )
    state.set_status(status)

    assert state.status == status
    assert len(emissions) == 1


def test_set_log_emits_signal() -> None:
    state = RepoState()
    emissions: list[str] = []
    state.state_changed.connect(lambda: emissions.append("changed"))

    commits = [
        Commit(
            oid="abc123",
            parents=[],
            author_name="Dev",
            author_email="dev@example.com",
            author_date="2024-01-01",
            subject="Test",
        )
    ]
    state.set_log(commits)

    assert state.log == commits
    assert len(emissions) == 1


def test_set_branches_emits_signal() -> None:
    state = RepoState()
    emissions: list[str] = []
    state.state_changed.connect(lambda: emissions.append("changed"))

    branches = [
        Branch(
            name="main",
            is_current=True,
            upstream="origin/main",
            ahead=0,
            behind=0,
            gone=False,
        )
    ]
    state.set_branches(branches)

    assert state.branches == branches
    assert len(emissions) == 1


def test_set_diff_text_emits_signal() -> None:
    state = RepoState()
    emissions: list[str] = []
    state.state_changed.connect(lambda: emissions.append("changed"))

    state.set_diff_text("diff content")

    assert state.diff_text == "diff content"
    assert len(emissions) == 1


def test_set_error_emits_signal() -> None:
    state = RepoState()
    emissions: list[str] = []
    state.state_changed.connect(lambda: emissions.append("changed"))

    error = ValueError("test error")
    state.set_error(error)

    assert state.last_error == error
    assert len(emissions) == 1


def test_set_busy_emits_signal() -> None:
    state = RepoState()
    emissions: list[str] = []
    state.state_changed.connect(lambda: emissions.append("changed"))

    state.set_busy(True)

    assert state.busy is True
    assert len(emissions) == 1


def test_clearing_state_values() -> None:
    state = RepoState()

    state.set_repo_path("/repo")
    state.set_diff_text("diff")
    state.set_error(ValueError("error"))
    state.set_busy(True)

    state.set_repo_path(None)
    state.set_diff_text(None)
    state.set_error(None)
    state.set_busy(False)

    assert state.repo_path is None
    assert state.diff_text is None
    assert state.last_error is None
    assert state.busy is False


def test_multiple_signal_handlers() -> None:
    state = RepoState()
    emissions_a: list[str] = []
    emissions_b: list[str] = []

    state.state_changed.connect(lambda: emissions_a.append("a"))
    state.state_changed.connect(lambda: emissions_b.append("b"))

    state.set_repo_path("/repo")

    assert len(emissions_a) == 1
    assert len(emissions_b) == 1
