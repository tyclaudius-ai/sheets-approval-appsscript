#!/usr/bin/env python3
"""Lightweight sanity checks for this Apps Script microproduct.

Goal: catch broken packaging / missing files / accidental deletions.

Usage:
  python3 scripts/validate_repo.py

Options:
  --json   Emit machine-readable output (for dashboards/CI). Still exits non-zero on failure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


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


def validate() -> dict[str, Any]:
    """Return a structured validation report.

    Note: Callers decide whether to treat WARN/INFO as fatal.
    """

    report: dict[str, Any] = {
        "ok": True,
        "missingRequiredFiles": [],
        "missingScreenshotPlaceholders": [],
        "landingMissingScreenshotRefs": [],
        "missingCodeSnippets": [],
        "missingGalleryPNGs": [],
        "galleryPNGsStillPlaceholder": [],
    }

    missing_required = [p for p in REQUIRED_FILES if not (ROOT / p).exists()]
    if missing_required:
        report["ok"] = False
        report["missingRequiredFiles"] = missing_required

    missing_shots = [p for p in REQUIRED_SCREENSHOT_PLACEHOLDERS if not (ROOT / p).exists()]
    if missing_shots:
        report["ok"] = False
        report["missingScreenshotPlaceholders"] = missing_shots

    landing_path = ROOT / "landing/index.html"
    if landing_path.exists():
        landing = landing_path.read_text(encoding="utf-8")
        missing_refs = [p for p in REQUIRED_SCREENSHOT_PLACEHOLDERS if p not in landing]
        if missing_refs:
            report["ok"] = False
            report["landingMissingScreenshotRefs"] = missing_refs

    # appsscript.json should be valid JSON.
    manifest_path = ROOT / "appsscript.json"
    if manifest_path.exists():
        try:
            with manifest_path.open("r", encoding="utf-8") as f:
                json.load(f)
        except Exception as e:
            report["ok"] = False
            report["manifestJsonError"] = str(e)

    code_path = ROOT / "Code.gs"
    if code_path.exists():
        code = code_path.read_text(encoding="utf-8")
        missing_snips = [s for s in REQUIRED_CODE_SNIPPETS if s not in code]
        if missing_snips:
            report["ok"] = False
            report["missingCodeSnippets"] = missing_snips

    # Gallery PNG sanity checks (non-fatal; placeholders are allowed).
    missing_pngs = [p for p in OPTIONAL_GALLERY_PNGS if not (ROOT / p).exists()]
    if missing_pngs:
        report["missingGalleryPNGs"] = missing_pngs

    still_placeholder: list[str] = []
    for real_path, placeholder_path in PLACEHOLDER_PNG_TWINS.items():
        a = ROOT / real_path
        b = ROOT / placeholder_path
        if a.exists() and b.exists() and sha256_file(a) == sha256_file(b):
            still_placeholder.append(real_path)

    if still_placeholder:
        report["galleryPNGsStillPlaceholder"] = still_placeholder

    return report


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON report")
    args = ap.parse_args()

    report = validate()

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report.get("ok") else 1

    # Human-readable output.
    if not report.get("ok"):
        # Provide a compact reason summary.
        if report["missingRequiredFiles"]:
            raise SystemExit(f"Missing required files: {report['missingRequiredFiles']}")
        if report["missingScreenshotPlaceholders"]:
            raise SystemExit(f"Missing screenshot placeholders: {report['missingScreenshotPlaceholders']}")
        if report["landingMissingScreenshotRefs"]:
            raise SystemExit(f"landing/index.html missing screenshot refs: {report['landingMissingScreenshotRefs']}")
        if report.get("manifestJsonError"):
            raise SystemExit(f"appsscript.json invalid JSON: {report['manifestJsonError']}")
        if report["missingCodeSnippets"]:
            raise SystemExit(f"Code.gs missing expected snippets: {report['missingCodeSnippets']}")
        raise SystemExit("Repo validation failed")

    if report["missingGalleryPNGs"]:
        print(f"WARN: missing gallery PNGs (landing may look broken): {report['missingGalleryPNGs']}")

    if report["galleryPNGsStillPlaceholder"]:
        print(
            "INFO: these gallery PNGs are still placeholders (byte-identical to generated PNGs):\n"
            + "\n".join(f"  - {p}" for p in report["galleryPNGsStillPlaceholder"])
            + "\nTip: see REAL_SCREENSHOTS_GUIDE.md to replace them with real shots."
        )

    print("OK: repo validates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
