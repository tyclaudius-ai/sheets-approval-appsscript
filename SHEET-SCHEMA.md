# Sheet schema — Sheets Approval + Audit Trail

This script is deliberately “spreadsheet-first”: the sheet is the database.

## Tabs

### `Requests` (required)

Row 1 must contain headers. The script expects (recommended exact names):

- `RequestId` — string; generated if empty (`REQ-<uuid>`)
- `Title` — free text
- `Requester` — email/name
- `Status` — `PENDING | APPROVED | REJECTED`
- `Approver` — email (best-effort; may be `unknown`)
- `DecisionAt` — timestamp
- `DecisionNotes` — free text

You can add extra columns. They’ll be included in the audit snapshot JSON.

### `Audit` (required)

The script will create this tab if it doesn’t exist.

Headers:

- `EventAt`
- `Actor`
- `Action` — one of:
  - `APPROVED` / `REJECTED` / `PENDING`
  - `REAPPROVAL_REQUIRED`
  - `DEMO_SETUP`
- `RequestId`
- `RowNumber` — row index in `Requests`
- `SnapshotJSON` — JSON string of the row (plus extra metadata for some actions)
- `SnapshotHash` — sha256 hex of SnapshotJSON (tamper-evidence)

## Config knobs (in `Code.gs`)

All config lives in the `CFG` object at the top of `Code.gs`.

Key ones:

- `REAPPROVAL_ON_CHANGE` (default: true)
- `REAPPROVAL_EXEMPT_HEADERS` (default: decision/meta columns)
- `REAPPROVAL_TRACKED_HEADERS` (default: empty → any non-exempt change triggers)
- `LOCK_ROW_ON_APPROVE` (default: true)
- `LOCK_WARNING_ONLY` (default: true)

## Demo data

The menu item **Approvals → Create demo setup** generates correct headers and seeds a couple example rows.
