# ui_repo_picker Notes

Purpose
- Collect a repo path and emit a request to open it.
- Provide a browse button to avoid typing paths.

Flowchart: open repo

[user enters path + clicks Open]
        |
        v
[emit repo_opened(path)]

Flowchart: browse

[user clicks browse]
        |
        v
[QFileDialog returns directory]
        |
        v
[set line edit]
