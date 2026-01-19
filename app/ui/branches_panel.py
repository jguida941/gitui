"""Branches panel with list and actions."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.models import Branch, RemoteBranch


class BranchesPanel(QWidget):
    """Displays branches and emits branch-related intents."""

    refresh_requested = Signal()
    switch_requested = Signal(str)
    create_requested = Signal(str, str)
    delete_requested = Signal(str, bool)
    set_upstream_requested = Signal(str, object)
    delete_remote_requested = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self._branches: list[Branch] = []
        self._remote_branches: list[RemoteBranch] = []
        self._remotes: list[str] = []

        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Branch", "Upstream", "Ahead", "Behind", "Gone"])
        self._tree.itemSelectionChanged.connect(self._on_selection_changed)

        self._remote_tree = QTreeWidget()
        self._remote_tree.setHeaderLabels(["Remote", "Branch"])
        self._remote_tree.itemSelectionChanged.connect(
            self._on_remote_selection_changed
        )

        self._branch_combo = QComboBox()
        self._branch_combo.setToolTip("Select a branch for actions")

        self._start_point_combo = QComboBox()
        self._start_point_combo.setToolTip("Start point for new branches")

        self._new_branch = QLineEdit()
        self._new_branch.setPlaceholderText("new-branch-name")

        self._upstream_combo = QComboBox()
        self._upstream_combo.setToolTip("Upstream (remote/branch)")

        self._remote_branch_combo = QComboBox()
        self._remote_branch_combo.setToolTip("Select a remote branch to delete")

        self._force_delete = QComboBox()
        self._force_delete.addItems(["Delete", "Force Delete"])

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_requested.emit)
        header.addWidget(QLabel("Branches"))
        header.addStretch()
        header.addWidget(refresh)
        layout.addLayout(header)
        layout.addWidget(self._tree)

        remote_group = QGroupBox("Remote Branches")
        remote_layout = QVBoxLayout(remote_group)
        remote_layout.addWidget(self._remote_tree)
        remote_actions = QHBoxLayout()
        remote_actions.addWidget(QLabel("Remote"))
        remote_actions.addWidget(self._remote_branch_combo, 1)
        delete_remote = QPushButton("Delete Remote")
        delete_remote.clicked.connect(self._emit_delete_remote)
        remote_actions.addWidget(delete_remote)
        remote_layout.addLayout(remote_actions)
        layout.addWidget(remote_group)

        actions = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions)

        row = QHBoxLayout()
        row.addWidget(QLabel("Branch"))
        row.addWidget(self._branch_combo, 1)
        switch = QPushButton("Switch")
        switch.clicked.connect(self._emit_switch)
        row.addWidget(switch)
        actions_layout.addLayout(row)

        create_row = QHBoxLayout()
        create_row.addWidget(QLabel("New"))
        create_row.addWidget(self._new_branch, 1)
        create_row.addWidget(QLabel("From"))
        create_row.addWidget(self._start_point_combo, 1)
        create = QPushButton("Create")
        create.clicked.connect(self._emit_create)
        create_row.addWidget(create)
        actions_layout.addLayout(create_row)

        delete_row = QHBoxLayout()
        delete_row.addWidget(QLabel("Delete"))
        delete_row.addWidget(self._branch_combo, 1)
        delete_row.addWidget(self._force_delete)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._emit_delete)
        delete_row.addWidget(delete_btn)
        actions_layout.addLayout(delete_row)

        upstream_row = QHBoxLayout()
        upstream_row.addWidget(QLabel("Upstream"))
        upstream_row.addWidget(self._upstream_combo, 1)
        upstream_btn = QPushButton("Set Upstream")
        upstream_btn.clicked.connect(self._emit_set_upstream)
        upstream_row.addWidget(upstream_btn)
        actions_layout.addLayout(upstream_row)

        layout.addWidget(actions)

    def set_branches(self, branches: list[Branch] | None) -> None:
        """Populate the branch list and dropdowns."""
        self._branches = list(branches or [])
        self._tree.clear()

        current_branch = self._branch_combo.currentText()
        current_upstream = self._upstream_combo.currentText()

        for branch in self._branches:
            item = QTreeWidgetItem(
                [
                    ("* " if branch.is_current else "") + branch.name,
                    branch.upstream or "",
                    str(branch.ahead),
                    str(branch.behind),
                    "yes" if branch.gone else "",
                ]
            )
            item.setData(0, Qt.UserRole, branch.name)
            self._tree.addTopLevelItem(item)

        branch_names = [b.name for b in self._branches]
        self._branch_combo.clear()
        self._branch_combo.addItems(branch_names)
        if current_branch in branch_names:
            self._branch_combo.setCurrentText(current_branch)

        self._start_point_combo.clear()
        self._start_point_combo.addItems(["HEAD", *branch_names])

        self._rebuild_upstream(branch_names)
        if current_upstream:
            self._upstream_combo.setCurrentText(current_upstream)

    def set_remotes(self, remotes: list[str]) -> None:
        """Update the remotes used for upstream suggestions."""
        self._remotes = remotes
        branch_names = [b.name for b in self._branches]
        current_upstream = self._upstream_combo.currentText()
        self._rebuild_upstream(branch_names)
        if current_upstream:
            self._upstream_combo.setCurrentText(current_upstream)

    def set_remote_branches(self, branches: list[RemoteBranch] | None) -> None:
        """Populate the remote branch list and dropdown."""
        self._remote_branches = list(branches or [])
        self._remote_tree.clear()

        current_remote = self._remote_branch_combo.currentData()
        self._remote_branch_combo.clear()

        for branch in self._remote_branches:
            item = QTreeWidgetItem([branch.remote, branch.name])
            item.setData(0, Qt.UserRole, (branch.remote, branch.name))
            self._remote_tree.addTopLevelItem(item)
            self._remote_branch_combo.addItem(
                branch.full_name, (branch.remote, branch.name)
            )

        if current_remote:
            index = self._remote_branch_combo.findData(current_remote)
            if index >= 0:
                self._remote_branch_combo.setCurrentIndex(index)

    def _rebuild_upstream(self, branch_names: list[str]) -> None:
        # Build upstream options from remotes + branch names for quick selection.
        self._upstream_combo.clear()
        remotes = self._remotes or ["origin"]
        for remote in remotes:
            for branch in branch_names:
                self._upstream_combo.addItem(f"{remote}/{branch}")

    def _on_selection_changed(self) -> None:
        items = self._tree.selectedItems()
        if not items:
            return
        name = items[0].data(0, Qt.UserRole)
        if name:
            self._branch_combo.setCurrentText(name)

    def _on_remote_selection_changed(self) -> None:
        items = self._remote_tree.selectedItems()
        if not items:
            return
        data = items[0].data(0, Qt.UserRole)
        if data:
            index = self._remote_branch_combo.findData(data)
            if index >= 0:
                self._remote_branch_combo.setCurrentIndex(index)

    def _emit_switch(self) -> None:
        name = self._branch_combo.currentText()
        if name:
            self.switch_requested.emit(name)

    def _emit_create(self) -> None:
        name = self._new_branch.text().strip()
        start_point = self._start_point_combo.currentText() or "HEAD"
        if name:
            self.create_requested.emit(name, start_point)
            self._new_branch.clear()

    def _emit_delete(self) -> None:
        name = self._branch_combo.currentText()
        if name:
            force = self._force_delete.currentText() == "Force Delete"
            self.delete_requested.emit(name, force)

    def _emit_set_upstream(self) -> None:
        upstream = self._upstream_combo.currentText()
        branch = self._branch_combo.currentText() or None
        if upstream:
            self.set_upstream_requested.emit(upstream, branch)

    def _emit_delete_remote(self) -> None:
        data = self._remote_branch_combo.currentData()
        if not data:
            return
        remote, name = data
        if remote and name:
            self.delete_remote_requested.emit(remote, name)
