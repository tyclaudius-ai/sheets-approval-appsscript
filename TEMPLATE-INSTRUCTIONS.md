# Template / “One-click copy” instructions (manual)

Goal: let someone create their own copy of the demo Sheet + Apps Script with minimal friction.

> Note: Google doesn’t let you ship a true “one-click install” for Apps Script without the user authorizing it. The best you can do is **a Google Sheet template link** + a couple explicit steps to authorize.

## Option A (recommended): Google Sheet template link

1. Create a Google Sheet that contains the tabs/headers your script expects.
   - Easiest: run **Approvals → Create demo setup** in a fresh Sheet, then tweak copy.
2. In that same Sheet, open **Extensions → Apps Script**.
3. Paste in `Code.gs` from this repo.
4. (Optional) Add any config edits you want in `CFG`.
5. In Apps Script, run any function once (e.g. `onOpen`) so it prompts authorization.
   - You can also leave this step for the user; they’ll be prompted on first use.
6. Back in Google Sheets, click **File → Make a copy**.
7. Share the *template* as a “Make a copy” link:
   - Click **Share** → set access to **Anyone with the link: Viewer**.
   - Copy the link and convert it to a template-style URL by ensuring it includes `/copy`.
     - Typical pattern:
       - Original: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit#gid=0`
       - Template copy: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/copy`

   Tip: if you have any Sheet URL (or just the Sheet ID), you can generate the `/copy` URL with:

   ```bash
   python3 scripts/make_sheet_copy_link.py "<sheet-url-or-id>"
   ```

### What the user does

1. Open the `/copy` link → clicks **Make a copy**.
2. In their copy, reload the Sheet.
3. Use **Approvals → Create demo setup** (if not already present) and then **Approve row**.
4. First run will prompt Google authorization.

## Option B: “Copy/paste installer” (works even without template)

If you can’t (or don’t want to) host a template sheet:

1. User creates a new Google Sheet.
2. User opens **Extensions → Apps Script**.
3. User pastes `Code.gs`.
4. User returns to the Sheet and runs **Approvals → Create demo setup**.

## Suggested deliverables (if selling/handing off)

- A `/copy` template link
- A 60–90s Loom walking through:
  - Make a copy → authorize → Approve row → show Audit log
- 3 screenshots (see `SCREENSHOTS.md`)
