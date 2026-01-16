# PySide6 Git Desktop - Scoped Plan (CommandRunner + ADRs + CI/CD)

Goal
- Thin PySide6 GUI on top of the real git CLI, so you stop memorizing commands,
  keep full parity, and avoid re-implementing Git.
- Backend is the "porcelain"; UI is the "dashboard".

Why this plan
- Build slowly and safely without major refactors by locking boundaries early
  (Runner -> Service -> Model -> UI).

## North Star (hard rules)
1. UI never executes commands. UI calls intent methods only.
2. All process execution goes through CommandRunner. No duplicated QProcess or
   subprocess logic anywhere.
3. GitService contains intents + parsing only. No UI, no QProcess, no streaming
   logic.
4. Parsing uses machine formats first (porcelain v2 -z, record separators for
   log).
5. Everything is testable: parsers and services can run with a FakeCommandRunner.

## Decisions locked early (avoid churn)
- Repo scope: single repo at a time.
- CommandRunner: single active command.
- Types: mypy lenient until Phase 1 completes, then tighten.
- Git executable discovery: assume `git` in PATH (configurable later if needed).
- Auth prompts: keep `GIT_TERMINAL_PROMPT=0` and surface failures.
- Locale/encoding: `LANG=C.UTF-8` with platform fallback plan if needed.
- Repo context: use QProcess working dir (not `git -C`) for now.

## Repo layout (target shape)

```
.gitui/
  AGENTS.md
  CHANGELOG.md
  app/
    main.py
    ui/
      main_window.py
      console_widget.py
      repo_picker.py
      status_panel.py
      diff_viewer.py
      commit_panel.py
      branches_panel.py
      log_panel.py
      dialogs/
        confirm_dialog.py
        error_dialog.py
    core/
      models.py        # dataclasses: RepoStatus, FileChange, Commit, etc.
      repo_state.py    # RepoState snapshot + signals
      controller.py    # RepoController: refresh, execute intents, update state
      errors.py        # typed errors: CommandFailed, NotARepo, AuthError...
    exec/
      command_runner.py  # QProcess engine (single source of truth)
      command_models.py  # CommandResult, RunHandle, CommandSpec
      command_queue.py   # optional (Phase 1.5/2), coalescing refresh
    git/
      git_runner.py      # adapter: args -> CommandRunner (env defaults etc.)
      git_service.py     # intent methods
      parse_status.py
      parse_log.py
      parse_diff.py      # optional (mostly plain text)
    utils/
      logging.py
      settings.py        # QSettings wrapper
      paths.py
  tests/
    test_parse_status.py
    test_parse_log.py
    test_git_service.py
    test_controller.py
  docs/
    README.md
    adr/
      ADR-0001-command-runner.md
      ADR-0002-git-cli-backend.md
      ADR-0003-machine-parsing.md
      ADR-0004-ui-intent-boundary.md
    notes/
      README.md
      command_runner.md
    agents.md
    roadmap.md
    structure.md
  .github/workflows/
    ci.yml
  pyproject.toml
  README.md
```

## Documentation + scope control

Agent contract (docs/agents.md)
- Do not add new layers (no extra "manager" classes) without an ADR.
- No UI direct git calls.
- No subprocess module. Use QProcess in CommandRunner only.
- No parsing of human git output when a machine format exists.
- No refactors across phases unless explicitly planned.

ADRs (write early, 1 page each)
- ADR-0001: CommandRunner is the single execution path.
- ADR-0002: Git CLI backend (not pygit2) for parity.
- ADR-0003: Parse porcelain v2 -z and structured log formats.
- ADR-0004: UI -> Controller -> Service boundary (intents only).

## CI/CD plan (light but real from Day 1)

Tools (Python)
- ruff (lint + format)
- mypy (types)
- pytest (+ coverage)
- optional later: pip-audit / bandit

CI workflow (.github/workflows/ci.yml)
- install deps
- ruff format --check
- ruff check
- mypy app
- pytest -q --cov=app --cov-report=term-missing

Gate thresholds
- Coverage: >= 60% in Phase 0/1, raise later.
- Mypy can be warn-only at first; enforce once stable.

## Phase 0 - Foundation (runner-first)

Purpose: lock architecture, avoid refactors later.

Deliverables
1) CommandRunner (QProcess)
   - stream stdout/stderr
   - capture full output
   - cancel/terminate/kill
   - timing + exit code
   - emits signals for console
2) ConsoleWidget (UI placeholder only in Phase 0)
   - shows live output per command
   - keeps a scrollback log
3) GitRunner
   - wraps CommandRunner to run git
   - injects env defaults:
     - GIT_PAGER=cat
     - GIT_TERMINAL_PROMPT=0
     - LANG=C.UTF-8 (or platform-safe)
     - --no-color where needed
4) RepoPicker + Open Repo (UI placeholder only in Phase 0)
   - validate with git rev-parse --is-inside-work-tree

Tests
- unit tests for CommandResult shape and error mapping (fake runner)
- smoke test for parsing git --version output (optional)

Definition of Done
- You can open a repo and run git status via the runner and see output in
  console.
- Cancel button works.
- No UI executes commands directly.

## Phase 1 - Daily workflow MVP (useful app)

Purpose: status -> stage -> diff -> commit -> push.

1) RepoState + Controller
- RepoController owns:
  - current repo path
  - refresh timer
  - executes service intents
  - updates RepoState and emits stateChanged

2) Status (machine-parseable)
- Command: `git status --porcelain=v2 -b -z`
- UI:
  - 3 grouped lists: staged/unstaged/untracked
  - selection triggers diff load
- Backend intents:
  - status() -> RepoStatus
- Tests:
  - test_parse_status.py for porcelain v2 -z parsing
  - include filenames with spaces/newlines (edge cases)

3) Diff viewer
- Commands:
  - `git diff --no-color -- <file>`
  - `git diff --cached --no-color -- <file>`
- Backend intents:
  - diff_file(path, staged) -> str
- UI:
  - toggle staged/unstaged
  - show diff in a text view (QPlainTextEdit initially)

4) Stage / unstage / discard (guard rails)
- Commands:
  - stage: `git add -- <paths>`
  - unstage: `git restore --staged -- <paths>`
  - discard: `git restore -- <paths>` (confirm dialog)
- Backend intents:
  - stage(paths)
  - unstage(paths)
  - discard(paths)

5) Commit panel
- Commands:
  - `git commit -m <msg>`
  - amend: `git commit --amend -m <msg>`
- Backend intents:
  - commit(message, amend=False)
- UI:
  - message box
  - amend checkbox

6) Fetch / Pull / Push
- Commands:
  - `git fetch`
  - `git pull --ff-only`
  - `git push` (+ -u origin branch if missing upstream)
- Backend intents:
  - fetch(), pull_ff_only(), push(auto_set_upstream=True)

Phase 1 DoD
- Open repo
- Status grouped lists
- Stage/unstage/discard
- Diff viewer works
- Commit works
- Fetch/pull/push works
- Console logs every command with timestamps

## Phase 1.2 - Theme Editor (UI customization)

Purpose: allow users to change fonts, colors, metrics, and effects without code.

Deliverables
- ThemeEngine
  - presets + custom save/load
  - undo/redo stack
  - QSS generation for the entire app
- ThemeEditorDialog
  - tabbed controls (colors/fonts/metrics/effects)
  - import/export JSON/QSS
  - live preview panel
- ThemePreview widget gallery

DoD
- Theme Editor opens from menu
- Presets apply instantly
- Export JSON/QSS works

## Phase 1.5 - CommandQueue (optional but recommended)

Purpose: prevent refresh fights and button spam.

Add
- CommandQueue with:
  - single active command
  - queued actions
  - coalesce refresh requests (if 5 refreshes requested, run 1)

Rules
- user actions have priority over background refresh
- refresh is skipped if a command is running unless explicitly forced

DoD
- UI stays responsive, no "10 git status calls" storms.

## Phase 2 - History + Branches (power features)

Purpose: log browsing and branch management.

1) Log viewer (structured)
- Command:
  - `git log --date=iso-strict --pretty=format:%H%x1f%P%x1f%an%x1f%ae%x1f%ad%x1f%s%x1e -n 300`
- Backend intents:
  - log(limit) -> list[Commit]
  - diff_commit(hash) -> str (diff vs parent)
  - show_commit(hash) optional (details)
- UI:
  - commit table/list
  - details pane
  - diff vs parent button
- Tests:
  - parse log records with separators

2) Branches panel
- Commands:
  - list: `git branch --format="%(refname:short)|%(HEAD)|%(upstream:short)|%(upstream:track)"`
  - switch: `git switch <name>`
  - create: `git switch -c <name> [<start-point>]`
  - delete: `git branch -d <name>` (confirm force delete later)
- Backend intents:
  - branches()
  - checkout(branch)
  - create_branch(name, from_ref="HEAD")
  - delete_branch(name, force=False)

DoD
- browse commits, diff commits
- switch/create/delete branches with confirmations
- branch panel updates repo state cleanly

## Phase 2.5 - Insights + Graphs (PyQtGraph + QGraphicsView)

Purpose: visualize repo activity using existing git data.

Prereq
- Complete the core command audit (docs/notes/core_command_audit.md).

Charts (PyQtGraph)
- Commit activity timeline (daily/weekly counts).
- Author contribution bars.
- Churn timeline (added/removed lines).

Graph (QGraphicsView)
- Commit DAG with lanes + edges.

Commands
- Activity timeline: `git log --date=iso-strict --pretty=format:%ad%x1e`
- Author contributions: `git shortlog -sne`
- Churn: `git log --numstat --pretty=format:%ad%x1e`
- Commit graph data: `git log --pretty=format:%H%x1f%P%x1f%ad%x1f%s%x1e -n 500`

Backend intents
- activity_raw(limit) -> RunHandle
- shortlog_raw() -> RunHandle
- churn_raw(limit) -> RunHandle
- graph_log_raw(limit) -> RunHandle

Tests
- parsers for timeline/shortlog/numstat/graph records
- unit tests for aggregator logic (counts per day/author)
- manual checks: chart totals match CLI output

DoD
- charts render in the Insights panel
- commit graph shows parents and lanes
- data matches CLI output for a sample repo

## Phase 3 - Stash, Tags, Remotes (fills daily gaps)

Stash
- list, save, apply, pop, drop

Tags
- list, create, delete, push tags

Remotes
- list remotes, set-url, add/remove, set upstream explicitly

All through intents and CommandRunner.

## Phase 3.5 - Power CLI Tools (daily productivity)

Purpose: add high-value git tools power users expect in a GUI.

Prereq
- Complete the core command audit (docs/notes/core_command_audit.md).

Commands (safe defaults)
- `git show <sha>` (commit details + patch)
- `git log --follow -- <file>` (file history)
- `git blame --line-porcelain <file>` (line ownership)
- `git grep -n <pattern>` (repo search)
- `git diff --stat` / `git diff --name-status` (summary views)
- `git fetch --prune` (cleanup stale remotes)

Guarded actions (confirm dialogs + previews)
- `git clean -nd` (preview) / `git clean -fd` (execute)
- `git revert <sha>`
- `git reset --soft|--mixed|--hard <ref>`
- `git cherry-pick <sha>`

Optional GitHub CLI (requires `gh` + ADR)
- list PRs, open PR, create PR, open in browser

## Phase 4 - Hard parts (do not start here)

These are where GUIs get painful. You can still support them via a
"terminal fallback" early.

1) Conflicts center
- detect conflicts (`git diff --name-only --diff-filter=U`)
- list conflicted files
- buttons: open external merge tool, mark resolved, continue/abort

2) Rebase / cherry-pick / merge flows
- show progress
- provide abort/continue buttons
- keep raw stderr visible

3) Partial staging (hunks/lines)
- a real hunk UI + apply patch
- postpone until the rest is stable

## Phase 5 - Nice-to-haves (Git+ extras)

Purpose: add value beyond git CLI once core git features are stable.

Data sources (no new deps)
- `git log --date=iso-strict --pretty=format:... --numstat`
- `git shortlog -sne`
- `git for-each-ref --format=...` (stale branch age)
- `git reflog` (recovery hints and risky actions)

Features (ordered by likely usefulness)
- Commit graph view (DAG lanes) with filters (author/path/grep).
- Insights dashboard: activity timeline, churn/hot files, author stats (bus factor).
- Repo health flags: unpushed commits, stale branches, missing upstreams.
- Release notes drafts from commit subjects by tag range.
- File history + blame view with line-level author context.

DoD
- Analytics computed locally and shown in UI (tables + lightweight charts).
- Export stats to CSV/JSON for external plotting.
- No new deps without ADR; start with pure Python + Qt primitives.

## AI-friendly work pattern (to avoid scope blowups)

For each phase, run this loop:
1) Create a Phase Ticket (1 feature only)
2) Write/adjust ADR if it changes architecture
3) Implement backend intent + parser + tests
4) Wire UI to the intent
5) Verify console output + error handling
6) Merge

Never implement UI first. Never add features without intents.

## Suggested initial ADR titles
- ADR-0001: Single CommandRunner using QProcess
- ADR-0002: Git CLI backend for parity; pygit2 optional later
- ADR-0003: Use machine-readable git output (porcelain v2 -z, record separators)
- ADR-0004: UI calls intent methods only; no direct command execution

## Minimal milestone checklist
- Phase 0: CommandRunner + Console + Open Repo
- Phase 1: Status + Diff + Stage/Unstage/Discard + Commit + Push/Pull/Fetch
- Phase 1.5: CommandQueue
- Phase 2: Log + Branches
- Phase 3: Stash/Tags/Remotes
- Phase 4: Conflicts/Rebase/Partial staging
- Phase 5: Nice-to-haves (Git+ extras)
