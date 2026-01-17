"""Property-based tests for parsers using Hypothesis.

These tests ensure parsers handle arbitrary input without crashing.
"""

from __future__ import annotations

import pytest

# Skip property tests if Hypothesis isn't installed.
pytest.importorskip("hypothesis")

from hypothesis import given, settings
from hypothesis import strategies as st

from app.git.parse_branches import parse_branches
from app.git.parse_conflicts import parse_conflict_paths
from app.git.parse_diff import parse_diff_text
from app.git.parse_log import parse_log_records
from app.git.parse_remote_branches import parse_remote_branches
from app.git.parse_status import parse_status_porcelain_v2


@given(st.binary())
@settings(max_examples=200)
def test_parse_status_never_crashes(data: bytes) -> None:
    result = parse_status_porcelain_v2(data)
    assert result is not None
    assert hasattr(result, "branch")
    assert hasattr(result, "staged")
    assert hasattr(result, "unstaged")


@given(st.binary())
@settings(max_examples=200)
def test_parse_log_never_crashes(data: bytes) -> None:
    result = parse_log_records(data)
    assert isinstance(result, list)


@given(st.binary())
@settings(max_examples=200)
def test_parse_branches_never_crashes(data: bytes) -> None:
    result = parse_branches(data)
    assert isinstance(result, list)


@given(st.binary())
@settings(max_examples=200)
def test_parse_remote_branches_never_crashes(data: bytes) -> None:
    result = parse_remote_branches(data)
    assert isinstance(result, list)


@given(st.binary())
@settings(max_examples=200)
def test_parse_diff_never_crashes(data: bytes) -> None:
    result = parse_diff_text(data)
    assert isinstance(result, str)


@given(st.binary())
@settings(max_examples=200)
def test_parse_conflicts_never_crashes(data: bytes) -> None:
    result = parse_conflict_paths(data)
    assert isinstance(result, list)


@given(st.text())
@settings(max_examples=100)
def test_parse_diff_handles_unicode(text: str) -> None:
    data = text.encode("utf-8")
    result = parse_diff_text(data)
    assert result == text


@given(st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10))
@settings(max_examples=100)
def test_parse_log_handles_structured_records(fields: list[str]) -> None:
    record = "\x1f".join(fields) + "\x1e"
    data = record.encode("utf-8")
    result = parse_log_records(data)
    assert isinstance(result, list)


@given(st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=5))
@settings(max_examples=100)
def test_parse_branches_handles_pipe_separated(fields: list[str]) -> None:
    line = "|".join(fields)
    data = line.encode("utf-8")
    result = parse_branches(data)
    assert isinstance(result, list)
