# Manual Testing Checklist

Pre-reqs
- Install deps: `pip install .[dev]`
- Ensure PySide6 is available for QProcess-based runs.
- Have a local fixture repo with: staged/unstaged/untracked files, at least
  two commits (one merge), an upstream-tracking branch, one stash, one tag,
  and a local remote (bare repo is fine).

Repo fixture setup (recommended)
- [ ] Create a throwaway repo + bare remote and add `origin`.
- [ ] Create staged/unstaged/untracked files (include a filename with spaces).
- [ ] Create a second branch, push with `-u`, and make it ahead/behind once.
- [ ] Create a tag and a stash.
- [ ] Optional: create a merge conflict to test conflict detection.

Automated checks
- [ ] `pytest -q` (ensure Hypothesis is installed so property tests run)
- [ ] `pytest --cov --cov-report=json:coverage.json`
- [ ] `scripts/run-mutation.sh` (mutmut mutation score + survivors list).
- [ ] `python scripts/check_coverage.py coverage.json` after `pytest --cov-report=json:coverage.json`.
- [ ] `python scripts/manual_smoke.py --repo /path/to/repo` prints status output and `exit=0`.

Backend (CLI) spot checks
- [ ] Status parsing: run `git status --porcelain=v2 -b -z` and confirm
      branch/upstream/ahead/behind and file buckets match expectations.
- [ ] Diff text: run `git diff --no-color -- <file>` and
      `git diff --cached --no-color -- <file>`.
- [ ] Log parsing: create a merge commit and run
      `git log --date=iso-strict --pretty=format:"%H%x1f%P%x1f%an%x1f%ae%x1f%ad%x1f%s%x1e" -n 5`
      to confirm 2 parents show up for merges.
- [ ] Branch parsing: run
      `git branch --format="%(refname:short)|%(HEAD)|%(upstream:short)|%(upstream:track)"`
      to confirm current, upstream, ahead/behind, gone cases.
- [ ] Conflict detection: create a merge conflict and run
      `git diff --name-only --diff-filter=U` to confirm conflicted paths show up.
- [ ] Stash parsing: create a stash and run
      `git stash list --date=iso-strict --pretty=format:"%H%x1f%gd%x1f%gs%x1f%ad%x1e"`
      to confirm data matches expectations.
- [ ] Tag parsing: create a tag and run `git tag --list` to confirm output.
- [ ] Remote parsing: run `git remote -v` to confirm fetch/push lines.

Core commands audit (must pass before graphs or power tools)
- [ ] Run the sequence in `docs/notes/core_command_audit.md`.
- [ ] Record any failures and fix backend parsing or intent wiring first.

Error-path checks
- [ ] Invalid repo path: run `python scripts/manual_smoke.py --repo /nope` and
      confirm non-zero exit.
- [ ] Push without upstream: in a new branch, run `git push` and confirm the
      expected upstream error text.
- [ ] Delete unmerged branch: run `git branch -d <name>` and confirm git refuses
      unless forced.

GUI checks (when UI is wired)
- [ ] Launch the app (`python -m app.main --repo /path/to/repo`) and open a repo.
- [ ] Status list shows staged/unstaged/untracked groups.
- [ ] Selecting a staged/unstaged file updates the diff viewer.
- [ ] Conflict list shows conflicted files (if any).
- [ ] Stash/tag/remote panels display parsed lists.
- [ ] Log view renders commits and merge parents.
- [ ] Branches panel shows current + upstream/ahead/behind, and switching works.
- [ ] Console logs each command with timestamps and exit codes.

Insights & graphs (when implemented)
- [ ] Activity timeline counts match `git log --date=iso-strict --pretty=format:%ad%x1e`.
- [ ] Author bars match `git shortlog -sne` totals.
- [ ] Churn chart matches `git log --numstat --pretty=format:%ad%x1e`.
- [ ] Commit graph lanes/edges match `git log --pretty=format:%H%x1f%P%x1f%ad%x1f%s%x1e`.

Power tools (when implemented)
- [ ] `git show <sha>` view matches CLI output.
- [ ] `git log --follow -- <file>` view matches CLI output.
- [ ] `git blame --line-porcelain <file>` view matches CLI output.
- [ ] `git grep -n <pattern>` results match CLI output.
- [ ] Summary views match `git diff --stat` and `git diff --name-status`.
- [ ] `git fetch --prune` removes stale remotes in UI.
- [ ] Guarded actions require confirmation and preview:
      `git clean -nd` before `git clean -fd`,
      `git reset --hard` confirms destructive behavior.

Flowchart: manual test flow

[setup fixture repo] -> [run automated checks] -> [run CLI spot checks] -> [run GUI checks]
