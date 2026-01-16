from __future__ import annotations

from app.core.models import Tag


def parse_tags(payload: bytes) -> list[Tag]:
    """Parse `git tag --list` output into Tag objects."""
    text = payload.decode("utf-8", errors="replace")
    tags: list[Tag] = []

    # Tags are one per line in list output.
    for line in text.splitlines():
        name = line.strip()
        if not name:
            continue
        tags.append(Tag(name=name))

    return tags
