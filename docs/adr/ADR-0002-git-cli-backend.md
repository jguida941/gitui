# ADR-0002: Git CLI backend for parity

Status: accepted

Context
- We want full parity with git behavior without re-implementing git.
- Direct CLI use keeps features aligned with installed git.

Decision
- Use the git CLI as the backend (porcelain commands and machine formats).
- Do not depend on pygit2 for core behavior in Phase 0-2.

Consequences
- Feature coverage matches the user's installed git version.
- Parsing and error handling become critical for a stable UI.
