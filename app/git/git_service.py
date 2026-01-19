from __future__ import annotations

from collections.abc import Sequence

from app.core.models import (
    Branch,
    Commit,
    Remote,
    RemoteBranch,
    RepoStatus,
    StashEntry,
    Tag,
)
from app.exec.command_models import RunHandle
from app.exec.command_runner import CommandRunner
from app.git.git_runner import GitRunner
from app.git.parse_branches import parse_branches
from app.git.parse_conflicts import parse_conflict_paths
from app.git.parse_diff import parse_diff_text
from app.git.parse_log import parse_log_records
from app.git.parse_remote_branches import parse_remote_branches
from app.git.parse_remotes import parse_remotes
from app.git.parse_stash import parse_stash_records
from app.git.parse_status import parse_status_porcelain_v2
from app.git.parse_tags import parse_tags

# ─────────────────────────────────────────────────────────────────────────────
# Git Output Formats
#
# We use custom format strings to get machine-readable output from git.
# Using non-printable ASCII separators makes parsing reliable:
#   \x1f (Unit Separator) - separates fields within a record
#   \x1e (Record Separator) - separates records from each other
#
# These are safe because they won't appear in commit messages or file names.
# ─────────────────────────────────────────────────────────────────────────────

# Log format: oid, parents, author_name, author_email, author_date, subject
LOG_FORMAT = "%H%x1f%P%x1f%an%x1f%ae%x1f%ad%x1f%s%x1e"

# Stash format: oid, reflog_selector (stash@{n}), subject, date
STASH_FORMAT = "%H%x1f%gd%x1f%gs%x1f%ad%x1e"

# Branch format: name, is_current (*), upstream, tracking status (+n/-n)
BRANCH_FORMAT = "%(refname:short)|%(HEAD)|%(upstream:short)|%(upstream:track)"


# ─────────────────────────────────────────────────────────────────────────────
# GitService: Intent layer between Controller and GitRunner.
#
# This class provides:
#   - High-level git operations as methods (stage, commit, push, etc.)
#   - Raw command methods (*_raw) that return RunHandle for async execution
#   - Parse methods that convert git output bytes into domain objects
#
# Design:
#   - All commands go through GitRunner (which wraps CommandRunner)
#   - Raw methods are async - they return immediately with a RunHandle
#   - Results come back via CommandRunner.command_finished signal
#   - Controller calls parse_* methods to convert output to domain objects
# ─────────────────────────────────────────────────────────────────────────────


class GitService:
    """Intent layer for git operations and parsing."""

    def __init__(self, runner: GitRunner) -> None:
        # GitRunner is the only path to execute git commands.
        self._runner = runner

    @property
    def runner(self) -> CommandRunner:
        """Expose CommandRunner so controllers can subscribe to signals."""
        return self._runner.runner

    def status_raw(self, repo_path: str) -> RunHandle:
        """Run git status using machine-readable output."""
        # --porcelain=v2: Stable machine-readable format with more detail
        # -b: Include branch info (name, upstream, ahead/behind)
        # -z: Use NUL as separator (safe for filenames with special chars)
        return self._runner.run(
            ["status", "--porcelain=v2", "-b", "-z"],
            cwd=repo_path,
        )

    def diff_file_raw(
        self, repo_path: str, path: str, staged: bool = False
    ) -> RunHandle:
        """Run git diff for a single file."""
        # --no-color: Raw diff without ANSI escape codes
        # --cached: Show staged changes (index vs HEAD) instead of working tree
        # --: Separates options from file paths (prevents path confusion)
        args = ["diff", "--no-color"]
        if staged:
            args.append("--cached")
        args.extend(["--", path])
        return self._runner.run(args, cwd=repo_path)

    def stage(self, repo_path: str, paths: Sequence[str]) -> RunHandle:
        """Stage files (git add)."""
        return self._runner.run(["add", "--", *paths], cwd=repo_path)

    def unstage(self, repo_path: str, paths: Sequence[str]) -> RunHandle:
        """Unstage files (git restore --staged)."""
        return self._runner.run(["restore", "--staged", "--", *paths], cwd=repo_path)

    def discard(self, repo_path: str, paths: Sequence[str]) -> RunHandle:
        """Discard local changes (git restore)."""
        return self._runner.run(["restore", "--", *paths], cwd=repo_path)

    def commit(self, repo_path: str, message: str, amend: bool = False) -> RunHandle:
        """Commit staged changes with a message."""
        args = ["commit"]
        if amend:
            args.append("--amend")
        args.extend(["-m", message])
        return self._runner.run(args, cwd=repo_path)

    def fetch(self, repo_path: str) -> RunHandle:
        """Fetch from remotes."""
        return self._runner.run(["fetch"], cwd=repo_path)

    def pull_ff_only(self, repo_path: str) -> RunHandle:
        """Pull with fast-forward only."""
        return self._runner.run(["pull", "--ff-only"], cwd=repo_path)

    def push(
        self,
        repo_path: str,
        set_upstream: bool = False,
        remote: str | None = None,
        branch: str | None = None,
    ) -> RunHandle:
        """Push to remote (optionally set upstream)."""
        args = ["push"]
        if set_upstream:
            if not remote or not branch:
                raise ValueError(
                    "remote and branch are required when set_upstream is True"
                )
            args.extend(["-u", remote, branch])
        return self._runner.run(args, cwd=repo_path)

    def log_raw(self, repo_path: str, limit: int = 300) -> RunHandle:
        """Return structured log output for recent commits."""
        return self._runner.run(
            [
                "log",
                "--date=iso-strict",
                f"--pretty=format:{LOG_FORMAT}",
                "-n",
                str(limit),
            ],
            cwd=repo_path,
        )

    def branches_raw(self, repo_path: str) -> RunHandle:
        """List branches with upstream tracking info."""
        return self._runner.run(["branch", f"--format={BRANCH_FORMAT}"], cwd=repo_path)

    def remote_branches_raw(self, repo_path: str) -> RunHandle:
        """List remote-tracking branches."""
        return self._runner.run(
            ["branch", "-r", "--format=%(refname:short)"], cwd=repo_path
        )

    def conflicts_raw(self, repo_path: str) -> RunHandle:
        """List conflicted paths using diff-filter=U."""
        return self._runner.run(
            ["diff", "--name-only", "--diff-filter=U"], cwd=repo_path
        )

    def stash_list_raw(self, repo_path: str) -> RunHandle:
        """List stashes using structured output for parsing."""
        return self._runner.run(
            ["stash", "list", "--date=iso-strict", f"--pretty=format:{STASH_FORMAT}"],
            cwd=repo_path,
        )

    def stash_save(
        self,
        repo_path: str,
        message: str | None = None,
        include_untracked: bool = False,
    ) -> RunHandle:
        """Create a stash with an optional message."""
        args = ["stash", "push"]
        if include_untracked:
            args.append("-u")
        if message:
            args.extend(["-m", message])
        return self._runner.run(args, cwd=repo_path)

    def stash_apply(self, repo_path: str, ref: str | None = None) -> RunHandle:
        """Apply a stash without dropping it."""
        args = ["stash", "apply"]
        if ref:
            args.append(ref)
        return self._runner.run(args, cwd=repo_path)

    def stash_pop(self, repo_path: str, ref: str | None = None) -> RunHandle:
        """Apply a stash and drop it if successful."""
        args = ["stash", "pop"]
        if ref:
            args.append(ref)
        return self._runner.run(args, cwd=repo_path)

    def stash_drop(self, repo_path: str, ref: str | None = None) -> RunHandle:
        """Drop a stash entry without applying it."""
        args = ["stash", "drop"]
        if ref:
            args.append(ref)
        return self._runner.run(args, cwd=repo_path)

    def tags_raw(self, repo_path: str) -> RunHandle:
        """List tags in the repo."""
        return self._runner.run(["tag", "--list"], cwd=repo_path)

    def create_tag(
        self, repo_path: str, name: str, ref: str | None = None
    ) -> RunHandle:
        """Create a lightweight tag at the given ref (default HEAD)."""
        args = ["tag", name]
        if ref:
            args.append(ref)
        return self._runner.run(args, cwd=repo_path)

    def delete_tag(self, repo_path: str, name: str) -> RunHandle:
        """Delete a local tag."""
        return self._runner.run(["tag", "-d", name], cwd=repo_path)

    def push_tag(self, repo_path: str, name: str, remote: str = "origin") -> RunHandle:
        """Push a single tag to a remote."""
        return self._runner.run(["push", remote, name], cwd=repo_path)

    def push_tags(self, repo_path: str, remote: str = "origin") -> RunHandle:
        """Push all tags to a remote."""
        return self._runner.run(["push", remote, "--tags"], cwd=repo_path)

    def remotes_raw(self, repo_path: str) -> RunHandle:
        """List remotes with their fetch/push URLs."""
        return self._runner.run(["remote", "-v"], cwd=repo_path)

    def add_remote(self, repo_path: str, name: str, url: str) -> RunHandle:
        """Add a new remote."""
        return self._runner.run(["remote", "add", name, url], cwd=repo_path)

    def remove_remote(self, repo_path: str, name: str) -> RunHandle:
        """Remove an existing remote."""
        return self._runner.run(["remote", "remove", name], cwd=repo_path)

    def set_remote_url(self, repo_path: str, name: str, url: str) -> RunHandle:
        """Update a remote's URL."""
        return self._runner.run(["remote", "set-url", name, url], cwd=repo_path)

    def set_upstream(
        self, repo_path: str, upstream: str, branch: str | None = None
    ) -> RunHandle:
        """Set upstream tracking for a branch (default: current branch)."""
        args = ["branch", "--set-upstream-to", upstream]
        if branch:
            args.append(branch)
        return self._runner.run(args, cwd=repo_path)

    def switch_branch(self, repo_path: str, name: str) -> RunHandle:
        """Switch to an existing branch."""
        return self._runner.run(["switch", name], cwd=repo_path)

    def create_branch(
        self, repo_path: str, name: str, from_ref: str = "HEAD"
    ) -> RunHandle:
        """Create and switch to a new branch."""
        return self._runner.run(["switch", "-c", name, from_ref], cwd=repo_path)

    def delete_branch(
        self, repo_path: str, name: str, force: bool = False
    ) -> RunHandle:
        """Delete a local branch."""
        flag = "-D" if force else "-d"
        return self._runner.run(["branch", flag, name], cwd=repo_path)

    def delete_remote_branch(self, repo_path: str, remote: str, name: str) -> RunHandle:
        """Delete a remote branch via push --delete."""
        return self._runner.run(["push", remote, "--delete", name], cwd=repo_path)

    def is_inside_work_tree_raw(self, repo_path: str) -> RunHandle:
        """Check if a path is inside a git work tree."""
        return self._runner.run(
            ["rev-parse", "--is-inside-work-tree"],
            cwd=repo_path,
        )

    def version_raw(self) -> RunHandle:
        """Return the git version output (raw)."""
        return self._runner.run(["--version"])

    def parse_status(self, payload: bytes) -> RepoStatus:
        """Parse porcelain v2 status output into RepoStatus."""
        return parse_status_porcelain_v2(payload)

    def parse_log(self, payload: bytes) -> list[Commit]:
        """Parse structured log output into Commit objects."""
        return parse_log_records(payload)

    def parse_diff(self, payload: bytes) -> str:
        """Return diff output as text for display."""
        return parse_diff_text(payload)

    def parse_branches(self, payload: bytes) -> list[Branch]:
        """Parse branch list output into Branch objects."""
        return parse_branches(payload)

    def parse_remote_branches(self, payload: bytes) -> list[RemoteBranch]:
        """Parse remote branch list output into RemoteBranch objects."""
        return parse_remote_branches(payload)

    def parse_conflicts(self, payload: bytes) -> list[str]:
        """Parse conflicted paths into a list of strings."""
        return parse_conflict_paths(payload)

    def parse_stashes(self, payload: bytes) -> list[StashEntry]:
        """Parse stash list output into StashEntry objects."""
        return parse_stash_records(payload)

    def parse_tags(self, payload: bytes) -> list[Tag]:
        """Parse tag list output into Tag objects."""
        return parse_tags(payload)

    def parse_remotes(self, payload: bytes) -> list[Remote]:
        """Parse remote list output into Remote objects."""
        return parse_remotes(payload)
