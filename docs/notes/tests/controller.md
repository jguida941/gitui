# tests_controller Notes

Purpose
- Validate RepoController error handling and status flow without real git.

Flowchart: test_refresh_status_without_repo_sets_error

[RepoController.refresh_status]
        |
        v
[NotARepo set on state]

Flowchart: test_open_repo_success_triggers_status_refresh

[open_repo]
        |
        v
[pending validate_repo]
        |
        v
[simulate command_finished ok]
        |
        v
[repo_path set + refresh_status called]

Flowchart: test_status_result_updates_state

[refresh_status]
        |
        v
[simulate command_finished ok]
        |
        v
[state.status set]

Flowchart: test_log_result_updates_state

[refresh_log]
        |
        v
[simulate command_finished ok]
        |
        v
[state.log set]

Flowchart: test_branches_result_updates_state

[refresh_branches]
        |
        v
[simulate command_finished ok]
        |
        v
[state.branches set]

Flowchart: test_stage_triggers_status_refresh

[stage]
        |
        v
[simulate command_finished ok]
        |
        v
[refresh_status enqueued + status_raw called]

Flowchart: test_fetch_triggers_branches_refresh

[fetch]
        |
        v
[simulate command_finished ok]
        |
        v
[refresh_branches enqueued + branches_raw called]

Flowchart: test_pull_triggers_status_refresh

[pull_ff_only]
        |
        v
[simulate command_finished ok]
        |
        v
[refresh_status enqueued + status_raw called]

Flowchart: test_push_triggers_branches_refresh

[push]
        |
        v
[simulate command_finished ok]
        |
        v
[refresh_branches enqueued + branches_raw called]

Flowchart: test_open_repo_false_sets_error

[open_repo]
        |
        v
[simulate command_finished stdout=false]
        |
        v
[NotARepo set on state]

Flowchart: test_failed_command_sets_command_failed

[refresh_status]
        |
        v
[simulate command_finished exit_code!=0]
        |
        v
[CommandFailed set on state]

Flowchart: test_parse_error_sets_parse_error

[refresh_status]
        |
        v
[parse_status raises]
        |
        v
[ParseError set on state]

Flowchart: test_stashes_result_updates_state

[refresh_stashes]
        |
        v
[simulate command_finished ok]
        |
        v
[state.stashes set]

Flowchart: test_tags_result_updates_state

[refresh_tags]
        |
        v
[simulate command_finished ok]
        |
        v
[state.tags set]

Flowchart: test_remotes_result_updates_state

[refresh_remotes]
        |
        v
[simulate command_finished ok]
        |
        v
[state.remotes set]

Flowchart: test_conflicts_result_updates_state

[refresh_conflicts]
        |
        v
[simulate command_finished ok]
        |
        v
[state.conflicts set]

Flowchart: test_request_diff_updates_state

[request_diff]
        |
        v
[simulate command_finished ok]
        |
        v
[state.diff_text set]

Flowchart: test_methods_require_repo_path

[call controller method with no repo]
        |
        v
[NotARepo set on state]

Flowchart: test_methods_call_service

[call controller method with repo]
        |
        v
[service method invoked]

Flowchart: test_commit_triggers_status_and_log_refresh

[commit]
        |
        v
[simulate command_finished ok]
        |
        v
[refresh_status + refresh_log invoked]

Flowchart: test_stash_actions_refresh

[stash action]
        |
        v
[simulate command_finished ok]
        |
        v
[refresh_status and/or refresh_stashes]

Flowchart: test_remote_actions_refresh_remotes

[remote action]
        |
        v
[simulate command_finished ok]
        |
        v
[refresh_remotes invoked]

Flowchart: test_set_upstream_refreshes_branches

[set_upstream]
        |
        v
[simulate command_finished ok]
        |
        v
[refresh_branches invoked]
