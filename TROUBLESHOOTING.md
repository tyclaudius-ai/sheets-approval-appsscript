# Troubleshooting (Sheets Approval + Audit Trail)

Quick fixes for the most common “why isn’t it working?” cases.

## 1) I don’t see the **Approvals** menu

- **Reload the spreadsheet tab** (Cmd/Ctrl+R). The menu is added in `onOpen()`.
- Confirm you pasted the code into the **bound** Apps Script project for this spreadsheet:
  - Spreadsheet → **Extensions → Apps Script**
  - File should be `Code.gs` (name doesn’t matter, contents do)
- Make sure there isn’t a **syntax error**:
  - In Apps Script editor: click **Run** (any function) → errors will show.

## 2) It says I need authorization / permissions

That’s expected on first run.

- In the Apps Script editor, run `onOpen` or `createDemoSetup` once.
- Follow the Google authorization flow.
- Return to the sheet and reload.

If you’re on a locked-down Google Workspace domain:
- Your admin may block scripts, triggers, or `Session.getActiveUser()`.
- The script still works, but emails/user identities may show as blank or “unknown”.

## 3) Approve/Reject does nothing (or logs errors)

Checklist:

- You must have a tab named **`Requests`** (case-sensitive by default).
- You must have headers in **row 1** (and data starting row 2).
- The action operates on the **currently selected row**.
  - Click any cell in the row you intend to approve/reject.

## 4) My sheet has different column names

This MVP expects recommended headers. If you changed names:

- Either rename your headers to match the recommended ones (fastest), or
- Update the config block in `Code.gs` (look for `CFG` / header names).

Reference: `SHEET-SCHEMA.md`.

## 5) Re-approval on edit isn’t triggering

There are two trigger modes:

- **Simple trigger**: `onEdit(e)` (default). Works for typical manual edits.
- **Installable trigger**: needed on some domains or for reliability.
  - Use **Approvals → Install re-approval trigger (optional)**.

Notes:

- `onEdit` only fires for **user edits**. It may not fire for:
  - imports,
  - formula recalculation,
  - other scripts writing values.

If you need drift detection for non-`onEdit` changes:

- Add an `ApprovedHash` column.
- Use **Approvals → Scan approved rows for changes**.

## 6) Row protection fails on approval

Some domains restrict editing protections to owners/admins.

- By default, protection is **warning-only** to avoid hard failures.
- If you switched to enforced locks (`CFG.LOCK_WARNING_ONLY = false`) and it breaks, set it back to `true`.

## 7) Where are the logs?

- Apps Script editor → **Executions** (left sidebar)
- Or **View → Logs** (during a manual Run)

## 8) I want a clean demo quickly

Use:

- **Approvals → Create demo setup**

Then follow `DEMO-TEMPLATE.md` for a 2-minute walkthrough.
