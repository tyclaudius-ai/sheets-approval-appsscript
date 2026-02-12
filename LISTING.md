# Sheets Approval + Audit Trail (Google Apps Script)

A lightweight approval workflow for Google Sheets with an **append-only audit log**.

Use it when you want non-technical teammates to request edits, reviewers to approve/reject, and everyone to have a clear “who changed what, when, and why” paper trail — **without** paying for heavyweight SaaS.

## What it does

- **Request / Approve / Reject** changes via a custom **Approvals** menu
- Writes an **append-only Audit** tab (timestamped events)
  - Optional: **hash chain** (`PrevChainHash` + `ChainHash`) for stronger tamper-evidence
- **Auto re-approval on edit**: if an **APPROVED** row is changed, it automatically flips back to **PENDING** and logs a `REAPPROVAL_REQUIRED` event
- Optional **tracked headers allowlist** so only meaningful columns trigger re-approval
- Optional **row lock warning** (warning-only by default)
- Includes a **Help / Docs sidebar** inside the sheet

## Perfect for

- Budget approvals / purchasing logs
- Launch checklists
- Content calendars
- Hiring pipelines
- Ops runbooks / change control

## What you get

- `Code.gs` Google Apps Script source
- `README.md` + setup checklist
- Demo template script + demo CSVs
- Packaging script that builds a **client-ready zip** bundle with checksums

## Setup (2–5 minutes)

1) Create a Google Sheet (or use your existing one)
2) Extensions → Apps Script → paste the code (or import the bundle)
3) Reload the sheet
4) Approvals → **Create demo setup** (optional) to generate example tabs and sample rows

Full walkthrough:
- `SETUP-CHECKLIST.md`
- `TEMPLATE-INSTRUCTIONS.md`

## Screenshots to include in a listing

See `SCREENSHOTS.md` for a suggested shot list.

## FAQ

**Does this require OAuth / a backend?**
No. It runs in your Google Workspace / Google account as Apps Script.

**Can I customize statuses, columns, and tracked fields?**
Yes — see `SHEET-SCHEMA.md` and the configuration section in `README.md`.

**Does it prevent edits completely?**
By default it doesn’t hard-block; it flips status back to PENDING and logs the audit event. You can make it stricter if desired.

## License

MIT — see `LICENSE`.
