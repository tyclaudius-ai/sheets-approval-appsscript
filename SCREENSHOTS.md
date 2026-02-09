# Suggested screenshots (for a demo / listing)

You can capture these in ~5 minutes to make the repo / landing page feel “real” and to support a productized offer.

## Minimum set (4)

1) **Custom menu visible**
   - Sheet open, menu bar showing: `Approvals`

2) **Requests sheet (before decision)**
   - A couple rows in `Requests` with `Status=PENDING`

3) **Approve action outcome**
   - Same row after `Approvals → Approve row`
   - Show `Status=APPROVED`, `Approver`, `DecisionAt`

4) **Audit trail entry**
   - `Audit` tab showing the new event row appended

## Nice-to-have (3)

5) **Create demo setup**
   - Show the `Approvals → Create demo setup` menu item

6) **Re-approval required after change**
   - Show an edit to an approved row reverting to `PENDING`
   - In `Audit`, show `REAPPROVAL_REQUIRED`

7) **Help/Docs sidebar**
   - `Approvals → Help / Docs` sidebar open

## Where to put them

- Folder: `docs/screenshots/`
- Recommended names:
  - `01-menu.png`
  - `02-requests-pending.png`
  - `03-approved-row.png`
  - `04-audit-entry.png`

### Included placeholders

This repo includes a minimal **SVG placeholder set** (so you can ship a “screenshot set” without real screenshots yet):

- `docs/screenshots/01-menu.svg`
- `docs/screenshots/02-requests-pending.svg`
- `docs/screenshots/03-approved-row.svg`
- `docs/screenshots/04-audit-entry.svg`
- `docs/screenshots/05-reapproval-required.svg`
- `docs/screenshots/06-help-sidebar.svg`

They’re linked from `landing/index.html`.

For a real listing, replace the SVGs with real screenshots (PNG) using the same base names.
