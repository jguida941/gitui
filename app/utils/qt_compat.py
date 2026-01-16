from __future__ import annotations

import os
from collections.abc import Callable


def _build_fallback() -> tuple[type, type, type]:
    """Return minimal Qt stand-ins for test environments without PySide6."""

    class QObject:
        """Minimal QObject stand-in used when PySide6 is unavailable."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            # No Qt behavior; enough for tests to construct objects.
            super().__init__()

    class _SignalInstance:
        """Per-instance signal handler list for the fallback Signal."""

        def __init__(self) -> None:
            self._handlers: list[Callable[..., object]] = []

        def connect(self, handler: Callable[..., object]) -> None:
            """Register a handler for future emits."""
            self._handlers.append(handler)

        def emit(self, *args: object, **kwargs: object) -> None:
            """Invoke handlers in registration order."""
            for handler in list(self._handlers):
                handler(*args, **kwargs)

    class Signal:
        """Descriptor that supplies a per-instance signal replacement."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            self._name: str | None = None

        def __set_name__(self, _owner: type, name: str) -> None:
            self._name = f"__signal_{name}"

        def __get__(self, instance: object, _owner: type | None = None) -> object:
            if instance is None:
                return self
            key = self._name or "__signal"
            signal = instance.__dict__.get(key)
            if signal is None:
                signal = _SignalInstance()
                instance.__dict__[key] = signal
            return signal

    class QProcess:
        """Placeholder QProcess that raises when used without PySide6."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            raise ModuleNotFoundError(
                "PySide6 is required to run QProcess-based commands."
            )

    return QObject, Signal, QProcess


_FORCE_FALLBACK = os.environ.get("GITUI_FORCE_QT_FALLBACK") == "1"

if not _FORCE_FALLBACK:
    try:
        # Prefer real Qt types when PySide6 is installed.
        from PySide6.QtCore import QObject, QProcess, Signal  # type: ignore

        PYSIDE6_AVAILABLE = True
    except ModuleNotFoundError:
        PYSIDE6_AVAILABLE = False
        QObject, Signal, QProcess = _build_fallback()
else:
    PYSIDE6_AVAILABLE = False
    QObject, Signal, QProcess = _build_fallback()
