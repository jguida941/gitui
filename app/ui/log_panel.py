"""Commit history panel with a simple table view."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.models import Commit


class LogPanel(QWidget):
    """Displays recent commits and emits refresh intent."""

    refresh_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Hash", "Subject", "Author", "Date"])
        self._table.setSortingEnabled(True)

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_requested.emit)
        header.addWidget(QLabel("Commit History"))
        header.addStretch()
        header.addWidget(refresh)
        layout.addLayout(header)
        layout.addWidget(self._table)

    def set_commits(self, commits: list[Commit] | None) -> None:
        """Populate the table with commit metadata."""
        rows = commits or []
        self._table.setRowCount(len(rows))
        for row, commit in enumerate(rows):
            self._table.setItem(row, 0, QTableWidgetItem(commit.oid[:8]))
            self._table.setItem(row, 1, QTableWidgetItem(commit.subject))
            self._table.setItem(row, 2, QTableWidgetItem(commit.author_name))
            self._table.setItem(row, 3, QTableWidgetItem(commit.author_date))
