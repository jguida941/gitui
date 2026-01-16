from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, QToolButton, QWidget


class RepoPicker(QWidget):
    """Collects a repo path and emits a request to open it."""

    repo_opened = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText("Path to repository")

        self._browse_button = QToolButton()
        self._browse_button.setText("…")

        self._open_button = QPushButton("Open")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._path_edit)
        layout.addWidget(self._browse_button)
        layout.addWidget(self._open_button)

        self._browse_button.clicked.connect(self._browse)
        self._open_button.clicked.connect(self._emit_open)

    def set_repo_path(self, path: str | None) -> None:
        """Update the text field when the controller accepts a path."""
        self._path_edit.setText(path or "")

    def _emit_open(self) -> None:
        """Emit the repo path when the user clicks Open."""
        path = self._path_edit.text().strip()
        if path:
            self.repo_opened.emit(path)

    def _browse(self) -> None:
        """Open a directory picker for convenience."""
        path = QFileDialog.getExistingDirectory(self, "Select Repository")
        if path:
            self._path_edit.setText(path)
