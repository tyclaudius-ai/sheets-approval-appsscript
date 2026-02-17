# Screenshot redaction (PII removal)

If you capture **real** Google Sheets screenshots, they can unintentionally include:

- your Google account avatar/name/email (top-right)
- the spreadsheet name
- other identifying UI elements

This repo includes a small helper to **blur** (or pixelate) configured regions.

## Quick usage

List presets:

```bash
python3 scripts/redact_screenshots.py --list-presets
```

Redact the common Google account area (writes to a separate folder):

```bash
python3 scripts/redact_screenshots.py \
  --preset sheets_account_topright \
  --in docs/screenshots \
  --out /tmp/sheets-approval-redacted
```

In-place (overwrites files):

```bash
python3 scripts/redact_screenshots.py \
  --preset sheets_account_topright \
  --in docs/screenshots \
  --inplace
```

## Notes

- Presets use **fractional coordinates** so they work across different resolutions.
- If you need custom redaction rectangles, edit `scripts/redact_screenshots.py` and add a preset.
- This is optional; the primary requirement is still: capture **real** screenshots.
