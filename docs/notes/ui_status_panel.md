# ui_status_panel Notes

Purpose
- Show staged/unstaged/untracked/conflicted lists from RepoStatus.
- Emit diff requests for staged/unstaged selections.

Flowchart: set_status

[RepoStatus]
        |
        v
[populate list widgets]
        |
        v
[update group titles with counts]

Flowchart: diff selection

[user selects staged/unstaged item]
        |
        v
[emit diff_requested(path, staged)]
