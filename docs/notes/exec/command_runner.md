# CommandRunner Notes

Purpose
- CommandRunner is the single gateway for running external commands.
- It owns QProcess, buffers stdout/stderr, and emits lifecycle signals.
- UI does not touch QProcess directly.

Glossary
- CommandSpec: a "recipe" for a command (args, cwd, env).
- RunHandle: a small immutable label for one running command.
- CommandResult: the final output (exit code, stdout, stderr, duration).
- QProcess: Qt object that runs a child process asynchronously.

Why monotonic time
- We use a monotonic clock for durations so time never goes backward.
- That avoids negative or wrong durations if the system clock changes.

Internal state (maps)
- _processes[run_id] -> QProcess
  Keeps the process alive and lets us look it up when signals fire.
- _handles[run_id] -> RunHandle
  Lets us map events to the correct run.
- _stdout_buffers[run_id] / _stderr_buffers[run_id]
  Accumulates output to build a CommandResult at the end.

Signal lifecycle
- command_started(handle)
- command_stdout(handle, bytes)
- command_stderr(handle, bytes)
- command_finished(handle, CommandResult)

Flowchart: run()

[call run(spec)]
        |
        v
  [validate args]
        |
        v
  [_new_handle(spec)] ---> [store handle]
        |
        v
  [create QProcess]
        |
        v
  [set cwd/env]
        |
        v
  [connect signals]
        |
        v
   [start process]
        |
        v
  emit command_started(handle)

Flowchart: stdout/stderr

QProcess stdout ready
        |
        v
   _on_stdout(run_id)
        |
        v
  read stdout bytes
        |
        v
  buffer + emit command_stdout

QProcess stderr ready
        |
        v
   _on_stderr(run_id)
        |
        v
  read stderr bytes
        |
        v
  buffer + emit command_stderr

Flowchart: finished

QProcess finished
        |
        v
 _on_finished(run_id, exit_code)
        |
        v
  compute duration (monotonic)
        |
        v
  build CommandResult
        |
        v
  emit command_finished(handle, result)
        |
        v
  cleanup maps + deleteLater()

Cancel / Kill
- cancel(handle) -> terminate() requests a graceful exit.
- kill(handle) -> kill() forces immediate termination.

Common questions
- Why not subprocess? We use QProcess to stay async and Qt-native.
- Why store processes? If we don't keep references, Qt can GC them.
- Why buffers? We want both streaming output and a final result.
