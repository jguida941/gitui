from __future__ import annotations

from app.core.models import RemoteBranch


def parse_remote_branches(payload: bytes) -> list[RemoteBranch]:
    """Parse `git branch -r --format=...` output into RemoteBranch objects."""
    text = payload.decode("utf-8", errors="replace")
    branches: list[RemoteBranch] = []

    for line in text.splitlines():
        name = line.strip()
        if not name:
            continue
        if "->" in name:
            continue

        if "/" not in name:
            continue
        remote, branch = name.split("/", 1)
        if not remote or not branch:
            continue
        if branch == "HEAD":
            continue

        branches.append(
            RemoteBranch(
                remote=remote,
                name=branch,
                full_name=name,
            )
        )

    return branches
