#!/usr/bin/env python3
"""Generate a quick status report for the docs screenshot set.

This helps answer: which screenshots are still placeholders, which are "real-ish"
(generated), and which appear to be true manual captures.

It compares the hashes of:
- docs/screenshots/<file> (current canonical screenshot)
- docs/screenshots/png/<file> (the original placeholder PNGs)
- docs/screenshots/realish-hashes.json (hashes of generated "real-ish" outputs)

Output:
- prints Markdown to stdout by default
- optionally writes to docs/screenshots/STATUS.md

Usage:
  python3 scripts/screenshot_status.py
  python3 scripts/screenshot_status.py --write

"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOP = ROOT / "docs" / "screenshots"
PLACEHOLDER_DIR = TOP / "png"
MANIFEST_PATH = TOP / "manifest.json"
REALISH_HASHES_PATH = TOP / "realish-hashes.json"
OUT_PATH = TOP / "STATUS.md"


@dataclass(frozen=True)
class Row:
    id: str
    file: str
    heading: str
    caption: str


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest() -> list[Row]:
    data = json.loads(MANIFEST_PATH.read_text("utf-8"))
    items = data.get("items") or []
    out: list[Row] = []
    for it in items:
        out.append(
            Row(
                id=str(it.get("id") or ""),
                file=str(it.get("file") or ""),
                heading=str(it.get("heading") or ""),
                caption=str(it.get("caption") or ""),
            )
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help=f"Write to {OUT_PATH.relative_to(ROOT)}")
    args = ap.parse_args()

    if not MANIFEST_PATH.exists():
        raise SystemExit(f"Missing manifest: {MANIFEST_PATH}")

    realish_hashes: dict[str, str] = {}
    if REALISH_HASHES_PATH.exists():
        rh = json.loads(REALISH_HASHES_PATH.read_text("utf-8"))
        # Format: { kind, generatedAt, files: { "01-menu.png": "<sha256>" } }
        if isinstance(rh, dict) and isinstance(rh.get("files"), dict):
            realish_hashes = {str(k): str(v) for k, v in rh["files"].items()}

    rows = load_manifest()
    now = datetime.now(timezone.utc)

    md: list[str] = []
    md.append(f"# Screenshot status\n")
    md.append(f"Generated: {now.isoformat()}\n")
    md.append("Legend:\n")
    md.append("- **placeholder**: canonical PNG matches docs/screenshots/png/<file>\n")
    md.append("- **real-ish**: canonical PNG matches docs/screenshots/realish-hashes.json\n")
    md.append("- **custom**: canonical PNG differs from both placeholder + real-ish\n")
    md.append("\n")
    md.append("| id | file | status | notes |\n")
    md.append("|---:|---|---|---|\n")

    for r in rows:
        out_path = TOP / r.file
        ph_path = PLACEHOLDER_DIR / r.file

        status = "missing"
        notes: list[str] = []

        if not out_path.exists():
            status = "missing"
            notes.append("canonical file missing")
        else:
            out_hash = sha256_file(out_path)
            realish_hash = realish_hashes.get(r.file)

            ph_hash = sha256_file(ph_path) if ph_path.exists() else None

            if ph_hash and out_hash == ph_hash:
                status = "placeholder"
            elif realish_hash and out_hash == realish_hash:
                status = "real-ish"
            else:
                status = "custom"

            notes.append(r.heading)

        md.append(f"| `{r.id}` | `{r.file}` | **{status}** | {' — '.join(notes)} |\n")

    text = "".join(md)

    if args.write:
        OUT_PATH.write_text(text, "utf-8")
        print(f"Wrote {OUT_PATH.relative_to(ROOT)}")
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
