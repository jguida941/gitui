from __future__ import annotations

from app.git.parse_remote_branches import parse_remote_branches


def test_parse_remote_branches_filters_and_splits() -> None:
    payload = b"\n".join(
        [
            b"origin/main",
            b"origin/feature/one",
            b"upstream/dev",
            b"origin/HEAD",
            b"malformed",
            b"",
        ]
    )

    branches = parse_remote_branches(payload)

    assert [b.full_name for b in branches] == [
        "origin/main",
        "origin/feature/one",
        "upstream/dev",
    ]
    assert branches[0].remote == "origin"
    assert branches[0].name == "main"
