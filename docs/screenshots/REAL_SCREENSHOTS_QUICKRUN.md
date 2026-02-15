# Real screenshots — quick run (10 minutes)

This repo ships with **placeholders / real‑ish mocks** so the docs look good without a Google login.

For a Marketplace listing you eventually want **REAL** screenshots captured from an actual Google Sheet.

## What you need

- Google account that can create a new Sheet
- Chrome (recommended)
- This repo checked out locally

## Capture setup (once)

1) Create a new Google Sheet.
2) Extensions → **Apps Script**.
3) Paste in this repo’s `Code.gs`.
4) Save.
5) Reload the Sheet.
6) Run **Approvals → Create demo setup**.

If Google prompts for authorization, complete it once.

## Global framing settings

- Chrome zoom: **100%** (View → Actual Size)
- Sheets zoom (bottom-right): **100%**
- Tight crops: no browser tabs / address bar / macOS menu bar
- Wide enough that right-side columns like `Status`, `Approver`, `DecisionAt` are visible

## Shotlist

Use the canonical shotlist (exact framing):
- `docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md`

Expected output filenames:
- `01-menu.png`
- `02-requests-pending.png`
- `03-approved-row.png`
- `04-audit-entry.png`
- `05-reapproval-required.png`
- `06-help-sidebar.png`

## Optional: guided capture + install (fastest, least error-prone)

If you want to avoid hunting through a pile of Desktop screenshots, you can run the installer in **guided** mode.
It will step through 01..06, wait for a **new** screenshot each time, and install them automatically.

```bash
python3 scripts/install_real_screenshots.py --from ~/Desktop --guided
# (By default, this opens the current canonical screenshots as a framing reference before each capture.)
# If your system produces tiny/blank captures sometimes, add e.g. --min-bytes 80000
```

If you want the same flow but **no per-shot prompts** (it just waits for each new screenshot in order):

```bash
python3 scripts/install_real_screenshots.py --from ~/Desktop --watch
```

Then run the pipeline below to validate + optimize + render the gallery.

## Optional: generate a Markdown status report

If you want a quick “what’s real vs placeholder” summary you can paste into an issue/PR:

```bash
python3 scripts/check_screenshots.py --report-md docs/screenshots/SCREENSHOTS_REPORT.md
```

## Install + verify (fast path)

After capturing (usually they land on your Desktop), run:

```bash
python3 scripts/screenshots_pipeline.py \
  --from ~/Desktop \
  --check \
  --require-real-screenshots \
  --optimize \
  --width 1400 \
  --status \
  --render-gallery \
  --open-gallery
```

This will:
- rename/copy screenshots into `docs/screenshots/*.png`
- verify they’re **not** placeholders or real-ish mocks
- generate `docs/screenshots/optimized/*.jpg`
- refresh `docs/screenshots/STATUS.md`
- re-render the HTML gallery

If you want an animated preview:

```bash
python3 scripts/screenshots_pipeline.py --make-gif --gif-width 900 --gif-ms 900
```
