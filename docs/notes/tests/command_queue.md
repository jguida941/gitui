# tests_command_queue Notes

Purpose
- Validate background coalescing and user-priority scheduling.

Flowchart: test_queue_coalesces_background_items

[mark queue running]
        |
        v
[enqueue refresh #1]
        |
        v
[enqueue refresh #2]
        |
        v
[older refresh dropped]
        |
        v
[mark idle -> run newest refresh]

Flowchart: test_queue_prefers_user_priority

[mark queue running]
        |
        v
[enqueue background]
        |
        v
[enqueue user]
        |
        v
[mark idle -> user runs first]
