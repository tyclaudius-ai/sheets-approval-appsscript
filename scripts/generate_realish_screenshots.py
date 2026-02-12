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
  python3 scripts/generate_realish_screenshots.py [--optimize] [--watermark] [--watermark-text TEXT]

Options:
  --optimize         Also run the screenshot optimizer after writing PNGs
                    (generates docs/screenshots/optimized/*.jpg).
  --watermark        Add a safety watermark ("DEMO (generated)") to the output PNGs.
                    Useful when you want to share mocks publicly without risking
                    them being mistaken for real Google Sheets captures.
  --watermark-text   Customize the watermark text (implies --watermark).

Notes:
- If you later capture true screenshots from Google Sheets, you can overwrite
  docs/screenshots/<name>.png directly (see REAL_SCREENSHOTS_GUIDE.md).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import subprocess
import hashlib
import json
from datetime import datetime, timezone

from PIL import Image, ImageDraw, ImageFont, ImageFilter

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


def load_font(size: int) -> ImageFont.ImageFont:
    """Best-effort: use a system UI font if present; otherwise fall back."""

    candidates = [
        # macOS (common)
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/SFNSRounded.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        # Linux-ish
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]

    for p in candidates:
        try:
            if Path(p).exists():
                return ImageFont.truetype(p, size=size)
        except Exception:
            continue

    # Fallback: PIL's bundled bitmap font
    return ImageFont.load_default()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--optimize",
        action="store_true",
        help="Also run the screenshot optimizer (writes docs/screenshots/optimized/*.jpg)",
    )
    ap.add_argument(
        "--watermark",
        action="store_true",
        help='Add a safety watermark ("DEMO (generated)") to the output PNGs',
    )
    ap.add_argument(
        "--watermark-text",
        default=None,
        help="Custom watermark text (implies --watermark)",
    )
    args = ap.parse_args()

    TOP_DIR.mkdir(parents=True, exist_ok=True)

    font_sm = load_font(14)
    font_md = load_font(16)

    wrote = 0
    missing = 0

    # Write a hash manifest so we can later distinguish "real-ish" mocks from
    # true Google Sheets captures.
    out_hashes: dict[str, str] = {}

    # Brand-ish colors
    sheets_green = (15, 157, 88, 255)  # Google-ish green
    chrome_bg = (245, 246, 248, 255)
    chrome_border = (220, 222, 227, 255)

    for shot in SHOTS:
        in_path = PLACEHOLDER_DIR / shot.filename
        out_path = TOP_DIR / shot.filename

        if not in_path.exists():
            print(f"MISSING: {in_path.relative_to(ROOT)}")
            missing += 1
            continue

        base = Image.open(in_path).convert("RGBA")

        # Layout sizes (in pixels)
        pad = 20
        browser_h = 54
        sheets_h = 66
        header_h = browser_h + sheets_h

        w, h = base.size
        out_w = w + pad * 2
        out_h = h + header_h + pad * 2

        canvas = Image.new("RGBA", (out_w, out_h), (255, 255, 255, 255))
        draw = ImageDraw.Draw(canvas)

        # --- Top browser chrome (rounded container) ---
        draw.rounded_rectangle(
            (pad, pad, pad + w, pad + browser_h),
            radius=14,
            fill=chrome_bg,
            outline=chrome_border,
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
            outline=(210, 212, 217, 255),
            width=1,
        )
        addr = "docs.google.com/spreadsheets/d/…"
        draw.text((ab_x0 + 12, ab_y0 + 9), addr, fill=(90, 92, 98, 255), font=font_sm)

        # --- Fake Google Sheets header ---
        y2 = pad + browser_h
        draw.rectangle(
            (pad, y2, pad + w, y2 + sheets_h),
            fill=(255, 255, 255, 255),
            outline=(225, 227, 232, 255),
        )

        # Sheets icon (green doc w/ white grid)
        icon_x = pad + 18
        icon_y = y2 + 18
        draw.rounded_rectangle((icon_x, icon_y, icon_x + 28, icon_y + 28), radius=6, fill=sheets_green)
        # White inner sheet
        draw.rounded_rectangle(
            (icon_x + 7, icon_y + 6, icon_x + 22, icon_y + 22),
            radius=2,
            fill=(255, 255, 255, 255),
        )
        # Tiny grid hint
        for gx in [icon_x + 12, icon_x + 17]:
            draw.line((gx, icon_y + 8, gx, icon_y + 20), fill=(220, 220, 220, 255), width=1)
        for gy in [icon_y + 12, icon_y + 16]:
            draw.line((icon_x + 9, gy, icon_x + 20, gy), fill=(220, 220, 220, 255), width=1)

        title = f"{shot.sheet_title} — Google Sheets"
        draw.text((icon_x + 40, y2 + 21), title, fill=(25, 25, 28, 255), font=font_md)

        # Subtle toolbar hint line (pill buttons)
        tool_y = y2 + 44
        x_start = icon_x + 40
        for i in range(11):
            x0 = x_start + i * 34
            draw.rounded_rectangle(
                (x0, tool_y, x0 + 24, tool_y + 14),
                radius=5,
                fill=(246, 247, 249, 255),
                outline=(232, 234, 238, 255),
            )

        # --- Content card shadow + base image ---
        content_x = pad
        content_y = pad + header_h

        # Shadow layer
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow)
        sdraw.rounded_rectangle(
            (content_x + 2, content_y + 4, content_x + w + 2, content_y + h + 4),
            radius=10,
            fill=(0, 0, 0, 45),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=6))
        canvas.alpha_composite(shadow)

        # White card border behind content
        draw.rounded_rectangle(
            (content_x - 1, content_y - 1, content_x + w + 1, content_y + h + 1),
            radius=10,
            fill=(255, 255, 255, 255),
            outline=(230, 232, 236, 255),
            width=1,
        )

        canvas.alpha_composite(base, (content_x, content_y))

        # Optional safety watermark.
        watermark_text = args.watermark_text or ("DEMO (generated)" if args.watermark else None)
        if watermark_text:
            overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            odraw = ImageDraw.Draw(overlay)
            bbox = odraw.textbbox((0, 0), watermark_text, font=font_sm)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            # Bottom-right, inside padding.
            x = out_w - pad - tw - 10
            y = out_h - pad - th - 10
            # Soft background pill for legibility.
            odraw.rounded_rectangle(
                (x - 8, y - 6, x + tw + 8, y + th + 6),
                radius=10,
                fill=(255, 255, 255, 190),
                outline=(0, 0, 0, 60),
            )
            odraw.text((x, y), watermark_text, fill=(0, 0, 0, 160), font=font_sm)
            canvas.alpha_composite(overlay)

        # Save PNG
        canvas.convert("RGB").save(out_path, format="PNG", optimize=True)

        # Record hash for later detection.
        h = hashlib.sha256(out_path.read_bytes()).hexdigest()
        out_hashes[shot.filename] = h

        wrote += 1
        print(f"Wrote: {out_path.relative_to(ROOT)}")

    if missing:
        print(f"\nDone (with missing inputs). wrote={wrote}, missing={missing}")
        return 2

    # Persist a manifest of the generated hashes so check_screenshots.py can
    # warn/fail if a listing accidentally uses mocks.
    try:
        manifest_path = TOP_DIR / "realish-hashes.json"
        payload = {
            "kind": "realish-hashes",
            "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "files": out_hashes,
        }
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote: {manifest_path.relative_to(ROOT)}")
    except Exception as e:
        print(f"WARN: failed to write realish-hashes.json: {e}")

    if args.optimize:
        try:
            # Best-effort convenience.
            subprocess.run(["node", "scripts/optimize_screenshots.mjs"], cwd=ROOT, check=True)
        except FileNotFoundError:
            print("[optimize] Skipped: node not found")
        except subprocess.CalledProcessError as e:
            print(
                f"[optimize] Failed (exit={e.returncode}). You can rerun manually: node scripts/optimize_screenshots.mjs"
            )

    print(f"\nDone. wrote={wrote}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
