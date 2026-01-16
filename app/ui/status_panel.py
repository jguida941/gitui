from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGroupBox, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from app.core.models import FileChange, RepoStatus


class StatusPanel(QWidget):
    """Displays staged/unstaged/untracked status groups."""

    diff_requested = Signal(str, bool)

    def __init__(self) -> None:
        super().__init__()
        self._staged_group, self._staged_list = self._make_group("Staged")
        self._unstaged_group, self._unstaged_list = self._make_group("Unstaged")
        self._untracked_group, self._untracked_list = self._make_group("Untracked")
        self._conflicted_group, self._conflicted_list = self._make_group("Conflicted")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._staged_group)
        layout.addWidget(self._unstaged_group)
        layout.addWidget(self._untracked_group)
        layout.addWidget(self._conflicted_group)
        layout.addStretch()

        # Only staged/unstaged lists trigger diffs; others are read-only for now.
        self._staged_list.itemSelectionChanged.connect(
            lambda: self._on_selection(self._staged_list, staged=True, allow_diff=True)
        )
        self._unstaged_list.itemSelectionChanged.connect(
            lambda: self._on_selection(self._unstaged_list, staged=False, allow_diff=True)
        )
        self._untracked_list.itemSelectionChanged.connect(
            lambda: self._on_selection(self._untracked_list, staged=False, allow_diff=False)
        )
        self._conflicted_list.itemSelectionChanged.connect(
            lambda: self._on_selection(self._conflicted_list, staged=False, allow_diff=False)
        )

    def set_status(self, status: RepoStatus | None) -> None:
        """Populate lists based on the latest RepoStatus snapshot."""
        if status is None:
            self._clear_all()
            return

        self._populate(self._staged_list, status.staged)
        self._populate(self._unstaged_list, status.unstaged)
        self._populate(self._untracked_list, status.untracked)
        self._populate(self._conflicted_list, status.conflicted)

        self._staged_group.setTitle(f"Staged ({len(status.staged)})")
        self._unstaged_group.setTitle(f"Unstaged ({len(status.unstaged)})")
        self._untracked_group.setTitle(f"Untracked ({len(status.untracked)})")
        self._conflicted_group.setTitle(f"Conflicted ({len(status.conflicted)})")

    def _make_group(self, title: str) -> tuple[QGroupBox, QListWidget]:
        """Create a labeled list group for a status bucket."""
        group = QGroupBox(title)
        list_widget = QListWidget()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(list_widget)
        return group, list_widget

    def _populate(self, list_widget: QListWidget, items: list[FileChange]) -> None:
        """Fill a list widget with file paths, storing path in item data."""
        list_widget.clear()
        for change in items:
            item = QListWidgetItem(change.path)
            item.setData(Qt.UserRole, change.path)
            list_widget.addItem(item)

    def _clear_all(self) -> None:
        """Clear all list widgets when no status is available."""
        for widget in (self._staged_list, self._unstaged_list, self._untracked_list, self._conflicted_list):
            widget.clear()

    def _on_selection(self, source: QListWidget, staged: bool, allow_diff: bool) -> None:
        """Emit diff requests and clear selections in other buckets."""
        if not source.selectedItems():
            return

        for widget in (self._staged_list, self._unstaged_list, self._untracked_list, self._conflicted_list):
            if widget is source:
                continue
            widget.blockSignals(True)
            widget.clearSelection()
            widget.blockSignals(False)

        if not allow_diff:
            return

        item = source.selectedItems()[0]
        path = item.data(Qt.UserRole)
        if path:
            self.diff_requested.emit(path, staged)
