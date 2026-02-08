#!/usr/bin/env python3
"""Generate a Google Sheets "make a copy" link from a sheet URL or ID.

Why: when selling/sharing this Apps Script microproduct, you often want a clean
`/copy` URL that prompts the viewer to make their own copy.

Usage:
  python3 scripts/make_sheet_copy_link.py <sheet-url-or-id>

Examples:
  python3 scripts/make_sheet_copy_link.py https://docs.google.com/spreadsheets/d/1AbC.../edit#gid=0
  python3 scripts/make_sheet_copy_link.py 1AbCDEFgHIjKlmNoPqrSTuvWXyZ0123456789

Output:
  https://docs.google.com/spreadsheets/d/<SHEET_ID>/copy
"""

from __future__ import annotations

import re
import sys


SHEET_ID_RE = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)")
BARE_ID_RE = re.compile(r"^[a-zA-Z0-9-_]{20,}$")


def extract_sheet_id(s: str) -> str | None:
    s = s.strip()
    m = SHEET_ID_RE.search(s)
    if m:
        return m.group(1)
    if BARE_ID_RE.match(s):
        return s
    return None


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] in {"-h", "--help"}:
        print(__doc__.strip())
        return 2

    sheet_id = extract_sheet_id(argv[1])
    if not sheet_id:
        print("ERROR: could not extract a Google Sheet ID from input.", file=sys.stderr)
        return 1

    print(f"https://docs.google.com/spreadsheets/d/{sheet_id}/copy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
