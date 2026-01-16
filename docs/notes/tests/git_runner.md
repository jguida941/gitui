# tests_git_runner Notes

Purpose
- Verify GitRunner merges default env and builds a CommandSpec.

Flowchart: test_git_runner_builds_command_spec_with_defaults

[GitRunner.run]
        |
        v
[merge env + build CommandSpec]
        |
        v
[FakeCommandRunner captures spec]
