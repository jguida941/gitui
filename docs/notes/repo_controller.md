# RepoController Notes

Purpose
- Owns the "intent -> result" flow.
- Starts git commands and updates RepoState when results arrive.

Pending map
- _pending maps run_id -> PendingAction(kind, flags).
- This lets us decide how to interpret each CommandResult and which refreshes to run.
- Refresh flags enqueue follow-up commands; the queue runs them sequentially.

Flowchart: open_repo()

[call open_repo(path)]
        |
        v
[git rev-parse --is-inside-work-tree]
        |
        v
[pending: validate_repo]
        |
        v
[command_finished]
        |
        v
[set repo_path or NotARepo]
        |
        v
[refresh_status]

Flowchart: refresh_status()

[call refresh_status()]
        |
        v
[git status --porcelain=v2 -b -z]
        |
        v
[pending: status]
        |
        v
[command_finished]
        |
        v
[parse status -> RepoState.set_status]

Flowchart: mutating actions

[stage/unstage/commit/etc]
        |
        v
[pending: refresh_status/branches/log flags]
        |
        v
[command_finished]
        |
        v
[trigger refresh_* based on flags]

Flowchart: refresh_lists (stashes/tags/remotes)

[refresh_*()]
        |
        v
[git list command]
        |
        v
[pending: stashes/tags/remotes]
        |
        v
[command_finished]
        |
        v
[parse list -> RepoState.set_*]

Flowchart: refresh_conflicts

[refresh_conflicts()]
        |
        v
[git diff --name-only --diff-filter=U]
        |
        v
[pending: conflicts]
        |
        v
[command_finished]
        |
        v
[parse conflicts -> RepoState.set_conflicts]
