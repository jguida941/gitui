from app.exec.command_queue import CommandQueue, QueueItem, QueuePriority


def test_queue_coalesces_background_items() -> None:
    queue = CommandQueue()
    ran: list[str] = []

    queue.mark_running()

    queue.enqueue(
        QueueItem(
            key="refresh",
            run=lambda: (ran.append("first"), queue.mark_idle()),
            priority=QueuePriority.BACKGROUND,
        )
    )
    queue.enqueue(
        QueueItem(
            key="refresh",
            run=lambda: (ran.append("second"), queue.mark_idle()),
            priority=QueuePriority.BACKGROUND,
        )
    )

    queue.mark_idle()
    assert ran == ["second"]


def test_queue_prefers_user_priority() -> None:
    queue = CommandQueue()
    ran: list[str] = []

    queue.mark_running()

    queue.enqueue(
        QueueItem(
            key="refresh",
            run=lambda: (ran.append("background"), queue.mark_idle()),
            priority=QueuePriority.BACKGROUND,
        )
    )
    queue.enqueue(
        QueueItem(
            key="stage",
            run=lambda: (ran.append("user"), queue.mark_idle()),
            priority=QueuePriority.USER,
        )
    )

    queue.mark_idle()
    assert ran[0] == "user"
