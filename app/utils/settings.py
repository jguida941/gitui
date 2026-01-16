from __future__ import annotations


class SettingsStore:
    """Simple in-memory settings store used until QSettings is wired in."""

    def __init__(self) -> None:
        # Keep config in a dict so tests can exercise settings without Qt.
        self._values: dict[str, str] = {}

    def get(self, key: str, default: str | None = None) -> str | None:
        """Return a setting value or default if missing."""
        return self._values.get(key, default)

    def set(self, key: str, value: str) -> None:
        """Store a setting value."""
        self._values[key] = value
