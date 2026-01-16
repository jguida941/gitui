# Insights + Analytics Notes

Purpose
- Capture the Git+ features that go beyond the core git flows.
- Keep analytics derived from git CLI output (no new deps without ADR).

Inputs
- `git log --date=iso-strict --pretty=format:... --numstat`
- `git shortlog -sne`
- `git for-each-ref --format=...`
- `git reflog`

Outputs
- Commit graph lanes for history navigation.
- Activity timeline, churn/hot files, and author stats.
- Repo health flags (unpushed, stale branches, missing upstreams).
- Release notes drafts from commit subjects and tags.
- File history + blame view with author context.

Flowchart: insights pipeline

[git commands] -> [parse records] -> [aggregate stats] -> [render tables/charts] -> [export CSV/JSON]
