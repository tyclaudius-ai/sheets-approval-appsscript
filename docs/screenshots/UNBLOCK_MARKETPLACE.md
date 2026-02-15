# Unblock Marketplace listing (real screenshots)

If you’re doing the Marketplace listing, this repo is currently **blocked** until the 6 canonical screenshots are captured from a real Google Sheet.

## 1) Capture (5–10 min)

Follow:
- `REAL_SCREENSHOTS_QUICKRUN.md`

Output files (exact names):
- `01-menu.png`
- `02-requests-pending.png`
- `03-approved-row.png`
- `04-audit-entry.png`
- `05-reapproval-required.png`
- `06-help-sidebar.png`

## 2) Install + validate (single command)

Assuming macOS screenshots land on your Desktop:

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

## 3) Confirm it’s unblocked

This should pass:

```bash
python3 scripts/check_screenshots.py --fail-on-placeholders --fail-on-realish
```

If it fails, open `docs/screenshots/STATUS.md` and fix whatever is flagged.
