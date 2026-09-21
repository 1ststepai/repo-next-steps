#!/usr/bin/env python3
"""Same as `python3 -m repo_next_steps` — inspect a public GitHub repo."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from repo_next_steps.engine import main

if __name__ == "__main__":
    raise SystemExit(main())
