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
- Recommended names (these are what the landing page should reference):
  - `docs/screenshots/01-menu.png`
  - `docs/screenshots/02-requests-pending.png`
  - `docs/screenshots/03-approved-row.png`
  - `docs/screenshots/04-audit-entry.png`

Tip: see `REAL_SCREENSHOTS_GUIDE.md` for the full 5–10 minute capture flow.

Also useful:
- Shot list: `docs/screenshots/REAL_SCREENSHOTS_SHOTLIST.md`
- Quick run: `docs/screenshots/REAL_SCREENSHOTS_QUICKRUN.md`

### Included placeholders + generated PNGs

This repo includes a minimal **SVG placeholder set** (so you can ship a “screenshot set” without real screenshots yet):

- `docs/screenshots/01-menu.svg`
- `docs/screenshots/02-requests-pending.svg`
- `docs/screenshots/03-approved-row.svg`
- `docs/screenshots/04-audit-entry.svg`
- `docs/screenshots/05-reapproval-required.svg`
- `docs/screenshots/06-help-sidebar.svg`

They’re linked from `landing/index.html`.

A matching **PNG set** is also available (generated from the SVG placeholders):

- `docs/screenshots/png/01-menu.png`
- `docs/screenshots/png/02-requests-pending.png`
- `docs/screenshots/png/03-approved-row.png`
- `docs/screenshots/png/04-audit-entry.png`
- `docs/screenshots/png/05-reapproval-required.png`
- `docs/screenshots/png/06-help-sidebar.png`

This repo also includes *top-level* PNGs at:

- `docs/screenshots/01-menu.png`
- `docs/screenshots/02-requests-pending.png`
- `docs/screenshots/03-approved-row.png`
- `docs/screenshots/04-audit-entry.png`
- `docs/screenshots/05-reapproval-required.png`
- `docs/screenshots/06-help-sidebar.png`

These are intended to be the “canonical” screenshot filenames that the landing page references.

- In early drafts they may be **placeholder-derived** (either direct placeholder copies or *real-ish* generated mocks).
- For a real listing, overwrite the top-level PNGs with **true Google Sheets captures** using the same filenames.

To verify you’re no longer using placeholders/mocks:

```bash
python3 scripts/check_screenshots.py --require-real-screenshots
```

If you want a one-click workflow for capture+install on macOS, use the bundled capture pack zip:

- `dist/real-screenshots-capture-pack-DRAFT-latest.zip`
