from __future__ import annotations

import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Configure a simple root logger for CLI/debug use.

    We avoid multiple handlers so repeated setup calls stay idempotent.
    """
    root = logging.getLogger()
    if root.handlers:
        return
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")
