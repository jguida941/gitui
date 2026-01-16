# Agents Contract

This project builds a PySide6 Git UI on top of the git CLI. Keep these rules:

- Do not add new layers (no extra "manager" classes) without an ADR.
- UI calls intent methods only; no UI direct git calls.
- All command execution goes through CommandRunner (PySide6 QProcess only).
- Do not use subprocess for git.
- Prefer machine-readable git output when available.
- Avoid cross-phase refactors unless explicitly planned.
- Phase 0 started backend-only; UI wiring is allowed now but must honor the intent boundary.
- Only add UI logic once the underlying intent + tests exist.
- Do not add new dependencies without an ADR.
- Placeholder files exist for modularization and tracking; adjust structure if it improves maintainability.
- If structure changes, update docs/roadmap.md and docs/structure.md.
- This is a learning project: do not start coding unless explicitly asked; work with me step-by-step as a teacher.
- Add brief, intent-level comments in code so each block is understandable; use docs/notes/ for deeper explanations.
- Target per-file coverage >= 90% and mutation kill rate >= 90% (goal 100%) with targeted tests.
- Update CHANGELOG.md after each ADR or major feature milestone (or meaningful push).
- For any new file or major change, add/update a matching note in docs/notes with a simple flowchart.
- Keep following docs/roadmap.md; expand tests and plan items when gaps are found.
- If a better approach is discovered, pause and propose it before implementing.
- When making changes, report files changed, new tests added, and how it respects ADRs.
- Plan of record: docs/roadmap.md
- Repo layout reference: docs/structure.md
