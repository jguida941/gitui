# tests_parse_diff Notes

Purpose
- Ensure diff payloads decode to text safely and preserve newlines.

Flowchart: test_parse_diff_text_basic

[bytes diff payload]
        |
        v
[parse_diff_text]
        |
        v
[assert key lines present]
