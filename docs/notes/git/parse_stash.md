# parse_stash Notes

Purpose
- Parse structured `git stash list` output into StashEntry objects.
- Uses record and field separators to avoid newline ambiguity.

Format
- Each record: oid<US>selector<US>summary<US>date<RS>
- US = unit separator (0x1f), RS = record separator (0x1e).

Flowchart: parse_stash_records

[stash list bytes]
        |
        v
[decode utf-8, replace errors]
        |
        v
[split by record separator]
        |
        v
[split fields by unit separator]
        |
        v
[StashEntry objects]
