#!/usr/bin/env python3
"""Generate an animated GIF preview from the screenshot set.

This keeps docs/screenshots/approval-flow.gif in sync with the canonical
screenshot ordering defined by docs/screenshots/manifest.json.

Inputs (preferred):
- docs/screenshots/optimized/<id>.jpg (if present)
Fallback:
- docs/screenshots/<file> (from manifest)

Output:
- docs/screenshots/approval-flow.gif

Usage:
  python3 scripts/make_screenshot_gif.py

Options:
  --max-width 900        Downscale frames wider than this (keeps aspect)
  --duration-ms 900      Frame duration in ms
  --pause-ms 1500        Extra pause on the last frame
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


@dataclass(frozen=True)
class ManifestItem:
    id: str
    file: str


def _load_manifest_items(manifest_path: Path) -> list[ManifestItem]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    items = data.get("items")
    if not isinstance(items, list) or not items:
        raise SystemExit(f"manifest has no items: {manifest_path}")

    out: list[ManifestItem] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        item_id = it.get("id")
        file = it.get("file")
        if not item_id or not file:
            raise SystemExit(f"manifest item missing id/file: {it}")
        out.append(ManifestItem(id=str(item_id), file=str(file)))
    return out


def _best_image_path(docs_dir: Path, optimized_dir: Path, item: ManifestItem) -> Path:
    opt_jpg = optimized_dir / f"{item.id}.jpg"
    if opt_jpg.exists():
        return opt_jpg

    p = docs_dir / item.file
    if p.exists():
        return p

    raise SystemExit(f"missing image for {item.id}: tried {opt_jpg} then {p}")


def _pad_to(img: Image.Image, w: int, h: int, bg=(255, 255, 255)) -> Image.Image:
    if img.mode != "RGB":
        img = img.convert("RGB")
    canvas = Image.new("RGB", (w, h), color=bg)
    x = (w - img.width) // 2
    y = (h - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-width", type=int, default=900)
    ap.add_argument("--duration-ms", type=int, default=900)
    ap.add_argument("--pause-ms", type=int, default=1500)
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    docs_dir = root / "docs" / "screenshots"
    optimized_dir = docs_dir / "optimized"
    manifest_path = docs_dir / "manifest.json"
    out_path = docs_dir / "approval-flow.gif"

    items = _load_manifest_items(manifest_path)
    srcs = [_best_image_path(docs_dir, optimized_dir, it) for it in items]

    frames: list[Image.Image] = []
    max_w = 0
    max_h = 0

    for p in srcs:
        im = Image.open(p)
        im.load()

        # Normalize to RGB and downscale for size control.
        if im.mode == "RGBA":
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")

        if args.max_width and im.width > args.max_width:
            h = int(im.height * (args.max_width / im.width))
            im = im.resize((args.max_width, h), Image.Resampling.LANCZOS)

        frames.append(im)
        max_w = max(max_w, im.width)
        max_h = max(max_h, im.height)

    padded = [_pad_to(f, max_w, max_h) for f in frames]

    # Convert to palette images to keep file size sane.
    pal_frames: list[Image.Image] = []
    for im in padded:
        pal = im.convert(
            "P",
            palette=Image.Palette.ADAPTIVE,
            colors=256,
            dither=Image.Dither.FLOYDSTEINBERG,
        )
        pal_frames.append(pal)

    durations = [max(1, args.duration_ms)] * len(pal_frames)
    if durations:
        durations[-1] += max(0, args.pause_ms)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pal_frames[0].save(
        out_path,
        save_all=True,
        append_images=pal_frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )

    print(f"Wrote: {out_path} ({out_path.stat().st_size/1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
