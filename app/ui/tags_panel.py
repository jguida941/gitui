"""Tags panel with list and tag actions."""

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

from app.core.models import Tag


class TagsPanel(QWidget):
    """Shows tags and emits tag-related intents."""

    refresh_requested = Signal()
    create_requested = Signal(str, object)
    delete_requested = Signal(str)
    push_tag_requested = Signal(str, str)
    push_tags_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Tag"])
        self._tree.itemSelectionChanged.connect(self._on_selection_changed)

        self._tag_combo = QComboBox()
        self._tag_combo.setToolTip("Select a tag")

        self._new_tag = QLineEdit()
        self._new_tag.setPlaceholderText("v1.0.0")

        self._ref = QLineEdit()
        self._ref.setPlaceholderText("Optional ref (commit, branch)")

        self._remote_combo = QComboBox()
        self._remote_combo.addItem("origin")

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_requested.emit)
        header.addWidget(QLabel("Tags"))
        header.addStretch()
        header.addWidget(refresh)
        layout.addLayout(header)
        layout.addWidget(self._tree)

        actions = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions)

        create_row = QHBoxLayout()
        create_row.addWidget(QLabel("New Tag"))
        create_row.addWidget(self._new_tag, 1)
        create_row.addWidget(QLabel("Ref"))
        create_row.addWidget(self._ref, 1)
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self._emit_create)
        create_row.addWidget(create_btn)
        actions_layout.addLayout(create_row)

        tag_row = QHBoxLayout()
        tag_row.addWidget(QLabel("Tag"))
        tag_row.addWidget(self._tag_combo, 1)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._emit_delete)
        tag_row.addWidget(delete_btn)
        actions_layout.addLayout(tag_row)

        push_row = QHBoxLayout()
        push_row.addWidget(QLabel("Remote"))
        push_row.addWidget(self._remote_combo)
        push_btn = QPushButton("Push Tag")
        push_btn.clicked.connect(self._emit_push_tag)
        push_all_btn = QPushButton("Push All")
        push_all_btn.clicked.connect(self._emit_push_all)
        push_row.addWidget(push_btn)
        push_row.addWidget(push_all_btn)
        actions_layout.addLayout(push_row)

        layout.addWidget(actions)

    def set_tags(self, tags: list[Tag] | None) -> None:
        """Populate tag list and dropdown."""
        self._tree.clear()
        self._tag_combo.clear()
        for tag in tags or []:
            item = QTreeWidgetItem([tag.name])
            item.setData(0, Qt.UserRole, tag.name)
            self._tree.addTopLevelItem(item)
            self._tag_combo.addItem(tag.name)

    def set_remotes(self, remotes: list[str]) -> None:
        """Update the remote dropdown for tag pushing."""
        self._remote_combo.clear()
        self._remote_combo.addItems(remotes or ["origin"])

    def _on_selection_changed(self) -> None:
        items = self._tree.selectedItems()
        if not items:
            return
        name = items[0].data(0, Qt.UserRole)
        if name:
            self._tag_combo.setCurrentText(name)

    def _emit_create(self) -> None:
        name = self._new_tag.text().strip()
        ref = self._ref.text().strip() or None
        if name:
            self.create_requested.emit(name, ref)
            self._new_tag.clear()
            self._ref.clear()

    def _emit_delete(self) -> None:
        name = self._tag_combo.currentText()
        if name:
            self.delete_requested.emit(name)

    def _emit_push_tag(self) -> None:
        name = self._tag_combo.currentText()
        remote = self._remote_combo.currentText() or "origin"
        if name:
            self.push_tag_requested.emit(name, remote)

    def _emit_push_all(self) -> None:
        remote = self._remote_combo.currentText() or "origin"
        self.push_tags_requested.emit(remote)
