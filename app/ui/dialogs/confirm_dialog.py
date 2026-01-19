"""Confirmation dialog for destructive actions."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout, QWidget


class ConfirmDialog(QDialog):
    """Simple yes/no confirmation dialog."""

    def __init__(
        self,
        title: str,
        message: str,
        parent: QWidget | None = None,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(420, 160)

        layout = QVBoxLayout(self)
        label = QLabel(message)
        label.setWordWrap(True)
        layout.addWidget(label)

        buttons = QDialogButtonBox()
        confirm = buttons.addButton(
            confirm_text, QDialogButtonBox.ButtonRole.AcceptRole
        )
        cancel = buttons.addButton(cancel_text, QDialogButtonBox.ButtonRole.RejectRole)
        confirm.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def ask(
        parent: QWidget | None,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
    ) -> bool:
        """Open a modal confirmation dialog and return True on confirm."""
        dialog = ConfirmDialog(title, message, parent, confirm_text, cancel_text)
        return dialog.exec() == QDialog.Accepted
