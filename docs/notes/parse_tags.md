# parse_tags Notes

Purpose
- Parse `git tag --list` output into Tag objects.

Flowchart: parse_tags

[tags list bytes]
        |
        v
[decode + splitlines]
        |
        v
[strip empty lines]
        |
        v
[Tag objects]
