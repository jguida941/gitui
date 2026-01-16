from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from app.utils.qt_compat import QObject, Signal

# ─────────────────────────────────────────────────────────────────────────────
# CommandQueue: Serializes git commands to prevent race conditions.
#
# Why we need this:
#   - Git operations can conflict if run concurrently (e.g., two commits)
#   - User actions should not be blocked by background refreshes
#   - Background refreshes should coalesce (only run the latest one)
#
# How it works:
#   - Commands are added to a queue with a priority (USER or BACKGROUND)
#   - USER priority commands always run before BACKGROUND ones
#   - BACKGROUND commands with the same key coalesce (keep newest)
#   - Only one command runs at a time; next starts when current finishes
#
# Example flow:
#   1. User clicks "refresh" -> BACKGROUND refresh_status queued
#   2. User clicks "refresh" again -> old refresh replaced with new one
#   3. User clicks "commit" -> USER commit queued, runs first
#   4. Commit finishes -> background refresh runs
# ─────────────────────────────────────────────────────────────────────────────


class QueuePriority(Enum):
    """Priority buckets for queued actions."""

    USER = "user"  # User-initiated actions (stage, commit, push)
    BACKGROUND = "background"  # Automatic refreshes (status, log, branches)


@dataclass(frozen=True)
class QueueItem:
    """Queued command action with an optional coalesce key."""

    key: str  # Identifier for coalescing (e.g., "refresh_status")
    run: Callable[[], object]  # Function to execute when this item runs
    priority: QueuePriority  # USER runs before BACKGROUND


class CommandQueue(QObject):
    """Serializes command execution and coalesces background refreshes."""

    # Emitted whenever the queue state changes (for UI updates).
    queue_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._running = False  # True while a command is executing
        self._queue: list[QueueItem] = []  # Pending items waiting to run

    @property
    def running(self) -> bool:
        """True when a command is currently running."""
        return self._running

    def enqueue(self, item: QueueItem) -> None:
        """Add a command to the queue, coalescing by key for background tasks."""
        if item.priority == QueuePriority.BACKGROUND:
            # Background tasks coalesce: if there's already a pending task with
            # the same key, replace it with this newer one. This prevents
            # queueing multiple redundant refreshes.
            self._queue = [q for q in self._queue if q.key != item.key]

        self._queue.append(item)
        self.queue_changed.emit()
        # Try to run immediately if nothing else is running.
        self._try_start_next()

    def mark_running(self) -> None:
        """Mark the queue as running (called externally to block queue)."""
        self._running = True
        self.queue_changed.emit()

    def mark_idle(self) -> None:
        """Mark the queue as idle and start the next command if any."""
        self._running = False
        self.queue_changed.emit()
        # Check if there's another command waiting to run.
        self._try_start_next()

    def _try_start_next(self) -> None:
        """Start the next queued item if not currently running."""
        if self._running or not self._queue:
            return

        # USER priority items always run before BACKGROUND ones.
        # This ensures user actions aren't blocked by pending refreshes.
        user_items = [q for q in self._queue if q.priority == QueuePriority.USER]
        item = user_items[0] if user_items else self._queue[0]
        self._queue.remove(item)

        self._running = True
        self.queue_changed.emit()
        # Run the item. It's responsible for calling mark_idle() when done
        # (typically via _on_command_finished in the controller).
        item.run()
