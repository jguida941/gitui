from __future__ import annotations

from app.git.parse_diff import parse_diff_text


def test_parse_diff_text_basic() -> None:
    payload = b"diff --git a/file.txt b/file.txt\n@@ -1 +1 @@\n-old\n+new"
    result = parse_diff_text(payload)
    assert "diff --git" in result
    assert "-old" in result
    assert "+new" in result


def test_parse_diff_text_empty() -> None:
    result = parse_diff_text(b"")
    assert result == ""


def test_parse_diff_text_utf8() -> None:
    payload = "diff\n+emoji: 🔥".encode()
    result = parse_diff_text(payload)
    assert "🔥" in result


def test_parse_diff_text_invalid_utf8_replaced() -> None:
    payload = b"diff\n\xff\xfe invalid bytes"
    result = parse_diff_text(payload)
    assert "diff" in result
    assert "invalid bytes" in result


def test_parse_diff_text_multiline() -> None:
    payload = b"line1\nline2\nline3"
    result = parse_diff_text(payload)
    assert result == "line1\nline2\nline3"
