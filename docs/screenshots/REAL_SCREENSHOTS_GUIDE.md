# Real screenshots guide (Marketplace-ready)

This repo ships with **placeholders / “real‑ish” mocks** so docs look good without needing a Google login.

If you’re preparing a Marketplace listing, you eventually want **REAL** screenshots captured from an actual Google Sheet.

## Fast path (recommended)

Follow:
- **Quick run:** `docs/screenshots/REAL_SCREENSHOTS_QUICKRUN.md`

That flow supports a guided “capture one → auto‑install → next” process:

```bash
python3 scripts/install_real_screenshots.py --from ~/Desktop --guided
```

Then validate + optimize + refresh the gallery:

```bash
python3 scripts/screenshots_pipeline.py \
  --from ~/Desktop \
  --check \
  --require-real-screenshots \
  --optimize \
  --width 1400 \
  --status \
  --render-gallery
```

## Canonical framing + shotlist

For consistent, product‑ready framing, use:
- `docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md`

## Common pitfalls

- **Accidentally capturing browser chrome** (tabs/address bar): crop tighter.
- **Inconsistent zoom:** keep Chrome zoom **100%** and Sheets zoom **100%**.
- **“Real‑ish” mocks still installed:** run the pipeline with `--require-real-screenshots` to fail fast.
- **Tiny/blank captures** (rare macOS bug): add e.g. `--min-bytes 80000` to the installer.

## Status / diagnostics

Generate a status report anytime:

```bash
python3 scripts/check_screenshots.py --report-md docs/screenshots/REAL_SCREENSHOTS_STATUS.md
```
