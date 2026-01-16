# ui_branches_panel Notes

Purpose
- Display branches and expose switch/create/delete/upstream actions.
- Keep actions intent-only; the panel emits signals and never runs git.

Key elements
- Tree shows branch name, upstream, ahead/behind, and gone status.
- Action row uses dropdowns for existing branches and start points.
- Upstream suggestions are built from remotes + branch names.

Flowchart: BranchesPanel

[set_branches] -> [populate tree + dropdowns]
        |
        v
[action click] -> [emit intent signal]
