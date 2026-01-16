# GitRunner Notes

Purpose
- GitRunner is a thin wrapper around CommandRunner.
- It injects safe defaults (no pager, no prompts, stable locale).

Defaults
- GIT_PAGER=cat (avoid paging output)
- GIT_TERMINAL_PROMPT=0 (fail fast instead of blocking on auth)
- LANG=C.UTF-8 (stable, English-ish output for parsing)

Flowchart: run()

[call GitRunner.run(args, cwd, env)]
        |
        v
  [merge default env + overrides]
        |
        v
  [build CommandSpec with "git" + args]
        |
        v
  [delegate to CommandRunner.run(spec)]
        |
        v
  [return RunHandle]
