"""Shared fixtures for tests."""

from __future__ import annotations

import pytest

from app.core.models import Branch, BranchInfo, Commit, RepoStatus
from app.exec.command_models import CommandSpec, RunHandle
from app.exec.fake_command_runner import FakeCommandRunner


class DummySignal:
    def __init__(self) -> None:
        self._handlers: list = []

    def connect(self, callback) -> None:
        self._handlers.append(callback)

    def emit(self, *args, **kwargs) -> None:
        for handler in self._handlers:
            handler(*args, **kwargs)


class DummyRunner:
    def __init__(self) -> None:
        self.command_finished = DummySignal()


class DummyService:
    def __init__(self) -> None:
        self._runner = DummyRunner()
        self._next_run_id = 1
        # Track the latest handle so tests can simulate completion.
        self.last_handle: RunHandle | None = None
        self.status_calls = 0
        self.validate_calls = 0
        self.log_calls = 0
        self.branches_calls = 0
        self.stage_calls = 0
        self.unstage_calls = 0
        self.discard_calls = 0
        self.commit_calls = 0
        self.fetch_calls = 0
        self.pull_calls = 0
        self.push_calls = 0
        self.diff_calls = 0

    @property
    def runner(self):
        return self._runner

    def _handle(self, args: list[str], repo_path: str | None = None) -> RunHandle:
        spec = CommandSpec(args=args, cwd=repo_path, env={})
        handle = RunHandle(run_id=self._next_run_id, spec=spec, started_at_ms=0)
        self._next_run_id += 1
        self.last_handle = handle
        return handle

    def is_inside_work_tree_raw(self, repo_path: str) -> RunHandle:
        self.validate_calls += 1
        return self._handle(["git", "rev-parse"], repo_path)

    def status_raw(self, repo_path: str) -> RunHandle:
        self.status_calls += 1
        return self._handle(["git", "status"], repo_path)

    def log_raw(self, repo_path: str, limit: int = 300) -> RunHandle:
        self.log_calls += 1
        return self._handle(["git", "log", "-n", str(limit)], repo_path)

    def branches_raw(self, repo_path: str) -> RunHandle:
        self.branches_calls += 1
        return self._handle(["git", "branch"], repo_path)

    def diff_file_raw(
        self, repo_path: str, path: str, staged: bool = False
    ) -> RunHandle:
        self.diff_calls += 1
        return self._handle(["git", "diff", path], repo_path)

    def stage(self, repo_path: str, paths: list[str]) -> RunHandle:
        self.stage_calls += 1
        return self._handle(["git", "add", "--", *paths], repo_path)

    def unstage(self, repo_path: str, paths: list[str]) -> RunHandle:
        self.unstage_calls += 1
        return self._handle(["git", "restore", "--staged", "--", *paths], repo_path)

    def discard(self, repo_path: str, paths: list[str]) -> RunHandle:
        self.discard_calls += 1
        return self._handle(["git", "restore", "--", *paths], repo_path)

    def commit(self, repo_path: str, message: str, amend: bool = False) -> RunHandle:
        self.commit_calls += 1
        args = ["git", "commit", "-m", message]
        if amend:
            args.append("--amend")
        return self._handle(args, repo_path)

    def fetch(self, repo_path: str) -> RunHandle:
        self.fetch_calls += 1
        return self._handle(["git", "fetch"], repo_path)

    def pull_ff_only(self, repo_path: str) -> RunHandle:
        self.pull_calls += 1
        return self._handle(["git", "pull", "--ff-only"], repo_path)

    def push(
        self,
        repo_path: str,
        set_upstream: bool = False,
        remote: str | None = None,
        branch: str | None = None,
    ) -> RunHandle:
        self.push_calls += 1
        return self._handle(["git", "push"], repo_path)

    def parse_status(self, _payload: bytes) -> RepoStatus:
        return RepoStatus(
            branch=BranchInfo(
                name="main", head_oid=None, upstream=None, ahead=0, behind=0
            ),
            staged=[],
            unstaged=[],
            untracked=[],
            conflicted=[],
        )

    def parse_log(self, _payload: bytes) -> list[Commit]:
        return [
            Commit(
                oid="abc123",
                parents=[],
                author_name="Dev",
                author_email="dev@example.com",
                author_date="2024-01-01T00:00:00Z",
                subject="Test commit",
            )
        ]

    def parse_branches(self, _payload: bytes) -> list[Branch]:
        return [
            Branch(
                name="main",
                is_current=True,
                upstream="origin/main",
                ahead=0,
                behind=0,
                gone=False,
            )
        ]

    def parse_diff(self, payload: bytes) -> str:
        return payload.decode("utf-8", errors="replace")


@pytest.fixture
def fake_runner() -> FakeCommandRunner:
    return FakeCommandRunner()


@pytest.fixture
def dummy_service() -> DummyService:
    return DummyService()
