# Setup Checklist — Sheets Approval + Audit Trail

Use this when installing the script into a real Sheet.

## 1) Sheet structure
- [ ] Create a tab named **Requests**
- [ ] Add headers on row 1 (recommended names):
  - [ ] RequestId
  - [ ] Title
  - [ ] Requester
  - [ ] Status
  - [ ] Approver
  - [ ] DecisionAt
  - [ ] DecisionNotes
- [ ] Create a tab named **Audit** (or let the script create headers)

## 2) Install Apps Script
- [ ] Extensions → Apps Script
- [ ] Paste `Code.gs`
- [ ] Save
- [ ] Reload the spreadsheet

## 3) First run permissions
- [ ] Click **Approvals → Approve row** once on a test row
- [ ] Accept permissions prompt

## 4) Validate behavior
- [ ] Select a row in Requests and Approve
- [ ] Confirm row updates (Status/Approver/DecisionAt)
- [ ] Confirm a new Audit event row appears

## 5) Optional hardening
- [ ] If your org supports protections, decide:
  - [ ] Warning‑only (default) vs enforced protection (`CFG.LOCK_WARNING_ONLY = false`)
- [ ] Ensure Sheet sharing permissions match who can approve
- [ ] If emails are blank, confirm Workspace policy for `Session.getActiveUser().getEmail()`

## 6) Go live
- [ ] Delete test rows
- [ ] Communicate: “Select row → Approvals menu → Approve/Reject”
