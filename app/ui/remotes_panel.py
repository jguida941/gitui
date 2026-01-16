"""Remotes panel for managing git remotes."""
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

from app.core.models import Remote


class RemotesPanel(QWidget):
    """Shows remotes and emits add/remove/update intents."""

    refresh_requested = Signal()
    add_requested = Signal(str, str)
    remove_requested = Signal(str)
    set_url_requested = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Remote", "Fetch URL", "Push URL"])
        self._tree.itemSelectionChanged.connect(self._on_selection_changed)

        self._remote_combo = QComboBox()
        self._remote_combo.setToolTip("Select a remote")

        self._name = QLineEdit()
        self._name.setPlaceholderText("origin")

        self._url = QLineEdit()
        self._url.setPlaceholderText("https://github.com/user/repo.git")

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_requested.emit)
        header.addWidget(QLabel("Remotes"))
        header.addStretch()
        header.addWidget(refresh)
        layout.addLayout(header)
        layout.addWidget(self._tree)

        actions = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions)

        add_row = QHBoxLayout()
        add_row.addWidget(QLabel("Name"))
        add_row.addWidget(self._name, 1)
        add_row.addWidget(QLabel("URL"))
        add_row.addWidget(self._url, 2)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self._emit_add)
        add_row.addWidget(add_btn)
        actions_layout.addLayout(add_row)

        edit_row = QHBoxLayout()
        edit_row.addWidget(QLabel("Remote"))
        edit_row.addWidget(self._remote_combo, 1)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self._emit_remove)
        set_url_btn = QPushButton("Set URL")
        set_url_btn.clicked.connect(self._emit_set_url)
        edit_row.addWidget(remove_btn)
        edit_row.addWidget(set_url_btn)
        actions_layout.addLayout(edit_row)

        layout.addWidget(actions)

    def set_remotes(self, remotes: list[Remote] | None) -> None:
        """Populate remote list and dropdown."""
        self._tree.clear()
        self._remote_combo.clear()

        for remote in remotes or []:
            item = QTreeWidgetItem(
                [remote.name, remote.fetch_url or "", remote.push_url or ""]
            )
            item.setData(0, Qt.UserRole, remote.name)
            self._tree.addTopLevelItem(item)
            self._remote_combo.addItem(remote.name)

    def _on_selection_changed(self) -> None:
        items = self._tree.selectedItems()
        if not items:
            return
        name = items[0].data(0, Qt.UserRole)
        if name:
            self._remote_combo.setCurrentText(name)

    def _emit_add(self) -> None:
        name = self._name.text().strip()
        url = self._url.text().strip()
        if name and url:
            self.add_requested.emit(name, url)
            self._name.clear()
            self._url.clear()

    def _emit_remove(self) -> None:
        name = self._remote_combo.currentText()
        if name:
            self.remove_requested.emit(name)

    def _emit_set_url(self) -> None:
        name = self._remote_combo.currentText()
        url = self._url.text().strip()
        if name and url:
            self.set_url_requested.emit(name, url)
