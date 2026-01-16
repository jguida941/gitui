# ui_git_toolbar Notes

Purpose
- Provide quick access to common git actions.
- Emit intent-only signals for RepoController wiring.

Key elements
- Refresh, Stage All, Unstage All, Discard, Fetch, Pull, Push.
- Uses tooltips for discoverability.

Flowchart: GitToolbar

[toolbar click] -> [emit action signal] -> [controller intent]
