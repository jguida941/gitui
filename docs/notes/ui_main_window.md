# ui_main_window Notes

Purpose
- Compose the main layout: repo picker, tabs, diff viewer, console.
- Wire UI signals to RepoController intents and CommandRunner output.
- Surface errors via status bar + error dialog.

Key elements
- GitToolbar provides one-click actions (refresh/stage/fetch/pull/push).
- Left tabs host Changes (status + commit), Log, Branches, Stashes, Tags, Remotes.
- Splitters keep the diff viewer and console adjustable.

Flowchart: MainWindow

[RepoPicker] -> [controller.open_repo]
        |
        v
[RepoState change] -> [update panels + diff + title]
        |
        v
[User action] -> [emit intent -> controller]
