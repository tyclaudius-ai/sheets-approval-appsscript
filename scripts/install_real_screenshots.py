#!/usr/bin/env python3
"""Install/rename *real* screenshots into docs/screenshots with stable filenames.

This repo ships placeholder screenshots so the landing page renders out of the box.
When you capture real screenshots (usually on macOS), you typically get files like:
  Screenshot 2026-02-10 at 1.23.45 PM.png

This helper copies/renames those captures into the exact filenames the docs expect:
  docs/screenshots/01-menu.png
  docs/screenshots/02-requests-pending.png
  ...

It supports three workflows:
- guided: wait for you to capture each screenshot (01..06) and auto-install sequentially
- interactive: choose which existing captures map to each target filename
- non-interactive: map newest N files to 01..06 automatically (risky)

Usage:
  python3 scripts/install_real_screenshots.py --from ~/Desktop

Options:
  --from DIR            Directory to scan for source images (default: ~/Desktop)
  --glob PATTERN        Glob pattern(s). Repeatable. (defaults: Screenshot*.png, Screen Shot*.png)
  --include-jpg         Also include *.jpg/*.jpeg matches (off by default)
  --guided              Step through the shotlist and wait for a *new* capture each step.
  --timeout-seconds     Per-shot timeout for --guided (default: 600)
  --poll-ms             Poll interval for --guided (default: 750)
  --open               When selecting a candidate, open it in Preview (macOS `open`).
  --since-minutes       Only consider candidate files modified in the last N minutes.
  --non-interactive     Take the newest N files in order and map to 01..06 (risky)
  --dry-run             Print actions without copying
  --check               After copying, run scripts/check_screenshots.py
  --optimize            After copying, run scripts/optimize_screenshots.mjs (reads manifest.json)

Tip:
  For best results, set Chrome zoom=100% and Google Sheets zoom=100%.
"""

from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


TARGETS = [
    ("01-menu.png", "01 — Custom menu visible (Approvals menu open)"),
    ("02-requests-pending.png", "02 — Requests sheet showing PENDING rows"),
    ("03-approved-row.png", "03 — Approved row (Status=APPROVED + approver/time)"),
    ("04-audit-entry.png", "04 — Audit tab showing appended event"),
    ("05-reapproval-required.png", "05 — Re-approval required after edit (optional but recommended)"),
    ("06-help-sidebar.png", "06 — Help/Docs sidebar open (optional but recommended)"),
]


@dataclass(frozen=True)
class Candidate:
    path: Path
    mtime: float
    size: int


def expand(p: str) -> Path:
    return Path(os.path.expanduser(p)).resolve()


def find_candidates(src_dir: Path, patterns: list[str]) -> list[Candidate]:
    hits: list[Candidate] = []
    for pat in patterns:
        for s in glob.glob(str(src_dir / pat)):
            p = Path(s)
            try:
                st = p.stat()
            except FileNotFoundError:
                continue
            if not p.is_file():
                continue
            hits.append(Candidate(path=p, mtime=st.st_mtime, size=st.st_size))

    # newest first
    hits.sort(key=lambda c: c.mtime, reverse=True)

    # de-dupe exact paths
    seen: set[Path] = set()
    out: list[Candidate] = []
    for c in hits:
        if c.path in seen:
            continue
        seen.add(c.path)
        out.append(c)
    return out


def fmt_bytes(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n/1024:.1f}{unit}"
        n /= 1024
    return f"{n}B"


def fmt_mtime(ts: float) -> str:
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)


def prompt(msg: str) -> str:
    try:
        return input(msg)
    except KeyboardInterrupt:
        print("\nAborted.")
        raise SystemExit(130)


def wait_for_new_capture(
    *,
    src_dir: Path,
    patterns: list[str],
    seen_paths: set[Path],
    since_ts: float,
    timeout_seconds: int,
    poll_ms: int,
) -> Path:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        candidates = find_candidates(src_dir, patterns)
        for c in candidates:
            # In guided mode we want *new* files, but allow brand new names even if timestamps jitter.
            if c.path in seen_paths:
                continue
            if c.mtime < since_ts:
                continue
            return c.path
        time.sleep(max(0.1, poll_ms / 1000.0))

    raise TimeoutError(
        f"Timed out after {timeout_seconds}s waiting for a new screenshot capture in {src_dir}"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", default="~/Desktop", help="Directory to scan for screenshots")
    ap.add_argument(
        "--glob",
        dest="globs",
        action="append",
        help="Glob pattern (relative to --from). Repeatable.",
    )
    ap.add_argument("--include-jpg", action="store_true", help="Also include Screenshot*.jpg/jpeg")

    ap.add_argument(
        "--guided",
        action="store_true",
        help="Guided mode: step through the shotlist and wait for a NEW capture each step.",
    )
    ap.add_argument(
        "--timeout-seconds",
        type=int,
        default=600,
        help="Per-shot timeout for --guided (default: 600).",
    )
    ap.add_argument(
        "--poll-ms",
        type=int,
        default=750,
        help="Poll interval for --guided (default: 750).",
    )

    ap.add_argument(
        "--since-minutes",
        type=int,
        help="Only consider candidate files modified in the last N minutes (helps avoid picking old screenshots).",
    )
    ap.add_argument(
        "--open",
        action="store_true",
        help="When selecting a candidate, open it in Preview (macOS `open`).",
    )
    ap.add_argument("--non-interactive", action="store_true", help="Map newest N files to targets without prompts")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true", help="Run scripts/check_screenshots.py after copying")
    ap.add_argument("--optimize", action="store_true", help="Run scripts/optimize_screenshots.mjs after copying")
    args = ap.parse_args()

    if args.guided and args.non_interactive:
        print("--guided and --non-interactive are mutually exclusive", file=sys.stderr)
        return 2

    src_dir = expand(args.src)
    if not src_dir.exists():
        print(f"Source dir does not exist: {src_dir}", file=sys.stderr)
        return 2

    base_globs = args.globs or ["Screenshot*.png", "Screen Shot*.png"]

    patterns: list[str] = []
    patterns.extend(base_globs)
    if args.include_jpg:
        for g in base_globs:
            if g.lower().endswith(".png"):
                patterns += [g[:-4] + ".jpg", g[:-4] + ".jpeg"]
            else:
                patterns += [g + ".jpg", g + ".jpeg"]

    candidates = find_candidates(src_dir, patterns)

    if args.since_minutes is not None:
        cutoff = datetime.now().timestamp() - (args.since_minutes * 60)
        candidates = [c for c in candidates if c.mtime >= cutoff]

    if not candidates and not args.guided:
        note = "" if args.since_minutes is None else f" (after since-minutes={args.since_minutes})"
        print(f"No candidates found in {src_dir} matching {patterns}{note}", file=sys.stderr)
        return 1

    dest_dir = Path(__file__).resolve().parent.parent / "docs" / "screenshots"
    dest_dir.mkdir(parents=True, exist_ok=True)

    if args.guided:
        print("Guided screenshot install")
        print(f"  Watching: {src_dir}")
        print(f"  Patterns: {patterns}")
        print(f"  Timeout:  {args.timeout_seconds}s per shot")
        print("")
        print("Tip: for each step, take a screenshot (Cmd+Shift+4) and wait for it to appear.")
        print("")

        # Establish baseline "seen" set so we only accept new captures.
        seen_paths = {c.path for c in find_candidates(src_dir, patterns)}
        since_ts = time.time() - 2.0

        planned: list[tuple[Path, Path, str]] = []
        for (target_fname, desc) in TARGETS:
            prompt(f"\nReady for {target_fname} — {desc}. Press Enter when you are about to capture… ")
            try:
                p = wait_for_new_capture(
                    src_dir=src_dir,
                    patterns=patterns,
                    seen_paths=seen_paths,
                    since_ts=since_ts,
                    timeout_seconds=args.timeout_seconds,
                    poll_ms=args.poll_ms,
                )
            except TimeoutError as e:
                print(str(e), file=sys.stderr)
                return 1

            seen_paths.add(p)
            try:
                since_ts = max(since_ts, p.stat().st_mtime)
            except Exception:
                since_ts = time.time()

            planned.append((p, dest_dir / target_fname, desc))
            print(f"  Found: {p.name} -> {target_fname}")

        print("\nPlanned actions:")
        repo_root = Path(__file__).resolve().parent.parent
        for src_path, dest_path, desc in planned:
            print(f"  - COPY {src_path.name} -> {dest_path.relative_to(repo_root)} ({desc})")

        if args.dry_run:
            print("\nDry run; no files copied.")
            return 0

        ok = prompt("\nProceed? [y/N]: ").strip().lower()
        if ok != "y":
            print("Cancelled.")
            return 0

        for src_path, dest_path, _desc in planned:
            shutil.copy2(src_path, dest_path)

        print("\nDone. Copied all guided screenshots.")

    else:
        print("Found candidates (newest first):")
        if args.since_minutes is not None:
            print(f"  (filtered to last {args.since_minutes} minutes)")
        for i, c in enumerate(candidates[:20], start=1):
            print(f"  [{i:2d}] {c.path.name}  ({fmt_mtime(c.mtime)} · {fmt_bytes(c.size)})")
        if len(candidates) > 20:
            print(f"  ... and {len(candidates) - 20} more")
        print("")

        chosen: list[Path | None] = []

        if args.non_interactive:
            if len(candidates) < len(TARGETS):
                print(
                    f"Need at least {len(TARGETS)} files for non-interactive mode; found {len(candidates)}",
                    file=sys.stderr,
                )
                return 2
            chosen = [c.path for c in candidates[: len(TARGETS)]]
            # non-interactive uses oldest-to-newest ordering so 01..06 aligns with capture order
            chosen = list(reversed(chosen))
        else:
            print("For each target, type the candidate number to use (or Enter to skip).")
            print("Tip: capture shots in order 01..06 so the newest list is easy to map.")
            if args.open:
                print("Tip: --open will open each selection in Preview so you can sanity-check framing.")
            print("")

            for (fname, desc) in TARGETS:
                resp = prompt(
                    f"Select for {fname} — {desc} [1-{min(len(candidates), 99)} / Enter=skip]: "
                ).strip()
                if not resp:
                    chosen.append(None)
                    continue
                try:
                    idx = int(resp)
                except ValueError:
                    print("  Not a number; skipping.")
                    chosen.append(None)
                    continue
                if idx < 1 or idx > len(candidates):
                    print("  Out of range; skipping.")
                    chosen.append(None)
                    continue
                p = candidates[idx - 1].path
                if args.open:
                    try:
                        subprocess.run(["open", str(p)], check=False)
                    except Exception:
                        pass
                chosen.append(p)

        # execute
        print("\nPlanned actions:")
        actions: list[tuple[Path | None, Path, str]] = []
        for (target_fname, desc), src_path in zip(TARGETS, chosen):
            if src_path is None:
                actions.append((None, dest_dir / target_fname, desc))
            else:
                actions.append((Path(src_path), dest_dir / target_fname, desc))

        repo_root = Path(__file__).resolve().parent.parent

        for src_path, dest_path, desc in actions:
            if src_path is None:
                print(f"  - SKIP {dest_path.name} ({desc})")
            else:
                print(f"  - COPY {src_path.name} -> {dest_path.relative_to(repo_root)} ({desc})")

        if args.dry_run:
            print("\nDry run; no files copied.")
            return 0

        if not args.non_interactive:
            ok = prompt("\nProceed? [y/N]: ").strip().lower()
            if ok != "y":
                print("Cancelled.")
                return 0

        copied = 0
        for src_path, dest_path, _desc in actions:
            if src_path is None:
                continue
            shutil.copy2(src_path, dest_path)
            copied += 1

        print(f"\nDone. Copied {copied} file(s).")

    repo_root = Path(__file__).resolve().parent.parent

    if args.check:
        print("\n[screenshots] Running check_screenshots.py …")
        subprocess.run([sys.executable, str(repo_root / "scripts" / "check_screenshots.py")], check=False)

    if args.optimize:
        print("\n[screenshots] Running optimize_screenshots.mjs …")
        subprocess.run(["node", str(repo_root / "scripts" / "optimize_screenshots.mjs")], cwd=str(repo_root), check=False)

    print("\nSanity check: open landing/index.html and confirm the screenshot gallery looks right.")
    print("Preview helper: python3 scripts/serve_landing.py --open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
