#!/bin/zsh
set -euo pipefail

# One-command helper to install + validate REAL screenshots and rebuild the gallery.
# Intended to be double-clicked on macOS.

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

PYTHON=${PYTHON:-python3}

"$PYTHON" scripts/real_screenshots_quickrun.py \
  --from AUTO \
  --require-pixels 1688x1008 \
  --fail-on-dim-mismatch
