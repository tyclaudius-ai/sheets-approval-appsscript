# Jaxon: capture REAL screenshots (10 minutes)

Goal: replace the current **“real-ish” generated** PNGs in `docs/screenshots/` with **real Google Sheets screenshots** (same filenames).

When you’re done, `docs/screenshots/REAL_SCREENSHOTS_STATUS.md` should **NOT** list “Real-ish generated screenshots detected”.

## 1) Generate the capture pack (optional but recommended)
From repo root:

```bash
cd sheets-approval-appsscript
python3 scripts/make_real_screenshot_capture_pack.py --out ~/Desktop/real-screenshots-capture-pack.zip
open ~/Desktop/real-screenshots-capture-pack.zip
```

(You can also just follow the guides directly without the zip.)

## 2) In Google Sheets, open the demo template
- Use the repo’s demo/template sheet (the one used for screenshots).
- Run the custom menu item to create/populate demo rows if needed.

Tip: maximize the browser window; keep zoom consistent across shots.

## 3) Capture these 6 shots (exact filenames)
Save each capture to **Desktop** with these exact names:

- `01-menu.png`
- `02-requests-pending.png`
- `03-approved-row.png`
- `04-audit-entry.png`
- `05-reapproval-required.png`
- `06-help-sidebar.png`

Framing reference:
- Shotlist: `docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md`
- Cheatsheet: `docs/screenshots/CAPTURE-CHEATSHEET.md`

## 4) Install + validate + optimize
From repo root:

```bash
cd sheets-approval-appsscript
python3 scripts/screenshots_pipeline.py \
  --from ~/Desktop \
  --check \
  --min-bytes 50000 \
  --fail-on-placeholders \
  --fail-on-realish \
  --status \
  --render-gallery \
  --optimize
```

If this passes, the repo is now listing-ready.

## 5) Build the marketplace pack (sanity)

```bash
python3 scripts/make_marketplace_pack.py --require-real-screenshots
```

If it fails, open `docs/screenshots/REAL_SCREENSHOTS_STATUS.md` and it will tell you exactly what’s wrong.
