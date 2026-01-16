# parse_log Notes

Purpose
- Decode structured git log records into Commit objects.

Record format
- Each record uses field separators (\x1f) and record separators (\x1e).
- Fields: oid, parents, author_name, author_email, author_date, subject.

Parsing flow

[decode bytes to text]
        |
        v
[split records by \x1e]
        |
        v
[split fields by \x1f]
        |
        v
[build Commit list]

Notes
- Empty record (after trailing \x1e) is skipped.
- Parent list is space-separated; empty string means root commit.
