from app.git.parse_tags import parse_tags


def test_parse_tags_basic() -> None:
    payload = b"v1.0.0\n\nrelease-2024\n"

    tags = parse_tags(payload)
    assert [tag.name for tag in tags] == ["v1.0.0", "release-2024"]
