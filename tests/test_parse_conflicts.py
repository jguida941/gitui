from app.git.parse_conflicts import parse_conflict_paths


def test_parse_conflict_paths_basic() -> None:
    payload = b"file1.txt\npath/with space.txt\n\n"

    paths = parse_conflict_paths(payload)
    assert paths == ["file1.txt", "path/with space.txt"]
