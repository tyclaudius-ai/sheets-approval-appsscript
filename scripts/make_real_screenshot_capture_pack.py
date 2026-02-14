#!/usr/bin/env python3
"""Build a small zip bundle to make capturing REAL screenshots fast.

This repo ships with placeholder screenshots (and “real‑ish” generated mocks)
so the landing page / docs look good without a Google login.

But for a Marketplace listing you eventually want REAL screenshots captured from
an actual Google Sheet.

This script produces a zip containing:
- docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md (what to capture)
- docs/screenshots/CAPTURE-CHEATSHEET.md (fast capture workflow)
- docs/screenshots/manifest.json (canonical filenames)
- scripts/install_real_screenshots.py (+ requirements)
- scripts/check_screenshots.py (verification)

Usage:
  python3 scripts/make_real_screenshot_capture_pack.py
  python3 scripts/make_real_screenshot_capture_pack.py --out dist/my-pack.zip

After unzipping on the capture machine:
  python3 scripts/install_real_screenshots.py --from ~/Desktop --check
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import time
import zipfile


ROOT = Path(__file__).resolve().parents[1]

INCLUDE_PATHS = [
    Path("docs/screenshots/REAL_SCREENSHOTS_QUICKRUN.md"),
    Path("docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md"),
    Path("docs/screenshots/CAPTURE-CHEATSHEET.md"),
    Path("docs/screenshots/manifest.json"),
    Path("scripts/install_real_screenshots.py"),
    Path("scripts/check_screenshots.py"),
    Path("scripts/screenshots_pipeline.py"),
    Path("scripts/requirements.txt"),
]


def _timestamp_slug() -> str:
    # UTC timestamp, filesystem safe.
    return time.strftime("%Y%m%d-%H%M%SZ", time.gmtime())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        help="Output zip path (default: dist/real-screenshots-capture-pack-<ts>.zip)",
        default=None,
    )
    args = ap.parse_args()

    out_path = (
        Path(args.out)
        if args.out
        else ROOT / "dist" / f"real-screenshots-capture-pack-{_timestamp_slug()}.zip"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    missing: list[str] = []
    for rel in INCLUDE_PATHS:
        p = ROOT / rel
        if not p.exists():
            missing.append(str(rel))

    if missing:
        raise SystemExit(
            "Missing required files (did you move things?):\n  - "
            + "\n  - ".join(missing)
        )

    # Write zip
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # Helpful top-level README inside the zip
        readme = """Sheets Approvals — REAL screenshots capture pack

Goal:
  Replace placeholder screenshots under docs/screenshots/*.png with REAL captures.

Start here:
  docs/screenshots/REAL_SCREENSHOTS_QUICKRUN.md
  docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md

Workflow (macOS example):
  1) Capture screenshots to Desktop (cmd+shift+4 / cmd+shift+5)
  2) Run the all-in-one pipeline (install + verify + optimize + refresh docs):
       python3 scripts/screenshots_pipeline.py --from ~/Desktop --check --require-real-screenshots --optimize --width 1400 --status --render-gallery
  3) (Optional) Animated preview:
       python3 scripts/screenshots_pipeline.py --make-gif --gif-width 900 --gif-ms 900

Notes:
  - This pack intentionally does NOT include any screenshots.
  - No Google login automation is attempted.
"""
        z.writestr("README_CAPTURE_PACK.txt", readme)

        for rel in INCLUDE_PATHS:
            src = ROOT / rel
            z.write(src, arcname=str(rel))

    size_kb = os.path.getsize(out_path) / 1024
    print(f"Wrote {out_path} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
