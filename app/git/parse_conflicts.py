from __future__ import annotations


def parse_conflict_paths(payload: bytes) -> list[str]:
    """Parse conflicted file paths from `git diff --name-only --diff-filter=U`."""
    text = payload.decode("utf-8", errors="replace")
    paths: list[str] = []

    # Each line is a file path; blank lines are ignored.
    for line in text.splitlines():
        path = line.strip()
        if path:
            paths.append(path)

    return paths
