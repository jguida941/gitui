# tests_git_service Notes

Purpose
- Validate that GitRunner and GitService build correct CommandSpec args.
- Avoid real processes by using FakeCommandRunner.

Covered cases
- GitRunner default env injection.
- status_raw uses porcelain v2 args.
- diff_file_raw staged/unstaged paths.
- stage/unstage/discard commands.
- commit and amend flags.
- fetch/pull/push (including upstream).
- log_raw format and branches_raw format.
- conflicts_raw for diff-filter=U.
- branch switch/create/delete.
- stash list/save/apply/pop/drop.
- tag list/create/delete/push.
- remote list/add/remove/set-url/set-upstream.

Flowchart: generic intent test

[create FakeCommandRunner]
        |
        v
[create GitRunner + GitService]
        |
        v
[call intent method]
        |
        v
[assert CommandSpec args and cwd]
