# Jaxon: capture REAL screenshots (10 minutes)

Goal: replace the current **“real-ish” generated** PNGs in `docs/screenshots/` with **real Google Sheets screenshots** (same filenames).

When you’re done, `docs/screenshots/REAL_SCREENSHOTS_STATUS.md` should **NOT** list “Real-ish generated screenshots detected”.

## 1) Use the capture pack (recommended)
Fast path:

- Use the latest zip already built in `dist/`:

```bash
cd sheets-approval-appsscript
open dist/real-screenshots-capture-pack-DRAFT-latest.zip
```

Unzip it, then **double-click `CAPTURE_MAC.command`**.

It will:
- open the shotlist/checklist
- wait for 6 NEW screenshots (Desktop)
- install + validate + optimize them

(Alternative: you can regenerate the pack any time via `python3 scripts/make_real_screenshot_capture_pack.py`.)

## 2) In Google Sheets, open the demo template
- Use the repo’s demo/template sheet (the one used for screenshots).
- Run the custom menu item to create/populate demo rows if needed.

Tip: maximize the browser window; keep zoom consistent across shots.

Even easier capture method (no Desktop file juggling):
- Use **Cmd+Ctrl+Shift+4** (screenshot → clipboard)
- Then from the unzipped capture pack folder run:

```bash
python3 -m pip install -r scripts/requirements.txt
python3 scripts/capture_clipboard_shotlist.py --target-dir docs/screenshots --require-pixels 1688x1008
python3 scripts/screenshots_pipeline.py --check --require-real-screenshots --optimize --width 1400 --status --render-gallery
```

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
