# Demo Template (copy/paste) — Sheets Approvals + Audit Trail

This repo is intentionally **copy/paste-first** (no Marketplace add-on install).

If you want a clean demo in ~2 minutes, do this:

## 1) Create a fresh Google Sheet (two options)

### Option A — start from scratch
- Google Drive → **New → Google Sheets**
- Name it: `Approvals Demo`

### Option B — use the prebuilt demo workbook (.xlsx)
- Download: `demo/Sheets-Approvals-Demo.xlsx`
- Upload it to Google Drive → open as a Google Sheet

If you want to regenerate the .xlsx locally:
```bash
python3 -m pip install -r scripts/requirements.txt
python3 scripts/make_demo_xlsx.py
```

## 2) Install the script
1. In the Sheet: **Extensions → Apps Script**
2. Delete any default code, then paste in `Code.gs` from this repo
3. **Save**
4. Go back to the Sheet tab and **reload** the page

You should now see a menu called **Approvals**.

## 3) Generate the demo data (one click)
In the Sheet: **Approvals → Create demo setup**

This will:
- create `Requests` and `Audit` tabs
- add the correct headers
- seed a few example rows

## 4) Run the approval flow
1. Open the `Requests` tab
2. Click any seeded row (row 2+)
3. Run **Approvals → Approve row**
4. Check the `Audit` tab: you should see a new event with:
   - action name
   - actor (email if available)
   - row snapshot
   - sha256 hash

## 5) Demo “re-approval required after change”
1. Approve a row
2. Edit a tracked cell on that row (e.g., `Title`)
3. The row should automatically revert to `PENDING`
4. The `Audit` tab should include a `REAPPROVAL_REQUIRED` event

### Configuration note
The “which edits count” behavior is controlled by these constants in `Code.gs`:
- `CFG.REAPPROVAL_EXEMPT_HEADERS`
- `CFG.REAPPROVAL_TRACKED_HEADERS`

If `REAPPROVAL_TRACKED_HEADERS` is empty, any non-exempt edit triggers re-approval.

## Suggested screenshots (for a sales page)
1. The **Approvals** menu visible in the Sheet
2. A `Requests` row before/after approval (Status, Approver, DecisionAt)
3. The `Audit` sheet showing appended rows + hashes
4. Editing an approved row → automatic revert to PENDING + audit event
