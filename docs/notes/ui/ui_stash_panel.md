# ui_stash_panel Notes

Purpose
- Show stash entries and provide save/apply/pop/drop controls.
- Use dropdown selection to avoid manual ref typing.

Key elements
- Tree lists stash ref, summary, date.
- Action row emits signals for save/apply/pop/drop.
- Optional include-untracked toggle on save.

Flowchart: StashPanel

[set_stashes] -> [populate tree + combo]
        |
        v
[action click] -> [emit stash_* intent]
