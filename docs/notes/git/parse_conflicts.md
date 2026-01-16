# parse_conflicts Notes

Purpose
- Parse conflicted file paths from `git diff --name-only --diff-filter=U`.

Flowchart: parse_conflict_paths

[conflict list bytes]
        |
        v
[decode + splitlines]
        |
        v
[strip blanks]
        |
        v
[list[str] paths]
