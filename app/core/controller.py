from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from app.core.errors import CommandFailed, NotARepo, ParseError
from app.core.repo_state import RepoState
from app.exec.command_queue import CommandQueue, QueueItem, QueuePriority
from app.git.git_service import GitService
from app.utils.qt_compat import QObject

# ─────────────────────────────────────────────────────────────────────────────
# PendingAction: Tracks in-flight commands so we can route results correctly.
# When a command completes, we look up its PendingAction to know:
#   - kind: What type of operation it was (status, commit, etc.)
#   - refresh_*: Which data views to reload after success
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PendingAction:
    """Tracks which intent a RunHandle belongs to."""

    # Routing key for _on_command_finished to select the parse/update path.
    kind: str
    # Used only when validating a repo path.
    repo_path: str | None = None
    # Diff actions track the file path for UI context.
    path: str | None = None
    # Diff actions need the staged/unstaged choice.
    staged: bool = False

    # Flags to trigger automatic refreshes after mutating operations succeed.
    refresh_status: bool = False
    refresh_branches: bool = False
    refresh_log: bool = False
    refresh_stashes: bool = False
    refresh_tags: bool = False
    refresh_remotes: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# RepoController: The "brain" of the application.
#
# Architecture:
#   UI ──> Controller ──> GitService ──> CommandRunner ──> git subprocess
#                │                              │
#                └── RepoState <── parse ───────┘
#
# Flow:
#   1. UI calls a controller method (e.g., commit())
#   2. Controller enqueues the action with a priority
#   3. Queue runs the action when ready (serializes commands)
#   4. GitService starts the git command via CommandRunner
#   5. CommandRunner emits command_finished when done
#   6. Controller receives result, parses it, updates RepoState
#   7. RepoState emits state_changed, UI reacts
#
# Key design decisions:
#   - Commands are queued to prevent race conditions
#   - User actions (stage, commit) have priority over background refreshes
#   - Background refreshes coalesce (only the latest refresh runs)
#   - All state changes go through RepoState for consistent UI updates
# ─────────────────────────────────────────────────────────────────────────────


class RepoController(QObject):
    """Coordinates git intents, queueing, and state updates."""

    def __init__(
        self,
        service: GitService,
        state: RepoState | None = None,
        queue: CommandQueue | None = None,
    ) -> None:
        super().__init__()
        # Service builds git commands and parses outputs.
        self._service = service
        # State changes emit signals for UI listeners.
        self._state = state or RepoState()
        # Serializes command execution and coalesces background refreshes.
        self._queue = queue or CommandQueue()

        # Map run_id -> PendingAction so we know how to handle each completion.
        self._pending: dict[int, PendingAction] = {}

        # Wire up the completion callback so we process results.
        self._service.runner.command_finished.connect(self._on_command_finished)

    @property
    def state(self) -> RepoState:
        """Expose the current repo state for the UI."""
        return self._state

    def _enqueue(self, key: str, priority: QueuePriority, run: Callable[[], None]) -> None:
        """Add a command to the queue with the given priority."""
        self._queue.enqueue(QueueItem(key=key, run=run, priority=priority))

    def open_repo(self, repo_path: str) -> None:
        """Validate a repo path and set it if valid."""

        def action() -> None:
            # Ask git whether this path is inside a work tree.
            handle = self._service.is_inside_work_tree_raw(repo_path)
            self._pending[handle.run_id] = PendingAction(kind="validate_repo", repo_path=repo_path)
            self._state.set_busy(True)

        self._enqueue("open_repo", QueuePriority.USER, action)

    def refresh_status(self) -> None:
        """Fetch status for the current repo, if set."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            # Run porcelain v2 status and mark it as pending.
            handle = self._service.status_raw(self._state.repo_path)
            self._pending[handle.run_id] = PendingAction(kind="status")
            self._state.set_busy(True)

        self._enqueue("refresh_status", QueuePriority.BACKGROUND, action)

    def refresh_log(self, limit: int = 300) -> None:
        """Fetch recent commits for the current repo."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.log_raw(self._state.repo_path, limit=limit)
            self._pending[handle.run_id] = PendingAction(kind="log")
            self._state.set_busy(True)

        self._enqueue("refresh_log", QueuePriority.BACKGROUND, action)

    def refresh_branches(self) -> None:
        """Fetch branch list for the current repo."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.branches_raw(self._state.repo_path)
            self._pending[handle.run_id] = PendingAction(kind="branches")
            self._state.set_busy(True)

        self._enqueue("refresh_branches", QueuePriority.BACKGROUND, action)

    def refresh_conflicts(self) -> None:
        """Fetch conflicted paths for the current repo."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.conflicts_raw(self._state.repo_path)
            self._pending[handle.run_id] = PendingAction(kind="conflicts")
            self._state.set_busy(True)

        self._enqueue("refresh_conflicts", QueuePriority.BACKGROUND, action)

    def refresh_stashes(self) -> None:
        """Fetch stash list for the current repo."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.stash_list_raw(self._state.repo_path)
            self._pending[handle.run_id] = PendingAction(kind="stashes")
            self._state.set_busy(True)

        self._enqueue("refresh_stashes", QueuePriority.BACKGROUND, action)

    def refresh_tags(self) -> None:
        """Fetch tag list for the current repo."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.tags_raw(self._state.repo_path)
            self._pending[handle.run_id] = PendingAction(kind="tags")
            self._state.set_busy(True)

        self._enqueue("refresh_tags", QueuePriority.BACKGROUND, action)

    def refresh_remotes(self) -> None:
        """Fetch remote list for the current repo."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.remotes_raw(self._state.repo_path)
            self._pending[handle.run_id] = PendingAction(kind="remotes")
            self._state.set_busy(True)

        self._enqueue("refresh_remotes", QueuePriority.BACKGROUND, action)

    def request_diff(self, path: str, staged: bool = False) -> None:
        """Load a diff for a single file in the current repo."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.diff_file_raw(self._state.repo_path, path, staged=staged)
            self._pending[handle.run_id] = PendingAction(kind="diff", path=path, staged=staged)
            self._state.set_busy(True)

        self._enqueue("diff", QueuePriority.USER, action)

    def stage(self, paths: list[str]) -> None:
        """Stage files and refresh status on success."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.stage(self._state.repo_path, paths)
            self._pending[handle.run_id] = PendingAction(kind="stage", refresh_status=True)
            self._state.set_busy(True)

        self._enqueue("stage", QueuePriority.USER, action)

    def unstage(self, paths: list[str]) -> None:
        """Unstage files and refresh status on success."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.unstage(self._state.repo_path, paths)
            self._pending[handle.run_id] = PendingAction(kind="unstage", refresh_status=True)
            self._state.set_busy(True)

        self._enqueue("unstage", QueuePriority.USER, action)

    def discard(self, paths: list[str]) -> None:
        """Discard local changes and refresh status on success."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.discard(self._state.repo_path, paths)
            self._pending[handle.run_id] = PendingAction(kind="discard", refresh_status=True)
            self._state.set_busy(True)

        self._enqueue("discard", QueuePriority.USER, action)

    def commit(self, message: str, amend: bool = False) -> None:
        """Commit staged changes and refresh status/log on success."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.commit(self._state.repo_path, message, amend=amend)
            self._pending[handle.run_id] = PendingAction(
                kind="commit", refresh_status=True, refresh_log=True
            )
            self._state.set_busy(True)

        self._enqueue("commit", QueuePriority.USER, action)

    def fetch(self) -> None:
        """Fetch and refresh branches if needed."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.fetch(self._state.repo_path)
            self._pending[handle.run_id] = PendingAction(kind="fetch", refresh_branches=True)
            self._state.set_busy(True)

        self._enqueue("fetch", QueuePriority.USER, action)

    def pull_ff_only(self) -> None:
        """Pull with fast-forward only and refresh status."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.pull_ff_only(self._state.repo_path)
            self._pending[handle.run_id] = PendingAction(kind="pull", refresh_status=True)
            self._state.set_busy(True)

        self._enqueue("pull", QueuePriority.USER, action)

    def push(
        self, set_upstream: bool = False, remote: str | None = None, branch: str | None = None
    ) -> None:
        """Push to remote and refresh branches if needed."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.push(
                self._state.repo_path,
                set_upstream=set_upstream,
                remote=remote,
                branch=branch,
            )
            self._pending[handle.run_id] = PendingAction(kind="push", refresh_branches=True)
            self._state.set_busy(True)

        self._enqueue("push", QueuePriority.USER, action)

    def switch_branch(self, name: str) -> None:
        """Switch branches and refresh status/branches."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.switch_branch(self._state.repo_path, name)
            self._pending[handle.run_id] = PendingAction(
                kind="switch_branch", refresh_status=True, refresh_branches=True
            )
            self._state.set_busy(True)

        self._enqueue("switch_branch", QueuePriority.USER, action)

    def create_branch(self, name: str, from_ref: str = "HEAD") -> None:
        """Create and switch to a new branch, then refresh status/branches."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.create_branch(self._state.repo_path, name, from_ref=from_ref)
            self._pending[handle.run_id] = PendingAction(
                kind="create_branch", refresh_status=True, refresh_branches=True
            )
            self._state.set_busy(True)

        self._enqueue("create_branch", QueuePriority.USER, action)

    def delete_branch(self, name: str, force: bool = False) -> None:
        """Delete a branch and refresh branch list."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.delete_branch(self._state.repo_path, name, force=force)
            self._pending[handle.run_id] = PendingAction(
                kind="delete_branch", refresh_branches=True
            )
            self._state.set_busy(True)

        self._enqueue("delete_branch", QueuePriority.USER, action)

    def stash_save(self, message: str | None = None, include_untracked: bool = False) -> None:
        """Create a stash and refresh status + stashes."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.stash_save(
                self._state.repo_path,
                message=message,
                include_untracked=include_untracked,
            )
            self._pending[handle.run_id] = PendingAction(
                kind="stash_save", refresh_status=True, refresh_stashes=True
            )
            self._state.set_busy(True)

        self._enqueue("stash_save", QueuePriority.USER, action)

    def stash_apply(self, ref: str | None = None) -> None:
        """Apply a stash and refresh status."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.stash_apply(self._state.repo_path, ref=ref)
            self._pending[handle.run_id] = PendingAction(kind="stash_apply", refresh_status=True)
            self._state.set_busy(True)

        self._enqueue("stash_apply", QueuePriority.USER, action)

    def stash_pop(self, ref: str | None = None) -> None:
        """Pop a stash and refresh status + stashes."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.stash_pop(self._state.repo_path, ref=ref)
            self._pending[handle.run_id] = PendingAction(
                kind="stash_pop", refresh_status=True, refresh_stashes=True
            )
            self._state.set_busy(True)

        self._enqueue("stash_pop", QueuePriority.USER, action)

    def stash_drop(self, ref: str | None = None) -> None:
        """Drop a stash entry and refresh stash list."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.stash_drop(self._state.repo_path, ref=ref)
            self._pending[handle.run_id] = PendingAction(kind="stash_drop", refresh_stashes=True)
            self._state.set_busy(True)

        self._enqueue("stash_drop", QueuePriority.USER, action)

    def create_tag(self, name: str, ref: str | None = None) -> None:
        """Create a tag and refresh tag list."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.create_tag(self._state.repo_path, name, ref=ref)
            self._pending[handle.run_id] = PendingAction(kind="create_tag", refresh_tags=True)
            self._state.set_busy(True)

        self._enqueue("create_tag", QueuePriority.USER, action)

    def delete_tag(self, name: str) -> None:
        """Delete a tag and refresh tag list."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.delete_tag(self._state.repo_path, name)
            self._pending[handle.run_id] = PendingAction(kind="delete_tag", refresh_tags=True)
            self._state.set_busy(True)

        self._enqueue("delete_tag", QueuePriority.USER, action)

    def push_tag(self, name: str, remote: str = "origin") -> None:
        """Push a tag to a remote."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.push_tag(self._state.repo_path, name, remote=remote)
            self._pending[handle.run_id] = PendingAction(kind="push_tag")
            self._state.set_busy(True)

        self._enqueue("push_tag", QueuePriority.USER, action)

    def push_tags(self, remote: str = "origin") -> None:
        """Push all tags to a remote."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.push_tags(self._state.repo_path, remote=remote)
            self._pending[handle.run_id] = PendingAction(kind="push_tags")
            self._state.set_busy(True)

        self._enqueue("push_tags", QueuePriority.USER, action)

    def add_remote(self, name: str, url: str) -> None:
        """Add a remote and refresh remotes list."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.add_remote(self._state.repo_path, name, url)
            self._pending[handle.run_id] = PendingAction(kind="add_remote", refresh_remotes=True)
            self._state.set_busy(True)

        self._enqueue("add_remote", QueuePriority.USER, action)

    def remove_remote(self, name: str) -> None:
        """Remove a remote and refresh remotes list."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.remove_remote(self._state.repo_path, name)
            self._pending[handle.run_id] = PendingAction(kind="remove_remote", refresh_remotes=True)
            self._state.set_busy(True)

        self._enqueue("remove_remote", QueuePriority.USER, action)

    def set_remote_url(self, name: str, url: str) -> None:
        """Update a remote URL and refresh remotes list."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.set_remote_url(self._state.repo_path, name, url)
            self._pending[handle.run_id] = PendingAction(
                kind="set_remote_url", refresh_remotes=True
            )
            self._state.set_busy(True)

        self._enqueue("set_remote_url", QueuePriority.USER, action)

    def set_upstream(self, upstream: str, branch: str | None = None) -> None:
        """Set upstream tracking and refresh branches list."""
        if not self._state.repo_path:
            self._state.set_error(NotARepo("(none)"))
            return

        def action() -> None:
            handle = self._service.set_upstream(self._state.repo_path, upstream, branch=branch)
            self._pending[handle.run_id] = PendingAction(kind="set_upstream", refresh_branches=True)
            self._state.set_busy(True)

        self._enqueue("set_upstream", QueuePriority.USER, action)

    # ─────────────────────────────────────────────────────────────────────────
    # Command Completion Handler: The central routing logic.
    #
    # When any git command finishes, this method:
    #   1. Looks up the PendingAction to understand what command it was
    #   2. Checks for errors (non-zero exit code)
    #   3. Routes to the appropriate parser based on action.kind
    #   4. Updates RepoState with parsed results
    #   5. Triggers any follow-up refreshes (e.g., refresh status after commit)
    #   6. Clears the busy flag when no more commands are pending
    # ─────────────────────────────────────────────────────────────────────────

    def _on_command_finished(self, handle: object, result: object) -> None:
        """Handle completed commands and update RepoState."""
        try:
            # PySide6 signals use `object` type to avoid registration friction.
            # We know these are actually RunHandle and CommandResult.
            run_handle = handle  # type: ignore[assignment]
            cmd_result = result  # type: ignore[assignment]

            # Find and remove the pending action for this command.
            action = self._pending.pop(run_handle.run_id, None)
            if not action:
                # Unknown command (shouldn't happen) - ignore it.
                return

            # Any non-zero exit code is an error we surface to the UI.
            if not cmd_result.ok:
                self._state.set_error(
                    CommandFailed(
                        command_args=run_handle.spec.args,
                        exit_code=cmd_result.exit_code,
                        stdout=cmd_result.stdout,
                        stderr=cmd_result.stderr,
                    )
                )
                return

            # ───── Route by action kind to the appropriate handler ─────
            if action.kind == "validate_repo":
                output = cmd_result.stdout.decode("utf-8", errors="replace").strip()
                if output == "true":
                    self._state.set_repo_path(action.repo_path)
                    self._state.set_error(None)
                    self.refresh_status()
                else:
                    self._state.set_error(NotARepo(action.repo_path or ""))

            elif action.kind == "status":
                try:
                    status = self._service.parse_status(cmd_result.stdout)
                    self._state.set_status(status)
                    self._state.set_error(None)
                except Exception as exc:
                    self._state.set_error(ParseError(str(exc)))

            elif action.kind == "log":
                try:
                    commits = self._service.parse_log(cmd_result.stdout)
                    self._state.set_log(commits)
                    self._state.set_error(None)
                except Exception as exc:
                    self._state.set_error(ParseError(str(exc)))

            elif action.kind == "branches":
                try:
                    branches = self._service.parse_branches(cmd_result.stdout)
                    self._state.set_branches(branches)
                    self._state.set_error(None)
                except Exception as exc:
                    self._state.set_error(ParseError(str(exc)))

            elif action.kind == "conflicts":
                try:
                    conflicts = self._service.parse_conflicts(cmd_result.stdout)
                    self._state.set_conflicts(conflicts)
                    self._state.set_error(None)
                except Exception as exc:
                    self._state.set_error(ParseError(str(exc)))

            elif action.kind == "stashes":
                try:
                    stashes = self._service.parse_stashes(cmd_result.stdout)
                    self._state.set_stashes(stashes)
                    self._state.set_error(None)
                except Exception as exc:
                    self._state.set_error(ParseError(str(exc)))

            elif action.kind == "tags":
                try:
                    tags = self._service.parse_tags(cmd_result.stdout)
                    self._state.set_tags(tags)
                    self._state.set_error(None)
                except Exception as exc:
                    self._state.set_error(ParseError(str(exc)))

            elif action.kind == "remotes":
                try:
                    remotes = self._service.parse_remotes(cmd_result.stdout)
                    self._state.set_remotes(remotes)
                    self._state.set_error(None)
                except Exception as exc:
                    self._state.set_error(ParseError(str(exc)))

            elif action.kind == "diff":
                diff_text = self._service.parse_diff(cmd_result.stdout)
                self._state.set_diff_text(diff_text)
                self._state.set_error(None)

            # For mutating actions, trigger refreshes if requested.
            if action.refresh_status:
                self.refresh_status()
            if action.refresh_branches:
                self.refresh_branches()
            if action.refresh_log:
                self.refresh_log()
            if action.refresh_stashes:
                self.refresh_stashes()
            if action.refresh_tags:
                self.refresh_tags()
            if action.refresh_remotes:
                self.refresh_remotes()
        finally:
            # Busy is true if any actions remain in flight.
            self._state.set_busy(bool(self._pending))
            self._queue.mark_idle()
