# parse_remote_branches Notes

Purpose
- Decode `git branch -r --format=...` output into RemoteBranch objects.

Rules
- Skip blank lines and symbolic HEAD entries (e.g., origin/HEAD).
- Split `remote/name` at the first slash.

Parsing flow

[decode bytes to text]
        |
        v
[split lines by \n]
        |
        v
[filter blanks + origin/HEAD]
        |
        v
[split remote/name]
        |
        v
[build RemoteBranch list]
