from app.git.parse_stash import parse_stash_records


def test_parse_stash_records_basic() -> None:
    payload = (
        b"abc123\x1fstash@{0}\x1fWIP on main: msg\x1f2024-01-01T00:00:00Z\x1e"
        b"def456\x1fstash@{1}\x1fOn dev: more\x1f2024-01-02T00:00:00Z\x1e"
    )

    stashes = parse_stash_records(payload)
    assert len(stashes) == 2
    assert stashes[0].selector == "stash@{0}"
    assert stashes[0].summary == "WIP on main: msg"
    assert stashes[1].oid == "def456"


def test_parse_stash_records_missing_fields_padded() -> None:
    """Records with fewer than 4 fields are safely padded with empty strings."""
    payload = b"abc123\x1fstash@{0}\x1e"  # Only 2 fields instead of 4

    stashes = parse_stash_records(payload)
    assert len(stashes) == 1
    assert stashes[0].oid == "abc123"
    assert stashes[0].selector == "stash@{0}"
    assert stashes[0].summary == ""  # Padded field
    assert stashes[0].date == ""  # Padded field
