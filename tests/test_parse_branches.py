from app.git.parse_branches import parse_branches


def test_parse_branches_basic() -> None:
    payload = (
        b"main|*|origin/main|[ahead 1, behind 2]\n"
        b"feature||origin/feature|[behind 3]\n"
        b"topic|||\n"
    )

    branches = parse_branches(payload)
    assert len(branches) == 3

    main = branches[0]
    assert main.name == "main"
    assert main.is_current is True
    assert main.upstream == "origin/main"
    assert main.ahead == 1
    assert main.behind == 2
    assert main.gone is False

    feature = branches[1]
    assert feature.name == "feature"
    assert feature.is_current is False
    assert feature.upstream == "origin/feature"
    assert feature.ahead == 0
    assert feature.behind == 3

    topic = branches[2]
    assert topic.name == "topic"
    assert topic.upstream is None
    assert topic.ahead == 0
    assert topic.behind == 0
    assert topic.gone is False


def test_parse_branches_gone() -> None:
    payload = b"old| |origin/old|[gone]\n"
    branches = parse_branches(payload)
    assert branches[0].gone is True


def test_parse_branches_ignores_empty_lines_and_bad_counts() -> None:
    payload = b"\ninvalid| |origin/invalid|[ahead nope, behind ???]\n"
    branches = parse_branches(payload)
    assert len(branches) == 1
    assert branches[0].ahead == 0
    assert branches[0].behind == 0


def test_parse_branches_handles_unbracketed_track() -> None:
    payload = b"dev||origin/dev|ahead 2, behind 1\n"
    branch = parse_branches(payload)[0]
    assert branch.ahead == 2
    assert branch.behind == 1
