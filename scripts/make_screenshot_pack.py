#!/usr/bin/env python3
"""Build a listing-ready screenshot pack ZIP.

Why
---
Marketplaces (Upwork Project Catalog, Gumroad, etc.) often want a simple set of
images you can upload without hunting through the repo.

This script packages:
- PNG originals (docs/screenshots/*.png)
- Optimized JPGs if present (docs/screenshots/optimized/*.jpg)
- approval-flow.gif if present
- manifest.json + STATUS.md

Output
------
Writes a zip under dist/ (repo root) and prints the path.

Examples
--------
# After generating/optimizing screenshots:
python3 scripts/make_screenshot_pack.py

# Custom output path:
python3 scripts/make_screenshot_pack.py --out dist/screenshots-pack.zip
"""

from __future__ import annotations

import argparse
import json
import time
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs" / "screenshots"


def add_file(zf: zipfile.ZipFile, path: Path, arcname: str) -> None:
    if not path.exists():
        return
    zf.write(str(path), arcname=arcname)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        help="Output zip path (default: dist/screenshot-pack-YYYYMMDD-HHMM.zip)",
    )
    args = ap.parse_args()

    manifest_path = DOCS_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    items = manifest.get("items", [])

    ts = time.strftime("%Y%m%d-%H%M")
    out_path = Path(args.out) if args.out else (REPO_ROOT / "dist" / f"screenshot-pack-{ts}.zip")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Always include meta files.
        add_file(zf, manifest_path, "manifest.json")
        add_file(zf, DOCS_DIR / "STATUS.md", "STATUS.md")
        add_file(zf, DOCS_DIR / "README.md", "README.md")

        # Optional animated gif.
        add_file(zf, DOCS_DIR / "approval-flow.gif", "approval-flow.gif")

        # Include per-item images.
        for item in items:
            file_png = item.get("file")
            if not file_png:
                continue
            png_path = DOCS_DIR / file_png
            jpg_path = DOCS_DIR / "optimized" / (Path(file_png).stem + ".jpg")

            add_file(zf, png_path, f"png/{png_path.name}")
            if jpg_path.exists():
                add_file(zf, jpg_path, f"jpg/{jpg_path.name}")

    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
