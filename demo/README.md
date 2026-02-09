# Demo files

This folder contains **offline demo assets** you can use to quickly show the workflow without needing a pre-made Google Sheet template link.

## What’s included

- `Requests.csv` — sample Requests tab data
- `Audit.csv` — sample Audit tab data
- `Sheets-Approvals-Demo.xlsx` — an Excel workbook with the two tabs pre-built (useful for importing into Google Sheets)

## Fastest way to get a working Google Sheet demo

1) Create a new Google Sheet.
2) **File → Import** → **Upload** → select `Sheets-Approvals-Demo.xlsx`.
   - Choose **Replace spreadsheet** (if it’s a fresh Sheet) or **Insert new sheet(s)**.
3) Go to **Extensions → Apps Script**.
4) Copy/paste `Code.gs` from the repo (and keep `appsscript.json`).
5) Back in the Sheet, reload the page.
6) Use **Approvals → Create demo setup** (optional; it will ensure the expected tabs/headers exist).
7) Try **Approvals → Approve row** on a sample request.

Notes:
- You’ll be prompted to authorize the script on first run.
- The canonical tab/column contract is documented in `SHEET-SCHEMA.md`.
