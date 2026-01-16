# command_models Notes

Purpose
- Define immutable data carriers for command execution.
- Immutability keeps run metadata safe to share across layers.

Flowchart: command lifecycle

[CommandSpec]
        |
        v
[CommandRunner.run]
        |
        v
[RunHandle]
        |
        v
[CommandResult]
