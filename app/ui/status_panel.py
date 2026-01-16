from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from app.core.models import FileChange, RepoStatus


class StatusPanel(QWidget):
    """Displays staged/unstaged/untracked status groups."""

    diff_requested = Signal(str, bool)
    stage_requested = Signal(object)
    unstage_requested = Signal(object)
    discard_requested = Signal(object)

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

        self._wire_context_menus()

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
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(list_widget)
        return group, list_widget

    def _wire_context_menus(self) -> None:
        """Attach right-click menus to each status list."""
        menu_map = {
            "staged": self._staged_list,
            "unstaged": self._unstaged_list,
            "untracked": self._untracked_list,
            "conflicted": self._conflicted_list,
        }
        for status, widget in menu_map.items():
            widget.setProperty("gitStatus", status)
            widget.setContextMenuPolicy(Qt.CustomContextMenu)
            widget.customContextMenuRequested.connect(
                lambda pos, w=widget, s=status: self._show_context_menu(w, s, pos)
            )

    def _selected_paths(self, widget: QListWidget) -> list[str]:
        """Extract selected file paths from a list widget."""
        paths: list[str] = []
        for item in widget.selectedItems():
            path = item.data(Qt.UserRole)
            if path:
                paths.append(path)
        return paths

    def _show_context_menu(self, widget: QListWidget, status: str, pos) -> None:
        """Build context menu entries based on status bucket."""
        paths = self._selected_paths(widget)
        if not paths:
            return

        menu = QMenu(self)
        if status in {"unstaged", "untracked"}:
            stage_action = menu.addAction("Stage")
            diff_action = menu.addAction("View Diff")
            discard_action = None
            # Untracked files are removed via git clean, so we skip discard here.
            if status == "unstaged":
                discard_action = menu.addAction("Discard")
        elif status == "staged":
            stage_action = None
            diff_action = menu.addAction("View Diff")
            discard_action = menu.addAction("Unstage")
        else:
            stage_action = None
            diff_action = None
            discard_action = None

        action = menu.exec(widget.mapToGlobal(pos))
        if action is None:
            return

        if action == stage_action:
            self.stage_requested.emit(paths)
        elif action == discard_action and status == "staged":
            self.unstage_requested.emit(paths)
        elif action == discard_action:
            self.discard_requested.emit(paths)
        elif action == diff_action:
            self.diff_requested.emit(paths[0], status == "staged")

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
