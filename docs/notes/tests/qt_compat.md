# tests_qt_compat Notes

Purpose
- Exercise Qt compatibility fallbacks and PySide6 availability.

Flowchart: test_qt_compat_fallback_signal

[force fallback]
        |
        v
[Signal emits -> handler list]
        |
        v
[assert handler called]
