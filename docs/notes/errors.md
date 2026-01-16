# Errors Notes

Purpose
- Typed errors used by controllers and UI error dialogs.

Errors
- GitUIError: base class.
- CommandFailed: non-zero exit from a command.
- NotARepo: path is not inside a git work tree.
- AuthError: authentication failure.
- ParseError: parsing of git output failed.

Flowchart: command failure

[command_finished with exit_code != 0]
        |
        v
[raise CommandFailed]
        |
        v
[RepoState.last_error updated]
        |
        v
[UI shows error dialog]
