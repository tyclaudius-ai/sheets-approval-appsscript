#!/usr/bin/env python3
"""Lightweight sanity checks for this Apps Script microproduct.

Goal: catch broken packaging / missing files / accidental deletions.

Usage:
  python3 scripts/validate_repo.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "Code.gs",
    "Docs.html",
    "appsscript.json",
    "README.md",
    "ONE_PAGER.md",
    "SETUP-CHECKLIST.md",
    "DEMO-TEMPLATE.md",
    "CLIENT-HANDOFF.md",
    "OUTREACH-TEMPLATES.md",
    "SHEET-SCHEMA.md",
    "SCREENSHOTS.md",
    "TEMPLATE-INSTRUCTIONS.md",
    "landing/index.html",
    "landing/style.css",
]

# Placeholder screenshots are intentionally SVG so you can ship a "screenshot set"
# without leaking client data. The landing page should reference them.
REQUIRED_SCREENSHOT_PLACEHOLDERS = [
    "docs/screenshots/01-menu.svg",
    "docs/screenshots/02-requests-pending.svg",
    "docs/screenshots/03-approved-row.svg",
    "docs/screenshots/04-audit-entry.svg",
    "docs/screenshots/05-reapproval-required.svg",
    "docs/screenshots/06-help-sidebar.svg",
]

# Top-level PNGs are what the landing page uses for the gallery. They can be either:
# - real screenshots (preferred for a listing)
# - placeholder PNGs (generated from SVGs) as a safe default
OPTIONAL_GALLERY_PNGS = [
    "docs/screenshots/01-menu.png",
    "docs/screenshots/02-requests-pending.png",
    "docs/screenshots/03-approved-row.png",
    "docs/screenshots/04-audit-entry.png",
    "docs/screenshots/05-reapproval-required.png",
    "docs/screenshots/06-help-sidebar.png",
]

# If a top-level PNG byte-for-byte matches its generated placeholder twin, we
# consider it "still placeholder" (not an error; just useful signal).
PLACEHOLDER_PNG_TWINS = {
    "docs/screenshots/01-menu.png": "docs/screenshots/png/01-menu.png",
    "docs/screenshots/02-requests-pending.png": "docs/screenshots/png/02-requests-pending.png",
    "docs/screenshots/03-approved-row.png": "docs/screenshots/png/03-approved-row.png",
    "docs/screenshots/04-audit-entry.png": "docs/screenshots/png/04-audit-entry.png",
    "docs/screenshots/05-reapproval-required.png": "docs/screenshots/png/05-reapproval-required.png",
    "docs/screenshots/06-help-sidebar.png": "docs/screenshots/png/06-help-sidebar.png",
}

REQUIRED_CODE_SNIPPETS = [
    "function onOpen",
    "function onEdit",
    "function createDemoSetup",
    "REAPPROVAL_REQUIRED",
    "APPROVED",
    "PENDING",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    missing = [p for p in REQUIRED_FILES if not (ROOT / p).exists()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")

    # Screenshot placeholder set should exist.
    missing_shots = [p for p in REQUIRED_SCREENSHOT_PLACEHOLDERS if not (ROOT / p).exists()]
    if missing_shots:
        raise SystemExit(f"Missing screenshot placeholders: {missing_shots}")

    # landing/index.html should reference each placeholder (ensures the landing page doesn't drift).
    landing = (ROOT / "landing/index.html").read_text(encoding="utf-8")
    missing_refs = [p for p in REQUIRED_SCREENSHOT_PLACEHOLDERS if p not in landing]
    if missing_refs:
        raise SystemExit(f"landing/index.html missing screenshot refs: {missing_refs}")

    # appsscript.json should be valid JSON.
    manifest_path = ROOT / "appsscript.json"
    with manifest_path.open("r", encoding="utf-8") as f:
        json.load(f)

    code = (ROOT / "Code.gs").read_text(encoding="utf-8")
    missing_snips = [s for s in REQUIRED_CODE_SNIPPETS if s not in code]
    if missing_snips:
        raise SystemExit(f"Code.gs missing expected snippets: {missing_snips}")

    # Gallery PNG sanity checks (non-fatal; placeholders are allowed).
    missing_pngs = [p for p in OPTIONAL_GALLERY_PNGS if not (ROOT / p).exists()]
    if missing_pngs:
        print(f"WARN: missing gallery PNGs (landing may look broken): {missing_pngs}")

    still_placeholder: list[str] = []
    for real_path, placeholder_path in PLACEHOLDER_PNG_TWINS.items():
        a = ROOT / real_path
        b = ROOT / placeholder_path
        if a.exists() and b.exists() and sha256_file(a) == sha256_file(b):
            still_placeholder.append(real_path)

    if still_placeholder:
        print(
            "INFO: these gallery PNGs are still placeholders (byte-identical to generated PNGs):\n"
            + "\n".join(f"  - {p}" for p in still_placeholder)
            + "\nTip: see REAL_SCREENSHOTS_GUIDE.md to replace them with real shots."
        )

    print("OK: repo validates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
