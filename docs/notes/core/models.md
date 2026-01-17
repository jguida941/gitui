# Models Notes

Purpose
- Defines shared dataclasses used by parsers and UI.
- Keeps a stable contract between git parsing and presentation.

Models
- FileChange: one path with staged/unstaged status codes.
- BranchInfo: branch name + upstream tracking state.
- Branch: branch list row with upstream tracking info.
- RemoteBranch: remote-tracking branch (remote/name).
- RepoStatus: grouped changes for the status UI.
- Commit: structured log entry (for history view).
- StashEntry: stash list row with selector + summary.
- Tag: tag name entry.
- Remote: remote name with fetch/push URLs.

Flowchart: status parsing -> UI

[git status porcelain v2 bytes]
        |
        v
[parse_status_porcelain_v2]
        |
        v
[RepoStatus + FileChange]
        |
        v
[UI renders staged/unstaged/untracked/conflicted]

Flowchart: log parsing -> UI

[git log bytes]
        |
        v
[parse_log_records]
        |
        v
[list[Commit]]
        |
        v
[UI renders history]

Flowchart: stash/tag/remote parsing -> UI

[stash/tag/remote bytes]
        |
        v
[parse_* helpers]
        |
        v
[list[StashEntry|Tag|Remote]]
        |
        v
[UI renders lists]
