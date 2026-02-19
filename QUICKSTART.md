# Quickstart — Sheets Approvals + Audit Trail

If you want to see this working fast (no Marketplace add-on), follow this.

## 1) Create a new Google Sheet
- Google Drive → **New → Google Sheets**
- Name it: `Approvals Demo`

## 2) Install the script (copy/paste)
1. In the Sheet: **Extensions → Apps Script**
2. Delete any default code
3. Paste in `Code.gs` from this repo
4. Click **Save**
5. Go back to the Sheet and **reload**

You should now see a menu called **Approvals**.

> First time you run a menu action, Google will ask for authorization.

## 3) One-click demo data
In the Sheet: **Approvals → Create demo setup**

This creates:
- `Requests` tab (example request rows)
- `Audit` tab (append-only-ish events + sha256 snapshot hash)

## 4) Try the approval flow
1. Click any request row (row 2+)
2. **Approvals → Approve row**
3. Check the `Audit` tab: you’ll see a new event

## 5) Try “re-approval required after change”
1. Approve a row
2. Edit a meaningful cell (e.g., `Title`)

Expected (default config):
- The row auto-reverts to `PENDING`
- The `Audit` tab logs a `REAPPROVAL_REQUIRED` event

If it doesn’t revert automatically:
- Some Google Workspace domains restrict simple triggers.
- Run **Approvals → Install re-approval trigger (optional)** and edit again.

## Next: real screenshots / landing page
- Suggested screenshots checklist: `SCREENSHOTS.md`
- Screenshot set + capture checklist + gallery: `docs/screenshots/README.md`
- Replace placeholder screenshots with real PNGs: `REAL_SCREENSHOTS_GUIDE.md` (fastest path: `docs/screenshots/REAL_SCREENSHOTS_QUICKRUN.md`)
- Local preview of the landing page: `python3 scripts/serve_landing.py --open`

If you want a talk-track style walkthrough, see `DEMO.md` (or start at `START_HERE.md`).
