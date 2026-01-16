# qt_compat Notes

Purpose
- Allow backend modules to import Qt types when PySide6 is missing during tests.
 - Provide a forced fallback path for coverage and local testing.

Behavior
- If PySide6 is installed, export real QObject/Signal/QProcess.
- If missing (or if `GITUI_FORCE_QT_FALLBACK=1`), export lightweight stubs for
  QObject/Signal and a QProcess placeholder that raises on use.

Flowchart: module import

[import app.utils.qt_compat]
        |
        v
[try PySide6 import]
   |            \
   v             v
[success]     [ModuleNotFound]
   |             |
   v             v
[real Qt types] [stub types + raise-on-use QProcess]
