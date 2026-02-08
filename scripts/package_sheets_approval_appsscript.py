#!/usr/bin/env python3
"""Package the Sheets Approval + Audit Trail microproduct into a distributable zip.

Why: makes it easy to hand a client a single artifact containing Code.gs + docs + landing page.

Usage:
  python3 scripts/package_sheets_approval_appsscript.py
  python3 scripts/package_sheets_approval_appsscript.py --out dist/sheets-approval.zip

By default writes to:
  dist/sheets-approval-appsscript-bundle-<timestamp>.zip
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[1]
# This script lives in the repo at: sheets-approval-appsscript/scripts/
# Package files from the repo root.
PKG_DIR = ROOT
DEFAULT_INCLUDE = [
    "Code.gs",
    "appsscript.json",
    "README.md",
    "ONE_PAGER.md",
    "SETUP-CHECKLIST.md",
    "DEMO-TEMPLATE.md",
    "OUTREACH-TEMPLATES.md",
    "landing/index.html",
    "landing/style.css",
]


def _git_sha() -> str | None:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT)
        return out.decode().strip()
    except Exception:
        return None


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        help="Output zip path (default: dist/sheets-approval-appsscript-bundle-<timestamp>.zip)",
        default=None,
    )
    ap.add_argument(
        "--include",
        action="append",
        default=[],
        help="Additional relative paths under secret-project-2/sheets-approval-appsscript to include",
    )
    args = ap.parse_args()

    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    out_path = Path(args.out) if args.out else (ROOT / "dist" / f"sheets-approval-appsscript-bundle-{ts}.zip")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    include = DEFAULT_INCLUDE + list(args.include)

    missing: list[str] = []
    files: list[tuple[Path, str]] = []
    for rel in include:
        p = PKG_DIR / rel
        if not p.exists():
            missing.append(rel)
            continue
        files.append((p, rel))

    if missing:
        raise SystemExit(f"Missing expected files: {missing}")

    manifest = {
        "name": "sheets-approval-appsscript",
        "builtAt": ts,
        "gitSha": _git_sha(),
        "files": [],
    }

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for src, rel in files:
            arcname = f"sheets-approval-appsscript/{rel}"
            z.write(src, arcname)
            manifest["files"].append(
                {
                    "path": rel,
                    "sha256": _sha256_file(src),
                    "bytes": src.stat().st_size,
                }
            )

        z.writestr(
            "sheets-approval-appsscript/manifest.json",
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        )

    size_kb = out_path.stat().st_size / 1024.0
    print(f"Wrote: {out_path} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
