# Demo (2–5 minutes) — Sheets Approvals + Audit Trail

Use this when you want a **repeatable live demo** that shows:
1) approve/reject workflow
2) append-only-ish audit trail
3) “re-approval required after change”

This repo is intentionally **copy/paste-first** (not a Marketplace add-on).

## Prep (pick one)

### Option A — fastest live demo (blank Sheet)
1. Google Drive → **New → Google Sheets**
2. Name it: `Approvals Demo`

### Option B — offline-ish demo workbook
1. Download: `demo/Sheets-Approvals-Demo.xlsx`
2. Upload to Drive → open as a Google Sheet

To regenerate the `.xlsx` locally:

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

## 3) Demo flow (talk-track)

### A) Show the “workflow” at a glance (10–20s)
- `Requests` tab → point at `Status / Approver / DecisionAt / DecisionNotes`.
- One-liner: “The sheet stays the source of truth; this is intentionally lightweight.”

### B) Approve a request (45–90s)
1. Click a row with `Status = PENDING`.
2. Run **Approvals → Approve row**.
3. Enter a short note (e.g., “Approved for Q1 spend”).

Callouts:
- `Status` flips to **APPROVED**.
- `Approver` + `DecisionAt` are filled.
- The decision note is stored on the row.

### C) Show the audit trail (30–60s)
1. Switch to the `Audit` tab.
2. Point at:
   - event type (`APPROVE` / `REJECT` / `RESET` / `REAPPROVAL_REQUIRED`)
   - actor (user/email when available)
   - timestamp
   - row snapshot + sha256 hash

One-liner: “Every action becomes an append-only-ish event with a snapshot so it’s explainable later.”

### D) Demonstrate “re-approval required after change” (45–90s)
1. Go back to `Requests`.
2. Edit a meaningful cell in the **approved** row (e.g., Title / Amount).

Expected (default config):
- Status goes back to **PENDING**
- `Audit` appends `REAPPROVAL_REQUIRED`

If it doesn’t revert:
- Some Google Workspace domains restrict simple triggers.
- Run **Approvals → Install re-approval trigger (optional)** and edit again.

Optional alternative demo:
- If you have an `ApprovedHash` column: **Approvals → Scan approved rows for changes**

### E) (Optional) 10-second config knobs
In `Code.gs`:
- `CFG.REAPPROVAL_EXEMPT_HEADERS`
- `CFG.REAPPROVAL_TRACKED_HEADERS`

Rule of thumb: if `REAPPROVAL_TRACKED_HEADERS` is empty, **any non-exempt edit** triggers re-approval.

## Suggested screenshot set (for a listing / landing page)
Use `SCREENSHOTS.md` as canonical.

Recommended 6-shot set (matches `docs/screenshots/01..06-*.png`):
1. Approvals menu visible
2. Requests sheet (pending)
3. Approved outcome (Status/Approver/DecisionAt)
4. Audit entry appended (hash visible)
5. Edit approved row → revert to PENDING + `REAPPROVAL_REQUIRED`
6. Help / Docs sidebar open

If you’re not logged into Google on this machine, you can generate *real-ish* placeholders:

```bash
python3 scripts/generate_realish_screenshots.py --optimize
python3 scripts/screenshots_pipeline.py
```

When you have real PNGs, overwrite `docs/screenshots/01..06-*.png` 1:1 and re-run:

```bash
python3 scripts/screenshots_pipeline.py
python3 scripts/check_screenshots.py --require-real-screenshots
```

macOS fastest path (recommended):

```bash
./CAPTURE_MAC.command
```
