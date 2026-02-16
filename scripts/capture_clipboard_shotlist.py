#!/usr/bin/env python3
"""Interactive helper to save macOS clipboard screenshots into the canonical shotlist.

Why:
- Marketplace listings want REAL screenshots (not generated real-ish mocks).
- Capturing 6 shots and naming them correctly is tedious.

This script prompts you shot-by-shot:
1) Take a screenshot to the clipboard (Cmd+Ctrl+Shift+4 on macOS)
2) Press Enter
3) The clipboard image is written to the correct `docs/screenshots/0X-*.png` path.

Notes:
- macOS only (uses `osascript` to read clipboard as PNG).
- It will, by default, only capture shots that are currently "real-ish" (generated)
  or missing. Use `--all` to capture everything.

Usage:
  python3 scripts/capture_clipboard_shotlist.py
  python3 scripts/capture_clipboard_shotlist.py --all
  python3 scripts/capture_clipboard_shotlist.py --target-dir docs/screenshots
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_SHOTLIST = [
    "01-menu.png",
    "02-requests-pending.png",
    "03-approved-row.png",
    "04-audit-entry.png",
    "05-reapproval-required.png",
    "06-help-sidebar.png",
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_realish_hashes(realish_hashes_path: Path) -> set[str]:
    try:
        data = json.loads(realish_hashes_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return set(str(x) for x in data)
        if isinstance(data, dict) and "sha256" in data and isinstance(data["sha256"], list):
            return set(str(x) for x in data["sha256"])
        # common format in this repo: {"files": {name: sha}} or {name: sha}
        if isinstance(data, dict):
            hashes: list[str] = []
            if "files" in data and isinstance(data["files"], dict):
                hashes.extend(str(v) for v in data["files"].values())
            else:
                hashes.extend(str(v) for v in data.values() if isinstance(v, str))
            return set(hashes)
    except Exception:
        return set()
    return set()


def _needs_replacement(target: Path, realish_hashes: set[str]) -> bool:
    if not target.exists():
        return True
    try:
        return _sha256(target) in realish_hashes
    except Exception:
        return True


def _write_clipboard_png(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Write clipboard PNG bytes to a file using AppleScript.
    # If clipboard doesn't contain an image, osascript will error.
    script = f'''
set theFile to (POSIX file "{str(out_path)}")
set theData to the clipboard as «class PNGf»
set outFile to open for access theFile with write permission
set eof outFile to 0
write theData to outFile
close access outFile
'''

    subprocess.run(["osascript", "-e", script], check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--target-dir",
        default="docs/screenshots",
        help="Directory containing the canonical screenshots (default: docs/screenshots)",
    )
    ap.add_argument(
        "--all",
        action="store_true",
        help="Capture all shots (default captures only missing or real-ish-generated ones)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be captured and exit",
    )
    ap.add_argument(
        "--min-bytes",
        type=int,
        default=50_000,
        help="Reject captures smaller than this many bytes (default: 50000)",
    )
    args = ap.parse_args()

    target_dir = ROOT / args.target_dir
    realish_hashes = _load_realish_hashes(ROOT / "docs/screenshots/realish-hashes.json")

    targets: list[Path] = []
    for name in DEFAULT_SHOTLIST:
        p = target_dir / name
        if args.all or _needs_replacement(p, realish_hashes):
            targets.append(p)

    if not targets:
        print("Nothing to capture: all required shots already look non-real-ish.")
        return 0

    if args.dry_run:
        print("Will capture:")
        for t in targets:
            print(f"- {t.relative_to(ROOT)}")
        return 0

    print("\nClipboard capture mode (macOS):")
    print("- For each shot, take a screenshot *to clipboard* (Cmd+Ctrl+Shift+4)")
    print("- Then press Enter here to save it to the correct filename\n")

    for i, out_path in enumerate(targets, start=1):
        rel = out_path.relative_to(ROOT)
        print(f"[{i}/{len(targets)}] Ready for: {rel}")
        input("  Take screenshot → clipboard, then press Enter (or Ctrl+C to abort)… ")

        tmp = out_path.with_suffix(".tmp.png")
        try:
            if tmp.exists():
                tmp.unlink()
            _write_clipboard_png(tmp)
        except subprocess.CalledProcessError:
            if tmp.exists():
                tmp.unlink()
            print("  ERROR: clipboard did not contain an image PNG. Try capturing again.")
            return 2

        size = tmp.stat().st_size if tmp.exists() else 0
        if size < args.min_bytes:
            tmp.unlink(missing_ok=True)
            print(f"  ERROR: capture too small ({size} bytes < {args.min_bytes}). Retake.")
            return 2

        # Atomic-ish replace
        tmp.replace(out_path)
        print(f"  Saved {rel} ({size} bytes)")

        # give the user a breath between shots
        time.sleep(0.15)

    print("\nDone. Next steps:")
    print("  python3 scripts/check_screenshots.py --require-real-screenshots")
    print("  python3 scripts/screenshots_pipeline.py --optimize --width 1400 --status --render-gallery")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
