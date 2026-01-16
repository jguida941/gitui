from __future__ import annotations

from collections.abc import Mapping, Sequence

from app.exec.command_models import CommandSpec, RunHandle
from app.exec.command_runner import CommandRunner


class GitRunner:
    """Thin wrapper that runs git commands with safe defaults."""

    def __init__(self, runner: CommandRunner, git_executable: str = "git") -> None:
        # CommandRunner is the single execution path.
        self._runner = runner
        self._git_executable = git_executable

        # Defaults keep output stable and avoid interactive prompts.
        self._default_env = {
            "GIT_PAGER": "cat",
            "GIT_TERMINAL_PROMPT": "0",
            "LANG": "C.UTF-8",
        }

    @property
    def runner(self) -> CommandRunner:
        """Expose the underlying CommandRunner for signal wiring."""
        return self._runner

    def run(
        self,
        args: Sequence[str],
        cwd: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> RunHandle:
        """Run a git command and return a handle."""
        if not args:
            raise ValueError("GitRunner.run requires at least one arg")

        # Merge default environment with caller overrides.
        merged_env = dict(self._default_env)
        if env:
            merged_env.update(env)

        spec = CommandSpec(
            args=[self._git_executable, *args],
            cwd=cwd,
            env=merged_env,
        )
        return self._runner.run(spec)
