# GitService Notes

Purpose
- GitService is the intent layer: it defines "what we want to do" in git.
- It also owns parsing helpers so controllers do not parse directly.

Current intents (raw)
- status_raw(repo_path)
- diff_file_raw(repo_path, path, staged)
- stage(repo_path, paths)
- unstage(repo_path, paths)
- discard(repo_path, paths)
- commit(repo_path, message, amend)
- fetch(repo_path)
- pull_ff_only(repo_path)
- push(repo_path, set_upstream, remote, branch)
- log_raw(repo_path, limit)
- branches_raw(repo_path)
- conflicts_raw(repo_path)
- stash_list_raw(repo_path)
- stash_save(repo_path, message, include_untracked)
- stash_apply(repo_path, ref)
- stash_pop(repo_path, ref)
- stash_drop(repo_path, ref)
- tags_raw(repo_path)
- create_tag(repo_path, name, ref)
- delete_tag(repo_path, name)
- push_tag(repo_path, name, remote)
- push_tags(repo_path, remote)
- remotes_raw(repo_path)
- add_remote(repo_path, name, url)
- remove_remote(repo_path, name)
- set_remote_url(repo_path, name, url)
- set_upstream(repo_path, upstream, branch)
- switch_branch(repo_path, name)
- create_branch(repo_path, name, from_ref)
- delete_branch(repo_path, name, force)
- is_inside_work_tree_raw(repo_path)
- version_raw()

Parsing helpers
- parse_status(payload) -> RepoStatus
- parse_log(payload) -> list[Commit]
- parse_diff(payload) -> str
- parse_branches(payload) -> list[Branch]
- parse_conflicts(payload) -> list[str]
- parse_stashes(payload) -> list[StashEntry]
- parse_tags(payload) -> list[Tag]
- parse_remotes(payload) -> list[Remote]

Formats
- LOG_FORMAT: record/field separators for log parsing.
- STASH_FORMAT: record/field separators for stash parsing.

Flowchart: status_raw()

[call status_raw(repo_path)]
        |
        v
[build args for porcelain v2]
        |
        v
[GitRunner.run(args, cwd=repo_path)]
        |
        v
[return RunHandle]

Flowchart: parse_status()

[raw status bytes]
        |
        v
[parse_status_porcelain_v2]
        |
        v
[RepoStatus]
