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
- docs/screenshots/deck.html + gallery.html (printable views)
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
import subprocess
import time
import zipfile


ROOT = Path(__file__).resolve().parents[1]

INCLUDE_PATHS = [
    # The script itself (so the capture machine doesn't need a full repo checkout)
    Path("Code.gs"),

    # The actual capture instructions
    Path("docs/screenshots/README.md"),
    Path("docs/screenshots/REAL_SCREENSHOTS_QUICKRUN.md"),
    Path("docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md"),
    Path("docs/screenshots/CAPTURE-CHEATSHEET.md"),
    Path("docs/screenshots/manifest.json"),

    # Handy printable views (generated from manifest.json)
    Path("docs/screenshots/deck.html"),
    Path("docs/screenshots/gallery.html"),
    Path("docs/screenshots/capture-checklist.html"),

    # Install + verification helpers
    Path("scripts/install_real_screenshots.py"),
    Path("scripts/check_screenshots.py"),
    Path("scripts/capture_clipboard_shotlist.py"),
    Path("scripts/screenshots_pipeline.py"),
    Path("scripts/render_screenshots_gallery.py"),
    Path("scripts/requirements.txt"),
]


def _timestamp_slug() -> str:
    # UTC timestamp, filesystem safe.
    return time.strftime("%Y%m%d-%H%M%SZ", time.gmtime())


def _build_status_report_md() -> str:
    """Generate a Markdown status report describing current screenshot state.

    This is intended as a convenience inside the capture pack zip so whoever
    is capturing screenshots can see exactly what’s missing (without running
    anything first).

    Best-effort: if generation fails for any reason, return a short note.
    """

    try:
        tmp = ROOT / "tmp"
        tmp.mkdir(parents=True, exist_ok=True)
        out = tmp / "real-screenshots-status.md"

        # Best-effort: always succeed (check_screenshots may exit non-zero when
        # placeholders/real-ish are present).
        subprocess.run(
            [
                "python3",
                str(ROOT / "scripts" / "check_screenshots.py"),
                "--report-md",
                str(out),
            ],
            check=False,
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if out.exists():
            return out.read_text(encoding="utf-8")
    except Exception:
        pass

    return (
        "# Real screenshots status\n\n"
        "(Status report generation failed on the packaging machine.)\n\n"
        "Run this after unzipping:\n\n"
        "```bash\n"
        "python3 scripts/check_screenshots.py --report-md tmp/real-screenshots-status.md\n"
        "```\n"
    )


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
        readme = """# Sheets Approvals — REAL screenshots capture pack

Goal: replace placeholder screenshots under `docs/screenshots/*.png` with **REAL** captures from an actual Google Sheet.

## What’s included

- `Code.gs` (paste into Apps Script)
- Shotlist + framing guide under `docs/screenshots/`
- Helper scripts to install + validate screenshots (`scripts/*`)

## Capture workflow (macOS example)

1) Create a new Google Sheet.
2) Extensions → **Apps Script**.
3) Paste `Code.gs` (from this zip) into the editor.
4) Save, then reload the Sheet.
5) Run **Approvals → Create demo setup**.
6) Capture the 6 screenshots from:
   - `docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md`

## Install + verify

### Option A (macOS): double-click runner

After unzipping, double-click:

- `CAPTURE_MAC.command`

It will:
- open the capture checklist
- run a guided installer that waits for 6 **new** screenshots on your Desktop
- verify + optimize them

macOS may warn about running downloaded scripts; if so, right-click → Open.

### Option B (macOS): capture from clipboard (recommended)

From the unzipped folder:

```bash
python3 -m pip install -r scripts/requirements.txt
python3 scripts/capture_clipboard_shotlist.py --target-dir docs/screenshots
python3 scripts/screenshots_pipeline.py --check --require-real-screenshots --optimize --width 1400 --status --render-gallery
```

Tip: use **Cmd+Ctrl+Shift+4** to capture to the clipboard (not a file).

### Option C (any OS): run the pipeline (file-based)

Your screenshots usually land on Desktop. From the unzipped folder:

```bash
python3 -m pip install -r scripts/requirements.txt

python3 scripts/screenshots_pipeline.py \
  --from ~/Desktop \
  --check \
  --require-real-screenshots \
  --optimize \
  --width 1400 \
  --status \
  --render-gallery
```

Optional animated preview:

```bash
python3 scripts/screenshots_pipeline.py --make-gif --gif-width 900 --gif-ms 900
```

Notes:
- This pack intentionally does NOT include any screenshots.
- No Google login automation is attempted.
"""
        z.writestr("README_CAPTURE_PACK.md", readme)

        # Convenience: include a pre-generated status report so the capturer can
        # immediately see what needs to be replaced.
        z.writestr("REAL_SCREENSHOTS_STATUS.md", _build_status_report_md())

        # Convenience: a double-clickable macOS runner.
        # - .command files are meant to be executed by Terminal on macOS.
        # - This is best-effort; if you're on Linux/Windows you can ignore it.
        capture_cmd = """#!/bin/bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

echo "[capture] Installing python requirements (best-effort)…"
python3 -m pip install -r scripts/requirements.txt >/dev/null || true

echo "[capture] Opening capture checklist…"
if command -v open >/dev/null 2>&1; then
  open "docs/screenshots/capture-checklist.html" || true
  open "docs/screenshots/deck.html" || true
  open "docs/screenshots/REAL_SCREENSHOTS_QUICKRUN.md" || true
  open "docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md" || true
fi

echo "[capture] Clipboard capture mode (fastest):"
echo "  Use Cmd+Ctrl+Shift+4 to capture to clipboard (not file)."
echo "  This will prompt you 6 times and write into docs/screenshots/*.png"
python3 scripts/capture_clipboard_shotlist.py --target-dir docs/screenshots

echo "[capture] Verifying + optimizing…"
python3 scripts/screenshots_pipeline.py \
  --check \
  --require-real-screenshots \
  --optimize \
  --width 1400 \
  --status \
  --render-gallery

echo "[capture] Done. Opening the gallery to sanity-check results…"
if command -v open >/dev/null 2>&1; then
  open "docs/screenshots/gallery.html" || true
fi

echo "[capture] If you want to re-run verification later:"
echo "  python3 scripts/check_screenshots.py --report-md docs/screenshots/REAL_SCREENSHOTS_STATUS.md"
"""
        zi = zipfile.ZipInfo("CAPTURE_MAC.command")
        # Mark as executable (0755) on Unix-y systems so macOS can double-click it.
        zi.external_attr = 0o755 << 16
        z.writestr(zi, capture_cmd)

        for rel in INCLUDE_PATHS:
            src = ROOT / rel
            z.write(src, arcname=str(rel))

    size_kb = os.path.getsize(out_path) / 1024
    print(f"Wrote {out_path} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
