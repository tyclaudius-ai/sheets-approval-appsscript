# Demo Walkthrough (2–5 minutes)

This is a simple, repeatable demo flow you can run live in a Google Sheet.

## 0) Setup (30–60s)

1. Open the demo spreadsheet.
2. If needed, run **Approvals → Create demo setup** (creates `Requests` + `Audit` and seeds a few rows).
3. Make sure you can see the **Approvals** menu in the top bar.

If you *don’t* see the menu: reload the sheet; if still missing, re-check that `Code.gs` is installed in **Extensions → Apps Script**.

## 1) Show the “workflow” in one glance (10–20s)

- Point to the `Requests` tab.
- Highlight the `Status / Approver / DecisionAt / DecisionNotes` columns.
- Mention: “This is intentionally lightweight—no external DB; the sheet stays the source of truth.”

## 2) Approve a request (45–90s)

1. Click a row with `Status = PENDING`.
2. Run **Approvals → Approve row**.
3. Enter a short note (e.g., “Approved for Q1 spend”).

Call out what happened:

- `Status` flips to **APPROVED**.
- `Approver` and `DecisionAt` are filled.
- The decision note is stored on the row (and also recorded in the audit trail).

## 3) Show the audit trail (30–60s)

1. Switch to the `Audit` tab.
2. Point at:
   - event type (`APPROVE` / `REJECT` / `RESET` / `REAPPROVAL_REQUIRED`)
   - actor (user/email when available)
   - timestamp
   - row snapshot + sha256 hash

One-liner: “Every action becomes an append-only-ish event with a row snapshot so it’s auditable later.”

## 4) Demonstrate “re-approval required after change” (45–90s)

1. Go back to `Requests`.
2. Edit a meaningful cell in the **approved** row (e.g., change Title or Amount).

Expected behavior (default config):

- The row re-opens (Status goes back to **PENDING**).
- An audit event is appended: `REAPPROVAL_REQUIRED`.

If your domain blocks triggers:

- Use **Approvals → Install re-approval trigger (optional)**.
- Or demonstrate drift detection with:
  - **Approvals → Scan approved rows for changes** (requires `ApprovedHash` column).

## 5) Optional: row protection (20–40s)

If enabled for your environment, mention:

- Approved rows can be protected (warning-only by default).
- This prevents “silent edits” after approval.

## 6) Close (10–20s)

- “Copy/paste install takes ~90 seconds.” (link: `QUICKSTART.md`)
- “You can deliver this as a template link or a zip bundle.” (link: `CLIENT-HANDOFF.md`)
- “Next upgrades: multi-step approvals, notifications, exportable audit reports.”

## Suggested screenshots for a listing

Use `SCREENSHOTS.md` as the canonical list.

If you’re not logged into Google on this machine, you can still generate *real-ish* placeholders:

```bash
python3 scripts/generate_realish_screenshots.py --optimize
python3 scripts/screenshots_pipeline.py
```

When you have real PNGs, overwrite `docs/screenshots/01..06-*.png` 1:1 and re-run:

```bash
python3 scripts/screenshots_pipeline.py --fail-on-placeholders
```
