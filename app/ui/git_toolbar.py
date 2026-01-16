"""Toolbar with quick git actions."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QToolBar


class GitToolbar(QToolBar):
    """Quick-access toolbar for common git operations."""

    refresh_requested = Signal()
    stage_all_requested = Signal()
    unstage_all_requested = Signal()
    discard_all_requested = Signal()
    fetch_requested = Signal()
    pull_requested = Signal()
    push_requested = Signal()

    def __init__(self) -> None:
        super().__init__("Git Actions")
        self.setMovable(False)
        self._setup_actions()

    def _setup_actions(self) -> None:
        refresh = self.addAction("Refresh")
        refresh.setToolTip("Refresh status for the current repo")
        refresh.triggered.connect(self.refresh_requested.emit)

        self.addSeparator()

        stage_all = self.addAction("Stage All")
        stage_all.setToolTip("Stage all unstaged and untracked files")
        stage_all.triggered.connect(self.stage_all_requested.emit)

        unstage_all = self.addAction("Unstage All")
        unstage_all.setToolTip("Unstage all staged files")
        unstage_all.triggered.connect(self.unstage_all_requested.emit)

        discard_all = self.addAction("Discard")
        discard_all.setToolTip("Discard all unstaged changes")
        discard_all.triggered.connect(self.discard_all_requested.emit)

        self.addSeparator()

        fetch = self.addAction("Fetch")
        fetch.setToolTip("Fetch updates from remotes")
        fetch.triggered.connect(self.fetch_requested.emit)

        pull = self.addAction("Pull")
        pull.setToolTip("Pull with fast-forward only")
        pull.triggered.connect(self.pull_requested.emit)

        push = self.addAction("Push")
        push.setToolTip("Push to the current upstream")
        push.triggered.connect(self.push_requested.emit)
