# Changelog

All notable changes to **Sheets Approvals + Audit Trail** will be documented here.

This project is intentionally simple (Apps Script + docs). Releases are “ship when useful” rather than strict semver.

## 2026-02-17
- Added real-screenshot capture workflow + helpers:
  - Guided shotlist capture tool (`scripts/capture_clipboard_shotlist.py`)
  - Install/check/optimize pipeline (`scripts/install_real_screenshots.py`, `scripts/check_screenshots.py`, `scripts/screenshots_pipeline.py`)
  - Shareable capture pack builder (`scripts/make_real_screenshot_capture_pack.py`)
- Marketplace pack improvements:
  - Auto-generates screenshot status reports (MD + HTML) during pack build
  - Generates stable `dist/*-latest.zip` pointers for easy uploads

## 2026-02-16
- Screenshot QA tooling:
  - Placeholder vs real-ish detection + strict gating modes
  - HTML report with thumbnails for fast review
  - Optional redaction helper (`scripts/redact_screenshots.py`) for account-area blur/pixelation
- Documentation polish for DEMO/QUICKSTART + marketplace checklist updates

## 2026-02-11
- Initial public-ready packaging and listing assets:
  - Bundle packager (`scripts/package_sheets_approval_appsscript.py`)
  - Marketplace packager (`scripts/make_marketplace_pack.py`)
  - Listing copy + outreach templates + intake questions
