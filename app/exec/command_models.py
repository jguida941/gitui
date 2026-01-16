from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandSpec:
    """Immutable description of a command to execute."""

    # Keep this immutable so callers can safely share specs across layers.
    args: Sequence[str]  # Program + arguments, e.g. ["git", "status"].
    cwd: str | None = None  # Working directory for the process.
    env: Mapping[str, str] | None = None  # Env var overrides.


@dataclass(frozen=True)
class RunHandle:
    """Immutable reference to a running command."""

    # Stable ID lets us correlate signals without storing process objects in UI.
    run_id: int
    spec: CommandSpec  # Command + args + cwd + env.
    started_at_ms: int  # Monotonic ms timestamp.


@dataclass(frozen=True)
class CommandResult:
    """Final output of a completed command."""

    # Keep raw bytes for parsers; decoding happens at the edges.
    exit_code: int
    stdout: bytes  # Collected stdout bytes.
    stderr: bytes  # Collected stderr bytes.
    duration_ms: int  # Runtime in milliseconds (monotonic).

    @property
    def ok(self) -> bool:
        return self.exit_code == 0
