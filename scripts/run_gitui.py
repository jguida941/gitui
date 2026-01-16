#!/usr/bin/env python3
"""Launch GitUI with correct Python path."""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Set up paths before any app imports
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

if __name__ == "__main__":
    from app.main import main
    raise SystemExit(main())
