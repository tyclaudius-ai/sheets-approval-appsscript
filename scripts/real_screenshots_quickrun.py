#!/usr/bin/env python3
"""One-command helper to install + validate REAL screenshots and rebuild the gallery.

This is a thin wrapper around existing scripts:
- install_real_screenshots.py
- check_screenshots.py
- screenshots_pipeline.py

Designed so Jaxon (or anyone) can run ONE command after capturing screenshots.

Usage:
  python3 scripts/real_screenshots_quickrun.py

Optional:
  python3 scripts/real_screenshots_quickrun.py --require-pixels 1688x1008 --fail-on-dim-mismatch
  python3 scripts/real_screenshots_quickrun.py --no-open   # CI/headless
  python3 scripts/real_screenshots_quickrun.py --open      # force-open status+gallery (macOS)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    print("\n$ " + " ".join(cmd))
    subprocess.run(cmd, cwd=str(REPO_ROOT), check=True)


def is_macos() -> bool:
    return sys.platform == "darwin"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--from",
        dest="from_dir",
        default="AUTO",
        help="Where to look for newly captured screenshots (AUTO|~/Desktop|~/Downloads|...).",
    )
    ap.add_argument(
        "--require-pixels",
        default=None,
        help='Optional pixel gate like "1688x1008" (pairs with --fail-on-dim-mismatch).',
    )
    ap.add_argument(
        "--fail-on-dim-mismatch",
        action="store_true",
        help="If set, any dimension mismatch fails the run.",
    )
    ap.add_argument(
        "--redact-preset",
        default=None,
        help="Optional redaction preset to run after install (e.g. sheets_account_topright_large).",
    )
    ap.add_argument(
        "--open",
        action="store_true",
        help="Force opening the HTML status + gallery (macOS only).",
    )
    ap.add_argument(
        "--no-open",
        action="store_true",
        help="Never open files automatically (useful for CI/headless).",
    )
    args = ap.parse_args()

    def maybe_pbcopy(path: Path) -> None:
        if not is_macos():
            return
        if not path.exists():
            return
        if not (sys.stdout.isatty() and sys.stderr.isatty()):
            return
        try:
            # macOS clipboard
            txt = path.read_text(encoding="utf-8")
            subprocess.run(["pbcopy"], input=txt.encode("utf-8"), check=True)
            print(f"[clipboard] Copied {path.as_posix()} to clipboard")
        except Exception:
            # Clipboard is a nice-to-have; never fail the run on this.
            pass

    # 1) Always emit a fresh status report first (useful even if nothing else happens)
    run(
        [
            sys.executable,
            "scripts/check_screenshots.py",
            "--report-md",
            "docs/screenshots/REAL_SCREENSHOTS_STATUS.md",
            "--report-html",
            "docs/screenshots/REAL_SCREENSHOTS_STATUS.html",
            "--report-json",
            "docs/screenshots/REAL_SCREENSHOTS_STATUS.json",
            "--report-jaxon",
            "docs/screenshots/JAXON_NEXT_ACTIONS.md",
        ]
    )
    maybe_pbcopy(REPO_ROOT / "docs/screenshots/JAXON_NEXT_ACTIONS.md")

    # 2) Attempt install+optimize from the configured directory (or AUTO)
    # This is safe even if the user hasn't captured anything yet; it will error with a clear message.
    install_cmd = [
        sys.executable,
        "scripts/install_real_screenshots.py",
        "--from",
        args.from_dir,
        "--check",
        "--optimize",
    ]
    if args.redact_preset:
        install_cmd += ["--redact-preset", args.redact_preset]

    try:
        run(install_cmd)
    except subprocess.CalledProcessError as e:
        print(
            "\nInstall step failed (likely: no new screenshots found yet).\n"
            "If you just captured shots, ensure they are saved to Desktop/Downloads (or use --from).\n"
            "You can also use the guided flow:\n"
            "  python3 scripts/install_real_screenshots.py --from AUTO --guided\n",
            file=sys.stderr,
        )

        should_open = (
            is_macos()
            and not args.no_open
            and (args.open or (sys.stdout.isatty() and sys.stderr.isatty()))
        )

        # On macOS, pop open the quickrun docs so the user can recover fast.
        if should_open:
            quickrun_md = REPO_ROOT / "docs/screenshots/REAL_SCREENSHOTS_QUICKRUN.md"
            shotlist_md = REPO_ROOT / "docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md"
            cheatsheet_md = REPO_ROOT / "docs/screenshots/CAPTURE-CHEATSHEET.md"
            for p in (quickrun_md, shotlist_md, cheatsheet_md):
                if p.exists():
                    try:
                        run(["open", str(p)])
                    except Exception:
                        pass

        return e.returncode

    # 3) Validate that everything is truly REAL (not placeholder/real-ish) + (optionally) pixel dims
    check_cmd = [
        sys.executable,
        "scripts/check_screenshots.py",
        "--require-real-screenshots",
    ]
    if args.require_pixels:
        check_cmd += ["--require-pixels", args.require_pixels]
        if args.fail_on_dim_mismatch:
            check_cmd += ["--fail-on-dim-mismatch"]
    run(check_cmd)

    # 4) Rebuild derived assets + gallery
    pipeline_cmd = [
        sys.executable,
        "scripts/screenshots_pipeline.py",
        "--optimize",
        "--width",
        "1400",
        "--status",
        "--render-gallery",
    ]
    run(pipeline_cmd)

    # Re-emit next-actions after changes (handy to paste into chat/PR notes).
    run(
        [
            sys.executable,
            "scripts/check_screenshots.py",
            "--report-jaxon",
            "docs/screenshots/JAXON_NEXT_ACTIONS.md",
        ]
    )
    maybe_pbcopy(REPO_ROOT / "docs/screenshots/JAXON_NEXT_ACTIONS.md")

    should_open = (
        is_macos()
        and not args.no_open
        and (args.open or (sys.stdout.isatty() and sys.stderr.isatty()))
    )

    # 5) Open the visual status + gallery on macOS for sanity check
    if should_open:
        status_html = REPO_ROOT / "docs/screenshots/REAL_SCREENSHOTS_STATUS.html"
        gallery_html = REPO_ROOT / "docs/screenshots/gallery.html"
        if status_html.exists():
            run(["open", str(status_html)])
        if gallery_html.exists():
            run(["open", str(gallery_html)])

    print("\nOK: installed + validated REAL screenshots and rebuilt the gallery.")
    print("Next: run make_marketplace_pack if you want a fresh listing bundle:")
    print("  python3 scripts/make_marketplace_pack.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
