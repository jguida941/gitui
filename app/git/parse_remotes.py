from __future__ import annotations

from app.core.models import Remote


def parse_remotes(payload: bytes) -> list[Remote]:
    """Parse `git remote -v` output into Remote objects."""
    text = payload.decode("utf-8", errors="replace")
    remotes: dict[str, Remote] = {}

    for line in text.splitlines():
        if not line.strip():
            continue

        parts = line.split()
        if len(parts) < 3:
            continue

        name = parts[0]
        kind = parts[-1].strip("()").lower()
        url = " ".join(parts[1:-1])

        current = remotes.get(name)
        if current is None:
            current = Remote(name=name, fetch_url=None, push_url=None)

        if kind == "fetch":
            current = Remote(name=name, fetch_url=url, push_url=current.push_url)
        elif kind == "push":
            current = Remote(name=name, fetch_url=current.fetch_url, push_url=url)
        else:
            # Unknown kind; skip without failing.
            continue

        remotes[name] = current

    return list(remotes.values())
