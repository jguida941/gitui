# ui_branches_panel Notes

Purpose
- Display local and remote branches and expose branch actions.
- Keep actions intent-only; the panel emits signals and never runs git.

Key elements
- Local tree shows branch name, upstream, ahead/behind, and gone status.
- Remote tree lists remote-tracking branches by remote/name.
- Action row uses dropdowns for existing branches and start points.
- Upstream suggestions are built from remotes + branch names.
- Remote actions allow deleting a selected remote branch.

Flowchart: BranchesPanel

[set_branches/set_remote_branches] -> [populate trees + dropdowns]
        |
        v
[action click] -> [emit intent signal]
