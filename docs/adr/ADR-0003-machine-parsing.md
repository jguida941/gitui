# ADR-0003: Machine-readable git output

Status: accepted

Context
- Human-readable output is not stable enough for parsing.
- Git provides machine formats for status and log.

Decision
- Prefer machine-readable formats (e.g., `status --porcelain=v2 -z`, record separators for log).
- Use `git branch --format=...` (local + remote) to avoid parsing human branch output.
- Only parse human output when no machine format exists.

Consequences
- Parsers can be deterministic and tested with fixtures.
- UI can present accurate grouped changes and logs.
