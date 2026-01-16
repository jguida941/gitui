# ADR-0007: Controller routes results; services only parse

Status: accepted

Context
- We want a clean UI boundary and a single place to map results to state.
- Services should not own UI state or command lifecycle.

Decision
- RepoController routes CommandResult to RepoState based on intent kind.
- GitService owns command intents + parsing helpers only.

Consequences
- UI has a single state source (RepoState).
- Parsing logic is centralized in GitService and testable.
