# Sheets Approval + Audit Trail — one‑pager

A lightweight approval workflow that lives **inside Google Sheets** (Google Apps Script). Designed for teams that already run purchases, requests, checklists, and signoffs in Sheets—but need **accountability**.

## What it gives you
- **Approve / Reject / Reset** actions from a custom menu
- A `Requests` sheet where each request row carries:
  - `Status` (PENDING/APPROVED/REJECTED)
  - `Approver`, `DecisionAt`, `DecisionNotes`
- An append-only-ish `Audit` sheet that logs every decision/event with:
  - actor, timestamp, action, and a **row snapshot**
  - optional **hash chain** for tamper-evidence
- Optional guardrails:
  - **Re-approval required after change** (auto-reopens APPROVED rows on meaningful edits)
  - **Row protection** on approval (warning-only or enforced)

## Best fit use cases
- Purchase requests / reimbursements
- Vendor onboarding / approvals
- Change requests / engineering requests
- Access requests
- Any “we already use Sheets” workflow where decisions need a trail

## Deliverables (what a client actually receives)
- A working Google Sheet with the approval flow installed and tested
- Configuration set for your schema (tracked columns, exempt columns, statuses)
- A short handoff (doc or Loom) + troubleshooting notes

## Setup options (fixed price)
See `SALES.md` for the three packages:
1) Install + Configure
2) Install + Customize
3) Install + Automate

## Demo (2–5 minutes)
Use **Approvals → Create demo setup** then:
1) show the Approvals menu
2) approve a pending row
3) show the new Audit entry
4) edit a tracked cell to trigger re-approval

## Screenshot set (for a listing)
If you’re selling/marketing this as a template, capture real screenshots:
- Guide: `REAL_SCREENSHOTS_GUIDE.md`
- Gallery: `docs/screenshots/README.md`

## Notes / limits (honest)
- This is not a full workflow engine—it's a **pragmatic Sheets-native** approval layer.
- Security/roles are enforced via **Google Sheet permissions** (sharing + editor rights).
- The audit log is in a sheet: hashes make casual tampering detectable, not impossible.
