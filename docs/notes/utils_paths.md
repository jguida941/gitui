# utils_paths Notes

Purpose
- Normalize user-provided paths so git calls are consistent.

Flowchart: expand_path

[input path]
        |
        v
[expand ~ + absolutize]
        |
        v
[normalized path]
