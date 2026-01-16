# RepoState Notes

Purpose
- Holds the current repo path, status, and last error.
- Emits a single state_changed signal for the UI to refresh.

Fields
- repo_path: current repo path or None.
- status: latest RepoStatus snapshot or None.
- log: latest list of Commit objects or None.
- branches: latest list of Branch objects or None.
- stashes: latest list of StashEntry objects or None.
- tags: latest list of Tag objects or None.
- remotes: latest list of Remote objects or None.
- conflicts: latest list of conflicted paths or None.
- diff_text: latest diff text or None.
- last_error: last error (CommandFailed, NotARepo, etc.) or None.
- busy: true while commands are in flight.

Flowchart: update status

[controller parses RepoStatus]
        |
        v
[RepoState.set_status]
        |
        v
[state_changed signal]
        |
        v
[UI refreshes views]
