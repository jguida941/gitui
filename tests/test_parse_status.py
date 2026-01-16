from app.core.models import RepoStatus
from app.git.parse_status import parse_status_porcelain_v2


def test_parse_status_basic_lists() -> None:
    payload = (
        b"# branch.oid 1111111\x00"
        b"# branch.head main\x00"
        b"# branch.upstream origin/main\x00"
        b"# branch.ab +1 -2\x00"
        b"1 M. N... 100644 100644 100644 abcdef1 abcdef2 src/app.py\x00"
        b"1 .M N... 100644 100644 100644 abcdef1 abcdef2 README.md\x00"
        b"? untracked.txt\x00"
    )

    status = parse_status_porcelain_v2(payload)
    assert isinstance(status, RepoStatus)
    assert status.branch is not None
    assert status.branch.name == "main"
    assert status.branch.upstream == "origin/main"
    assert status.branch.ahead == 1
    assert status.branch.behind == 2

    assert [f.path for f in status.staged] == ["src/app.py"]
    assert [f.path for f in status.unstaged] == ["README.md"]
    assert [f.path for f in status.untracked] == ["untracked.txt"]
    assert status.conflicted == []


def test_parse_status_rename_and_conflict() -> None:
    payload = (
        b"2 R. N... 100644 100644 100644 abcdef1 abcdef2 R100 new.txt\x00"
        b"old.txt\x00"
        b"u UU N... 100644 100644 100644 100644 abcdef1 abcdef2 abcdef3 conflict.txt\x00"
    )

    status = parse_status_porcelain_v2(payload)
    assert status.staged[0].path == "new.txt"
    assert status.staged[0].orig_path == "old.txt"
    assert [f.path for f in status.conflicted] == ["conflict.txt"]


def test_parse_status_paths_with_spaces_and_newlines() -> None:
    payload = (
        b"# branch.head main\x00"
        b"1 M. N... 100644 100644 100644 abcdef1 abcdef2 spaced name.txt\x00"
        b"? weird\nname.txt\x00"
    )

    status = parse_status_porcelain_v2(payload)
    assert [f.path for f in status.staged] == ["spaced name.txt"]
    assert [f.path for f in status.untracked] == ["weird\nname.txt"]


def test_parse_status_malformed_branch_header_skipped() -> None:
    """Branch header with insufficient parts is safely skipped."""
    payload = (
        b"# branch.oid\x00"  # Missing value - only 2 parts
        b"# branch.head main\x00"
        b"1 M. N... 100644 100644 100644 abcdef1 abcdef2 file.txt\x00"
    )

    status = parse_status_porcelain_v2(payload)
    assert status.branch is not None
    assert status.branch.name == "main"


def test_parse_status_ahead_non_numeric_defaults_to_zero() -> None:
    """Non-numeric ahead value defaults to 0."""
    payload = b"# branch.ab +abc -2\x00"

    status = parse_status_porcelain_v2(payload)
    assert status.branch is not None
    assert status.branch.ahead == 0
    assert status.branch.behind == 2


def test_parse_status_behind_non_numeric_defaults_to_zero() -> None:
    """Non-numeric behind value defaults to 0."""
    payload = b"# branch.ab +1 -xyz\x00"

    status = parse_status_porcelain_v2(payload)
    assert status.branch is not None
    assert status.branch.ahead == 1
    assert status.branch.behind == 0
