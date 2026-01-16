from __future__ import annotations

from app.core.models import Branch


def parse_branches(payload: bytes) -> list[Branch]:
    """Parse `git branch --format=...` output into Branch objects."""
    text = payload.decode("utf-8", errors="replace")
    branches: list[Branch] = []

    for line in text.splitlines():
        if not line:
            continue

        parts = line.split("|")
        name = parts[0] if len(parts) > 0 else ""
        head_flag = parts[1] if len(parts) > 1 else ""
        upstream_raw = parts[2] if len(parts) > 2 else ""
        track_raw = parts[3] if len(parts) > 3 else ""

        upstream = upstream_raw or None
        is_current = head_flag.strip() == "*"

        ahead = 0
        behind = 0
        gone = False

        track = track_raw.strip()
        if track.startswith("[") and track.endswith("]"):
            track = track[1:-1]

        if track:
            if "gone" in track:
                gone = True
            for token in track.split(","):
                token = token.strip()
                if token.startswith("ahead "):
                    try:
                        ahead = int(token.split()[1])
                    except (IndexError, ValueError):
                        ahead = 0
                elif token.startswith("behind "):
                    try:
                        behind = int(token.split()[1])
                    except (IndexError, ValueError):
                        behind = 0

        branches.append(
            Branch(
                name=name,
                is_current=is_current,
                upstream=upstream,
                ahead=ahead,
                behind=behind,
                gone=gone,
            )
        )

    return branches
