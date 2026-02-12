#!/usr/bin/env python3
"""Generate a small animated GIF from the screenshot set.

This is meant for marketing/README previews when you don't have (or don't want)
video tooling.

Inputs (preferred):
- docs/screenshots/optimized/01-menu.jpg
- docs/screenshots/optimized/02-requests-pending.jpg
- docs/screenshots/optimized/03-approved-row.jpg
- docs/screenshots/optimized/04-audit-entry.jpg
- docs/screenshots/optimized/05-reapproval-required.jpg
- docs/screenshots/optimized/06-help-sidebar.jpg

Output:
- docs/screenshots/approval-flow.gif

Usage:
  python3 scripts/make_screenshot_gif.py

Options:
  --width 900        Resize frames to this width (keeps aspect)
  --ms 900           Frame duration in ms
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--width", type=int, default=900)
    ap.add_argument("--ms", type=int, default=900)
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    src_dir = root / "docs" / "screenshots" / "optimized"
    out_path = root / "docs" / "screenshots" / "approval-flow.gif"

    srcs = [
        src_dir / "01-menu.jpg",
        src_dir / "02-requests-pending.jpg",
        src_dir / "03-approved-row.jpg",
        src_dir / "04-audit-entry.jpg",
        src_dir / "05-reapproval-required.jpg",
        src_dir / "06-help-sidebar.jpg",
    ]

    missing = [p for p in srcs if not p.exists()]
    if missing:
        raise SystemExit(f"Missing inputs:\n" + "\n".join(f"- {p}" for p in missing))

    frames: list[Image.Image] = []
    for p in srcs:
        im = Image.open(p).convert("RGB")
        if args.width and im.width != args.width:
            h = int(im.height * (args.width / im.width))
            im = im.resize((args.width, h), Image.Resampling.LANCZOS)
        frames.append(im)

    # Convert to a palette image to keep file size sane.
    pal_frames: list[Image.Image] = []
    for i, im in enumerate(frames):
        # Floyd-Steinberg dithering improves gradients slightly for UI screenshots.
        pal = im.convert("P", palette=Image.Palette.ADAPTIVE, colors=256, dither=Image.Dither.FLOYDSTEINBERG)
        pal_frames.append(pal)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pal_frames[0].save(
        out_path,
        save_all=True,
        append_images=pal_frames[1:],
        duration=args.ms,
        loop=0,
        optimize=True,
        disposal=2,
    )

    print(f"Wrote: {out_path} ({out_path.stat().st_size/1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
