# tests_parse_branches Notes

Purpose
- Validate branch list parsing for current/upstream/track cases.

Flowchart: test_parse_branches_basic

[build payload with main/feature/topic]
        |
        v
[parse_branches]
        |
        v
[assert is_current/upstream/ahead/behind]

Flowchart: test_parse_branches_gone

[build payload with [gone]]
        |
        v
[parse_branches]
        |
        v
[assert gone == True]

Flowchart: test_parse_branches_ignores_empty_lines_and_bad_counts

[payload with empty line + invalid ahead/behind]
        |
        v
[parse_branches]
        |
        v
[assert counts default to 0]

Flowchart: test_parse_branches_handles_unbracketed_track

[payload without brackets]
        |
        v
[parse_branches]
        |
        v
[assert ahead/behind parsed]
