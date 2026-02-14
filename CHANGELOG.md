# Changelog

## v0.2.0 — 2026-02-13

- **Marketplace-ready packaging:** added a “marketplace pack” builder (`scripts/make_marketplace_pack.py`) plus static validation (`scripts/validate_marketplace_pack.py`).
- **Screenshots pipeline:** added an end-to-end pipeline to rebuild the screenshots gallery + optional optimized JPGs/GIF (`scripts/screenshots_pipeline.py`).
- **Real screenshots workflow:** added helper tooling + docs to capture and install real screenshots quickly (`REAL_SCREENSHOTS_GUIDE.md`, `scripts/make_real_screenshot_capture_pack.py`, `scripts/install_real_screenshots.py`).
- **Screenshot integrity checks:** added placeholder/real-ish detection to prevent shipping fake screenshots by accident (`scripts/check_screenshots.py`).
- **Docs + sales assets:** added/expanded listing copy, demo talk-tracks, checklists, and outreach templates.
- **Usability:** bulk approval actions for multi-row selections; various QA and UX polish.

## v0.1.3 — 2026-02-09

- Docs: added a concrete example for `REAPPROVAL_TRACKED_HEADERS` + `REAPPROVAL_FROM_STATUSES`.

## v0.1.2 — 2026-02-09

- **Reset behavior:** “Reset to pending” now clears `Approver`, `DecisionAt`, and `DecisionNotes` instead of attributing a user/time.

## v0.1.1 — 2026-02-09

- **Re-approval reliability:** added an optional **installable** onEdit trigger (Approvals menu → *Install re-approval trigger*) for domains/environments where simple triggers are unreliable.

## v0.1.0 — 2026-02-08

Initial public release.
