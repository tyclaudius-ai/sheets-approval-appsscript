# Real screenshots TODO (capture run)

Goal: replace any **placeholder** or **real-ish generated** screenshots in `docs/screenshots/*.png` with *true* Google Sheets captures.

## 0) Check current status

```bash
cd sheets-approval-appsscript
python3 scripts/check_screenshots.py --report-md docs/screenshots/REAL_SCREENSHOTS_STATUS.md
```

Open the report:

- `docs/screenshots/REAL_SCREENSHOTS_STATUS.md`

## 1) Capture the 6 required shots (checkboxes)

Shot framing + exact UI states are in:
- `docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md`
- `docs/screenshots/CAPTURE-CHEATSHEET.md`

Capture these files (exact names):

- [ ] `docs/screenshots/01-menu.png`
- [ ] `docs/screenshots/02-requests-pending.png`
- [ ] `docs/screenshots/03-approved-row.png`
- [ ] `docs/screenshots/04-audit-entry.png`
- [ ] `docs/screenshots/05-reapproval-required.png`
- [ ] `docs/screenshots/06-help-sidebar.png`

## 2) Install + verify

Put the screenshots somewhere easy (Desktop/Downloads), then:

```bash
python3 scripts/install_real_screenshots.py --from ~/Desktop --check --optimize
python3 scripts/check_screenshots.py --require-real-screenshots
```

## 3) Rebuild the gallery (optional but recommended)

```bash
python3 scripts/screenshots_pipeline.py --optimize --width 1400
```
