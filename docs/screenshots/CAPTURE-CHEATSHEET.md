# Screenshot capture cheatsheet (5–10 min)

Goal: replace placeholder images with **real Google Sheets screenshots** while keeping filenames stable.

## Target files (overwrite these)

- `docs/screenshots/01-menu.png`
- `docs/screenshots/02-requests-pending.png`
- `docs/screenshots/03-approved-row.png`
- `docs/screenshots/04-audit-entry.png`
- `docs/screenshots/05-reapproval-required.png`
- `docs/screenshots/06-help-sidebar.png`

## Setup (fresh demo sheet)

1) Create a new Google Sheet.
2) Extensions → Apps Script → paste `Code.gs` → Save.
3) Reload the Sheet.
4) Run: `Approvals → Create demo setup` (creates `Requests` + `Audit`).

## Capture checklist

Use macOS screenshot tool (Cmd+Shift+4) and capture tight rectangles (avoid browser chrome).

1) **01-menu**: `Approvals` menu open in the top menu bar.
2) **02-requests-pending**: `Requests` tab with a few `PENDING` rows.
3) **03-approved-row**: approve one row; show `APPROVED` + approver + timestamp columns.
4) **04-audit-entry**: `Audit` tab showing the newest appended event.
5) **05-reapproval-required**: edit a tracked cell on an approved row; show it reverting to `PENDING` / `REAPPROVAL_REQUIRED`.
6) **06-help-sidebar**: open `Approvals → Help / Docs`; capture the sidebar.

## Install screenshots

If your screenshots are on Desktop (default macOS naming), run:

```bash
python3 scripts/install_real_screenshots.py --from ~/Desktop
```

## Verify they’re not placeholders

```bash
python3 scripts/check_screenshots.py --fail-on-placeholders
```

For full details: `REAL_SCREENSHOTS_GUIDE.md`
