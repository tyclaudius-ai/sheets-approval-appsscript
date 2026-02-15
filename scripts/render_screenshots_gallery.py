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
OUT_DECK = SHOT_DIR / "deck.html"
OUT_CAPTURE = SHOT_DIR / "capture-checklist.html"


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    title = data.get("title", "Screenshots")
    items = data.get("items", [])

    # README.md
    # NOTE: This generator is meant to match the human-friendly README content
    # (with richer capture/packaging instructions), while keeping the screenshot
    # list itself manifest-driven.
    md: list[str] = []
    md.append("# Screenshots\n\n")
    md.append("These images are what the landing page (and a product listing) should reference.\n\n")
    md.append("If you haven’t captured real screenshots yet, the repo ships placeholder PNGs with the same filenames.\n\n")

    md.append("## Screenshot set\n")

    md.append("Tip: there’s also a simple, printable ‘deck’ view at [`deck.html`](./deck.html) (generated from the same manifest).\n")
    md.append("If you’re capturing real screenshots, there’s a printable checklist at [`capture-checklist.html`](./capture-checklist.html).\n")

    for it in items:
        heading = it.get("heading") or it.get("id")
        file = it.get("file")
        caption = (it.get("caption") or "").strip()
        md.append(f"\n{heading}\n\n")
        if caption:
            md.append(f"{caption}\n\n")
        md.append(f"![{it.get('id','screenshot')}](./{file})\n")

    md.append("\n## Capturing real screenshots\n\n")
    md.append("Fast path (10 minutes): [`REAL_SCREENSHOTS_QUICKRUN.md`](./REAL_SCREENSHOTS_QUICKRUN.md)\n\n")
    md.append("Full guide: [`REAL_SCREENSHOTS_GUIDE.md`](../../REAL_SCREENSHOTS_GUIDE.md)\n\n")
    md.append(
        "If you want a “handoff bundle” to send to whoever will do the capture, you can build a small zip with the shotlist + install/check scripts:\n\n"
    )
    md.append("```bash\npython3 scripts/make_real_screenshot_capture_pack.py\n```\n\n")

    md.append(
        "After capturing, the easiest path is to run the all-in-one pipeline (installs, validates, refreshes STATUS.md, and re-renders the gallery):\n\n"
    )
    md.append(
        "```bash\npython3 scripts/screenshots_pipeline.py --from ~/Desktop --check --fail-on-placeholders --status --render-gallery\n```\n\n"
    )

    md.append("If you prefer individual commands:\n\n")
    md.append(
        "```bash\n"
        "python3 scripts/check_screenshots.py\n"
        "python3 scripts/screenshot_status.py --write\n"
        "python3 scripts/render_screenshots_gallery.py\n"
        "```\n"
    )

    md.append("\n## Optional: optimized JPGs\n\n")
    md.append("If you run the screenshot optimizer, it will generate:\n\n")
    md.append("- `docs/screenshots/optimized/*.jpg`\n\n")
    md.append(
        "The landing page will automatically prefer these when present (via a `<picture>` tag), falling back to the PNGs.\n"
    )

    md.append("\n## Optional: animated preview GIF\n\n")
    md.append("Quick animated preview (useful for READMEs / listings):\n\n")
    md.append("![approval-flow](./approval-flow.gif)\n\n")
    md.append("You can (re)generate it from the optimized JPGs:\n\n")
    md.append("```bash\npython3 scripts/make_screenshot_gif.py\n```\n\n")
    md.append("Output:\n- `docs/screenshots/approval-flow.gif`\n\n")

    md.append("## Packaging a listing-ready ZIP\n\n")
    md.append("To generate a single ZIP you can upload to marketplaces:\n\n")
    md.append("```bash\npython3 scripts/make_screenshot_pack.py\n```\n\n")
    md.append("Output:\n- `dist/screenshot-pack-YYYYMMDD-HHMM.zip`\n")

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

    # deck.html (print-friendly)
    deck = []
    deck.append("<!doctype html>\n")
    deck.append("<html lang=\"en\">\n")
    deck.append("<head>\n")
    deck.append("  <meta charset=\"utf-8\"/>\n")
    deck.append("  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>\n")
    deck.append(f"  <title>{html.escape(title)} — Deck</title>\n")
    deck.append("  <style>\n")
    deck.append("    :root{--max:1100px;--border:#e5e7eb;--muted:#6b7280}\n")
    deck.append("    body{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;line-height:1.35;margin:24px;background:#fff;color:#111827}\n")
    deck.append("    header{max-width:var(--max);margin:0 auto 20px}\n")
    deck.append("    h1{margin:0 0 6px;font-size:28px}\n")
    deck.append("    .sub{color:var(--muted);font-size:14px}\n")
    deck.append("    .slide{max-width:var(--max);margin:18px auto;padding:16px;border:1px solid var(--border);border-radius:12px}\n")
    deck.append("    .slide h2{margin:0 0 10px;font-size:18px}\n")
    deck.append("    .slide img{width:100%;height:auto;border-radius:10px;border:1px solid #f3f4f6}\n")
    deck.append("    .cap{margin-top:10px;color:#374151}\n")
    deck.append("    .meta{margin-top:6px;color:var(--muted);font-size:12px}\n")
    deck.append("    @media print{\n")
    deck.append("      body{margin:0}\n")
    deck.append("      header{padding:16px 16px 0}\n")
    deck.append("      .slide{border:none;border-radius:0;page-break-after:always;break-after:page;padding:16px}\n")
    deck.append("      .slide:last-child{page-break-after:auto;break-after:auto}\n")
    deck.append("    }\n")
    deck.append("  </style>\n")
    deck.append("</head>\n")
    deck.append("<body>\n")
    deck.append("  <header>\n")
    deck.append(f"    <h1>{html.escape(title)} — Deck</h1>\n")
    deck.append("    <div class=\"sub\">Print-friendly view generated from <code>docs/screenshots/manifest.json</code>.</div>\n")
    deck.append("  </header>\n")

    for it in items:
        heading = it.get("heading") or it.get("id")
        file = it.get("file")
        caption = (it.get("caption") or "").strip()
        deck.append("  <section class=\"slide\">\n")
        deck.append(f"    <h2>{html.escape(heading)}</h2>\n")
        deck.append(f"    <img src=\"{html.escape(file)}\" alt=\"{html.escape(it.get('id','screenshot'))}\"/>\n")
        if caption:
            deck.append(f"    <div class=\"cap\">{html.escape(caption)}</div>\n")
        deck.append(f"    <div class=\"meta\">{html.escape(it.get('id',''))}</div>\n")
        deck.append("  </section>\n")

    deck.append("</body>\n</html>\n")
    OUT_DECK.write_text("".join(deck), encoding="utf-8")

    # capture-checklist.html (printable checklist + thumbnails)
    cap = []
    cap.append("<!doctype html>\n")
    cap.append('<html lang="en">\n')
    cap.append("<head>\n")
    cap.append("  <meta charset=\"utf-8\"/>\n")
    cap.append("  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"/>\n")
    cap.append(f"  <title>{html.escape(title)} — Capture checklist</title>\n")
    cap.append("  <style>\n")
    cap.append("    :root{--max:1100px;--border:#e5e7eb;--muted:#6b7280}\n")
    cap.append("    body{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;line-height:1.35;margin:24px;background:#fff;color:#111827}\n")
    cap.append("    header{max-width:var(--max);margin:0 auto 18px}\n")
    cap.append("    h1{margin:0 0 6px;font-size:26px}\n")
    cap.append("    .sub{color:var(--muted);font-size:14px}\n")
    cap.append("    .links{margin-top:10px;font-size:14px}\n")
    cap.append("    .links a{margin-right:12px}\n")
    cap.append("    .item{max-width:var(--max);margin:16px auto;padding:14px;border:1px solid var(--border);border-radius:12px}\n")
    cap.append("    .row{display:flex;gap:16px;align-items:flex-start}\n")
    cap.append("    .thumb{width:44%;min-width:320px}\n")
    cap.append("    img{width:100%;height:auto;border-radius:10px;border:1px solid #f3f4f6}\n")
    cap.append("    .meta{flex:1}\n")
    cap.append("    .meta h2{margin:0 0 6px;font-size:18px}\n")
    cap.append("    .file{color:var(--muted);font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;font-size:12px}\n")
    cap.append("    .cap{margin-top:8px;color:#374151}\n")
    cap.append("    .check{margin-top:10px;font-size:14px}\n")
    cap.append("    .check input{transform:scale(1.15);margin-right:8px}\n")
    cap.append("    @media print{\n")
    cap.append("      body{margin:0}\n")
    cap.append("      header{padding:16px 16px 0}\n")
    cap.append("      .item{border:none;border-radius:0;page-break-inside:avoid;break-inside:avoid;padding:12px 16px}\n")
    cap.append("      a{color:#111827;text-decoration:none}\n")
    cap.append("    }\n")
    cap.append("  </style>\n")
    cap.append("</head>\n")
    cap.append("<body>\n")
    cap.append("  <header>\n")
    cap.append(f"    <h1>{html.escape(title)} — Capture checklist</h1>\n")
    cap.append("    <div class=\"sub\">Print this (or keep it open) while you capture REAL screenshots. Generated from <code>docs/screenshots/manifest.json</code>.</div>\n")
    cap.append("    <div class=\"links\">\n")
    cap.append("      Helpful: ")
    cap.append("<a href=\"REAL_SCREENSHOTS_QUICKRUN.md\">quick run</a>")
    cap.append("<a href=\"REAL_SCREENSHOTS_SHOTLIST.md\">shotlist</a>")
    cap.append("<a href=\"CAPTURE-CHEATSHEET.md\">cheatsheet</a>")
    cap.append("<a href=\"gallery.html\">gallery</a>")
    cap.append("<a href=\"deck.html\">deck</a>\n")
    cap.append("    </div>\n")
    cap.append("  </header>\n")

    for idx, it in enumerate(items, start=1):
        heading = it.get("heading") or it.get("id")
        file = it.get("file")
        caption = (it.get("caption") or "").strip()
        item_id = it.get("id", "")

        cap.append("  <section class=\"item\">\n")
        cap.append("    <div class=\"row\">\n")
        cap.append("      <div class=\"thumb\">\n")
        cap.append(f"        <img src=\"{html.escape(file)}\" alt=\"{html.escape(item_id or 'screenshot')}\"/>\n")
        cap.append("      </div>\n")
        cap.append("      <div class=\"meta\">\n")
        cap.append(f"        <h2>{idx:02d} — {html.escape(heading)}</h2>\n")
        cap.append(f"        <div class=\"file\">Expected filename: {html.escape(file)}</div>\n")
        if caption:
            cap.append(f"        <div class=\"cap\">{html.escape(caption)}</div>\n")
        cap.append("        <div class=\"check\">\n")
        cap.append(f"          <label><input type=\"checkbox\"/>Captured (real)</label>\n")
        cap.append("        </div>\n")
        cap.append("      </div>\n")
        cap.append("    </div>\n")
        cap.append("  </section>\n")

    cap.append("</body>\n</html>\n")
    OUT_CAPTURE.write_text("".join(cap), encoding="utf-8")

    print(f"Wrote {OUT_README.relative_to(ROOT)}")
    print(f"Wrote {OUT_HTML.relative_to(ROOT)}")
    print(f"Wrote {OUT_DECK.relative_to(ROOT)}")
    print(f"Wrote {OUT_CAPTURE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
