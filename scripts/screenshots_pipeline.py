#!/usr/bin/env python3
"""Convenience pipeline for installing + validating + optimizing screenshot assets.

This repo supports two screenshot sets:
- Real screenshots: captured from Google Sheets (preferred for listings)
- "Real-ish" screenshots: generated offline (placeholders) for dev/demo

This script bundles the common commands into one repeatable pipeline.

Examples
--------
# Install real screenshots from Desktop, then validate, update STATUS.md, then build optimized JPGs
python3 scripts/screenshots_pipeline.py --from ~/Desktop --check --fail-on-placeholders --status --optimize --width 1400

# Guided mode (waits for each new capture) and avoids selecting old screenshots
python3 scripts/screenshots_pipeline.py --from ~/Desktop --guided --since-minutes 30 --open --check --require-real-screenshots --status --optimize --render-gallery

# Then generate the approval-flow.gif used in README/landing previews
python3 scripts/screenshots_pipeline.py --make-gif --gif-width 900 --gif-ms 900

# Package a listing-ready screenshot ZIP (PNG + optimized JPG + gif + manifest/status)
python3 scripts/screenshots_pipeline.py --pack

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


def pick_auto_from_dir() -> str:
    """Resolve 'AUTO' to a concrete directory (Desktop vs Downloads).

    The heavy lifting (globs, guided/watch modes, etc.) lives in install_real_screenshots.py.
    Here we just pick the most likely base folder.
    """

    for d in [Path.home() / "Desktop", Path.home() / "Downloads"]:
        if d.exists() and d.is_dir():
            return str(d)
    return str(Path.home())


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=str(REPO_ROOT), check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--from",
        dest="from_dir",
        help="Directory containing captured screenshots (e.g. ~/Desktop). Use 'AUTO' to choose Desktop/Downloads.",
    )
    ap.add_argument(
        "--guided",
        action="store_true",
        help="When used with --from, run the installer in guided mode (waits for each new capture).",
    )
    ap.add_argument(
        "--since-minutes",
        type=int,
        help="When used with --from, only consider screenshots modified in the last N minutes.",
    )
    ap.add_argument(
        "--open",
        action="store_true",
        help="When used with --from, open selected candidates in Preview during selection (macOS).",
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
        "--fail-on-realish",
        action="store_true",
        help="Fail if docs/screenshots/*.png are still known generated 'real-ish' mocks.",
    )
    ap.add_argument(
        "--require-real-screenshots",
        action="store_true",
        help="Convenience flag: equivalent to --fail-on-placeholders --fail-on-realish.",
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
        "--open-gallery",
        action="store_true",
        help="After --render-gallery, open docs/screenshots/gallery.html in your default browser (macOS).",
    )
    ap.add_argument(
        "--status",
        action="store_true",
        help="Regenerate docs/screenshots/STATUS.md (placeholder vs real-ish vs custom).",
    )
    ap.add_argument(
        "--make-gif",
        action="store_true",
        help="Generate docs/screenshots/approval-flow.gif from optimized JPGs.",
    )
    ap.add_argument(
        "--pack",
        action="store_true",
        help="Build a listing-ready screenshot ZIP under dist/ (wraps scripts/make_screenshot_pack.py).",
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

    # Convenience: 'real screenshots' means neither placeholders nor known generated "real-ish" mocks.
    if args.require_real_screenshots:
        args.fail_on_placeholders = True
        args.fail_on_realish = True

    # Default behavior: quick sanity check + refresh rendered gallery docs.
    if not (
        args.from_dir
        or args.check
        or args.fail_on_placeholders
        or args.fail_on_realish
        or args.require_real_screenshots
        or args.optimize
        or args.render_gallery
        or args.open_gallery
        or args.status
        or args.make_gif
        or args.pack
    ):
        args.check = True
        args.render_gallery = True
        args.status = True

    if args.from_dir:
        raw_from = args.from_dir.strip()
        if raw_from.upper() == "AUTO":
            from_dir = pick_auto_from_dir()
        else:
            from_dir = os.path.expanduser(raw_from)
        cmd = [sys.executable, "scripts/install_real_screenshots.py", "--from", from_dir]
        if args.guided:
            cmd.append("--guided")
        if args.since_minutes is not None:
            cmd += ["--since-minutes", str(args.since_minutes)]
        if args.open:
            cmd.append("--open")
        run(cmd)

    if args.check or args.fail_on_placeholders or args.fail_on_realish:
        cmd = [sys.executable, "scripts/check_screenshots.py"]
        if args.fail_on_placeholders:
            cmd.append("--fail-on-placeholders")
        if args.fail_on_realish:
            cmd.append("--fail-on-realish")
        run(cmd)

    if args.optimize:
        # The optimizer is best-effort and uses macOS sips; keep it separate.
        run(["node", "scripts/optimize_screenshots.mjs", "--width", str(args.width)])

    if args.status:
        run([sys.executable, "scripts/screenshot_status.py", "--write"])

    if args.render_gallery:
        run([sys.executable, "scripts/render_screenshots_gallery.py"])

        if args.open_gallery:
            gallery = REPO_ROOT / "docs" / "screenshots" / "gallery.html"
            if sys.platform == "darwin":
                run(["open", str(gallery)])
            else:
                print(f"(note) --open-gallery is currently macOS-only; open this file manually: {gallery}")

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

    if args.pack:
        run([sys.executable, "scripts/make_screenshot_pack.py"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
