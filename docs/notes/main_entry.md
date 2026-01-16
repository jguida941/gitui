# main Entry Notes

Purpose
- Launch the Qt application and wire the core controller stack.
- Provide a `--no-gui` path for tests and automation.
- Allow `--repo` to open a path on startup.

Flowchart: main()

[parse args]
        |
        v
[--no-gui?]
   |        \
  yes       no
   |         \
   v          v
[return 0] [QApplication + MainWindow]
               |
               v
       [show + exec]
