# Agents Contract

This file mirrors docs/agents.md and must be kept in sync.

This project builds a PySide6 Git UI on top of the git CLI. Keep these rules:

- Do not add new layers (no extra "manager" classes) without an ADR.
- UI calls intent methods only; no UI direct git calls.
- All command execution goes through CommandRunner (PySide6 QProcess only).
- Do not use subprocess for git.
- Prefer machine-readable git output when available.
- Avoid cross-phase refactors unless explicitly planned.
- Phase 0 is backend-only for implementation; UI files may exist as empty placeholders for tracking only.
- Do not add UI logic until CommandRunner + GitService + tests exist.
- Do not add new dependencies without an ADR.
- Placeholder files exist for modularization and tracking; adjust structure if it improves maintainability.
- If structure changes, update docs/roadmap.md and docs/structure.md.
- This is a learning project: do not start coding unless explicitly asked; work with me step-by-step as a teacher.
- When making changes, report files changed, new tests added, and how it respects ADRs.
- Plan of record: docs/roadmap.md
- Repo layout reference: docs/structure.md
