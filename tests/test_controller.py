import pytest

from app.core.controller import RepoController
from app.core.errors import CommandFailed, NotARepo, ParseError
from app.core.models import (
    Branch,
    BranchInfo,
    Commit,
    Remote,
    RemoteBranch,
    RepoStatus,
    StashEntry,
    Tag,
)
from app.exec.command_models import CommandResult, CommandSpec, RunHandle


class DummySignal:
    def connect(self, _callback) -> None:
        # No-op: tests drive controller callbacks directly.
        return None


class DummyRunner:
    def __init__(self) -> None:
        self.command_finished = DummySignal()


class DummyService:
    def __init__(self) -> None:
        self._runner = DummyRunner()
        self._next_run_id = 1
        # Track the latest handle so tests can simulate completion.
        self.last_handle: RunHandle | None = None
        # Allow tests to inject parse failures.
        self.parse_status_error: Exception | None = None
        self.status_calls = 0
        self.validate_calls = 0
        self.log_calls = 0
        self.branches_calls = 0
        self.remote_branches_calls = 0
        self.stage_calls = 0
        self.unstage_calls = 0
        self.discard_calls = 0
        self.commit_calls = 0
        self.fetch_calls = 0
        self.pull_calls = 0
        self.push_calls = 0
        self.stash_list_calls = 0
        self.stash_save_calls = 0
        self.stash_apply_calls = 0
        self.stash_pop_calls = 0
        self.stash_drop_calls = 0
        self.tags_calls = 0
        self.create_tag_calls = 0
        self.delete_tag_calls = 0
        self.push_tag_calls = 0
        self.push_tags_calls = 0
        self.remotes_calls = 0
        self.add_remote_calls = 0
        self.remove_remote_calls = 0
        self.set_remote_url_calls = 0
        self.set_upstream_calls = 0
        self.conflicts_calls = 0
        self.diff_calls = 0
        self.switch_branch_calls = 0
        self.create_branch_calls = 0
        self.delete_branch_calls = 0
        self.delete_remote_branch_calls = 0

    @property
    def runner(self):
        return self._runner

    def _handle(self, args: list[str], repo_path: str | None = None) -> RunHandle:
        spec = CommandSpec(args=args, cwd=repo_path, env={})
        handle = RunHandle(run_id=self._next_run_id, spec=spec, started_at_ms=0)
        self._next_run_id += 1
        # Keep the last handle so tests can simulate completion.
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

    def remote_branches_raw(self, repo_path: str) -> RunHandle:
        self.remote_branches_calls += 1
        return self._handle(["git", "branch", "-r"], repo_path)

    def diff_file_raw(
        self, repo_path: str, path: str, staged: bool = False
    ) -> RunHandle:
        self.diff_calls += 1
        args = ["git", "diff"]
        if staged:
            args.append("--cached")
        args.extend(["--", path])
        return self._handle(args, repo_path)

    def stash_list_raw(self, repo_path: str) -> RunHandle:
        self.stash_list_calls += 1
        return self._handle(["git", "stash", "list"], repo_path)

    def tags_raw(self, repo_path: str) -> RunHandle:
        self.tags_calls += 1
        return self._handle(["git", "tag", "--list"], repo_path)

    def remotes_raw(self, repo_path: str) -> RunHandle:
        self.remotes_calls += 1
        return self._handle(["git", "remote", "-v"], repo_path)

    def conflicts_raw(self, repo_path: str) -> RunHandle:
        self.conflicts_calls += 1
        return self._handle(
            ["git", "diff", "--name-only", "--diff-filter=U"], repo_path
        )

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

    def switch_branch(self, repo_path: str, name: str) -> RunHandle:
        self.switch_branch_calls += 1
        return self._handle(["git", "switch", name], repo_path)

    def create_branch(
        self, repo_path: str, name: str, from_ref: str = "HEAD"
    ) -> RunHandle:
        self.create_branch_calls += 1
        return self._handle(["git", "switch", "-c", name, from_ref], repo_path)

    def delete_branch(
        self, repo_path: str, name: str, force: bool = False
    ) -> RunHandle:
        self.delete_branch_calls += 1
        args = ["git", "branch", "-D" if force else "-d", name]
        return self._handle(args, repo_path)

    def delete_remote_branch(self, repo_path: str, remote: str, name: str) -> RunHandle:
        self.delete_remote_branch_calls += 1
        return self._handle(["git", "push", remote, "--delete", name], repo_path)

    def stash_save(
        self,
        repo_path: str,
        message: str | None = None,
        include_untracked: bool = False,
    ) -> RunHandle:
        self.stash_save_calls += 1
        args = ["git", "stash", "push"]
        if include_untracked:
            args.append("--include-untracked")
        if message:
            args.extend(["-m", message])
        return self._handle(args, repo_path)

    def stash_apply(self, repo_path: str, ref: str | None = None) -> RunHandle:
        self.stash_apply_calls += 1
        args = ["git", "stash", "apply"]
        if ref:
            args.append(ref)
        return self._handle(args, repo_path)

    def stash_pop(self, repo_path: str, ref: str | None = None) -> RunHandle:
        self.stash_pop_calls += 1
        args = ["git", "stash", "pop"]
        if ref:
            args.append(ref)
        return self._handle(args, repo_path)

    def stash_drop(self, repo_path: str, ref: str | None = None) -> RunHandle:
        self.stash_drop_calls += 1
        args = ["git", "stash", "drop"]
        if ref:
            args.append(ref)
        return self._handle(args, repo_path)

    def create_tag(
        self, repo_path: str, name: str, ref: str | None = None
    ) -> RunHandle:
        self.create_tag_calls += 1
        args = ["git", "tag", name]
        if ref:
            args.append(ref)
        return self._handle(args, repo_path)

    def delete_tag(self, repo_path: str, name: str) -> RunHandle:
        self.delete_tag_calls += 1
        return self._handle(["git", "tag", "-d", name], repo_path)

    def push_tag(self, repo_path: str, name: str, remote: str = "origin") -> RunHandle:
        self.push_tag_calls += 1
        return self._handle(["git", "push", remote, name], repo_path)

    def push_tags(self, repo_path: str, remote: str = "origin") -> RunHandle:
        self.push_tags_calls += 1
        return self._handle(["git", "push", "--tags", remote], repo_path)

    def add_remote(self, repo_path: str, name: str, url: str) -> RunHandle:
        self.add_remote_calls += 1
        return self._handle(["git", "remote", "add", name, url], repo_path)

    def remove_remote(self, repo_path: str, name: str) -> RunHandle:
        self.remove_remote_calls += 1
        return self._handle(["git", "remote", "remove", name], repo_path)

    def set_remote_url(self, repo_path: str, name: str, url: str) -> RunHandle:
        self.set_remote_url_calls += 1
        return self._handle(["git", "remote", "set-url", name, url], repo_path)

    def set_upstream(
        self, repo_path: str, upstream: str, branch: str | None = None
    ) -> RunHandle:
        self.set_upstream_calls += 1
        args = ["git", "branch", "--set-upstream-to", upstream]
        if branch:
            args.append(branch)
        return self._handle(args, repo_path)

    def parse_status(self, _payload: bytes) -> RepoStatus:
        if self.parse_status_error:
            raise self.parse_status_error
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

    def parse_remote_branches(self, _payload: bytes) -> list[RemoteBranch]:
        return [RemoteBranch(remote="origin", name="main", full_name="origin/main")]

    def parse_stashes(self, _payload: bytes) -> list[StashEntry]:
        return [
            StashEntry(
                oid="abc123",
                selector="stash@{0}",
                summary="WIP on main",
                date="2024-01-01T00:00:00Z",
            )
        ]

    def parse_tags(self, _payload: bytes) -> list[Tag]:
        return [Tag(name="v1.0.0")]

    def parse_remotes(self, _payload: bytes) -> list[Remote]:
        return [Remote(name="origin", fetch_url="https://x", push_url="https://x")]

    def parse_conflicts(self, _payload: bytes) -> list[str]:
        return ["conflict.txt"]

    def parse_diff(self, payload: bytes) -> str:
        return payload.decode("utf-8", errors="replace")

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


def _complete_last(
    controller: RepoController,
    service: DummyService,
    *,
    stdout: bytes = b"",
    stderr: bytes = b"",
    exit_code: int = 0,
) -> None:
    handle = service.last_handle
    assert handle is not None
    result = CommandResult(
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        duration_ms=1,
    )
    controller._on_command_finished(handle, result)


def test_refresh_status_without_repo_sets_error() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.refresh_status()

    assert isinstance(controller.state.last_error, NotARepo)


def test_open_repo_success_triggers_status_refresh() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.open_repo("/repo")
    assert controller.state.busy is True

    # Simulate validation success so the controller accepts the repo.
    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=0, stdout=b"true\n", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert controller.state.repo_path == "/repo"
    assert service.status_calls == 1


def test_status_result_updates_state() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.refresh_status()

    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=0, stdout=b"", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert controller.state.status is not None
    assert controller.state.last_error is None


def test_log_result_updates_state() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.refresh_log(limit=1)

    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=0, stdout=b"", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert controller.state.log is not None
    assert controller.state.last_error is None


def test_branches_result_updates_state() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.refresh_branches()

    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=0, stdout=b"", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    remote_handle = service.last_handle
    assert remote_handle is not None
    controller._on_command_finished(remote_handle, result)

    assert controller.state.branches is not None
    assert controller.state.remote_branches is not None
    assert controller.state.last_error is None


def test_stage_triggers_status_refresh() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.stage(["file.txt"])
    assert service.stage_calls == 1

    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=0, stdout=b"", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert service.status_calls == 1


def test_fetch_triggers_branches_refresh() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.fetch()
    assert service.fetch_calls == 1

    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=0, stdout=b"", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert service.branches_calls == 1


def test_pull_triggers_status_refresh() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.pull_ff_only()
    assert service.pull_calls == 1

    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=0, stdout=b"", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert service.status_calls == 1


def test_push_triggers_branches_refresh() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.push()
    assert service.push_calls == 1

    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=0, stdout=b"", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert service.branches_calls == 1


def test_open_repo_false_sets_error() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.open_repo("/repo")
    handle = service.last_handle
    assert handle is not None

    result = CommandResult(exit_code=0, stdout=b"false\n", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert isinstance(controller.state.last_error, NotARepo)


def test_failed_command_sets_command_failed() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.refresh_status()

    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=1, stdout=b"nope", stderr=b"bad", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert isinstance(controller.state.last_error, CommandFailed)


def test_parse_error_sets_parse_error() -> None:
    service = DummyService()
    controller = RepoController(service)
    service.parse_status_error = ValueError("bad parse")

    controller.state.set_repo_path("/repo")
    controller.refresh_status()

    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=0, stdout=b"", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert isinstance(controller.state.last_error, ParseError)


def test_stashes_result_updates_state() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.refresh_stashes()

    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=0, stdout=b"", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert controller.state.stashes is not None


def test_tags_result_updates_state() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.refresh_tags()

    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=0, stdout=b"", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert controller.state.tags is not None


def test_remotes_result_updates_state() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.refresh_remotes()

    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=0, stdout=b"", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert controller.state.remotes is not None


def test_conflicts_result_updates_state() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.refresh_conflicts()

    handle = service.last_handle
    assert handle is not None
    result = CommandResult(exit_code=0, stdout=b"", stderr=b"", duration_ms=1)
    controller._on_command_finished(handle, result)

    assert controller.state.conflicts == ["conflict.txt"]


def test_request_diff_updates_state() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.request_diff("file.txt", staged=True)
    assert service.diff_calls == 1

    _complete_last(controller, service, stdout=b"diff contents")
    assert controller.state.diff_text == "diff contents"


@pytest.mark.parametrize(
    ("method_name", "args", "kwargs"),
    [
        ("refresh_status", [], {}),
        ("refresh_log", [], {}),
        ("refresh_branches", [], {}),
        ("refresh_conflicts", [], {}),
        ("refresh_stashes", [], {}),
        ("refresh_tags", [], {}),
        ("refresh_remotes", [], {}),
        ("request_diff", ["file.txt"], {"staged": True}),
        ("stage", [["file.txt"]], {}),
        ("unstage", [["file.txt"]], {}),
        ("discard", [["file.txt"]], {}),
        ("commit", ["message"], {}),
        ("fetch", [], {}),
        ("pull_ff_only", [], {}),
        ("push", [], {"set_upstream": True, "remote": "origin", "branch": "main"}),
        ("switch_branch", ["main"], {}),
        ("create_branch", ["feature"], {"from_ref": "main"}),
        ("delete_branch", ["old"], {"force": True}),
        ("stash_save", [], {"message": "wip", "include_untracked": True}),
        ("stash_apply", [], {"ref": "stash@{0}"}),
        ("stash_pop", [], {"ref": "stash@{0}"}),
        ("stash_drop", [], {"ref": "stash@{0}"}),
        ("create_tag", ["v1.0.0"], {"ref": "HEAD"}),
        ("delete_tag", ["v1.0.0"], {}),
        ("push_tag", ["v1.0.0"], {"remote": "origin"}),
        ("push_tags", [], {"remote": "origin"}),
        ("add_remote", ["origin", "https://example.com"], {}),
        ("remove_remote", ["origin"], {}),
        ("set_remote_url", ["origin", "https://example.com"], {}),
        ("set_upstream", ["origin/main"], {"branch": "main"}),
    ],
)
def test_methods_require_repo_path(
    method_name: str, args: list[object], kwargs: dict[str, object]
) -> None:
    service = DummyService()
    controller = RepoController(service)

    method = getattr(controller, method_name)
    method(*args, **kwargs)

    assert isinstance(controller.state.last_error, NotARepo)


@pytest.mark.parametrize(
    ("method_name", "args", "kwargs", "counter"),
    [
        ("stage", [["file.txt"]], {}, "stage_calls"),
        ("unstage", [["file.txt"]], {}, "unstage_calls"),
        ("discard", [["file.txt"]], {}, "discard_calls"),
        ("commit", ["message"], {}, "commit_calls"),
        ("fetch", [], {}, "fetch_calls"),
        ("pull_ff_only", [], {}, "pull_calls"),
        ("push", [], {}, "push_calls"),
        ("switch_branch", ["main"], {}, "switch_branch_calls"),
        ("create_branch", ["feature"], {"from_ref": "main"}, "create_branch_calls"),
        ("delete_branch", ["old"], {"force": True}, "delete_branch_calls"),
        ("stash_save", [], {"message": "wip"}, "stash_save_calls"),
        ("stash_apply", [], {"ref": "stash@{0}"}, "stash_apply_calls"),
        ("stash_pop", [], {"ref": "stash@{0}"}, "stash_pop_calls"),
        ("stash_drop", [], {"ref": "stash@{0}"}, "stash_drop_calls"),
        ("create_tag", ["v1.0.0"], {}, "create_tag_calls"),
        ("delete_tag", ["v1.0.0"], {}, "delete_tag_calls"),
        ("push_tag", ["v1.0.0"], {}, "push_tag_calls"),
        ("push_tags", [], {}, "push_tags_calls"),
        ("add_remote", ["origin", "https://example.com"], {}, "add_remote_calls"),
        ("remove_remote", ["origin"], {}, "remove_remote_calls"),
        (
            "set_remote_url",
            ["origin", "https://example.com"],
            {},
            "set_remote_url_calls",
        ),
        ("set_upstream", ["origin/main"], {"branch": "main"}, "set_upstream_calls"),
    ],
)
def test_methods_call_service(
    method_name: str, args: list[object], kwargs: dict[str, object], counter: str
) -> None:
    service = DummyService()
    controller = RepoController(service)
    controller.state.set_repo_path("/repo")

    method = getattr(controller, method_name)
    method(*args, **kwargs)

    assert getattr(service, counter) == 1


def test_commit_triggers_status_and_log_refresh() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.commit("message")

    _complete_last(controller, service)

    assert service.status_calls == 1
    assert service.log_calls == 0

    _complete_last(controller, service)
    assert service.log_calls == 1


@pytest.mark.parametrize(
    ("method_name", "args"), [("unstage", [["file.txt"]]), ("discard", [["file.txt"]])]
)
def test_unstage_and_discard_trigger_status_refresh(
    method_name: str, args: list[object]
) -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    getattr(controller, method_name)(*args)

    _complete_last(controller, service)

    assert service.status_calls == 1


@pytest.mark.parametrize(
    ("method_name", "args", "kwargs"),
    [
        ("switch_branch", ["main"], {}),
        ("create_branch", ["feature"], {"from_ref": "main"}),
    ],
)
def test_branch_switches_refresh_status_and_branches(
    method_name: str, args: list[object], kwargs: dict[str, object]
) -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    getattr(controller, method_name)(*args, **kwargs)

    _complete_last(controller, service)

    assert service.status_calls == 1
    assert service.branches_calls == 0

    _complete_last(controller, service)
    assert service.branches_calls == 1


def test_delete_branch_refreshes_branches() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.delete_branch("old", force=True)

    _complete_last(controller, service)

    assert service.branches_calls == 1


def test_delete_remote_branch_refreshes_branches() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.delete_remote_branch("origin", "feature")

    _complete_last(controller, service)

    assert service.delete_remote_branch_calls == 1
    assert service.branches_calls == 1


@pytest.mark.parametrize(
    ("method_name", "kwargs", "expect_status", "expect_stashes"),
    [
        ("stash_save", {"message": "wip"}, True, True),
        ("stash_apply", {"ref": "stash@{0}"}, True, False),
        ("stash_pop", {"ref": "stash@{0}"}, True, True),
        ("stash_drop", {"ref": "stash@{0}"}, False, True),
    ],
)
def test_stash_actions_refresh(
    method_name: str,
    kwargs: dict[str, object],
    expect_status: bool,
    expect_stashes: bool,
) -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    getattr(controller, method_name)(**kwargs)

    _complete_last(controller, service)

    assert (service.status_calls == 1) is expect_status

    if expect_status and expect_stashes:
        _complete_last(controller, service)
        assert service.stash_list_calls == 1
    else:
        assert (service.stash_list_calls == 1) is expect_stashes


@pytest.mark.parametrize(
    ("method_name", "args"),
    [("create_tag", ["v1.0.0"]), ("delete_tag", ["v1.0.0"])],
)
def test_tag_actions_refresh_tags(method_name: str, args: list[object]) -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    getattr(controller, method_name)(*args)

    _complete_last(controller, service)

    assert service.tags_calls == 1


@pytest.mark.parametrize(
    ("method_name", "args"),
    [
        ("add_remote", ["origin", "https://example.com"]),
        ("remove_remote", ["origin"]),
        ("set_remote_url", ["origin", "https://example.com"]),
    ],
)
def test_remote_actions_refresh_remotes(method_name: str, args: list[object]) -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    getattr(controller, method_name)(*args)

    _complete_last(controller, service)

    assert service.remotes_calls == 1


def test_set_upstream_refreshes_branches() -> None:
    service = DummyService()
    controller = RepoController(service)

    controller.state.set_repo_path("/repo")
    controller.set_upstream("origin/main", branch="main")

    _complete_last(controller, service)

    assert service.branches_calls == 1
