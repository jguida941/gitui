from __future__ import annotations

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget


class ConsoleWidget(QWidget):
    """Scrollback console for command output."""

    def __init__(self) -> None:
        super().__init__()
        self._view = QPlainTextEdit()
        self._view.setReadOnly(True)
        self._view.setLineWrapMode(QPlainTextEdit.NoWrap)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._view)

    def append_event(self, message: str) -> None:
        """Log command lifecycle events (start/finish)."""
        self._append_line(f"[event] {message}")

    def append_stdout(self, data: bytes) -> None:
        """Append stdout bytes from a running command."""
        self._append_prefixed_lines("out", data)

    def append_stderr(self, data: bytes) -> None:
        """Append stderr bytes from a running command."""
        self._append_prefixed_lines("err", data)

    def clear(self) -> None:
        """Clear the console buffer."""
        self._view.clear()

    def _append_prefixed_lines(self, prefix: str, data: bytes) -> None:
        """Decode bytes and append each line with a stable prefix."""
        text = data.decode("utf-8", errors="replace")
        if not text:
            return
        for line in text.splitlines():
            self._append_line(f"[{prefix}] {line}")

    def _append_line(self, line: str) -> None:
        """Append a line and keep the view scrolled to the end."""
        self._view.appendPlainText(line)
        self._view.moveCursor(QTextCursor.End)
