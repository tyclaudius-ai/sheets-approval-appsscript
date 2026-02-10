# Real screenshot capture guide (Google Sheets Approvals + Audit Trail)

Goal: replace the placeholder images with **real** screenshots while keeping filenames stable so the landing page and docs don’t need edits.

## Quick rules (so the shots look clean)

- Use a **fresh demo copy** of the sheet (no client names/data).
- Use one browser (Chrome preferred) and keep the same:
  - zoom (recommend **100%** browser zoom)
  - Sheet zoom (recommend **100%**)
  - window size (recommend ~1280×720 or larger)
- Keep the UI **English** (if possible) so labels match docs.
- Hide any:
  - profile photo
  - email addresses (if they show in the top-right)
  - Drive folder names

## File locations + names (IMPORTANT)

Put the final screenshots here:

- `docs/screenshots/01-menu.png`
- `docs/screenshots/02-requests-pending.png`
- `docs/screenshots/03-approved-row.png`
- `docs/screenshots/04-audit-entry.png`
- `docs/screenshots/05-reapproval-required.png` (nice-to-have)
- `docs/screenshots/06-help-sidebar.png` (nice-to-have)

These paths are what the landing page references.

Right now those files exist as **copies of the placeholders** (generated PNGs). You’ll overwrite them with real screenshots.

## Suggested capture flow (5–10 min)

1) **Open the demo sheet**
   - Create a new Google Sheet.
   - Extensions → Apps Script → paste `Code.gs`.
   - Save.
   - Reload the Sheet.

2) **Seed demo data**
   - Run `Approvals → Create demo setup`.
   - Confirm you now have two tabs: `Requests` and `Audit`.

3) Capture each screenshot (use macOS screenshot tool)
   - Press **Cmd+Shift+4**, drag a clean rectangle around the relevant UI.
   - Avoid capturing the whole browser chrome unless it helps.

### 01 — Custom menu visible (`01-menu.png`)
- Show the top menu with the **Approvals** menu open.

### 02 — Requests sheet pending (`02-requests-pending.png`)
- On `Requests`, show a couple rows with `Status = PENDING`.

### 03 — Approved row (`03-approved-row.png`)
- Select a pending row.
- Run `Approvals → Approve row`.
- Capture the row showing `Status = APPROVED` plus `Approver` and `DecisionAt`.

### 04 — Audit entry appended (`04-audit-entry.png`)
- Switch to `Audit`.
- Capture the last row showing the newly appended event.

### 05 — Re-approval required (`05-reapproval-required.png`)
- Edit a tracked cell on an approved row (e.g., amount/description).
- Show it reverting to `PENDING`.
- Bonus: also show the `Audit` event `REAPPROVAL_REQUIRED` (either in the same shot if visible, or prioritize the Requests revert).

### 06 — Help/Docs sidebar (`06-help-sidebar.png`)
- Run `Approvals → Help / Docs`.
- Capture the sidebar.

## After capture

1) Rename/move screenshots to exactly the filenames above.
2) Sanity check locally by opening:
   - `landing/index.html`
   - confirm the gallery now shows the real screenshots.

## If you want *zero* personal info visible

Use a separate Chrome profile (no signed-in avatar), or blur the top-right profile area before saving.
