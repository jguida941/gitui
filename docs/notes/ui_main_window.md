# ui_main_window Notes

Purpose
- Compose the main UI layout and wire signals to the controller.
- Stream CommandRunner output into the console.

Flowchart: init

[build controller stack]
        |
        v
[construct widgets]
        |
        v
[wire signals + refresh state]

Flowchart: refresh

[RepoState changed]
        |
        v
[update repo picker + status + diff + title]
