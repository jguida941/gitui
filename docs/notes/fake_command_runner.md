# FakeCommandRunner Notes

Purpose
- FakeCommandRunner is a test double for CommandRunner.
- It records CommandSpec inputs and returns a deterministic RunHandle.

Why it exists
- Tests should not launch real processes.
- We can assert the intent layer builds the correct CommandSpec.

Flowchart: run(spec)

[call run(spec)]
        |
        v
[record spec in calls list]
        |
        v
[create RunHandle with run_id]
        |
        v
[return handle]
