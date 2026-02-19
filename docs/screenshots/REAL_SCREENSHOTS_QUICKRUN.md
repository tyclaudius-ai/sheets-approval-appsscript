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
- Target pixel dimensions (recommended): **1688x1008**
  - This repo’s current canonical placeholders are 1688×1008; matching dims makes it easier to compare framing and keeps Marketplace assets consistent.

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

## Optional: one-click macOS runner (fastest)

If you’re on macOS, you can double-click:

- `CAPTURE_MAC.command` (repo root)

It will:
- open the checklist + shotlist
- prompt you 6 times to capture each screenshot to your clipboard
- install + verify + optimize + re-render the gallery

If macOS warns about running a downloaded script, right-click → Open.

## Optional: one-click macOS *quickrun* (after you already captured files)

If you already captured the 6 PNGs to **Desktop/Downloads**, you can double-click:

- `QUICKRUN_MAC.command` (repo root)

It runs the strict install/validate pipeline (including a **1688×1008** pixel gate) and opens the status + gallery.

## Optional: guided capture + install (fastest, least error-prone)

If you want to avoid hunting through a pile of Desktop screenshots, you can run the installer in **guided** mode.
It will step through 01..06, wait for a **new** screenshot each time, and install them automatically.

```bash
python3 scripts/install_real_screenshots.py --from AUTO --guided
# AUTO picks whichever of ~/Desktop or ~/Downloads has the newest matching screenshot.
# (By default, this opens the current canonical screenshots as a framing reference before each capture.)
# If your system produces tiny/blank captures sometimes, add e.g. --min-bytes 80000
```

If you want the same flow but **no per-shot prompts** (it just waits for each new screenshot in order):

```bash
python3 scripts/install_real_screenshots.py --from AUTO --watch
```

Then run the pipeline below to validate + optimize + render the gallery.

## Optional: validate pixel dimensions (prevents accidental wrong zoom/crop)

```bash
python3 scripts/screenshots_pipeline.py --check --require-pixels 1688x1008 --fail-on-dim-mismatch
```

Or use the stricter “marketplace ready” gate (real screenshots + standard pixels) in one flag:

```bash
python3 scripts/check_screenshots.py --require-marketplace
```

## Optional: generate a status report (Markdown / HTML / JSON)

If you want a quick “what’s real vs placeholder” summary you can paste into an issue/PR:

```bash
python3 scripts/check_screenshots.py --report-md docs/screenshots/REAL_SCREENSHOTS_STATUS.md
```

If you want a visual report with thumbnails (easier to sanity-check framing):

```bash
python3 scripts/check_screenshots.py --report-html docs/screenshots/REAL_SCREENSHOTS_STATUS.html
```

If you want machine-readable output (nice for dashboards/automation):

```bash
python3 scripts/check_screenshots.py --report-json docs/screenshots/REAL_SCREENSHOTS_STATUS.json
```

(Those `REAL_SCREENSHOTS_STATUS.*` paths are the repo’s canonical “latest” status outputs.)

## Install + verify (fast path)

After capturing (usually they land on your Desktop), run **one command**:

```bash
python3 scripts/real_screenshots_quickrun.py
```

Optional pixel gate (recommended if you’ve ever had accidental zoom/crop drift):

```bash
python3 scripts/real_screenshots_quickrun.py --require-pixels 1688x1008 --fail-on-dim-mismatch
```

This will:
- write fresh `REAL_SCREENSHOTS_STATUS.{md,html,json}`
- rename/copy screenshots into `docs/screenshots/*.png`
- verify they’re **not** placeholders or real-ish mocks
- (optionally) enforce pixel dimensions
- generate `docs/screenshots/optimized/*.jpg`
- refresh `docs/screenshots/STATUS.md`
- re-render the HTML gallery
- open the status + gallery on macOS

If you prefer the underlying pipeline call directly, this is the equivalent:

```bash
python3 scripts/screenshots_pipeline.py \
  --from AUTO \
  --check \
  --require-real-screenshots \
  --optimize \
  --width 1400 \
  --status \
  --render-gallery \
  --open-gallery
```

## Optional: redact PII (blur account avatar/email)

If your captures include account-identifying info (usually top-right), you can redact after install:

```bash
python3 scripts/redact_screenshots.py --preset sheets_account_topright --in docs/screenshots --inplace
```

See: `docs/screenshots/REDACTION.md`

If you want an animated preview:

```bash
python3 scripts/screenshots_pipeline.py --make-gif --gif-width 900 --gif-ms 900
```
