# ADR-0006: Command failure mapping and error surfaces

Status: accepted

Context
- Git commands can fail for many reasons (auth, not a repo, conflicts).
- We need predictable error types to show in the UI.

Decision
- Non-zero exit codes are mapped to CommandFailed with stdout/stderr retained.
- Known error cases (NotARepo, AuthError) are raised where possible.
- Parsing failures raise ParseError.

Consequences
- UI can present consistent error dialogs.
- Logs and tests can assert exact error types.
