#!/usr/bin/env python3
"""Render docs/screenshots README + HTML gallery from docs/screenshots/manifest.json.

Why: keeps filenames/titles/captions in sync, and produces a clean gallery page you can
link in README / listings.

Usage:
  python3 scripts/render_screenshots_gallery.py

Outputs:
  - docs/screenshots/README.md
  - docs/screenshots/gallery.html
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOT_DIR = ROOT / "docs" / "screenshots"
MANIFEST = SHOT_DIR / "manifest.json"
OUT_README = SHOT_DIR / "README.md"
OUT_HTML = SHOT_DIR / "gallery.html"


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    title = data.get("title", "Screenshots")
    items = data.get("items", [])

    # README.md
    md = []
    md.append("# Screenshots\n")
    md.append("\n")
    md.append("These images are what the landing page (and a product listing) should reference.\n")
    md.append("\n")
    md.append("If you haven’t captured real screenshots yet, the repo ships placeholder PNGs with the same filenames.\n")
    md.append("\n")
    md.append("## Screenshot set\n")

    for it in items:
        heading = it.get("heading") or it.get("id")
        file = it.get("file")
        caption = it.get("caption", "")
        md.append(f"\n{heading}\n\n")
        if caption:
            md.append(f"{caption}\n\n")
        md.append(f"![{it.get('id','screenshot')}](./{file})\n")

    md.append("\n## Capturing real screenshots\n\n")
    md.append("Follow: [`REAL_SCREENSHOTS_GUIDE.md`](../../REAL_SCREENSHOTS_GUIDE.md)\n\n")
    md.append("After capturing, verify none are still placeholders:\n\n")
    md.append("```bash\npython3 scripts/check_screenshots.py\n```\n")
    md.append("\nOptional: regenerate this README + the HTML gallery from the manifest:\n\n")
    md.append("```bash\npython3 scripts/render_screenshots_gallery.py\n```\n")

    OUT_README.write_text("".join(md), encoding="utf-8")

    # gallery.html
    parts = []
    parts.append("<!doctype html>\n")
    parts.append("<html lang=\"en\">\n")
    parts.append("<head>\n")
    parts.append("  <meta charset=\"utf-8\"/>\n")
    parts.append("  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>\n")
    parts.append(f"  <title>{html.escape(title)}</title>\n")
    parts.append("  <style>\n")
    parts.append("    body{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;line-height:1.4;margin:24px;max-width:980px}\n")
    parts.append("    h1{margin:0 0 12px}\n")
    parts.append("    .item{margin:22px 0;padding:18px;border:1px solid #e5e7eb;border-radius:10px}\n")
    parts.append("    img{width:100%;height:auto;border-radius:8px;border:1px solid #f3f4f6}\n")
    parts.append("    .cap{color:#374151;margin:8px 0 0}\n")
    parts.append("    .id{color:#6b7280;font-size:12px;margin-top:6px}\n")
    parts.append("  </style>\n")
    parts.append("</head>\n")
    parts.append("<body>\n")
    parts.append(f"  <h1>{html.escape(title)}</h1>\n")
    parts.append("  <p>Generated from <code>docs/screenshots/manifest.json</code>.</p>\n")

    for it in items:
        heading = it.get("heading") or it.get("id")
        file = it.get("file")
        caption = it.get("caption", "")
        parts.append("  <div class=\"item\">\n")
        parts.append(f"    <h2>{html.escape(heading)}</h2>\n")
        parts.append(f"    <img src=\"{html.escape(file)}\" alt=\"{html.escape(it.get('id','screenshot'))}\"/>\n")
        if caption:
            parts.append(f"    <div class=\"cap\">{html.escape(caption)}</div>\n")
        parts.append(f"    <div class=\"id\">{html.escape(it.get('id',''))}</div>\n")
        parts.append("  </div>\n")

    parts.append("</body>\n</html>\n")
    OUT_HTML.write_text("".join(parts), encoding="utf-8")

    print(f"Wrote {OUT_README.relative_to(ROOT)}")
    print(f"Wrote {OUT_HTML.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
