# ui_log_panel Notes

Purpose
- Render recent commits in a sortable table.
- Provide a refresh control without direct git execution.

Key elements
- Table columns: short hash, subject, author, date.
- Refresh button emits a signal for RepoController.

Flowchart: LogPanel

[refresh click] -> [emit refresh_requested]
        |
        v
[set_commits] -> [populate table]
