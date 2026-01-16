from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QSplitter, QTabWidget, QVBoxLayout, QWidget

from app.core.controller import RepoController
from app.core.errors import CommandFailed
from app.core.repo_state import RepoState
from app.exec.command_runner import CommandRunner
from app.git.git_runner import GitRunner
from app.git.git_service import GitService
from app.ui.branches_panel import BranchesPanel
from app.ui.commit_panel import CommitPanel
from app.ui.console_widget import ConsoleWidget
from app.ui.dialogs.confirm_dialog import ConfirmDialog
from app.ui.dialogs.error_dialog import ErrorDialog
from app.ui.dialogs.theme_editor_dialog import ThemeEditorDialog
from app.ui.diff_viewer import DiffViewer
from app.ui.git_toolbar import GitToolbar
from app.ui.log_panel import LogPanel
from app.ui.remotes_panel import RemotesPanel
from app.ui.repo_picker import RepoPicker
from app.ui.status_panel import StatusPanel
from app.ui.stash_panel import StashPanel
from app.ui.tags_panel import TagsPanel


class MainWindow(QMainWindow):
    """Main application window wiring controller state to UI widgets."""

    def __init__(
        self,
        controller: RepoController | None = None,
        runner: CommandRunner | None = None,
    ) -> None:
        super().__init__()
        if (controller is None) != (runner is None):
            raise ValueError("controller and runner must be provided together")

        if controller is None or runner is None:
            controller, runner = self._build_controller()

        self._controller = controller
        self._runner = runner
        self._state = controller.state
        self._last_error: Exception | None = None

        self._repo_picker = RepoPicker()
        self._status_panel = StatusPanel()
        self._commit_panel = CommitPanel()
        self._branches_panel = BranchesPanel()
        self._log_panel = LogPanel()
        self._stash_panel = StashPanel()
        self._tags_panel = TagsPanel()
        self._remotes_panel = RemotesPanel()
        self._diff_viewer = DiffViewer()
        self._console = ConsoleWidget()
        self._toolbar = GitToolbar()
        self._tabs = QTabWidget()

        self._setup_menu()
        self._setup_layout()
        self._wire_events()
        self._refresh_from_state()

    def _build_controller(self) -> tuple[RepoController, CommandRunner]:
        """Create the default CommandRunner/GitService/RepoController stack."""
        runner = CommandRunner()
        git_runner = GitRunner(runner)
        service = GitService(git_runner)
        controller = RepoController(service)
        return controller, runner

    def _setup_menu(self) -> None:
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Repository...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._repo_picker.browse_repo)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        settings_action = QAction("&Theme Editor...", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._open_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self._controller.refresh_status)
        view_menu.addAction(refresh_action)

    def _open_settings(self) -> None:
        """Open the theme editor dialog."""
        dialog = ThemeEditorDialog(self)
        dialog.exec()

    def _setup_layout(self) -> None:
        """Compose the main window layout with splitters."""
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.addToolBar(self._toolbar)

        status_tab = QWidget()
        status_layout = QVBoxLayout(status_tab)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_split = QSplitter(Qt.Vertical)
        status_split.addWidget(self._status_panel)
        status_split.addWidget(self._commit_panel)
        status_split.setStretchFactor(0, 3)
        status_split.setStretchFactor(1, 1)
        status_layout.addWidget(status_split)

        self._tabs.addTab(status_tab, "Changes")
        self._tabs.addTab(self._log_panel, "Log")
        self._tabs.addTab(self._branches_panel, "Branches")
        self._tabs.addTab(self._stash_panel, "Stashes")
        self._tabs.addTab(self._tags_panel, "Tags")
        self._tabs.addTab(self._remotes_panel, "Remotes")

        main_split = QSplitter(Qt.Horizontal)
        main_split.addWidget(self._tabs)
        main_split.addWidget(self._diff_viewer)
        main_split.setStretchFactor(0, 2)
        main_split.setStretchFactor(1, 3)

        outer_split = QSplitter(Qt.Vertical)
        outer_split.addWidget(main_split)
        outer_split.addWidget(self._console)
        outer_split.setStretchFactor(0, 3)
        outer_split.setStretchFactor(1, 1)

        layout.addWidget(self._repo_picker)
        layout.addWidget(outer_split)
        self.setCentralWidget(central)
        self.setWindowTitle("GitUI")
        self.resize(1100, 700)

    def _wire_events(self) -> None:
        """Connect UI signals to controller intents and runner output."""
        self._repo_picker.repo_opened.connect(self._controller.open_repo)
        self._status_panel.diff_requested.connect(self._controller.request_diff)
        self._status_panel.stage_requested.connect(self._controller.stage)
        self._status_panel.unstage_requested.connect(self._controller.unstage)
        self._status_panel.discard_requested.connect(self._confirm_discard)
        self._commit_panel.commit_requested.connect(self._controller.commit)

        self._branches_panel.refresh_requested.connect(self._controller.refresh_branches)
        self._branches_panel.switch_requested.connect(self._controller.switch_branch)
        self._branches_panel.create_requested.connect(self._controller.create_branch)
        self._branches_panel.delete_requested.connect(self._controller.delete_branch)
        self._branches_panel.set_upstream_requested.connect(self._controller.set_upstream)

        self._log_panel.refresh_requested.connect(self._controller.refresh_log)

        self._stash_panel.refresh_requested.connect(self._controller.refresh_stashes)
        self._stash_panel.save_requested.connect(self._controller.stash_save)
        self._stash_panel.apply_requested.connect(self._controller.stash_apply)
        self._stash_panel.pop_requested.connect(self._controller.stash_pop)
        self._stash_panel.drop_requested.connect(self._controller.stash_drop)

        self._tags_panel.refresh_requested.connect(self._controller.refresh_tags)
        self._tags_panel.create_requested.connect(self._controller.create_tag)
        self._tags_panel.delete_requested.connect(self._controller.delete_tag)
        self._tags_panel.push_tag_requested.connect(self._controller.push_tag)
        self._tags_panel.push_tags_requested.connect(self._controller.push_tags)

        self._remotes_panel.refresh_requested.connect(self._controller.refresh_remotes)
        self._remotes_panel.add_requested.connect(self._controller.add_remote)
        self._remotes_panel.remove_requested.connect(self._controller.remove_remote)
        self._remotes_panel.set_url_requested.connect(self._controller.set_remote_url)

        self._toolbar.refresh_requested.connect(self._controller.refresh_status)
        self._toolbar.stage_all_requested.connect(self._stage_all)
        self._toolbar.unstage_all_requested.connect(self._unstage_all)
        self._toolbar.discard_all_requested.connect(self._discard_all)
        self._toolbar.fetch_requested.connect(self._controller.fetch)
        self._toolbar.pull_requested.connect(self._controller.pull_ff_only)
        self._toolbar.push_requested.connect(self._controller.push)

        self._tabs.currentChanged.connect(self._on_tab_changed)
        self._state.state_changed.connect(self._refresh_from_state)

        # Log command lifecycle + output so users can see what git did.
        self._runner.command_started.connect(self._on_command_started)
        self._runner.command_stdout.connect(lambda _h, data: self._console.append_stdout(data))
        self._runner.command_stderr.connect(lambda _h, data: self._console.append_stderr(data))
        self._runner.command_finished.connect(self._on_command_finished)

    def _refresh_from_state(self) -> None:
        """Update widgets when RepoState changes."""
        self._repo_picker.set_repo_path(self._state.repo_path)
        self._status_panel.set_status(self._state.status)
        self._log_panel.set_commits(list(self._state.log or []))
        self._branches_panel.set_branches(list(self._state.branches or []))
        self._stash_panel.set_stashes(list(self._state.stashes or []))
        self._tags_panel.set_tags(list(self._state.tags or []))
        self._remotes_panel.set_remotes(list(self._state.remotes or []))
        self._diff_viewer.set_diff_text(self._state.diff_text)

        remotes = [remote.name for remote in self._state.remotes or []]
        self._branches_panel.set_remotes(remotes)
        self._tags_panel.set_remotes(remotes)

        title_suffix = self._state.repo_path or "(no repo)"
        self.setWindowTitle(f"GitUI - {title_suffix}")

        if self._state.last_error and self._state.last_error != self._last_error:
            self._console.append_event(f"error: {self._state.last_error}")
            self.statusBar().showMessage(str(self._state.last_error))
            if isinstance(self._state.last_error, CommandFailed):
                if self._maybe_handle_push_no_upstream(self._state.last_error):
                    self._last_error = self._state.last_error
                    return
            ErrorDialog.show_error(self, self._state.last_error)
            self._last_error = self._state.last_error
        elif self._state.last_error is None:
            self.statusBar().clearMessage()
            self._last_error = None

    def _on_command_started(self, handle: object) -> None:
        """Log command start events with argv for traceability."""
        run_handle = handle  # type: ignore[assignment]
        args = getattr(run_handle.spec, "args", None)
        command = " ".join(args) if args else "<command>"
        self._console.append_event(f"start: {command}")

    def _on_command_finished(self, handle: object, result: object) -> None:
        """Log command completion with exit code."""
        run_handle = handle  # type: ignore[assignment]
        cmd_result = result  # type: ignore[assignment]
        args = getattr(run_handle.spec, "args", None)
        command = " ".join(args) if args else "<command>"
        exit_code = getattr(cmd_result, "exit_code", "?")
        self._console.append_event(f"finish: {command} (exit {exit_code})")

    def _on_tab_changed(self, index: int) -> None:
        """Refresh data when a tab becomes active."""
        widget = self._tabs.widget(index)
        if widget is self._log_panel:
            self._controller.refresh_log()
        elif widget is self._branches_panel:
            self._controller.refresh_branches()
        elif widget is self._stash_panel:
            self._controller.refresh_stashes()
        elif widget is self._tags_panel:
            self._controller.refresh_tags()
        elif widget is self._remotes_panel:
            self._controller.refresh_remotes()

    def _stage_all(self) -> None:
        """Stage all unstaged and untracked files."""
        status = self._state.status
        if not status:
            return
        paths = [f.path for f in status.unstaged] + [f.path for f in status.untracked]
        if paths:
            self._controller.stage(paths)

    def _unstage_all(self) -> None:
        """Unstage all staged files."""
        status = self._state.status
        if not status:
            return
        paths = [f.path for f in status.staged]
        if paths:
            self._controller.unstage(paths)

    def _discard_all(self) -> None:
        """Discard all unstaged changes (excluding untracked files)."""
        status = self._state.status
        if not status:
            return
        if not ConfirmDialog.ask(
            self,
            "Discard Changes",
            "Discard all unstaged changes? This cannot be undone.",
            confirm_text="Discard",
        ):
            return
        paths = [f.path for f in status.unstaged]
        if paths:
            self._controller.discard(paths)

    def _confirm_discard(self, paths: list[str]) -> None:
        """Confirm before discarding selected changes."""
        if not paths:
            return
        if not ConfirmDialog.ask(
            self,
            "Discard Changes",
            f"Discard {len(paths)} selected change(s)? This cannot be undone.",
            confirm_text="Discard",
        ):
            return
        self._controller.discard(paths)

    def _maybe_handle_push_no_upstream(self, error: CommandFailed) -> bool:
        """Offer to set upstream and re-push when git reports missing upstream."""
        stderr = error.stderr.decode("utf-8", errors="replace").lower()
        if "no upstream branch" not in stderr:
            return False
        if "push" not in error.command_args:
            return False

        branch = self._current_branch_name()
        if not branch:
            return False
        remote = self._default_remote()

        if not ConfirmDialog.ask(
            self,
            "No Upstream",
            f"Branch '{branch}' has no upstream. Set upstream to "
            f"'{remote}/{branch}' and push now?",
            confirm_text="Set Upstream & Push",
        ):
            return True

        self._controller.push(set_upstream=True, remote=remote, branch=branch)
        return True

    def _current_branch_name(self) -> str | None:
        """Get the currently checked-out branch name, if known."""
        if self._state.status and self._state.status.branch:
            return self._state.status.branch.name
        for branch in self._state.branches or []:
            if branch.is_current:
                return branch.name
        return None

    def _default_remote(self) -> str:
        """Pick a default remote for upstream setup."""
        if self._state.remotes:
            return self._state.remotes[0].name
        return "origin"
