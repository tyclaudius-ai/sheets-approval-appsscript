#!/usr/bin/env python3
"""Convenience pipeline for installing + validating + optimizing screenshot assets.

This repo supports two screenshot sets:
- Real screenshots: captured from Google Sheets (preferred for listings)
- "Real-ish" screenshots: generated offline (placeholders) for dev/demo

This script bundles the common commands into one repeatable pipeline.

Examples
--------
# Install real screenshots from Desktop, then validate, then build optimized JPGs
python3 scripts/screenshots_pipeline.py --from ~/Desktop --check --fail-on-placeholders --optimize --width 1400

# Then generate the approval-flow.gif used in README/landing previews
python3 scripts/screenshots_pipeline.py --make-gif --gif-width 900 --gif-ms 900

# Just validate what's currently in docs/screenshots
python3 scripts/screenshots_pipeline.py --check --fail-on-placeholders

# After any changes, re-render gallery files
python3 scripts/screenshots_pipeline.py --render-gallery
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=str(REPO_ROOT), check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--from",
        dest="from_dir",
        help="Directory containing captured screenshots (e.g. ~/Desktop).",
    )
    ap.add_argument(
        "--check",
        action="store_true",
        help="Run scripts/check_screenshots.py to validate expected files exist.",
    )
    ap.add_argument(
        "--fail-on-placeholders",
        action="store_true",
        help="Fail if docs/screenshots/*.png are still placeholders.",
    )
    ap.add_argument(
        "--optimize",
        action="store_true",
        help="Generate optimized JPGs under docs/screenshots/optimized/.",
    )
    ap.add_argument(
        "--width",
        type=int,
        default=1400,
        help="Target width for optimized JPGs (default: 1400).",
    )
    ap.add_argument(
        "--render-gallery",
        action="store_true",
        help="Regenerate docs/screenshots/README.md + gallery.html from manifest.json.",
    )
    ap.add_argument(
        "--make-gif",
        action="store_true",
        help="Generate docs/screenshots/approval-flow.gif from optimized JPGs.",
    )
    ap.add_argument(
        "--gif-width",
        type=int,
        default=900,
        help="Frame resize width for --make-gif (default: 900).",
    )
    ap.add_argument(
        "--gif-ms",
        type=int,
        default=900,
        help="Frame duration in ms for --make-gif (default: 900).",
    )

    args = ap.parse_args()

    # Default behavior: quick sanity check + refresh rendered gallery docs.
    if not (
        args.from_dir
        or args.check
        or args.fail_on_placeholders
        or args.optimize
        or args.render_gallery
        or args.make_gif
    ):
        args.check = True
        args.render_gallery = True

    if args.from_dir:
        from_dir = os.path.expanduser(args.from_dir)
        run([sys.executable, "scripts/install_real_screenshots.py", "--from", from_dir])

    if args.check or args.fail_on_placeholders:
        cmd = [sys.executable, "scripts/check_screenshots.py"]
        if args.fail_on_placeholders:
            cmd.append("--fail-on-placeholders")
        run(cmd)

    if args.optimize:
        # The optimizer is best-effort and uses macOS sips; keep it separate.
        run(["node", "scripts/optimize_screenshots.mjs", "--width", str(args.width)])

    if args.render_gallery:
        run([sys.executable, "scripts/render_screenshots_gallery.py"])

    if args.make_gif:
        run(
            [
                sys.executable,
                "scripts/make_screenshot_gif.py",
                "--width",
                str(args.gif_width),
                "--ms",
                str(args.gif_ms),
            ]
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
