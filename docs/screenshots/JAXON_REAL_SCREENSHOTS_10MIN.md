# Jaxon: capture REAL screenshots (10 minutes)

Goal: replace the current **REALISH (generated)** PNGs in `docs/screenshots/` with **real Google Sheets screenshots** (same filenames).

Success criteria:
- `docs/screenshots/REAL_SCREENSHOTS_STATUS.md` shows **Status: ✅ OK**
- It does **not** list “Real-ish generated screenshots detected”.

## Option A (recommended): use the capture pack (fastest)

1) Unzip the latest capture pack:

```bash
cd sheets-approval-appsscript
open dist/real-screenshots-capture-pack-DRAFT-latest.zip
```

2) In the unzipped folder, double-click:
- `CAPTURE_MAC.command`

It will:
- open the shotlist + framing cheatsheet
- wait for **6 new screenshots** to appear on your **Desktop**
- install them into `docs/screenshots/`
- run validation + generate the status reports + optimize

If you prefer, you can regenerate the pack any time:

```bash
python3 scripts/make_real_screenshot_capture_pack.py
```

## Option B: clipboard capture (avoids Desktop renaming)

Use macOS screenshot-to-clipboard:
- Press **Cmd+Ctrl+Shift+4** (selection → clipboard)

Then run the guided shotlist capture:

```bash
cd sheets-approval-appsscript
python3 -m pip install -r scripts/requirements.txt
python3 scripts/capture_clipboard_shotlist.py \
  --target-dir docs/screenshots \
  --require-pixels 1688x1008
```

Finish with the pipeline:

```bash
python3 scripts/screenshots_pipeline.py \
  --check \
  --require-real-screenshots \
  --fail-on-placeholders \
  --fail-on-realish \
  --status \
  --render-gallery \
  --optimize
```

## Shotlist (must match EXACT filenames)

You need these 6 files (exact names):

- `01-menu.png`
- `02-requests-pending.png`
- `03-approved-row.png`
- `04-audit-entry.png`
- `05-reapproval-required.png`
- `06-help-sidebar.png`

Framing references:
- Shotlist: `docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md`
- Cheatsheet: `docs/screenshots/CAPTURE-CHEATSHEET.md`

Tip: maximize the browser window and keep zoom consistent across all 6 shots.

## Sanity: build the marketplace pack

Once status is ✅ OK:

```bash
cd sheets-approval-appsscript
python3 scripts/make_marketplace_pack.py --require-real-screenshots
```

If anything fails, open:
- `docs/screenshots/REAL_SCREENSHOTS_STATUS.md`
- `docs/screenshots/REAL_SCREENSHOTS_STATUS.html` (thumbnail view)
