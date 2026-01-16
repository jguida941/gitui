from __future__ import annotations

from app.core.models import BranchInfo, FileChange, RepoStatus

# ─────────────────────────────────────────────────────────────────────────────
# Git Status Porcelain v2 Parser
#
# This parses `git status --porcelain=v2 -b -z` output, which is a stable
# machine-readable format. The -z flag uses NUL as record separator (not \n)
# to handle filenames with special characters safely.
#
# Record types we handle:
#   # branch.* - Branch header lines (name, oid, upstream, ahead/behind)
#   1          - Ordinary changed entries (modified, added, deleted)
#   2          - Rename/copy entries (path changed, has orig_path in next record)
#   u          - Unmerged (conflicted) entries
#   ?          - Untracked files
#   !          - Ignored files (we skip these)
#
# XY status codes (e.g., "MM", "A.", ".D"):
#   X = staged status (index vs HEAD)
#   Y = unstaged status (worktree vs index)
#   . = no change in that area
#
# Reference: https://git-scm.com/docs/git-status#_porcelain_format_version_2
# ─────────────────────────────────────────────────────────────────────────────


def parse_status_porcelain_v2(payload: bytes) -> RepoStatus:
    """Parse `git status --porcelain=v2 -b -z` output.

    Returns a RepoStatus with grouped lists for staged, unstaged, untracked,
    and conflicted files.
    """
    staged: list[FileChange] = []
    unstaged: list[FileChange] = []
    untracked: list[FileChange] = []
    conflicted: list[FileChange] = []

    # Branch metadata (optional; may be absent for some repos).
    branch_name: str | None = None
    branch_oid: str | None = None
    branch_upstream: str | None = None
    ahead = 0
    behind = 0
    branch_seen = False

    def split_xy(xy: str) -> tuple[str, str]:
        """Return (staged, unstaged) status codes from XY."""
        if len(xy) >= 2:
            return xy[0], xy[1]
        return ".", "."

    def add_by_xy(change: FileChange, xy: str) -> None:
        """Append a change into staged/unstaged lists based on XY codes."""
        staged_code, unstaged_code = split_xy(xy)
        if staged_code != ".":
            staged.append(change)
        if unstaged_code != ".":
            unstaged.append(change)

    # Split by NUL (\x00) since -z flag uses it as separator.
    # This is safer than newline for filenames with special characters.
    records = payload.split(b"\x00")
    i = 0

    # Process each record. We use index-based iteration because rename/copy
    # entries consume the next record for the original path.
    while i < len(records):
        record = records[i]
        if not record:
            i += 1
            continue

        line = record.decode("utf-8", errors="replace")

        # ───── Branch header lines (start with "# ") ─────
        if line.startswith("# "):
            branch_seen = True
            parts = line.split(" ", 2)
            if len(parts) < 3:
                i += 1
                continue

            key = parts[1]
            value = parts[2]
            if key == "branch.oid":
                if value not in {"(initial)", "(unknown)"}:
                    branch_oid = value
            elif key == "branch.head":
                if value not in {"(detached)", "(unknown)"}:
                    branch_name = value
            elif key == "branch.upstream":
                branch_upstream = value
            elif key == "branch.ab":
                # Format: "+<ahead> -<behind>"
                for token in value.split():
                    if token.startswith("+"):
                        try:
                            ahead = int(token[1:])
                        except ValueError:
                            ahead = 0
                    elif token.startswith("-"):
                        try:
                            behind = int(token[1:])
                        except ValueError:
                            behind = 0

            i += 1
            continue

        # First character identifies the record type.
        record_type = line[0]

        # ───── Type "1": Ordinary changed entry ─────
        # Format: 1 <XY> <sub> <mH> <mI> <mW> <hH> <hI> <path>
        if record_type == "1":
            parts = line.split(" ", 8)
            xy = parts[1] if len(parts) > 1 else ".."  # XY status codes
            path = parts[8] if len(parts) > 8 else ""  # File path is last field
            change = FileChange(
                path=path,
                staged_status=split_xy(xy)[0],
                unstaged_status=split_xy(xy)[1],
            )
            add_by_xy(change, xy)

        # ───── Type "2": Rename/copy entry ─────
        # Format: 2 <XY> <sub> <mH> <mI> <mW> <hH> <hI> <X><score> <path><sep><origPath>
        # The original path is in the NEXT record (separated by NUL).
        elif record_type == "2":
            parts = line.split(" ", 9)
            xy = parts[1] if len(parts) > 1 else ".."
            path = parts[9] if len(parts) > 9 else ""
            # Read the original path from the next NUL-separated record.
            orig_path = None
            if i + 1 < len(records) and records[i + 1]:
                orig_path = records[i + 1].decode("utf-8", errors="replace")
                i += 1  # Skip the orig_path record in the next iteration
            change = FileChange(
                path=path,
                staged_status=split_xy(xy)[0],
                unstaged_status=split_xy(xy)[1],
                orig_path=orig_path,
            )
            add_by_xy(change, xy)

        # ───── Type "u": Unmerged/conflicted entry ─────
        # These appear during merge conflicts. Format has more fields for
        # tracking the three-way merge state (stage 1, 2, 3).
        elif record_type == "u":
            parts = line.split(" ", 10)
            xy = parts[1] if len(parts) > 1 else "UU"  # UU = both modified
            path = parts[10] if len(parts) > 10 else ""
            change = FileChange(
                path=path,
                staged_status=split_xy(xy)[0],
                unstaged_status=split_xy(xy)[1],
            )
            conflicted.append(change)

        # ───── Type "?": Untracked file ─────
        # Simple format: just "? <path>" with no status codes.
        elif record_type == "?":
            path = line[2:] if len(line) > 2 else ""  # Skip "? " prefix
            change = FileChange(path=path, staged_status="?", unstaged_status="?")
            untracked.append(change)

        # Ignored files ('!') and unknown records are skipped for now.

        i += 1

    branch = None
    if branch_seen or branch_name or branch_oid or branch_upstream or ahead or behind:
        branch = BranchInfo(
            name=branch_name,
            head_oid=branch_oid,
            upstream=branch_upstream,
            ahead=ahead,
            behind=behind,
        )

    return RepoStatus(
        branch=branch,
        staged=staged,
        unstaged=unstaged,
        untracked=untracked,
        conflicted=conflicted,
    )
