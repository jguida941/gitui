from __future__ import annotations

import runpy
import sys

import pytest

from app import main as app_main


def test_main_returns_zero() -> None:
    assert app_main.main(["--no-gui"]) == 0


def test_main_module_exit_code() -> None:
    sys.modules.pop("app.main", None)
    sys.argv = ["app.main", "--no-gui"]
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("app.main", run_name="__main__")

    assert exc_info.value.code == 0
