from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QDialog

from app.core.errors import CommandFailed
from app.ui.dialogs.confirm_dialog import ConfirmDialog
from app.ui.dialogs.error_dialog import ErrorDialog

app = QApplication.instance() or QApplication([])


def test_error_dialog_formats_command_failed() -> None:
    err = CommandFailed(["git", "status"], 1, b"out", b"err")
    dialog = ErrorDialog(err)
    details = dialog._format_details(err)
    assert "Exit code" in details


def test_confirm_dialog_ask(monkeypatch) -> None:
    monkeypatch.setattr(
        ConfirmDialog, "exec", lambda *_args, **_kwargs: QDialog.Accepted
    )
    assert ConfirmDialog.ask(None, "Confirm", "Proceed?") is True
