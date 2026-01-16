from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QMenu

from app.core.models import Branch, BranchInfo, Commit, FileChange, Remote, RepoStatus, StashEntry, Tag
from app.ui.branches_panel import BranchesPanel
from app.ui.commit_panel import CommitPanel
from app.ui.git_toolbar import GitToolbar
from app.ui.log_panel import LogPanel
from app.ui.remotes_panel import RemotesPanel
from app.ui.stash_panel import StashPanel
from app.ui.status_panel import StatusPanel
from app.ui.tags_panel import TagsPanel

app = QApplication.instance() or QApplication([])


def test_commit_panel_emits_commit() -> None:
    panel = CommitPanel()
    emitted: list[tuple[str, bool]] = []
    panel.commit_requested.connect(lambda msg, amend: emitted.append((msg, amend)))

    panel._message.setPlainText("feat: add panel")
    panel._update_state()
    panel._emit_commit()

    assert emitted == [("feat: add panel", False)]
    panel.clear()
    panel._apply_template("fix:")


def test_branches_panel_actions() -> None:
    panel = BranchesPanel()
    branches = [
        Branch(name="main", is_current=True, upstream="origin/main", ahead=0, behind=0, gone=False),
        Branch(name="dev", is_current=False, upstream=None, ahead=2, behind=1, gone=False),
    ]
    panel.set_branches(branches)
    panel.set_remotes(["origin", "upstream"])

    switched: list[str] = []
    created: list[tuple[str, str]] = []
    deleted: list[tuple[str, bool]] = []
    upstreams: list[tuple[str, str | None]] = []

    panel.switch_requested.connect(switched.append)
    panel.create_requested.connect(lambda name, start: created.append((name, start)))
    panel.delete_requested.connect(lambda name, force: deleted.append((name, force)))
    panel.set_upstream_requested.connect(lambda upstream, branch: upstreams.append((upstream, branch)))

    panel._branch_combo.setCurrentText("dev")
    panel._emit_switch()

    panel._new_branch.setText("feature-x")
    panel._start_point_combo.setCurrentText("main")
    panel._emit_create()

    panel._branch_combo.setCurrentText("dev")
    panel._force_delete.setCurrentText("Force Delete")
    panel._emit_delete()

    panel._upstream_combo.setCurrentIndex(0)
    panel._emit_set_upstream()

    assert switched == ["dev"]
    assert created == [("feature-x", "main")]
    assert deleted == [("dev", True)]
    assert upstreams


def test_log_panel_sets_commits() -> None:
    panel = LogPanel()
    commits = [
        Commit(
            oid="abc123",
            parents=[],
            author_name="Dev",
            author_email="dev@example.com",
            author_date="2024-01-01T00:00:00Z",
            subject="Test commit",
        )
    ]
    panel.set_commits(commits)
    assert panel._table.rowCount() == 1


def test_stash_panel_emits_actions() -> None:
    panel = StashPanel()
    stashes = [StashEntry(oid="1", selector="stash@{0}", summary="WIP", date="2024-01-01")]
    panel.set_stashes(stashes)

    saved: list[tuple[object, bool]] = []
    applied: list[object] = []
    popped: list[object] = []
    dropped: list[object] = []

    panel.save_requested.connect(lambda msg, inc: saved.append((msg, inc)))
    panel.apply_requested.connect(applied.append)
    panel.pop_requested.connect(popped.append)
    panel.drop_requested.connect(dropped.append)

    panel._message.setText("WIP")
    panel._include_untracked.setChecked(True)
    panel._emit_save()

    panel._stash_combo.setCurrentIndex(1)
    panel._emit_apply()
    panel._emit_pop()
    panel._emit_drop()

    assert saved == [("WIP", True)]
    assert applied and popped and dropped


def test_tags_panel_emits_actions() -> None:
    panel = TagsPanel()
    panel.set_tags([Tag(name="v1.0.0")])
    panel.set_remotes(["origin", "upstream"])

    created: list[tuple[str, object]] = []
    deleted: list[str] = []
    pushed: list[tuple[str, str]] = []
    pushed_all: list[str] = []

    panel.create_requested.connect(lambda name, ref: created.append((name, ref)))
    panel.delete_requested.connect(deleted.append)
    panel.push_tag_requested.connect(lambda name, remote: pushed.append((name, remote)))
    panel.push_tags_requested.connect(pushed_all.append)

    panel._new_tag.setText("v2.0.0")
    panel._ref.setText("HEAD")
    panel._emit_create()

    panel._tag_combo.setCurrentText("v1.0.0")
    panel._emit_delete()
    panel._emit_push_tag()
    panel._emit_push_all()

    assert created == [("v2.0.0", "HEAD")]
    assert deleted == ["v1.0.0"]
    assert pushed
    assert pushed_all


def test_remotes_panel_emits_actions() -> None:
    panel = RemotesPanel()
    panel.set_remotes([Remote(name="origin", fetch_url="git@x", push_url="git@x")])

    added: list[tuple[str, str]] = []
    removed: list[str] = []
    updated: list[tuple[str, str]] = []

    panel.add_requested.connect(lambda name, url: added.append((name, url)))
    panel.remove_requested.connect(removed.append)
    panel.set_url_requested.connect(lambda name, url: updated.append((name, url)))

    panel._name.setText("upstream")
    panel._url.setText("git@upstream")
    panel._emit_add()

    panel._remote_combo.setCurrentText("origin")
    panel._emit_remove()

    panel._remote_combo.setCurrentText("origin")
    panel._url.setText("git@new")
    panel._emit_set_url()

    assert added == [("upstream", "git@upstream")]
    assert removed == ["origin"]
    assert updated == [("origin", "git@new")]


def test_git_toolbar_signals() -> None:
    toolbar = GitToolbar()
    calls = []
    toolbar.refresh_requested.connect(lambda: calls.append("refresh"))
    toolbar.stage_all_requested.connect(lambda: calls.append("stage"))
    toolbar.unstage_all_requested.connect(lambda: calls.append("unstage"))
    toolbar.discard_all_requested.connect(lambda: calls.append("discard"))
    toolbar.fetch_requested.connect(lambda: calls.append("fetch"))
    toolbar.pull_requested.connect(lambda: calls.append("pull"))
    toolbar.push_requested.connect(lambda: calls.append("push"))

    for action in toolbar.actions():
        if action.text():
            action.trigger()

    assert calls == ["refresh", "stage", "unstage", "discard", "fetch", "pull", "push"]


def test_status_panel_context_menu(monkeypatch) -> None:
    panel = StatusPanel()
    panel.set_status(None)
    status = RepoStatus(
        branch=BranchInfo(name="main", head_oid=None, upstream=None, ahead=0, behind=0),
        staged=[FileChange(path="a.py", staged_status="M", unstaged_status="")],
        unstaged=[FileChange(path="b.py", staged_status="", unstaged_status="M")],
        untracked=[FileChange(path="c.py", staged_status="", unstaged_status="?")],
        conflicted=[],
    )
    panel.set_status(status)

    staged = panel._staged_list
    unstaged = panel._unstaged_list
    staged.setCurrentRow(0)
    unstaged.setCurrentRow(0)

    emitted = {"stage": 0, "unstage": 0, "discard": 0, "diff": 0}

    panel.stage_requested.connect(lambda _paths: emitted.__setitem__("stage", emitted["stage"] + 1))
    panel.unstage_requested.connect(lambda _paths: emitted.__setitem__("unstage", emitted["unstage"] + 1))
    panel.discard_requested.connect(lambda _paths: emitted.__setitem__("discard", emitted["discard"] + 1))
    panel.diff_requested.connect(lambda _path, _staged: emitted.__setitem__("diff", emitted["diff"] + 1))

    panel._on_selection(staged, staged=True, allow_diff=True)

    def exec_first(self, *_args, **_kwargs):
        return self.actions()[0] if self.actions() else None

    def exec_last(self, *_args, **_kwargs):
        return self.actions()[-1] if self.actions() else None

    monkeypatch.setattr(QMenu, "exec", exec_first)
    panel._show_context_menu(unstaged, "unstaged", QPoint(0, 0))

    monkeypatch.setattr(QMenu, "exec", exec_last)
    panel._show_context_menu(staged, "staged", QPoint(0, 0))

    assert emitted["stage"] == 1
    assert emitted["unstage"] == 1
