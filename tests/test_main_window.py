from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.core.errors import CommandFailed
from app.core.models import Branch, BranchInfo, Remote, RepoStatus
from app.core.repo_state import RepoState
from app.ui.dialogs.confirm_dialog import ConfirmDialog
from app.ui.main_window import MainWindow

app = QApplication.instance() or QApplication([])


class DummySignal:
    def __init__(self) -> None:
        self._handlers: list = []

    def connect(self, callback) -> None:
        self._handlers.append(callback)

    def emit(self, *args, **kwargs) -> None:
        for handler in self._handlers:
            handler(*args, **kwargs)


class DummyRunner:
    def __init__(self) -> None:
        self.command_started = DummySignal()
        self.command_stdout = DummySignal()
        self.command_stderr = DummySignal()
        self.command_finished = DummySignal()


class FakeController:
    def __init__(self) -> None:
        self.state = RepoState()
        self.calls: list[tuple[str, tuple, dict]] = []

    def __getattr__(self, name: str):
        def _noop(*args, **kwargs):
            self.calls.append((name, args, kwargs))

        return _noop

    def push(self, *args, **kwargs) -> None:  # type: ignore[override]
        self.calls.append(("push", args, kwargs))


def test_main_window_push_no_upstream_prompt(monkeypatch) -> None:
    controller = FakeController()
    runner = DummyRunner()
    window = MainWindow(controller=controller, runner=runner)  # type: ignore[arg-type]

    controller.state.set_status(
        RepoStatus(
            branch=BranchInfo(
                name="testing", head_oid=None, upstream=None, ahead=0, behind=0
            ),
            staged=[],
            unstaged=[],
            untracked=[],
            conflicted=[],
        )
    )
    controller.state.set_branches(
        [
            Branch(
                name="testing",
                is_current=True,
                upstream=None,
                ahead=0,
                behind=0,
                gone=False,
            )
        ]
    )
    controller.state.set_remotes([Remote(name="origin", fetch_url=None, push_url=None)])

    err = CommandFailed(
        ["git", "push"],
        128,
        b"",
        b"fatal: The current branch testing has no upstream branch.",
    )

    monkeypatch.setattr(
        ConfirmDialog, "ask", staticmethod(lambda *_args, **_kwargs: True)
    )
    handled = window._maybe_handle_push_no_upstream(err)

    assert handled is True
    assert controller.calls
    assert controller.calls[-1][0] == "push"
