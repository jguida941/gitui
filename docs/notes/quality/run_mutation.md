# run_mutation Notes

Purpose
- Wrapper script for mutmut using pyproject configuration.
- Target mutation kill rate >= 90% and triage survivors.

Notes
- Mutmut skips tests marked `qprocess` to avoid Qt/QProcess crashes.

Flowchart

[run script]
        |
        v
[mutmut run]
        |
        v
[mutmut results]
