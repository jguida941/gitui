"""Stash panel for listing and applying stash entries."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
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

from app.core.models import StashEntry


class StashPanel(QWidget):
    """Shows stashes and emits stash intent signals."""

    refresh_requested = Signal()
    save_requested = Signal(object, bool)
    apply_requested = Signal(object)
    pop_requested = Signal(object)
    drop_requested = Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Ref", "Summary", "Date"])
        self._tree.itemSelectionChanged.connect(self._on_selection_changed)

        self._stash_combo = QComboBox()
        self._stash_combo.setToolTip("Select a stash entry")

        self._message = QLineEdit()
        self._message.setPlaceholderText("Optional stash message")

        self._include_untracked = QCheckBox("Include untracked")

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh_requested.emit)
        header.addWidget(QLabel("Stashes"))
        header.addStretch()
        header.addWidget(refresh)
        layout.addLayout(header)
        layout.addWidget(self._tree)

        actions = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions)

        save_row = QHBoxLayout()
        save_row.addWidget(QLabel("Message"))
        save_row.addWidget(self._message, 1)
        save_row.addWidget(self._include_untracked)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._emit_save)
        save_row.addWidget(save_btn)
        actions_layout.addLayout(save_row)

        use_row = QHBoxLayout()
        use_row.addWidget(QLabel("Stash"))
        use_row.addWidget(self._stash_combo, 1)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._emit_apply)
        pop_btn = QPushButton("Pop")
        pop_btn.clicked.connect(self._emit_pop)
        drop_btn = QPushButton("Drop")
        drop_btn.clicked.connect(self._emit_drop)
        use_row.addWidget(apply_btn)
        use_row.addWidget(pop_btn)
        use_row.addWidget(drop_btn)
        actions_layout.addLayout(use_row)

        layout.addWidget(actions)

    def set_stashes(self, stashes: list[StashEntry] | None) -> None:
        """Populate stash list and dropdown."""
        self._tree.clear()
        self._stash_combo.clear()

        self._stash_combo.addItem("Latest", None)
        for stash in stashes or []:
            item = QTreeWidgetItem([stash.selector, stash.summary, stash.date])
            item.setData(0, Qt.UserRole, stash.selector)
            self._tree.addTopLevelItem(item)
            self._stash_combo.addItem(stash.selector, stash.selector)

    def _on_selection_changed(self) -> None:
        items = self._tree.selectedItems()
        if not items:
            return
        ref = items[0].data(0, Qt.UserRole)
        if ref:
            self._stash_combo.setCurrentText(ref)

    def _emit_save(self) -> None:
        message = self._message.text().strip() or None
        include_untracked = self._include_untracked.isChecked()
        self.save_requested.emit(message, include_untracked)
        self._message.clear()
        self._include_untracked.setChecked(False)

    def _emit_apply(self) -> None:
        ref = self._stash_combo.currentData()
        self.apply_requested.emit(ref)

    def _emit_pop(self) -> None:
        ref = self._stash_combo.currentData()
        self.pop_requested.emit(ref)

    def _emit_drop(self) -> None:
        ref = self._stash_combo.currentData()
        self.drop_requested.emit(ref)
