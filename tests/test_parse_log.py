from app.git.parse_log import parse_log_records


def test_parse_log_records_basic() -> None:
    payload = (
        b"aaaaaaaa\x1f\x1fAlice\x1falice@example.com\x1f"
        b"2024-01-01T00:00:00+00:00\x1fInitial commit\x1e"
        b"bbbbbbbb\x1f1111111 2222222\x1fBob\x1fbob@example.com\x1f"
        b"2024-01-02T00:00:00+00:00\x1fMerge branch\x1e"
    )

    commits = parse_log_records(payload)
    assert len(commits) == 2

    first = commits[0]
    assert first.oid == "aaaaaaaa"
    assert first.parents == []
    assert first.author_name == "Alice"
    assert first.author_email == "alice@example.com"
    assert first.author_date == "2024-01-01T00:00:00+00:00"
    assert first.subject == "Initial commit"

    second = commits[1]
    assert second.oid == "bbbbbbbb"
    assert second.parents == ["1111111", "2222222"]
    assert second.author_name == "Bob"
    assert second.author_email == "bob@example.com"
    assert second.author_date == "2024-01-02T00:00:00+00:00"
    assert second.subject == "Merge branch"
