# CommandQueue Notes

Purpose
- Serialize commands and coalesce background refreshes.
- Prefer user actions over background tasks.

Rules
- Only one command runs at a time.
- Background items with the same key are coalesced (newest wins).
- User items are preferred when both types are queued.
- The queued action should call mark_idle() when finished.

Flowchart: enqueue(background)

[enqueue background item]
        |
        v
[remove older items with same key]
        |
        v
[append to queue]
        |
        v
[start if idle]

Flowchart: enqueue(user)

[enqueue user item]
        |
        v
[append to queue]
        |
        v
[start if idle]
