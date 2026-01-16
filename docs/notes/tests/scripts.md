# tests_scripts Notes

Purpose
- Validate helper scripts (coverage gate + smoke test) without running real git.

Flowchart: test_check_coverage_passes

[write coverage.json]
        |
        v
[check_coverage.main]
        |
        v
[assert exit code 0]
