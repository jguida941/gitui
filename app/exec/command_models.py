from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class CommandSpec:
    args: Sequence[str]
    cwd: str | None = None
    env: Mapping[str, str] | None = None


@dataclass(frozen=True)
class CommandResult:
    exit_code: int
    stdout: bytes
    stderr: bytes
    duration_ms: int

    @property
    def ok(self) -> bool:
        return self.exit_code == 0
