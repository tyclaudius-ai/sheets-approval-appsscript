# Start here — Sheets Approvals + Audit Trail

Pick the path you want:

## 1) I just want to SEE it work (2–5 min demo)

- **Live demo talk-track:** `DEMO.md`
- **Offline-ish demo workbook:** `demo/README.md` (includes `demo/Sheets-Approvals-Demo.xlsx`)

Fastest flow:
1. Create a new Google Sheet
2. Extensions → Apps Script → paste `Code.gs`
3. Reload the sheet
4. Approvals → **Create demo setup**
5. Approvals → **Approve row** → then open `Audit`

## 2) I want to INSTALL this in a real sheet (copy/paste first)

- **90-second setup:** `QUICKSTART.md`
- **Full setup checklist:** `SETUP-CHECKLIST.md`
- **Troubleshooting (menus / permissions / triggers):** `TROUBLESHOOTING.md`
- **Sheet schema / column contract:** `SHEET-SCHEMA.md`

If you want a “one-click copy” experience:
- **Template link instructions:** `TEMPLATE-INSTRUCTIONS.md`

## 3) I want to DELIVER/SELL it (client handoff / marketplace bundle)

- **Client-ready handoff options:** `CLIENT-HANDOFF.md`
- **Listing copy (Gumroad/Ko-fi/Upwork Project Catalog):** `LISTING.md` + `MARKETPLACE-LISTING-COPY.md`
- **Sales notes + positioning:** `SALES.md` + `ONE_PAGER.md`

### Screenshots

- **Shot list:** `SCREENSHOTS.md`
- **Real screenshots (replace placeholders 1:1):** `REAL_SCREENSHOTS_GUIDE.md`
- **Rendered gallery (after screenshots are in place):** `docs/screenshots/README.md`

Sanity checks / pipeline:
```bash
# check whether repo screenshots are still placeholders
python3 scripts/check_screenshots.py

# regen gallery + (optional) optimize JPGs + (optional) make GIF
python3 scripts/screenshots_pipeline.py
```

### Bundle packaging (zip artifact)

Build a client-ready zip with checksums:
```bash
python3 scripts/package_sheets_approval_appsscript.py
# or
python3 scripts/package_sheets_approval_appsscript.py --out dist/sheets-approval.zip
```

Generate a marketplace “all-in-one” pack (bundle + listing docs + screenshots):
```bash
python3 scripts/make_marketplace_pack.py
```

## 4) I want the quick WHY / what it solves

- `README.md` (high-level overview)
- `DEMO.md` (shows the 3 key value props: approvals, audit trail, re-approval on edit)
