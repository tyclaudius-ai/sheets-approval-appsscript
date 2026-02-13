# Real screenshot shotlist (exact framing)

Use this when you want the **real** screenshot set to look consistent and “product ready”.

**Goals**
- Tight crops (avoid browser chrome + macOS menu bar).
- Consistent zoom across all shots.
- No personal data (use the demo setup rows).

## Global capture settings

- Browser: Chrome recommended
- Zoom: **100%** (View → Actual Size)
- Sheets zoom (bottom right): **100%**
- Window width: wide enough that the right-side columns (`Status`, `Approver`, `DecisionAt`, …) are visible without horizontal scroll.
- Prefer light mode (default) unless your listing is dark-mode themed.

## Before you start (demo state)

1) Create a new Google Sheet.
2) Extensions → Apps Script → paste `Code.gs` from this repo.
3) Reload the Sheet.
4) Run **Approvals → Create demo setup**.
5) Click into the `Requests` tab.

Tip: If Google prompts for permissions, complete the authorization once; after that, captures are fast.

---

## 01 — `01-menu.png` (Approvals menu)

**Show:** Google Sheets top menu with **Approvals** expanded.

**Steps**
1) Make sure the Sheet is loaded and you can see the normal Sheets menu bar.
2) Click **Approvals**.

**Frame**
- Include: the top menu bar area + the open dropdown.
- Exclude: browser tabs/address bar.

---

## 02 — `02-requests-pending.png` (Requests: pending rows)

**Show:** `Requests` sheet with multiple rows in **PENDING**.

**Steps**
1) In `Requests`, ensure you see at least 2–3 `PENDING` rows.
2) Scroll so the header row and the first few data rows are visible.

**Frame**
- Include: headers + a few rows.
- Prefer: show `Title`, `Requester`, `Status` at minimum.

---

## 03 — `03-approved-row.png` (Approved row)

**Show:** one row updated to **APPROVED** with approver + timestamp populated.

**Steps**
1) Click on a `PENDING` row.
2) Approvals → **Approve row**.
3) (If prompted) add a short decision note.

**Frame**
- Include: the approved row + the columns `Status`, `Approver`, `DecisionAt`.
- Prefer: include row number at left so it’s obvious it’s “a row action”.

---

## 04 — `04-audit-entry.png` (Audit trail)

**Show:** `Audit` sheet with the newest appended event row.

**Steps**
1) Click the `Audit` tab.
2) Scroll to the bottom (or to the newest event).

**Frame**
- Include: header + newest event row.
- If the row is wide, capture the left portion showing: event type, who, when, request id (whatever columns exist in your version).

---

## 05 — `05-reapproval-required.png` (Edit triggers re-approval)

**Show:** editing a tracked cell on an approved row causes **REAPPROVAL_REQUIRED** (or reverts to `PENDING`, depending on config) and logs an audit event.

**Steps**
1) Return to `Requests`.
2) On an **APPROVED** row, edit a meaningful cell (e.g., `Title`).
3) Confirm the `Status` changes accordingly.

**Frame**
- Include: the edited row + the `Status` cell clearly showing the re-opened state.

---

## 06 — `06-help-sidebar.png` (Help / Docs sidebar)

**Show:** the in-sheet **Help / Docs** sidebar.

**Steps**
1) Approvals → **Help / Docs**.

**Frame**
- Include: the sidebar content + enough of the sheet behind it that it feels “embedded in Sheets”.
- Exclude: browser chrome.

---

## Install + verify

1) Copy your new screenshots (usually on Desktop).
2) Run:

```bash
python3 scripts/install_real_screenshots.py --from ~/Desktop --check --optimize
python3 scripts/check_screenshots.py --fail-on-placeholders
```

Optional: run the full pipeline (install → validate → optimize):

```bash
python3 scripts/screenshots_pipeline.py --from ~/Desktop --check --fail-on-placeholders --optimize --width 1400
```

Optional: re-render the screenshots README + HTML gallery from `manifest.json`:

```bash
python3 scripts/screenshots_pipeline.py --render-gallery
```

Optional: generate the animated GIF preview (requires optimized JPGs):

```bash
python3 scripts/screenshots_pipeline.py --make-gif --gif-width 900 --gif-ms 900
```
