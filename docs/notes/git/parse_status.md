# parse_status Notes

Purpose
- Decode `git status --porcelain=v2 -b -z` output into RepoStatus.
- Group changes into staged, unstaged, untracked, and conflicted lists.

Key record types
- `#` branch headers: branch.oid, branch.head, branch.upstream, branch.ab.
- `1` ordinary changes (XY status + path).
- `2` rename/copy (XY status + path + orig_path).
- `u` unmerged/conflict entries.
- `?` untracked files.

Parsing flow

[split payload by NUL]
        |
        v
[parse branch headers]
        |
        v
[parse record types (1/2/u/?)]
        |
        v
[build FileChange lists]
        |
        v
[assemble RepoStatus + BranchInfo]

Notes
- Rename/copy records consume the next NUL token for orig_path.
- Paths may contain spaces, so we use maxsplit to preserve them.
