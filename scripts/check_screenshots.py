#!/usr/bin/env python3
"""Check whether docs/screenshots/*.png are real screenshots or placeholder copies.

This repo includes SVG placeholders and a generated PNG set under:
  docs/screenshots/png/*.png

The landing page references docs/screenshots/*.png.
During development, those files may be copies of the placeholder PNGs.

This script compares SHA256 hashes between:
  docs/screenshots/<name>.png
and
  docs/screenshots/png/<name>.png

If hashes match, the top-level PNG is still a placeholder copy.

Exit codes:
  0: ok (or placeholders found but not failing)
  2: placeholders found and --fail-on-placeholders is set
  3: missing files
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOP_DIR = ROOT / "docs" / "screenshots"
PLACEHOLDER_DIR = TOP_DIR / "png"

NAMES = [
    "01-menu.png",
    "02-requests-pending.png",
    "03-approved-row.png",
    "04-audit-entry.png",
    "05-reapproval-required.png",
    "06-help-sidebar.png",
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--fail-on-placeholders",
        action="store_true",
        help="Exit non-zero if any top-level screenshot PNG is still a placeholder copy.",
    )
    args = ap.parse_args()

    missing: list[str] = []
    placeholders: list[str] = []

    for name in NAMES:
        top = TOP_DIR / name
        ph = PLACEHOLDER_DIR / name

        if not top.exists():
            missing.append(str(top.relative_to(ROOT)))
            continue
        if not ph.exists():
            missing.append(str(ph.relative_to(ROOT)))
            continue

        try:
            if sha256(top) == sha256(ph):
                placeholders.append(name)
        except OSError:
            missing.append(name)

    if missing:
        print("[screenshots] MISSING files:")
        for m in missing:
            print(f"  - {m}")
        return 3

    if placeholders:
        print("[screenshots] PLACEHOLDER copies detected (top-level PNG matches placeholder PNG):")
        for n in placeholders:
            print(f"  - docs/screenshots/{n}")
        print("\nTo replace with real screenshots, see REAL_SCREENSHOTS_GUIDE.md")
        if args.fail_on_placeholders:
            return 2
        return 0

    print("[screenshots] OK — top-level screenshot PNGs do not match placeholder PNGs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
