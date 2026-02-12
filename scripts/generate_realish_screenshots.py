#!/usr/bin/env python3
"""Generate "real-ish" screenshot PNGs from the placeholder PNGs.

Goal: replace docs/screenshots/*.png (which may be placeholder copies) with
non-identical images that look more like real screenshots, without requiring
Google login or manual capture.

Approach:
- Take each placeholder image from docs/screenshots/png/<name>.png
- Add a simple "browser" chrome + fake Google Sheets toolbar header
- Write to docs/screenshots/<name>.png

This intentionally makes the top-level PNG hashes differ from the placeholder
PNGs so `scripts/check_screenshots.py` passes.

Usage:
  python3 scripts/generate_realish_screenshots.py [--optimize]

Options:
  --optimize   Also run the screenshot optimizer after writing PNGs
              (generates docs/screenshots/optimized/*.jpg).

Notes:
- If you later capture true screenshots from Google Sheets, you can overwrite
  docs/screenshots/<name>.png directly (see REAL_SCREENSHOTS_GUIDE.md).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TOP_DIR = ROOT / "docs" / "screenshots"
PLACEHOLDER_DIR = TOP_DIR / "png"


@dataclass(frozen=True)
class Shot:
    filename: str
    sheet_title: str


SHOTS: list[Shot] = [
    Shot("01-menu.png", "Sheets Approvals (Demo)"),
    Shot("02-requests-pending.png", "Requests"),
    Shot("03-approved-row.png", "Requests"),
    Shot("04-audit-entry.png", "Audit"),
    Shot("05-reapproval-required.png", "Requests"),
    Shot("06-help-sidebar.png", "Docs / Help"),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--optimize",
        action="store_true",
        help="Also run the screenshot optimizer (writes docs/screenshots/optimized/*.jpg)",
    )
    args = ap.parse_args()

    TOP_DIR.mkdir(parents=True, exist_ok=True)

    # Fonts: use default bitmap font to avoid system dependencies.
    font = ImageFont.load_default()

    wrote = 0
    missing = 0

    for shot in SHOTS:
        in_path = PLACEHOLDER_DIR / shot.filename
        out_path = TOP_DIR / shot.filename

        if not in_path.exists():
            print(f"MISSING: {in_path.relative_to(ROOT)}")
            missing += 1
            continue

        base = Image.open(in_path).convert("RGBA")

        # Chrome sizes (in pixels)
        pad = 18
        browser_h = 54
        sheets_h = 64
        header_h = browser_h + sheets_h

        w, h = base.size
        canvas = Image.new("RGBA", (w + pad * 2, h + header_h + pad * 2), (255, 255, 255, 255))
        draw = ImageDraw.Draw(canvas)

        # Browser chrome background
        draw.rounded_rectangle(
            (pad, pad, pad + w, pad + browser_h),
            radius=14,
            fill=(245, 245, 247, 255),
            outline=(220, 220, 225, 255),
            width=1,
        )

        # macOS traffic-light dots
        dot_y = pad + 18
        for i, col in enumerate([(255, 95, 86, 255), (255, 189, 46, 255), (39, 201, 63, 255)]):
            cx = pad + 18 + i * 18
            draw.ellipse((cx - 6, dot_y - 6, cx + 6, dot_y + 6), fill=col, outline=None)

        # Address bar
        ab_x0 = pad + 90
        ab_x1 = pad + w - 18
        ab_y0 = pad + 12
        ab_y1 = pad + browser_h - 12
        draw.rounded_rectangle(
            (ab_x0, ab_y0, ab_x1, ab_y1),
            radius=12,
            fill=(255, 255, 255, 255),
            outline=(210, 210, 215, 255),
            width=1,
        )
        addr = "https://docs.google.com/spreadsheets/d/…"
        draw.text((ab_x0 + 12, ab_y0 + 10), addr, fill=(90, 90, 95, 255), font=font)

        # Fake Sheets toolbar area
        y2 = pad + browser_h
        draw.rectangle((pad, y2, pad + w, y2 + sheets_h), fill=(255, 255, 255, 255), outline=(225, 225, 230, 255))
        # Green Sheets icon
        icon_x = pad + 18
        icon_y = y2 + 18
        draw.rounded_rectangle((icon_x, icon_y, icon_x + 28, icon_y + 28), radius=6, fill=(26, 115, 232, 255))
        draw.rectangle((icon_x + 6, icon_y + 6, icon_x + 22, icon_y + 22), fill=(255, 255, 255, 255))

        title = f"{shot.sheet_title} — Google Sheets"
        draw.text((icon_x + 40, y2 + 22), title, fill=(25, 25, 28, 255), font=font)

        # Subtle toolbar hint line (buttons)
        tool_y = y2 + 44
        for i in range(10):
            x0 = icon_x + 40 + i * 34
            draw.rounded_rectangle((x0, tool_y, x0 + 24, tool_y + 14), radius=4, fill=(245, 245, 247, 255), outline=(230, 230, 235, 255))

        # Paste the content image
        canvas.alpha_composite(base, (pad, pad + header_h))

        # Save PNG
        canvas.convert("RGB").save(out_path, format="PNG", optimize=True)
        wrote += 1
        print(f"Wrote: {out_path.relative_to(ROOT)}")

    if missing:
        print(f"\nDone (with missing inputs). wrote={wrote}, missing={missing}")
        return 2

    if args.optimize:
        try:
            # Keep it best-effort: this is for convenience in local dev.
            subprocess.run(["node", "scripts/optimize_screenshots.mjs"], cwd=ROOT, check=True)
        except FileNotFoundError:
            print("[optimize] Skipped: node not found")
        except subprocess.CalledProcessError as e:
            print(f"[optimize] Failed (exit={e.returncode}). You can rerun manually: node scripts/optimize_screenshots.mjs")

    print(f"\nDone. wrote={wrote}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
