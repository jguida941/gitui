# ui_commit_panel Notes

Purpose
- Collect commit messages with templates and an amend toggle.
- Emit commit intent only when message text is present.
- Keep the commit action gated so empty commits are harder by accident.

Key elements
- Template combo inserts a prefix when the message is empty.
- Character count updates as you type.
- Commit button sets a `primary` property for theme styling.

Flowchart: CommitPanel

[template select] -> [insert prefix if empty]
        |
        v
[message edit] -> [enable Commit button]
        |
        v
[Commit click] -> [emit commit_requested(message, amend)]
