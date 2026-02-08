# Microproduct One‑Pager — Sheets Approval + Audit Trail (Google Apps Script)

## The pitch
Turn any Google Sheet into a lightweight **approval workflow** in ~10 minutes.

Best for teams that already live in Sheets and just need:
- a clear **PENDING/APPROVED/REJECTED** state,
- a lightweight **audit trail**,
- and minimal process overhead.

## What you get
- Custom menu: **Approvals → Approve / Reject / Reset to pending**
- Works on the **selected row** in a `Requests` sheet
- Writes decision metadata back to the row:
  - Status, Approver, DecisionAt, DecisionNotes
- Appends an audit event into an `Audit` sheet:
  - action, actor, timestamp, row snapshot, and a **sha256 hash**
- Optional row protection on approval (warning‑only by default to avoid Workspace permission pain)

## Why this exists (pain)
If you’re using Sheets to track requests (purchase, access, content review, hiring, flight readiness checklists, etc.), approvals usually become:
- “Who approved this?” (lost in Slack threads)
- “When did it change?” (no timeline)
- “Who edited the row?” (hard to reconstruct)

This gives you **simple state + an audit log** without migrating to Jira/ServiceNow.

## Setup (buyer‑friendly)
1) Create / open the Google Sheet
2) Extensions → Apps Script
3) Paste `Code.gs`
4) Save + reload
5) Use menu: **Approvals**

## Deliverable formats
- Copy/paste script (current)
- Optional paid setup: I install it into your sheet(s), customize headers, and add basic guardrails

## Common customizations (paid add‑ons)
- Multi‑step approvals (e.g., Eng → Lead → Finance)
- Per‑row approver lists / validation
- Notifications (Slack/email)
- “Approve” link per request
- Exportable audit report (CSV/PDF)

## Pricing suggestion (for Jaxon)
- $49: Script + template sheet structure + docs
- $149: Installed + customized + 1 training call
- $499+: Multi‑step approvals + notifications + hardening
