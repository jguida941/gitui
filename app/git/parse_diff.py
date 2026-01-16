from __future__ import annotations


def parse_diff_text(payload: bytes) -> str:
    """Return diff output as text.

    We keep raw diff text for now; structured parsing is optional.
    """
    return payload.decode("utf-8", errors="replace")
