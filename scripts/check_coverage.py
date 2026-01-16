from __future__ import annotations

import json
import sys
from pathlib import Path

THRESHOLD = 90.0


def main() -> int:
    """Fail if any covered file drops below the per-file coverage threshold."""
    coverage_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("coverage.json")
    if not coverage_path.exists():
        print(f"coverage file not found: {coverage_path}")
        return 2

    data = json.loads(coverage_path.read_text(encoding="utf-8"))
    files = data.get("files", {})

    failures: list[tuple[str, float]] = []
    for path, info in files.items():
        summary = info.get("summary", {})
        percent = float(summary.get("percent_covered", 0.0))
        if percent < THRESHOLD:
            failures.append((path, percent))

    if failures:
        print(f"Per-file coverage below {THRESHOLD:.1f}%:")
        for path, percent in sorted(failures, key=lambda item: item[1]):
            print(f"  {percent:6.2f}%  {path}")
        return 1

    print(f"All files meet per-file coverage >= {THRESHOLD:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
