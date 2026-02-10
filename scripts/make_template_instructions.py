#!/usr/bin/env python3
"""Generate a filled "Make a copy" (template) install guide for this repo.

Why: When you sell/share this microproduct, the *best* onboarding UX is often a
Google Sheet template link ("/copy") plus clear authorization steps.

This script takes a Google Sheet URL or ID and prints a Markdown guide you can
paste into an email/Upwork/Notion/README.

Usage:
  python3 scripts/make_template_instructions.py <sheet-url-or-id>

Example:
  python3 scripts/make_template_instructions.py https://docs.google.com/spreadsheets/d/1AbC.../edit#gid=0

Output:
  (Markdown printed to stdout)
"""

from __future__ import annotations

import re
import sys
from datetime import datetime


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

    copy_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/copy"
    edit_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"

    today = datetime.utcnow().strftime("%Y-%m-%d")

    md = f"""# Google Sheets Approvals + Audit Trail — Template Install (Make a Copy)

_Last updated: {today}_

## 1) Make your copy

Open this link and click **Make a copy**:

- **Template copy link:** {copy_url}

(If you need the normal edit link: {edit_url})

## 2) Authorize Apps Script (first run)

1. In your copied Sheet, reload the page.
2. Click **Approvals → Create demo setup** (or any Approvals menu action).
3. The first time you run it, Google will ask you to **authorize** the script.
   - Choose your Google account
   - Click **Advanced** → **Go to (unsafe)** (if prompted)
   - Click **Allow**

## 3) Quick demo (60 seconds)

1. Go to the `Requests` tab.
2. Click any seeded row (row 2+).
3. Run **Approvals → Approve row**.
4. Confirm the `Audit` tab appended a new audit event.

## 4) Demo “re-approval required after change”

1. After approving a row, edit a tracked cell on that row (e.g., `Title`).
2. The row should automatically flip back to `PENDING`.
3. The `Audit` tab should append a `REAPPROVAL_REQUIRED` event.

## Notes / troubleshooting

- If you don’t see the **Approvals** menu: reload the Sheet once.
- If the demo tabs don’t exist: run **Approvals → Create demo setup**.
- If you want to control what edits trigger re-approval:
  - `CFG.REAPPROVAL_EXEMPT_HEADERS`
  - `CFG.REAPPROVAL_TRACKED_HEADERS`

---

If you want a “copy/paste installer” approach instead, see `DEMO-TEMPLATE.md` in the repo.
"""

    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
