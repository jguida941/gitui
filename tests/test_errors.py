from __future__ import annotations

from app.core.errors import AuthError, CommandFailed, NotARepo, ParseError


def test_command_failed_stores_attributes() -> None:
    exc = CommandFailed(
        command_args=["git", "push"],
        exit_code=128,
        stdout=b"output",
        stderr=b"error: failed",
    )
    assert exc.command_args == ["git", "push"]
    assert exc.exit_code == 128
    assert exc.stdout == b"output"
    assert exc.stderr == b"error: failed"
    assert "128" in str(exc)
    assert "git push" in str(exc)


def test_command_failed_accepts_tuple_args() -> None:
    exc = CommandFailed(
        command_args=("git", "status"),
        exit_code=1,
        stdout=b"",
        stderr=b"",
    )
    assert exc.command_args == ["git", "status"]


def test_not_a_repo_stores_path() -> None:
    exc = NotARepo(path="/tmp/not-a-repo")
    assert exc.path == "/tmp/not-a-repo"
    assert "/tmp/not-a-repo" in str(exc)


def test_auth_error_default_message() -> None:
    exc = AuthError()
    assert "Authentication failed" in str(exc)


def test_auth_error_custom_message() -> None:
    exc = AuthError("SSH key not found")
    assert "SSH key not found" in str(exc)


def test_parse_error_stores_message() -> None:
    exc = ParseError("Invalid format at line 5")
    assert "Invalid format at line 5" in str(exc)
