# parse_diff Notes

Purpose
- Keep diff output as raw text for the initial UI.

Parsing flow

[raw bytes]
    |
    v
[decode utf-8 with replacement]
    |
    v
[text displayed in UI]
