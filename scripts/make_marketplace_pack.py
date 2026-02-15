#!/usr/bin/env python3
"""Build a single ZIP containing everything needed for a marketplace/product listing.

Goal: one artifact you can upload/send that includes:
- a listing-ready screenshots zip
- the full product bundle zip (Code.gs + docs + landing)
- listing copy (LISTING.md) + sales/outreach docs

This intentionally does NOT require Google login; it packages whatever screenshots
are currently in docs/screenshots/*.png (placeholders or real).

Usage:
  python3 scripts/make_marketplace_pack.py
  python3 scripts/make_marketplace_pack.py --out dist/marketplace-pack.zip
  # enforce only true screenshots (fails on placeholders + known real-ish mocks)
  python3 scripts/make_marketplace_pack.py --require-real-screenshots

Outputs:
  dist/marketplace-pack-<timestamp>.zip (default)
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def _run(cmd: list[str]) -> None:
    subprocess.check_call(cmd, cwd=ROOT)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default=None,
        help="Output zip path (default: dist/marketplace-pack-<timestamp>.zip)",
    )
    ap.add_argument(
        "--bundle-out",
        default=None,
        help="Override output path for the product bundle zip (default: timestamped in dist/)",
    )
    ap.add_argument(
        "--screens-out",
        default=None,
        help="Override output path for the screenshot pack zip (default: timestamped in dist/)",
    )
    ap.add_argument(
        "--require-real-screenshots",
        action="store_true",
        help="Fail the build if docs/screenshots/*.png are placeholders or known 'real-ish' mocks.",
    )
    args = ap.parse_args()

    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    out_path = Path(args.out) if args.out else (DIST / f"marketplace-pack-{ts}.zip")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # 0) Always refresh the real-screenshots status report so the pack reflects current state.
    _run([
        "python3",
        "scripts/check_screenshots.py",
        "--report-md",
        "docs/screenshots/REAL_SCREENSHOTS_STATUS.md",
    ])

    # Optional guardrails: ensure screenshots are truly captured (not placeholders / not known mocks).
    if args.require_real_screenshots:
        _run([
            "python3",
            "scripts/check_screenshots.py",
            "--fail-on-placeholders",
            "--fail-on-realish",
        ])

    # 1) Build the inner artifacts.
    bundle_out = args.bundle_out
    if bundle_out:
        _run(["python3", "scripts/package_sheets_approval_appsscript.py", "--out", bundle_out])
        bundle_path = ROOT / bundle_out
    else:
        _run(["python3", "scripts/package_sheets_approval_appsscript.py"])
        # pick newest matching bundle
        bundles = sorted(DIST.glob("sheets-approval-appsscript-bundle-*.zip"), key=lambda p: p.stat().st_mtime)
        if not bundles:
            raise SystemExit("No bundle zip found under dist/. Did packaging fail?")
        bundle_path = bundles[-1]

    screens_out = args.screens_out
    if screens_out:
        _run(["python3", "scripts/make_screenshot_pack.py", "--out", screens_out])
        screens_path = ROOT / screens_out
    else:
        _run(["python3", "scripts/make_screenshot_pack.py"])
        packs = sorted(DIST.glob("screenshot-pack-*.zip"), key=lambda p: p.stat().st_mtime)
        if not packs:
            raise SystemExit("No screenshot pack zip found under dist/. Did make_screenshot_pack fail?")
        screens_path = packs[-1]

    # 2) Create the final marketplace pack.
    include_files = [
        # top-level navigation / quickstart
        "START_HERE.md",
        "README.md",
        "QUICKSTART.md",
        "SETUP-CHECKLIST.md",
        "TROUBLESHOOTING.md",
        "TEMPLATE-INSTRUCTIONS.md",

        # product + delivery docs
        "CLIENT-HANDOFF.md",
        "ONE_PAGER.md",
        "DEMO.md",
        "DEMO-WALKTHROUGH.md",
        "DEMO-TEMPLATE.md",

        # screenshots
        "SCREENSHOTS.md",
        "REAL_SCREENSHOTS_GUIDE.md",

        # marketplace / sales assets
        "LISTING.md",
        "MARKETPLACE-LISTING-COPY.md",
        "MARKETPLACE-CHECKLIST.md",
        "SALES.md",
        "OUTREACH-TEMPLATES.md",
        "INTAKE_QUESTIONS.md",
    ]

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # docs/copy
        for rel in include_files:
            p = ROOT / rel
            if p.exists() and p.is_file():
                z.write(p, f"marketplace-pack/{rel}")

        # inner zips
        z.write(bundle_path, f"marketplace-pack/dist/{bundle_path.name}")
        z.write(screens_path, f"marketplace-pack/dist/{screens_path.name}")

        # convenience: include rendered landing page + screenshots directory
        for sub in ["landing", "docs/screenshots"]:
            base = ROOT / sub
            if not base.exists():
                continue
            for fp in sorted(base.rglob("*")):
                if fp.is_dir():
                    continue
                if fp.name in {".DS_Store"}:
                    continue
                z.write(fp, f"marketplace-pack/{fp.relative_to(ROOT)}")

    size_kb = out_path.stat().st_size / 1024.0
    print(f"Wrote: {out_path} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
