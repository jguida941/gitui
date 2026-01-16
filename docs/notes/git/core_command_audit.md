# Core Command Audit Notes

Purpose
- Verify the Phase 0-3 command set works end-to-end before adding advanced features.
- Catch regressions early by auditing the real git CLI outputs.

Prereqs
- Use a fixture repo with staged/unstaged/untracked files, a merge commit,
  a second branch with upstream tracking, one stash, one tag, one remote,
  and an optional conflict.

Audit order (backend CLI first)
1) Status -> diff -> stage -> unstage -> discard
2) Commit (normal + amend)
3) Fetch -> pull --ff-only -> push
4) Log -> branches
5) Stash -> tags -> remotes
6) Conflicts (if available)

UI audit (after CLI passes)
- Wire minimal UI actions to existing intents and repeat the same order.

Flowchart: audit flow

[prepare fixture repo]
        |
        v
[run CLI audit in order]
        |
        v
[fix failures + retest]
        |
        v
[run UI audit in order]
        |
        v
[sign off before advanced features]
