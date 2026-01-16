from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure repo root is on sys.path so `app` imports resolve.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from PySide6.QtCore import QCoreApplication
except ModuleNotFoundError:
    QCoreApplication = None

from app.exec.command_runner import CommandRunner
from app.git.git_runner import GitRunner


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a git status smoke test.")
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to a git repo (default: current directory).",
    )
    args = parser.parse_args()

    if QCoreApplication is None:
        print("PySide6 is required to run this smoke test.", file=sys.stderr)
        return 1

    # Qt event loop is required for QProcess signals.
    app = QCoreApplication(sys.argv)
    runner = CommandRunner()
    git = GitRunner(runner)

    def on_stdout(_handle: object, data: bytes) -> None:
        sys.stdout.write(data.decode("utf-8", errors="replace"))
        sys.stdout.flush()

    def on_stderr(_handle: object, data: bytes) -> None:
        sys.stderr.write(data.decode("utf-8", errors="replace"))
        sys.stderr.flush()

    def on_finished(_handle: object, result: object) -> None:
        cmd_result = result  # type: ignore[assignment]
        print(f"\nexit={cmd_result.exit_code} duration_ms={cmd_result.duration_ms}")
        app.quit()

    runner.command_stdout.connect(on_stdout)
    runner.command_stderr.connect(on_stderr)
    runner.command_finished.connect(on_finished)

    # Run a simple status command (porcelain v2 for machine-readable output).
    git.run(["status", "--porcelain=v2", "-b", "-z"], cwd=args.repo)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
