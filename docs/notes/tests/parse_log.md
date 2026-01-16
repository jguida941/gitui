# tests_parse_log Notes

Purpose
- Validate log parsing with record/field separators.

Flowchart: test_parse_log_records_basic

[build payload with two records]
        |
        v
[parse_log_records]
        |
        v
[assert commit fields and parents list]
