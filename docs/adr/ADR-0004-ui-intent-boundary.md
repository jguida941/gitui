# ADR-0004: UI calls intent methods only

Status: accepted

Context
- UI code should stay thin and not own domain logic.
- A clear boundary enables testing and future refactors.

Decision
- UI triggers intent methods on the controller/service layer.
- UI does not execute git commands or parse git output.

Consequences
- Logic is centralized and testable.
- UI changes are less likely to break git behavior.
