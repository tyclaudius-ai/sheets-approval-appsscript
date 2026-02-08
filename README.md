# Sheets Approval + Audit Trail (MVP) — Google Apps Script

This is a minimal, copy-pasteable **Google Apps Script** that turns a Google Sheet into a lightweight approval workflow with an append-only audit log.

## What it does

- Adds a custom menu: **Approvals → Approve row / Reject row / Reset to pending**
- Operates on the **currently selected row** in a `Requests` sheet
- Writes approval state back onto the request row (status, approver, timestamp, notes)
- Appends an immutable-ish event into an `Audit` sheet (who/when/what/row snapshot + sha256 hash)

## Sheet setup

Create a Google Sheet with these tabs:

### `Requests`
Put headers on row 1 (exact names recommended):

- `RequestId` (string; can be blank, script will auto-generate if empty)
- `Title`
- `Requester`
- `Status` (PENDING | APPROVED | REJECTED)
- `Approver`
- `DecisionAt` (timestamp)
- `DecisionNotes`

You can add extra columns; the script logs a row snapshot to the audit trail.

### `Audit`
The script will create headers if missing.

## Install

1. Open your sheet → **Extensions → Apps Script**
2. Create a new project (or use the bound one)
3. Copy `Code.gs` from this folder into the Apps Script editor
4. Save
5. Reload the spreadsheet

You should see **Approvals** in the menu bar.

### Quick demo

Use **Approvals → Create demo setup** to generate the `Requests` + `Audit` tabs (with correct headers) and seed a couple example requests.

For a clean, step-by-step “demo in 2 minutes” script, see: **`DEMO-TEMPLATE.md`**.

For a quick checklist of suggested screenshots (useful for a demo/listing), see: **`SCREENSHOTS.md`**.

For “one-click copy” template-link instructions, see: **`TEMPLATE-INSTRUCTIONS.md`**.

For ready-to-paste marketplace listing copy (Gumroad/Ko-fi/Upwork Project Catalog), see: **`LISTING.md`**.

For the exact tab/column schema (and what’s configurable), see: **`SHEET-SCHEMA.md`**.

## Packaging (deliverable artifact)

To hand this to a client as a single zip bundle, you can generate a distributable artifact:

```bash
python3 scripts/package_sheets_approval_appsscript.py
# or choose a name:
python3 scripts/package_sheets_approval_appsscript.py --out dist/sheets-approval.zip
```

The zip includes Code.gs + docs + landing page and a `manifest.json` with sha256 checksums.

## Notes / Security

- Uses the active user email when available. Some domains may restrict `Session.getActiveUser().getEmail()`.
- This MVP does not enforce role-based access; rely on Google Sheet sharing permissions.
- Audit log is append-only by convention (it’s still a sheet). The stored **sha256 hash** makes casual tampering detectable. For stronger immutability, write events to an external store.
- Optional (default ON): **re-approval required after change**.
  - Implemented via a simple `onEdit(e)` trigger.
  - If a user edits a previously-approved row (`Status=APPROVED`), the script can auto-set it back to `PENDING` and append an audit event `REAPPROVAL_REQUIRED`.
  - Configure **which edits count**:
    - Exempt columns (never trigger): `CFG.REAPPROVAL_EXEMPT_HEADERS`
    - Tracked columns (only these trigger, if set): `CFG.REAPPROVAL_TRACKED_HEADERS` (leave empty to treat any non-exempt column as meaningful)
- Optional (default ON): **row protection on approval**.
  - By default it’s **warning-only**, to avoid hard permission failures on some Google Workspace domains.
  - You can switch to enforced protection by setting `CFG.LOCK_WARNING_ONLY = false` (requires editor/owner rights to manage protections).

## Next steps (non-MVP)

- Per-request approver lists / multi-step approvals
- Row-level locking + optimistic concurrency checks
- Slack/Email notifications
- Admin dashboard + exportable audit report
