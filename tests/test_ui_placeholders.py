from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from app.ui.branches_panel import BranchesPanel
from app.ui.commit_panel import CommitPanel
from app.ui.console_widget import ConsoleWidget
from app.ui.dialogs.confirm_dialog import ConfirmDialog
from app.ui.dialogs.error_dialog import ErrorDialog
from app.ui.theme.theme_editor_dialog import ThemeEditorDialog
from app.ui.diff_viewer import DiffViewer
from app.ui.log_panel import LogPanel
from app.ui.main_window import MainWindow
from app.ui.remotes_panel import RemotesPanel
from app.ui.repo_picker import RepoPicker
from app.ui.stash_panel import StashPanel
from app.ui.status_panel import StatusPanel
from app.ui.tags_panel import TagsPanel

app = QApplication.instance() or QApplication([])


@pytest.mark.parametrize(
    "factory",
    [
        lambda: MainWindow(),
        lambda: ConsoleWidget(),
        lambda: RepoPicker(),
        lambda: StatusPanel(),
        lambda: DiffViewer(),
        lambda: CommitPanel(),
        lambda: BranchesPanel(),
        lambda: LogPanel(),
        lambda: StashPanel(),
        lambda: TagsPanel(),
        lambda: RemotesPanel(),
        lambda: ConfirmDialog("Confirm", "Proceed?"),
        lambda: ErrorDialog(Exception("boom")),
        lambda: ThemeEditorDialog(),
    ],
)
def test_ui_placeholders_construct(factory) -> None:
    instance = factory()
    assert instance is not None
