# parse_branches Notes

Purpose
- Decode `git branch --format=...` output into Branch objects.

Format
- name|HEAD|upstream|upstream:track
- HEAD is '*' for current branch, empty otherwise.
- track values can be [ahead N], [behind N], [ahead N, behind M], or [gone].

Parsing flow

[decode bytes to text]
        |
        v
[split lines by \n]
        |
        v
[split fields by '|']
        |
        v
[parse track into ahead/behind/gone]
        |
        v
[build Branch list]
