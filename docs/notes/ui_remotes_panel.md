# ui_remotes_panel Notes

Purpose
- Display configured remotes and allow add/remove/update URL.
- Keep write operations behind explicit action buttons.

Key elements
- Tree lists name + fetch/push URLs.
- Add row captures name + URL for new remote.
- Edit row selects existing remote for remove/set-url.

Flowchart: RemotesPanel

[set_remotes] -> [populate tree + combo]
        |
        v
[action click] -> [emit remote intent]
