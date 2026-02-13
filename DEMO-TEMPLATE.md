# Demo Template (copy/paste) — Sheets Approvals + Audit Trail

> Recommended starting point: **`DEMO.md`** (single consolidated demo doc).

Goal: a **clean 2–3 minute demo** showing (1) approve/reject workflow, (2) append-only audit trail, (3) “re-approval required after change”.

This repo is intentionally **copy/paste-first** (no Marketplace add-on).

## Prep (pick one)

### Option A — fastest live demo (blank Sheet)
1. Google Drive → **New → Google Sheets**
2. Name it: `Approvals Demo`

### Option B — offline-ish demo workbook
1. Download: `demo/Sheets-Approvals-Demo.xlsx`
2. Upload to Drive → open as a Google Sheet

If you want to regenerate the `.xlsx` locally:

```bash
python3 -m pip install -r scripts/requirements.txt
python3 scripts/make_demo_xlsx.py
```

## 1) Install the script (60–90s)
1. In the Sheet: **Extensions → Apps Script**
2. Delete any default code → paste `Code.gs` from this repo
3. **Save**
4. Go back to the Sheet tab and **reload**

You should now see a menu called **Approvals**.

> First run note: Google will prompt for authorization the first time you use a menu action.

## 2) Generate demo data (10s)
In the Sheet: **Approvals → Create demo setup**

This will:
- create `Requests` and `Audit` tabs
- add headers
- seed a few example rows

## 3) Demo the approval flow (45s)
1. Open the `Requests` tab
2. Click any seeded row (row 2+)
3. Run **Approvals → Approve row**

Callouts:
- `Status` becomes `APPROVED`
- `Approver` + `DecisionAt` populated

Then open the `Audit` tab and call out:
- appended event row (who/when/what)
- **row snapshot** (so the audit is explainable)
- **sha256 hash** (tamper-detection)

## 4) Demo “re-approval required after change” (45s)
1. Go back to `Requests`
2. Edit a meaningful cell on the approved row (e.g., `Title`)

Expected:
- row reverts to `PENDING`
- `Audit` gets a `REAPPROVAL_REQUIRED` event

### If it doesn’t revert to PENDING
Some Google Workspace domains restrict simple triggers.

Fallback:
- run **Approvals → Install re-approval trigger (optional)**
- then edit the approved row again

## 5) (Optional) Quick config explanation (15s)
In `Code.gs`, these knobs control what edits require re-approval:
- `CFG.REAPPROVAL_EXEMPT_HEADERS`
- `CFG.REAPPROVAL_TRACKED_HEADERS`

If `REAPPROVAL_TRACKED_HEADERS` is empty, **any non-exempt edit** triggers re-approval.

## Suggested screenshot set (for a listing / landing page)
1. Approvals menu visible
2. Requests sheet (pending)
3. Approved outcome (Status/Approver/DecisionAt)
4. Audit entry appended (hash visible)
5. Edit approved row → revert to PENDING + audit event

(See `SCREENSHOTS.md` + `REAL_SCREENSHOTS_GUIDE.md` for the exact filenames/workflow.)
