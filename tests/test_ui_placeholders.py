from __future__ import annotations

import pytest

from app.ui.branches_panel import BranchesPanel
from app.ui.commit_panel import CommitPanel
from app.ui.console_widget import ConsoleWidget
from app.ui.dialogs.confirm_dialog import ConfirmDialog
from app.ui.dialogs.error_dialog import ErrorDialog
from app.ui.diff_viewer import DiffViewer
from app.ui.log_panel import LogPanel
from app.ui.main_window import MainWindow
from app.ui.remotes_panel import RemotesPanel
from app.ui.repo_picker import RepoPicker
from app.ui.stash_panel import StashPanel
from app.ui.status_panel import StatusPanel
from app.ui.tags_panel import TagsPanel


@pytest.mark.parametrize(
    "cls",
    [
        MainWindow,
        ConsoleWidget,
        RepoPicker,
        StatusPanel,
        DiffViewer,
        CommitPanel,
        BranchesPanel,
        LogPanel,
        StashPanel,
        TagsPanel,
        RemotesPanel,
        ConfirmDialog,
        ErrorDialog,
    ],
)
def test_ui_placeholders_construct(cls: type[object]) -> None:
    instance = cls()
    assert instance.__class__ is cls
