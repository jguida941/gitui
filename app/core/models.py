from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class FileChange:
    """Single file change from git status porcelain v2."""

    path: str
    staged_status: str
    unstaged_status: str
    orig_path: str | None = None


@dataclass(frozen=True)
class BranchInfo:
    """Branch and upstream tracking info for the current HEAD."""

    name: str | None
    head_oid: str | None
    upstream: str | None
    ahead: int
    behind: int


@dataclass(frozen=True)
class Branch:
    """Single branch row from `git branch --format=...` output."""

    name: str
    # The UI uses these flags to render tracking and HEAD markers.
    is_current: bool
    upstream: str | None
    ahead: int
    behind: int
    gone: bool


@dataclass(frozen=True)
class RepoStatus:
    """Snapshot of repo status grouped for the UI."""

    branch: BranchInfo | None
    staged: Sequence[FileChange]
    unstaged: Sequence[FileChange]
    untracked: Sequence[FileChange]
    conflicted: Sequence[FileChange]


@dataclass(frozen=True)
class Commit:
    """Commit metadata parsed from structured git log output."""

    oid: str
    parents: Sequence[str]
    author_name: str
    author_email: str
    # Keep raw ISO-8601 for now; formatting happens in UI.
    author_date: str
    subject: str


@dataclass(frozen=True)
class StashEntry:
    """Single stash row parsed from structured stash list output."""

    oid: str
    selector: str
    summary: str
    date: str


@dataclass(frozen=True)
class Tag:
    """Single tag name from git tag output."""

    name: str


@dataclass(frozen=True)
class Remote:
    """Remote name with optional fetch/push URLs."""

    name: str
    fetch_url: str | None
    push_url: str | None
