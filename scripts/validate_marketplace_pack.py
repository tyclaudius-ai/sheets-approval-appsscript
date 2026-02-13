#!/usr/bin/env python3
"""Validate a marketplace-pack zip created by scripts/make_marketplace_pack.py.

This is a *static* validator: it does not require Google login.

Checks:
- required top-level docs are present under marketplace-pack/
- inner dist zips exist (bundle + screenshot pack)
- screenshot pack zip contains at least N images
- no obvious junk files (e.g. .DS_Store)

Usage:
  python3 scripts/validate_marketplace_pack.py dist/marketplace-pack-*.zip
  python3 scripts/validate_marketplace_pack.py dist/marketplace-pack.zip --min-screens 6
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import zipfile


REQUIRED_DOCS = [
    "LISTING.md",
    "README.md",
    "DEMO.md",
    "SCREENSHOTS.md",
    "MARKETPLACE-CHECKLIST.md",
]


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]
    warnings: list[str]


def _zip_list(z: zipfile.ZipFile) -> set[str]:
    return {i.filename for i in z.infolist() if not i.is_dir()}


def validate_marketplace_pack(zip_path: Path, *, min_screens: int) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if not zip_path.exists():
        return ValidationResult(False, [f"File not found: {zip_path}"], [])

    with zipfile.ZipFile(zip_path, "r") as z:
        names = _zip_list(z)

        # junk
        junk = [n for n in names if n.endswith(".DS_Store") or "/__MACOSX/" in n]
        if junk:
            warnings.append(f"Found macOS junk entries ({len(junk)}): e.g. {junk[0]}")

        # required docs
        for rel in REQUIRED_DOCS:
            p = f"marketplace-pack/{rel}"
            if p not in names:
                errors.append(f"Missing required file in pack: {p}")

        # inner zips
        dist_zips = sorted([n for n in names if n.startswith("marketplace-pack/dist/") and n.endswith(".zip")])
        if len(dist_zips) < 2:
            errors.append(
                "Expected at least 2 inner zip files under marketplace-pack/dist/ (bundle + screenshots)"
            )
        screenshot_zip_name = None
        for n in dist_zips:
            if "screenshot-pack-" in n:
                screenshot_zip_name = n
                break
        if not screenshot_zip_name:
            warnings.append(
                "Could not find screenshot-pack-*.zip under marketplace-pack/dist/ (naming changed?)"
            )

        # screenshot count (from embedded screenshot pack)
        if screenshot_zip_name:
            with z.open(screenshot_zip_name) as embedded:
                # zipfile can read from a file-like object, but it needs random access.
                # Read into memory: screenshot packs are small.
                data = embedded.read()
            from io import BytesIO

            with zipfile.ZipFile(BytesIO(data), "r") as sz:
                snames = _zip_list(sz)
                pngs = [n for n in snames if n.lower().endswith(".png")]
                jpgs = [n for n in snames if n.lower().endswith((".jpg", ".jpeg"))]
                if len(pngs) + len(jpgs) < min_screens:
                    errors.append(
                        f"Screenshot pack has only {len(pngs)+len(jpgs)} images (< {min_screens})."
                    )

        # ensure screenshots directory included (for convenience)
        has_docs_screens = any(n.startswith("marketplace-pack/docs/screenshots/") for n in names)
        if not has_docs_screens:
            warnings.append(
                "Pack does not include marketplace-pack/docs/screenshots/ directory (convenience copy)."
            )

    return ValidationResult(ok=(len(errors) == 0), errors=errors, warnings=warnings)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("zip", type=Path, help="Path to dist/marketplace-pack-*.zip")
    ap.add_argument(
        "--min-screens",
        type=int,
        default=6,
        help="Minimum number of images expected in the embedded screenshot pack (default: 6)",
    )
    args = ap.parse_args()

    res = validate_marketplace_pack(args.zip, min_screens=args.min_screens)

    if res.warnings:
        print("WARNINGS:")
        for w in res.warnings:
            print(f"- {w}")
        print("")

    if res.errors:
        print("ERRORS:")
        for e in res.errors:
            print(f"- {e}")
        return 2

    print("OK: marketplace pack looks good")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
