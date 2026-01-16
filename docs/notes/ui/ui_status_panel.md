# ui_status_panel Notes

Purpose
- Show staged/unstaged/untracked/conflicted file lists.
- Emit diff requests and context-menu intents (stage/unstage/discard).

Key elements
- Lists are multi-select for batch actions.
- Context menus are tailored per bucket (e.g., untracked skips discard).
- Dynamic `gitStatus` property enables theme styling.

Flowchart: StatusPanel

[set_status] -> [populate lists]
        |
        v
[select file] -> [emit diff_requested]
        |
        v
[right-click] -> [emit stage/unstage/discard]
