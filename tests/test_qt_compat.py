from __future__ import annotations

import importlib

import pytest

import app.utils.qt_compat as qt_compat


def test_qt_compat_fallback_signal(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITUI_FORCE_QT_FALLBACK", "1")
    fallback = importlib.reload(qt_compat)

    class Dummy(fallback.QObject):
        ping = fallback.Signal()

    called: list[int] = []
    instance = Dummy()
    instance.ping.connect(lambda value: called.append(value))
    instance.ping.emit(123)

    assert called == [123]

    monkeypatch.delenv("GITUI_FORCE_QT_FALLBACK", raising=False)
    importlib.reload(qt_compat)


def test_qt_compat_uses_pyside6_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITUI_FORCE_QT_FALLBACK", raising=False)
    module = importlib.reload(qt_compat)

    if not module.PYSIDE6_AVAILABLE:
        pytest.skip("PySide6 not installed")

    instance = module.QObject()
    assert isinstance(instance, module.QObject)
