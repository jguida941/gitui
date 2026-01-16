from __future__ import annotations

from collections.abc import Sequence

from app.core.models import Branch, Commit, Remote, RepoStatus, StashEntry, Tag
from app.utils.qt_compat import QObject, Signal

# RepoState is the single source of truth for UI data.
# We centralize state here so UI widgets can subscribe to one signal and avoid
# brittle partial-update logic spread across the UI.

class RepoState(QObject):
    """Mutable state for the current repository view."""

    # Emitted whenever any state property changes.
    # UI components connect to this to know when to refresh.
    state_changed = Signal()

    def __init__(self) -> None:
        """Initialize empty state."""
        super().__init__()
        # Data loaded from git.
        self._repo_path: str | None = None
        self._status: RepoStatus | None = None
        self._log: Sequence[Commit] | None = None
        self._branches: Sequence[Branch] | None = None
        self._stashes: Sequence[StashEntry] | None = None
        self._tags: Sequence[Tag] | None = None
        self._remotes: Sequence[Remote] | None = None
        self._conflicts: Sequence[str] | None = None
        self._diff_text: str | None = None

        # UI-facing status flags.
        self._last_error: Exception | None = None
        self._busy = False

    @property
    def repo_path(self) -> str | None:
        """Current repo path or None."""
        return self._repo_path

    @property
    def status(self) -> RepoStatus | None:
        """Latest parsed repo status snapshot."""
        return self._status

    @property
    def log(self) -> Sequence[Commit] | None:
        """Latest parsed commit log, if loaded."""
        return self._log

    @property
    def branches(self) -> Sequence[Branch] | None:
        """Latest parsed branch list, if loaded."""
        return self._branches

    @property
    def stashes(self) -> Sequence[StashEntry] | None:
        """Latest parsed stash list, if loaded."""
        return self._stashes

    @property
    def tags(self) -> Sequence[Tag] | None:
        """Latest parsed tag list, if loaded."""
        return self._tags

    @property
    def remotes(self) -> Sequence[Remote] | None:
        """Latest parsed remote list, if loaded."""
        return self._remotes

    @property
    def conflicts(self) -> Sequence[str] | None:
        """Latest list of conflicted paths, if loaded."""
        return self._conflicts

    @property
    def diff_text(self) -> str | None:
        """Latest diff text for the selected file, if loaded."""
        return self._diff_text

    @property
    def last_error(self) -> Exception | None:
        """Most recent error, if any."""
        return self._last_error

    @property
    def busy(self) -> bool:
        """True when a command is running."""
        return self._busy

    def set_repo_path(self, path: str | None) -> None:
        """Update the current repo path and notify listeners."""
        self._repo_path = path
        self.state_changed.emit()

    def set_status(self, status: RepoStatus | None) -> None:
        """Update the current status snapshot and notify listeners."""
        self._status = status
        self.state_changed.emit()

    def set_log(self, commits: Sequence[Commit] | None) -> None:
        """Update the commit log and notify listeners."""
        self._log = commits
        self.state_changed.emit()

    def set_branches(self, branches: Sequence[Branch] | None) -> None:
        """Update the branch list and notify listeners."""
        self._branches = branches
        self.state_changed.emit()

    def set_stashes(self, stashes: Sequence[StashEntry] | None) -> None:
        """Update the stash list and notify listeners."""
        self._stashes = stashes
        self.state_changed.emit()

    def set_tags(self, tags: Sequence[Tag] | None) -> None:
        """Update the tag list and notify listeners."""
        self._tags = tags
        self.state_changed.emit()

    def set_remotes(self, remotes: Sequence[Remote] | None) -> None:
        """Update the remote list and notify listeners."""
        self._remotes = remotes
        self.state_changed.emit()

    def set_conflicts(self, conflicts: Sequence[str] | None) -> None:
        """Update the conflicted paths and notify listeners."""
        self._conflicts = conflicts
        self.state_changed.emit()

    def set_diff_text(self, diff_text: str | None) -> None:
        """Update the latest diff text and notify listeners."""
        self._diff_text = diff_text
        self.state_changed.emit()

    def set_error(self, error: Exception | None) -> None:
        """Update the last error and notify listeners."""
        self._last_error = error
        self.state_changed.emit()

    def set_busy(self, busy: bool) -> None:
        """Update busy flag and notify listeners."""
        self._busy = busy
        self.state_changed.emit()
