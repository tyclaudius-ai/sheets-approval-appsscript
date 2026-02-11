#!/usr/bin/env python3
"""One-command screenshots pipeline.

Runs, in order:
  1) Placeholder detection (docs/screenshots/*.png vs docs/screenshots/png/*.png)
  2) Gallery regeneration (docs/screenshots/README.md + docs/screenshots/gallery.html)
  3) Optional optimization to JPG (docs/screenshots/optimized/*.jpg) (macOS only)

This is meant to be run after you drop/capture real screenshots.

Exit codes:
  0: success
  2: placeholders detected and --fail-on-placeholders
  3: missing required files
  10+: a sub-step failed unexpectedly
"""

from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> int:
    p = subprocess.run(cmd, cwd=str(ROOT))
    return int(p.returncode)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--fail-on-placeholders",
        action="store_true",
        help="Exit non-zero if any top-level screenshot PNG is still a placeholder copy.",
    )
    ap.add_argument(
        "--optimize",
        action="store_true",
        help="Also generate resized/compressed JPGs under docs/screenshots/optimized/ (macOS only).",
    )
    ap.add_argument(
        "--width",
        type=int,
        default=1400,
        help="Width for optimized screenshots (only used with --optimize).",
    )
    ap.add_argument(
        "--format",
        default="jpg",
        choices=["jpg"],
        help="Output format for optimized screenshots (only used with --optimize).",
    )
    args = ap.parse_args()

    # 1) Placeholder check
    cmd = [
        sys.executable,
        "scripts/check_screenshots.py",
    ]
    if args.fail_on_placeholders:
        cmd.append("--fail-on-placeholders")

    rc = run(cmd)
    if rc != 0:
        return rc

    # 2) Gallery regen
    rc = run([sys.executable, "scripts/render_screenshots_gallery.py"])
    if rc != 0:
        return 11

    # 3) Optional optimization
    if args.optimize:
        if platform.system().lower() != "darwin":
            print("[screenshots] --optimize is macOS-only (uses 'sips'); skipping.")
            return 0

        rc = run(
            [
                "node",
                "scripts/optimize_screenshots.mjs",
                "--width",
                str(args.width),
                "--format",
                args.format,
            ]
        )
        if rc != 0:
            return 12

    print("[screenshots] Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
