from app.exec.fake_command_runner import FakeCommandRunner
from app.git.git_runner import GitRunner
from app.git.git_service import BRANCH_FORMAT, LOG_FORMAT, STASH_FORMAT, GitService


def test_git_runner_builds_command_spec_with_defaults() -> None:
    fake = FakeCommandRunner()
    runner = GitRunner(fake)

    runner.run(["status"], cwd="/repo")

    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "status"]
    assert spec.cwd == "/repo"
    assert spec.env["GIT_PAGER"] == "cat"
    assert spec.env["GIT_TERMINAL_PROMPT"] == "0"
    assert spec.env["LANG"] == "C.UTF-8"


def test_git_service_status_raw_uses_porcelain_v2() -> None:
    fake = FakeCommandRunner()
    runner = GitRunner(fake)
    service = GitService(runner)

    service.status_raw("/repo")

    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "status", "--porcelain=v2", "-b", "-z"]
    assert spec.cwd == "/repo"


def test_git_service_diff_file_raw_staged_and_unstaged() -> None:
    fake = FakeCommandRunner()
    service = GitService(GitRunner(fake))

    service.diff_file_raw("/repo", "file.txt", staged=False)
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "diff", "--no-color", "--", "file.txt"]

    service.diff_file_raw("/repo", "file.txt", staged=True)
    spec = fake.calls[-1]
    assert list(spec.args) == [
        "git",
        "diff",
        "--no-color",
        "--cached",
        "--",
        "file.txt",
    ]


def test_git_service_stage_unstage_discard() -> None:
    fake = FakeCommandRunner()
    service = GitService(GitRunner(fake))

    service.stage("/repo", ["a.txt", "b.txt"])
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "add", "--", "a.txt", "b.txt"]

    service.unstage("/repo", ["a.txt"])
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "restore", "--staged", "--", "a.txt"]

    service.discard("/repo", ["b.txt"])
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "restore", "--", "b.txt"]


def test_git_service_commit_amend() -> None:
    fake = FakeCommandRunner()
    service = GitService(GitRunner(fake))

    service.commit("/repo", "msg", amend=False)
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "commit", "-m", "msg"]

    service.commit("/repo", "msg", amend=True)
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "commit", "--amend", "-m", "msg"]


def test_git_service_fetch_pull_push() -> None:
    fake = FakeCommandRunner()
    service = GitService(GitRunner(fake))

    service.fetch("/repo")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "fetch"]

    service.pull_ff_only("/repo")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "pull", "--ff-only"]

    service.push("/repo")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "push"]

    service.push("/repo", set_upstream=True, remote="origin", branch="main")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "push", "-u", "origin", "main"]


def test_git_service_log_and_branches_raw() -> None:
    fake = FakeCommandRunner()
    service = GitService(GitRunner(fake))

    service.log_raw("/repo", limit=10)
    spec = fake.calls[-1]
    assert list(spec.args) == [
        "git",
        "log",
        "--date=iso-strict",
        f"--pretty=format:{LOG_FORMAT}",
        "-n",
        "10",
    ]

    service.branches_raw("/repo")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "branch", f"--format={BRANCH_FORMAT}"]

    service.remote_branches_raw("/repo")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "branch", "-r", "--format=%(refname:short)"]

    service.conflicts_raw("/repo")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "diff", "--name-only", "--diff-filter=U"]


def test_git_service_stash_raw_and_actions() -> None:
    fake = FakeCommandRunner()
    service = GitService(GitRunner(fake))

    service.stash_list_raw("/repo")
    spec = fake.calls[-1]
    assert list(spec.args) == [
        "git",
        "stash",
        "list",
        "--date=iso-strict",
        f"--pretty=format:{STASH_FORMAT}",
    ]

    service.stash_save("/repo", message="msg", include_untracked=True)
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "stash", "push", "-u", "-m", "msg"]

    service.stash_apply("/repo", ref="stash@{0}")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "stash", "apply", "stash@{0}"]

    service.stash_pop("/repo")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "stash", "pop"]

    service.stash_drop("/repo", ref="stash@{1}")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "stash", "drop", "stash@{1}"]


def test_git_service_tags_raw_and_actions() -> None:
    fake = FakeCommandRunner()
    service = GitService(GitRunner(fake))

    service.tags_raw("/repo")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "tag", "--list"]

    service.create_tag("/repo", "v1.0.0")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "tag", "v1.0.0"]

    service.create_tag("/repo", "v1.0.1", ref="HEAD~1")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "tag", "v1.0.1", "HEAD~1"]

    service.delete_tag("/repo", "v1.0.0")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "tag", "-d", "v1.0.0"]

    service.push_tag("/repo", "v1.0.0", remote="origin")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "push", "origin", "v1.0.0"]

    service.push_tags("/repo", remote="origin")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "push", "origin", "--tags"]


def test_git_service_remotes_raw_and_actions() -> None:
    fake = FakeCommandRunner()
    service = GitService(GitRunner(fake))

    service.remotes_raw("/repo")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "remote", "-v"]

    service.add_remote("/repo", "origin", "https://example.com/repo.git")
    spec = fake.calls[-1]
    assert list(spec.args) == [
        "git",
        "remote",
        "add",
        "origin",
        "https://example.com/repo.git",
    ]

    service.remove_remote("/repo", "origin")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "remote", "remove", "origin"]

    service.set_remote_url("/repo", "origin", "https://example.com/new.git")
    spec = fake.calls[-1]
    assert list(spec.args) == [
        "git",
        "remote",
        "set-url",
        "origin",
        "https://example.com/new.git",
    ]

    service.delete_remote_branch("/repo", "origin", "feature-x")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "push", "origin", "--delete", "feature-x"]

    service.set_upstream("/repo", "origin/main", branch="main")
    spec = fake.calls[-1]
    assert list(spec.args) == [
        "git",
        "branch",
        "--set-upstream-to",
        "origin/main",
        "main",
    ]


def test_git_service_branch_actions() -> None:
    fake = FakeCommandRunner()
    service = GitService(GitRunner(fake))

    service.switch_branch("/repo", "feature")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "switch", "feature"]

    service.create_branch("/repo", "feature", from_ref="HEAD")
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "switch", "-c", "feature", "HEAD"]

    service.delete_branch("/repo", "feature", force=False)
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "branch", "-d", "feature"]

    service.delete_branch("/repo", "feature", force=True)
    spec = fake.calls[-1]
    assert list(spec.args) == ["git", "branch", "-D", "feature"]


def test_git_service_runner_property_exposes_command_runner() -> None:
    """The runner property exposes the underlying CommandRunner."""
    fake = FakeCommandRunner()
    runner = GitRunner(fake)
    service = GitService(runner)

    # Access the runner property
    assert service.runner is fake


def test_git_service_push_set_upstream_missing_remote_raises() -> None:
    """push with set_upstream=True but missing remote raises ValueError."""
    import pytest

    fake = FakeCommandRunner()
    service = GitService(GitRunner(fake))

    with pytest.raises(ValueError, match="remote and branch are required"):
        service.push("/repo", set_upstream=True, remote=None, branch="main")


def test_git_service_push_set_upstream_missing_branch_raises() -> None:
    """push with set_upstream=True but missing branch raises ValueError."""
    import pytest

    fake = FakeCommandRunner()
    service = GitService(GitRunner(fake))

    with pytest.raises(ValueError, match="remote and branch are required"):
        service.push("/repo", set_upstream=True, remote="origin", branch=None)
