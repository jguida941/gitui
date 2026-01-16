# parse_remotes Notes

Purpose
- Parse `git remote -v` output into Remote objects.
- Captures fetch/push URLs per remote name.

Parsing rules
- Each line: <name> <url> (fetch|push)
- Unknown kinds are ignored.
- Results are grouped by remote name.

Flowchart: parse_remotes

[remote -v bytes]
        |
        v
[decode + splitlines]
        |
        v
[parse name/url/kind]
        |
        v
[group fetch/push by name]
        |
        v
[list[Remote]]
