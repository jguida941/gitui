"""Error dialog for surfacing git failures to the user."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QPlainTextEdit,
    QVBoxLayout,
    QLabel,
    QWidget,
)

from app.core.errors import CommandFailed


class ErrorDialog(QDialog):
    """Dialog that displays error details in a readable format."""

    def __init__(self, error: Exception, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("GitUI Error")
        self.setMinimumSize(620, 360)

        layout = QVBoxLayout(self)

        summary = QLabel(str(error))
        summary.setWordWrap(True)
        layout.addWidget(summary)

        details = QPlainTextEdit()
        details.setReadOnly(True)
        details.setLineWrapMode(QPlainTextEdit.NoWrap)
        details.setPlainText(self._format_details(error))
        layout.addWidget(details, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def show_error(parent: QWidget | None, error: Exception) -> None:
        """Open the error dialog modally."""
        dialog = ErrorDialog(error, parent)
        dialog.exec()

    def _format_details(self, error: Exception) -> str:
        """Format detailed error output for diagnostics."""
        if isinstance(error, CommandFailed):
            stdout = error.stdout.decode("utf-8", errors="replace")
            stderr = error.stderr.decode("utf-8", errors="replace")
            return (
                f"Command: {' '.join(error.command_args)}\n"
                f"Exit code: {error.exit_code}\n\n"
                f"STDOUT:\n{stdout}\n\n"
                f"STDERR:\n{stderr}"
            )
        return repr(error)
