# ui_confirm_dialog Notes

Purpose
- Confirm destructive actions (discard changes, etc.).

Key elements
- Uses standard Accept/Reject buttons.
- `ask()` helper returns True on confirm.

Flowchart: ConfirmDialog

[ask()] -> [show dialog] -> [user confirms?] -> [True/False]
