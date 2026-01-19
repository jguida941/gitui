from __future__ import annotations

import argparse
import sys

from app.core.controller import RepoController
from app.exec.command_runner import CommandRunner
from app.git.git_runner import GitRunner
from app.git.git_service import GitService


def build_controller() -> tuple[RepoController, CommandRunner]:
    """Construct the core runner/service/controller stack."""
    runner = CommandRunner()
    git_runner = GitRunner(runner)
    service = GitService(git_runner)
    controller = RepoController(service)
    return controller, runner


def main(argv: list[str] | None = None) -> int:
    """Launch the GUI unless explicitly disabled for tests."""
    parser = argparse.ArgumentParser(description="GitUI (PySide6)")
    parser.add_argument("--repo", help="Open a repo path on launch.")
    parser.add_argument(
        "--no-gui", action="store_true", help="Exit without launching Qt."
    )
    args = parser.parse_args(argv)

    if args.no_gui:
        return 0

    from PySide6.QtWidgets import QApplication

    from app.ui.main_window import MainWindow
    from app.ui.theme.theme_engine import init_theme

    app = QApplication(sys.argv)

    # Load saved theme preferences and apply stylesheet.
    init_theme()

    controller, runner = build_controller()
    window = MainWindow(controller, runner)

    if args.repo:
        controller.open_repo(args.repo)

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
