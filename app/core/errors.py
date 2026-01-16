from __future__ import annotations

from collections.abc import Sequence


class GitUIError(Exception):
    """Base error type for git UI domain failures."""


class CommandFailed(GitUIError):
    """Raised when a command exits non-zero."""

    def __init__(
        self,
        command_args: Sequence[str],
        exit_code: int,
        stdout: bytes,
        stderr: bytes,
    ) -> None:
        message = f"Command failed ({exit_code}): {' '.join(command_args)}"
        super().__init__(message)
        self.command_args = list(command_args)
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


class NotARepo(GitUIError):
    """Raised when a path is not inside a git work tree."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Not a git repository: {path}")
        self.path = path


class AuthError(GitUIError):
    """Raised when git authentication fails or is required."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message)


class ParseError(GitUIError):
    """Raised when parsing git output fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
