"""Commit message panel with templates and amend toggle."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CommitPanel(QWidget):
    """Collects commit message input and emits commit intent signals."""

    commit_requested = Signal(str, bool)

    def __init__(self) -> None:
        super().__init__()
        self._message = QPlainTextEdit()
        self._message.setPlaceholderText("Write a commit message...")
        self._message.textChanged.connect(self._update_state)

        self._template_combo = QComboBox()
        self._template_combo.addItems(
            ["Template...", "feat:", "fix:", "docs:", "refactor:", "test:", "chore:"]
        )
        self._template_combo.currentTextChanged.connect(self._apply_template)

        self._amend = QCheckBox("Amend last commit")
        self._count = QLabel("0 chars")

        self._commit_btn = QPushButton("Commit")
        self._commit_btn.setProperty("primary", True)
        self._commit_btn.clicked.connect(self._emit_commit)
        self._commit_btn.setEnabled(False)

        self._setup_ui()

    def _setup_ui(self) -> None:
        group = QGroupBox("Commit")
        layout = QVBoxLayout(group)

        template_row = QHBoxLayout()
        template_row.addWidget(QLabel("Template"))
        template_row.addWidget(self._template_combo, 1)
        template_row.addStretch()
        layout.addLayout(template_row)

        layout.addWidget(self._message)

        footer = QHBoxLayout()
        footer.addWidget(self._amend)
        footer.addStretch()
        footer.addWidget(self._count)
        footer.addWidget(self._commit_btn)
        layout.addLayout(footer)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(group)

    def _apply_template(self, text: str) -> None:
        # Only auto-insert a template if the message is empty.
        if text == "Template...":
            return
        if not self._message.toPlainText().strip():
            self._message.setPlainText(f"{text} ")
            cursor = self._message.textCursor()
            cursor.movePosition(QTextCursor.End)
            self._message.setTextCursor(cursor)

    def _emit_commit(self) -> None:
        message = self._message.toPlainText().strip()
        if not message:
            return
        self.commit_requested.emit(message, self._amend.isChecked())

    def _update_state(self) -> None:
        message = self._message.toPlainText().strip()
        self._commit_btn.setEnabled(bool(message))
        self._count.setText(f"{len(message)} chars")

    def clear(self) -> None:
        """Clear the commit message field after a successful commit."""
        self._message.clear()
        self._amend.setChecked(False)
        self._template_combo.setCurrentIndex(0)
