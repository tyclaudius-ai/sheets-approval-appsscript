# Marketplace listing copy (Sheets Approval + Audit Trail)

Use this as **copy/paste** for Gumroad / Ko‑fi / Upwork Project Catalog / a landing page.

> Notes:
> - Keep language concrete (what buttons they click / what they get).
> - Replace placeholders like **[YOUR SUPPORT EMAIL]**.
> - If you publish on Google Workspace Marketplace (as an add-on), you’ll need additional OAuth + verification steps; this repo is primarily a **DIY Apps Script template** + setup service.

---

## Title (pick 1)

1) **Sheets Approval + Audit Trail**
2) **Google Sheets Approvals (Request/Approve/Reject) + Audit Log**
3) **Change Control for Google Sheets (Approvals + Append‑Only Audit)**

## One‑liner

A lightweight approval workflow for Google Sheets: request edits, approve/reject, and keep an append‑only audit log — without heavyweight SaaS.

## Short description (1–2 sentences)

Turn any Google Sheet into a simple change‑control system. Teammates request edits, reviewers approve/reject, and every decision is logged to an append‑only Audit tab.

## “Perfect for” bullets

- Budget / purchasing approvals
- Hiring pipeline changes
- Launch checklists + ops runbooks
- Content calendars + marketing approvals
- Inventory adjustments / change logs

## Key features (bullets)

- **Approvals menu** inside the sheet (Request / Approve / Reject)
- **Append‑only audit log** with timestamped events (who/what/when)
- Optional **tamper‑evident hash chain** (PrevChainHash → ChainHash)
- **Auto re‑approval required**: if an approved row is edited, it flips back to **PENDING** and logs an event
- Optional **tracked headers allowlist** (only meaningful columns trigger re‑approval)
- Optional **row lock warning** (warning-only by default)
- Built‑in **Help / Docs sidebar**

## What you get (deliverables)

- Apps Script source (`Code.gs`) + config
- Quickstart + setup checklist
- Demo template data + walkthrough
- Packaging scripts to build a client-ready zip

## Setup (high level)

1) Open your Google Sheet
2) Extensions → Apps Script → paste/import the script
3) Reload the sheet
4) Approvals → **Create demo setup** (optional) to see it working in 60 seconds

## Requirements / constraints (be explicit)

- Requires a Google account with permission to edit the target sheet
- Runs as Google Apps Script (no external server required)
- You may need to authorize the script the first time you run it

## Support

- Support: **[YOUR SUPPORT EMAIL]**
- Optional done-for-you setup service: available (DM with your sheet + tracked columns)

## FAQ snippets

**Does it block edits?**
By default it’s “warning + audit + re-approval”. You can make it stricter if you want.

**Can I customize columns and statuses?**
Yes — see `SHEET-SCHEMA.md` and the config section in `README.md`.

**Is this a Google Workspace Marketplace add-on?**
Not by default. This is a DIY Apps Script template (and can be offered as a setup service). Publishing as an official Marketplace add-on is possible but requires additional Google verification steps.
