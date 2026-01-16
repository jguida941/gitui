# ui_tags_panel Notes

Purpose
- Display tags and provide create/delete/push actions.
- Offer a remote dropdown for push commands.

Key elements
- Tree shows tag names; combo mirrors selection.
- Create row supports optional ref input.
- Push row selects remote and emits intent signals.

Flowchart: TagsPanel

[set_tags] -> [populate tree + combo]
        |
        v
[action click] -> [emit tag intent]
