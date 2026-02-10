#!/usr/bin/env python3
"""Lightweight sanity checks for this Apps Script microproduct.

Goal: catch broken packaging / missing files / accidental deletions.

Usage:
  python3 scripts/validate_repo.py
"""

from __future__ import annotations

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

REQUIRED_CODE_SNIPPETS = [
    "function onOpen",
    "function onEdit",
    "function createDemoSetup",
    "REAPPROVAL_REQUIRED",
    "APPROVED",
    "PENDING",
]


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

    print("OK: repo validates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
