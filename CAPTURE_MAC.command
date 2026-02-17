#!/bin/bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

echo "[capture] Installing python requirements (best-effort)…"
python3 -m pip install -r scripts/requirements.txt >/dev/null || true

echo "[capture] Opening capture checklist…"
if command -v open >/dev/null 2>&1; then
  open "docs/screenshots/capture-checklist.html" || true
  open "docs/screenshots/deck.html" || true
  open "docs/screenshots/REAL_SCREENSHOTS_QUICKRUN.md" || true
  open "docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md" || true
fi

echo "[capture] Clipboard capture mode (fastest):"
echo "  Use Cmd+Ctrl+Shift+4 to capture to clipboard (not file)."
echo "  This will prompt you 6 times and write into docs/screenshots/*.png"
python3 scripts/capture_clipboard_shotlist.py --target-dir docs/screenshots

echo "[capture] Verifying + optimizing…"
python3 scripts/screenshots_pipeline.py \
  --check \
  --require-real-screenshots \
  --optimize \
  --width 1400 \
  --status \
  --render-gallery

echo "[capture] Done. Opening the gallery to sanity-check results…"
if command -v open >/dev/null 2>&1; then
  open "docs/screenshots/gallery.html" || true
fi

echo "[capture] If you want to re-run verification later:"
echo "  python3 scripts/check_screenshots.py --report-md docs/screenshots/REAL_SCREENSHOTS_STATUS.md"
