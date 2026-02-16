# Uninstall — Sheets Approvals + Audit Trail

These steps remove the script + any triggers, and optionally remove the demo tabs.

## 1) Remove triggers (recommended)
1. In the Sheet: **Extensions → Apps Script**
2. Left sidebar: **Triggers** (clock icon)
3. Delete any triggers created for this project (e.g. “re-approval trigger”).

> Why: installs sometimes add an installable trigger so edits can force re-approval even when simple triggers are restricted.

## 2) Remove the script project
Pick one:

### Option A — delete the Apps Script project
- In Apps Script: **Project Settings** → (or the file menu) **Delete project**

### Option B — keep the project but disable functionality
- Delete the contents of `Code.gs` (or remove the `onOpen` + menu actions)
- Save

## 3) (Optional) Remove demo/product tabs
If you used the demo setup, you can delete these sheets in the workbook:
- `Requests`
- `Audit`

## 4) Verify it’s gone
- Reload the Sheet.
- Confirm the **Approvals** menu no longer appears.
- Confirm no triggers remain in Apps Script.
