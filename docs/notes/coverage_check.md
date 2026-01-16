# coverage_check Notes

Purpose
- Enforce per-file coverage >= 90% using coverage.json output.

Flowchart

[coverage json]
        |
        v
[parse file summaries]
        |
        v
[fail if any file < 90%]
