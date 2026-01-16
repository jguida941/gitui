# tests_repo_state Notes

Purpose
- Confirm RepoState setters update data and emit the state_changed signal.

Flowchart: test_set_repo_path_emits_signal

[set_repo_path]
        |
        v
[state_changed emitted]
        |
        v
[assert repo_path updated]
