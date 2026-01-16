# tests_parse_status Notes

Purpose
- Validate porcelain v2 status parsing for key record types.

Flowchart: test_parse_status_basic_lists

[build payload with branch + 1/?, entries]
        |
        v
[parse_status_porcelain_v2]
        |
        v
[assert branch fields]
        |
        v
[assert staged/unstaged/untracked lists]

Flowchart: test_parse_status_rename_and_conflict

[build payload with rename + unmerged]
        |
        v
[parse_status_porcelain_v2]
        |
        v
[assert orig_path + conflicted list]

Flowchart: test_parse_status_paths_with_spaces_and_newlines

[build payload with spaced + newline paths]
        |
        v
[parse_status_porcelain_v2]
        |
        v
[assert staged/untracked paths preserved]
