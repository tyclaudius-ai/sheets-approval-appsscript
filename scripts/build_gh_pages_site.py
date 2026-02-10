#!/usr/bin/env python3
"""Build a minimal static site (for GitHub Pages) into dist/site.

Goal: host a simple landing page + docs + screenshot PNGs without relying on
GitHub's markdown renderer.

This copies:
- landing/*   -> dist/site/*
- key *.md    -> dist/site/*.md
- docs/screenshots/png -> dist/site/docs/screenshots/png

And rewrites landing/index.html links from "../X" to "X" so they resolve
within the built site.
"""

from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "dist" / "site"

LANDING_DIR = REPO_ROOT / "landing"
PNG_DIR = REPO_ROOT / "docs" / "screenshots" / "png"

DOC_FILES = [
    "README.md",
    "ONE_PAGER.md",
    "SETUP-CHECKLIST.md",
    "DEMO-TEMPLATE.md",
    "SCREENSHOTS.md",
    "SHEET-SCHEMA.md",
    "TEMPLATE-INSTRUCTIONS.md",
    "CLIENT-HANDOFF.md",
    "LISTING.md",
]


def main() -> None:
    if not LANDING_DIR.exists():
        raise SystemExit(f"missing landing dir: {LANDING_DIR}")

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Copy landing assets (style.css etc)
    for p in LANDING_DIR.iterdir():
        if p.is_dir():
            continue
        if p.name == "index.html":
            continue
        shutil.copy2(p, OUT_DIR / p.name)

    # Rewrite index.html for site root
    src_index = (LANDING_DIR / "index.html").read_text(encoding="utf-8")

    # Make ../ links resolve at site root
    rewritten = src_index.replace('href="../', 'href="').replace('src="../', 'src="')

    # Ensure the landing <title> is sane for Pages.
    # (No-op unless someone changes it upstream.)

    (OUT_DIR / "index.html").write_text(rewritten, encoding="utf-8")

    # Copy markdown docs into site root
    for name in DOC_FILES:
        src = REPO_ROOT / name
        if src.exists():
            shutil.copy2(src, OUT_DIR / name)

    # Copy screenshot PNGs
    if PNG_DIR.exists():
        dst_png = OUT_DIR / "docs" / "screenshots" / "png"
        dst_png.mkdir(parents=True, exist_ok=True)
        for p in PNG_DIR.glob("*.png"):
            shutil.copy2(p, dst_png / p.name)

    print(f"built: {OUT_DIR}")


if __name__ == "__main__":
    main()
