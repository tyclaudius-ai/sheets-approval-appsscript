#!/usr/bin/env python3

"""Redact sensitive UI elements in captured screenshots.

Use-case: You captured real Google Sheets screenshots for docs/marketplace, but they
contain identifiable info (account avatar/email, file name, etc.). This script lets
you blur or pixelate configured rectangular regions.

Design goals:
- Safe by default (writes to a separate output dir unless --inplace)
- Simple presets for the project shotlist
- Easy to tweak rectangles (fractions of width/height)

Examples:
  python3 scripts/redact_screenshots.py --list-presets
  python3 scripts/redact_screenshots.py --preset sheets_account_topright \
    --in docs/screenshots --out /tmp/redacted

  # In-place (overwrites files!)
  python3 scripts/redact_screenshots.py --preset sheets_account_topright \
    --in docs/screenshots --inplace
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

from PIL import Image, ImageFilter


RectFrac = Tuple[float, float, float, float]


@dataclass(frozen=True)
class Redaction:
    # Human label for logs
    name: str
    # Rect expressed as fractions of (w,h): (x0,y0,x1,y1) in [0,1]
    rect: RectFrac
    # blur radius in pixels
    blur: int = 12
    # pixelation block size (if set, pixelate instead of blur)
    pixelate: int | None = None


# Presets are intentionally conservative: focus on the Google account area.
# Users can extend / tweak by adding their own rectangles.
PRESETS: dict[str, List[Redaction]] = {
    # Common Google Sheets top-right identity area: avatar + account email menu.
    # Tuned for typical 16:9-ish captures; uses fractional coords so it scales.
    "sheets_account_topright": [
        Redaction(
            name="account-avatar-and-menu",
            rect=(0.84, 0.00, 1.00, 0.18),
            blur=18,
        ),
    ],
    # Slightly larger in case the account name/email dropdown is open.
    "sheets_account_topright_large": [
        Redaction(
            name="account-avatar-menu-large",
            rect=(0.78, 0.00, 1.00, 0.30),
            blur=18,
        ),
    ],
}


def frac_to_px(rect: RectFrac, w: int, h: int) -> Tuple[int, int, int, int]:
    x0, y0, x1, y1 = rect
    x0p = max(0, min(w, int(round(x0 * w))))
    y0p = max(0, min(h, int(round(y0 * h))))
    x1p = max(0, min(w, int(round(x1 * w))))
    y1p = max(0, min(h, int(round(y1 * h))))
    if x1p < x0p:
        x0p, x1p = x1p, x0p
    if y1p < y0p:
        y0p, y1p = y1p, y0p
    return x0p, y0p, x1p, y1p


def apply_redactions(img: Image.Image, redactions: Iterable[Redaction]) -> Image.Image:
    out = img.copy()
    w, h = out.size

    for r in redactions:
        x0, y0, x1, y1 = frac_to_px(r.rect, w, h)
        if x1 <= x0 or y1 <= y0:
            continue
        region = out.crop((x0, y0, x1, y1))

        if r.pixelate is not None and r.pixelate > 1:
            # Downscale then upscale with nearest-neighbor
            bw = max(1, (x1 - x0) // r.pixelate)
            bh = max(1, (y1 - y0) // r.pixelate)
            region_small = region.resize((bw, bh), resample=Image.Resampling.BILINEAR)
            region_pix = region_small.resize(region.size, resample=Image.Resampling.NEAREST)
            out.paste(region_pix, (x0, y0))
        else:
            out.paste(region.filter(ImageFilter.GaussianBlur(radius=r.blur)), (x0, y0))

    return out


def iter_images(root: Path) -> Iterable[Path]:
    exts = {".png", ".jpg", ".jpeg", ".webp"}
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def main() -> int:
    ap = argparse.ArgumentParser(description="Redact sensitive regions in screenshots (blur/pixelate rectangles).")
    ap.add_argument("--in", dest="in_dir", required=False, help="Input directory (default: current dir)")
    ap.add_argument("--out", dest="out_dir", required=False, help="Output directory (required unless --inplace)")
    ap.add_argument("--inplace", action="store_true", help="Overwrite images in place (dangerous)")
    ap.add_argument("--preset", required=False, default="sheets_account_topright", help="Redaction preset")
    ap.add_argument("--only", nargs="*", help="Only process these relative paths (e.g. docs/screenshots/01-menu.png)")
    ap.add_argument("--write-report", help="Write JSON report of what was redacted")
    ap.add_argument("--list-presets", action="store_true", help="List available presets and exit")

    args = ap.parse_args()

    if args.list_presets:
        print("Available presets:")
        for k in sorted(PRESETS.keys()):
            print(f"- {k} ({len(PRESETS[k])} region(s))")
        return 0

    preset = args.preset
    if preset not in PRESETS:
        raise SystemExit(f"Unknown preset: {preset}. Use --list-presets.")

    in_dir = Path(args.in_dir or os.getcwd()).expanduser().resolve()
    if not in_dir.exists() or not in_dir.is_dir():
        raise SystemExit(f"Input dir not found: {in_dir}")

    if args.inplace:
        out_dir = in_dir
    else:
        if not args.out_dir:
            raise SystemExit("--out is required unless --inplace")
        out_dir = Path(args.out_dir).expanduser().resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

    only: set[Path] | None = None
    if args.only:
        only = set(Path(p).as_posix() for p in args.only)  # normalize strings

    report = {
        "preset": preset,
        "in_dir": str(in_dir),
        "out_dir": str(out_dir),
        "inplace": bool(args.inplace),
        "files": [],
    }

    redactions = PRESETS[preset]

    candidates: List[Path]
    if only is not None:
        candidates = []
        for rel in sorted(only):
            src = (in_dir / rel).resolve() if not Path(rel).is_absolute() else Path(rel)
            # If user passed a path relative to repo root but in_dir is also repo root,
            # the join works; otherwise, allow absolute.
            if not src.exists():
                # try relative-as-given from cwd
                alt = Path(rel)
                if alt.exists():
                    src = alt.resolve()
                else:
                    raise SystemExit(f"--only path not found: {rel}")
            candidates.append(src)
    else:
        candidates = list(iter_images(in_dir))

    for src in candidates:
        # Determine output path
        if args.inplace:
            dst = src
            rel = src.relative_to(in_dir).as_posix() if src.is_relative_to(in_dir) else src.name
        else:
            rel = src.relative_to(in_dir).as_posix()
            dst = out_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)

        with Image.open(src) as img:
            img = img.convert("RGBA") if img.mode in ("P", "LA") else img
            redacted = apply_redactions(img, redactions)
            # Preserve PNG vs JPG etc.
            redacted.save(dst)

        report["files"].append(
            {
                "src": str(src),
                "dst": str(dst),
                "relative": rel,
                "applied": [
                    {
                        "name": r.name,
                        "rect": r.rect,
                        "blur": r.blur,
                        "pixelate": r.pixelate,
                    }
                    for r in redactions
                ],
            }
        )

    if args.write_report:
        outp = Path(args.write_report).expanduser().resolve()
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Redacted {len(report['files'])} file(s) using preset '{preset}'.")
    if not args.inplace:
        print(f"Output: {out_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
