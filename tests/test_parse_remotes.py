from app.git.parse_remotes import parse_remotes


def test_parse_remotes_fetch_and_push() -> None:
    payload = (
        b"origin\thttps://example.com/repo.git (fetch)\n"
        b"origin\thttps://example.com/repo.git (push)\n"
        b"upstream\tgit@github.com:org/repo.git (fetch)\n"
    )

    remotes = parse_remotes(payload)
    assert len(remotes) == 2
    assert remotes[0].name == "origin"
    assert remotes[0].fetch_url == "https://example.com/repo.git"
    assert remotes[0].push_url == "https://example.com/repo.git"
    assert remotes[1].name == "upstream"
    assert remotes[1].fetch_url == "git@github.com:org/repo.git"
    assert remotes[1].push_url is None


def test_parse_remotes_skips_unknown_and_short_lines() -> None:
    payload = (
        b"origin\n"
        b"origin\thttps://example.com/repo.git (mirror)\n"
        b"origin\thttps://example.com/repo.git (fetch)\n"
    )

    remotes = parse_remotes(payload)
    assert len(remotes) == 1
    assert remotes[0].fetch_url == "https://example.com/repo.git"
    assert remotes[0].push_url is None


def test_parse_remotes_merges_fetch_and_push_urls() -> None:
    payload = (
        b"origin\thttps://example.com/repo.git (fetch)\n"
        b"origin\tgit@github.com:org/repo.git (push)\n"
    )

    remotes = parse_remotes(payload)
    assert remotes[0].fetch_url == "https://example.com/repo.git"
    assert remotes[0].push_url == "git@github.com:org/repo.git"


def test_parse_remotes_empty_lines_skipped() -> None:
    """Empty lines in remote output are gracefully skipped."""
    payload = (
        b"origin\thttps://example.com/repo.git (fetch)\n"
        b"\n"  # Empty line
        b"   \n"  # Whitespace-only line
        b"origin\thttps://example.com/repo.git (push)\n"
    )

    remotes = parse_remotes(payload)
    assert len(remotes) == 1
    assert remotes[0].fetch_url == "https://example.com/repo.git"
    assert remotes[0].push_url == "https://example.com/repo.git"
