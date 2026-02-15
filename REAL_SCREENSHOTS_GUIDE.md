# REAL screenshots guide (5–10 minutes)

This repo ships with placeholder / “real‑ish” screenshots so the docs look good even without a Google login.

For a Marketplace listing you’ll eventually want **REAL** screenshots captured from an actual Google Sheet.

## Start here

- Quick run (fastest): `docs/screenshots/REAL_SCREENSHOTS_QUICKRUN.md`
- Exact framing + filenames: `docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md`
- Capture cheat sheet: `docs/screenshots/CAPTURE-CHEATSHEET.md`

## Recommended pipeline

After you capture screenshots (they usually land in `~/Desktop` on macOS):

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

Guided mode (waits for each new screenshot and installs them one-by-one):

```bash
python3 scripts/install_real_screenshots.py --from ~/Desktop --guided
```

## Why this file exists

Older docs + scripts referenced `REAL_SCREENSHOTS_GUIDE.md` at repo root.
The real instructions now live under `docs/screenshots/`.
This file stays as a stable entrypoint.
