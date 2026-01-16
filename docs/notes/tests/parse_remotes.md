# tests_parse_remotes Notes

Purpose
- Validate remote parsing for fetch/push URLs.

Flowchart: test_parse_remotes_fetch_and_push

[build payload with origin + upstream]
        |
        v
[parse_remotes]
        |
        v
[assert fetch/push URLs]

Flowchart: test_parse_remotes_skips_unknown_and_short_lines

[payload with short + unknown kind]
        |
        v
[parse_remotes]
        |
        v
[assert unknown lines skipped]

Flowchart: test_parse_remotes_merges_fetch_and_push_urls

[payload with fetch + push lines]
        |
        v
[parse_remotes]
        |
        v
[assert merged Remote]
