# tests_parsers_property Notes

Purpose
- Property tests ensure parsers handle arbitrary input without crashing.

Flowchart: test_parse_status_never_crashes

[generate random bytes]
        |
        v
[parse_status_porcelain_v2]
        |
        v
[assert result shape]
