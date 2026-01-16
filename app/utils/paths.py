from __future__ import annotations

import os


def expand_path(path: str) -> str:
    """Normalize paths so git commands always receive absolute paths."""
    return os.path.abspath(os.path.expanduser(path))
