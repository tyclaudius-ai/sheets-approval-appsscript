# Client handoff checklist (Sheets approvals microproduct)

Use this when you’re delivering this to a client or publishing it as a paid template.

## 0) Decide delivery mode

Choose ONE:

- **A. Template link** (recommended): client clicks a Google Sheets **/copy** link and then pastes Apps Script.
- **B. Zip bundle**: you send a zip containing `Code.gs` + docs + landing page.
- **C. “Done-for-you setup”**: you (or the client on a screenshare) installs the script + triggers.

## A) Template link delivery (best UX)

1. Create a demo sheet in your Google Drive.
2. In that sheet: Extensions → Apps Script → paste `Code.gs` (and `Docs.html` if desired) → Save.
3. Reload the sheet, then run:
   - **Approvals → Create demo setup** (creates `Requests` + `Audit` and seeds sample rows)
4. Share the sheet as a template:
   - Make sure the sheet itself is shareable (usually “Anyone with the link can view”).
   - Generate a **/copy** link using:
     ```bash
     python3 scripts/make_sheet_copy_link.py "<your-sheet-url>"
     ```
5. In your delivery message, include:
   - The /copy link
   - A 2-minute setup script (point them to `SETUP-CHECKLIST.md`)
   - A 2-minute demo script (point them to `DEMO-TEMPLATE.md`)

## B) Zip bundle delivery (email/DM attachment)

1. Generate zip:
   ```bash
   python3 scripts/package_sheets_approval_appsscript.py --out dist/sheets-approval.zip
   ```
2. Send the zip.
3. In your message, tell them:
   - Where to paste `Code.gs`
   - That **Approvals → Create demo setup** will create the tabs

## C) Done-for-you setup (higher price)

On a call/screenshare:

1. Create/open client’s sheet.
2. Paste `Code.gs`.
3. Run **Approvals → Create demo setup** (or map to their real columns).
4. If they need automatic re-approval and their domain restricts simple triggers:
   - Use **Approvals → Install re-approval trigger (optional)**.
5. Do one real approval and one “edit after approval” to confirm:
   - Status flips back to `PENDING`
   - `Audit` has `REAPPROVAL_REQUIRED`

## Final verification (always)

- [ ] Approvals menu appears after reload
- [ ] Approve/Reject writes back to `Requests`
- [ ] Audit log appends rows (and hash column populates)
- [ ] Re-approval-required behavior matches expectation
- [ ] Any domain-specific permission limitations are documented (email access, protections)

## Suggested deliverables to include

- `ONE_PAGER.md` (sales/overview)
- `SETUP-CHECKLIST.md` (implementation)
- `DEMO-TEMPLATE.md` (demo script)
- `SCREENSHOTS.md` (what screenshots to capture)
- `LISTING.md` (marketplace listing copy)
- `TEMPLATE-INSTRUCTIONS.md` (template /copy link)
