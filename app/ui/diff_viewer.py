from __future__ import annotations

from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget


class DiffViewer(QWidget):
    """Read-only view for diff text."""

    def __init__(self) -> None:
        super().__init__()
        self._view = QPlainTextEdit()
        self._view.setReadOnly(True)
        self._view.setLineWrapMode(QPlainTextEdit.NoWrap)
        # Tag this widget so the theme engine can target diff styling.
        self._view.setProperty("diffViewer", True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._view)

    def set_diff_text(self, diff_text: str | None) -> None:
        """Update the diff display with the latest text."""
        self._view.setPlainText(diff_text or "")
