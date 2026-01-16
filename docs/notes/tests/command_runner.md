# tests_command_runner Notes

Purpose
- Exercise QProcess-based command execution and signal flow.
- Use a fake QProcess when PySide6 is unavailable to keep coverage consistent.
- Mark QProcess tests with `qprocess` so mutmut can skip them.

Flowchart: test_command_runner_emits_output_and_result

[CommandRunner.run]
        |
        v
[QProcess emits stdout/stderr]
        |
        v
[command_finished -> CommandResult]
        |
        v
[assert output + exit code]
