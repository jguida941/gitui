from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QWidget

from app.core.controller import RepoController
from app.core.repo_state import RepoState
from app.exec.command_runner import CommandRunner
from app.git.git_runner import GitRunner
from app.git.git_service import GitService
from app.ui.console_widget import ConsoleWidget
from app.ui.diff_viewer import DiffViewer
from app.ui.repo_picker import RepoPicker
from app.ui.status_panel import StatusPanel


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
        self._diff_viewer = DiffViewer()
        self._console = ConsoleWidget()

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

    def _setup_layout(self) -> None:
        """Compose the main window layout with splitters."""
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        main_split = QSplitter(Qt.Horizontal)
        main_split.addWidget(self._status_panel)
        main_split.addWidget(self._diff_viewer)
        main_split.setStretchFactor(1, 1)

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
        self._diff_viewer.set_diff_text(self._state.diff_text)

        title_suffix = self._state.repo_path or "(no repo)"
        self.setWindowTitle(f"GitUI - {title_suffix}")

        if self._state.last_error and self._state.last_error != self._last_error:
            self._console.append_event(f"error: {self._state.last_error}")
            self.statusBar().showMessage(str(self._state.last_error))
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
