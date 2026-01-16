# ADR-0005: Single-repo scope and single active command

Status: accepted

Context
- Early stability is more valuable than multi-repo complexity.
- A single active command avoids race conditions and UI confusion.

Decision
- The app manages one repo at a time in Phase 0-1.
- CommandRunner executes one command at a time (no concurrency yet).

Consequences
- Simpler state management and fewer edge cases.
- Future multi-repo or concurrency support requires revisiting this ADR.
