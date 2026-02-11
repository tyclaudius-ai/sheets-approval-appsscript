# Screenshots

These images are what the landing page (and a product listing) should reference.

If you haven’t captured real screenshots yet, the repo ships placeholder PNGs with the same filenames.

## Screenshot set

1) Menu (Approvals)

Custom menu entry for Approvals actions (Approve/Reject, Create demo, Help).

![01-menu](./01-menu.png)

2) Requests sheet (pending)

Example request rows in PENDING state, ready for review/approval.

![02-requests-pending](./02-requests-pending.png)

3) Approved row

A request row marked APPROVED (showing status + timestamp/user columns as configured).

![03-approved-row](./03-approved-row.png)

4) Audit trail entry

Append-only audit log row capturing who approved/rejected what and when.

![04-audit-entry](./04-audit-entry.png)

5) Re-approval required

An edit to tracked cells triggers REAPPROVAL_REQUIRED (or reverts to PENDING), with an audit event.

![05-reapproval-required](./05-reapproval-required.png)

6) Help / Docs sidebar

In-sheet Help sidebar for quick onboarding and usage.

![06-help-sidebar](./06-help-sidebar.png)

## Capturing real screenshots

Quick path: [`CAPTURE-CHEATSHEET.md`](./CAPTURE-CHEATSHEET.md)

Full guide: [`REAL_SCREENSHOTS_GUIDE.md`](../../REAL_SCREENSHOTS_GUIDE.md)

After capturing, verify none are still placeholders:

```bash
python3 scripts/check_screenshots.py
```

Optional: regenerate this README + the HTML gallery from the manifest:

```bash
python3 scripts/render_screenshots_gallery.py
```

## Optimized versions (for listings / smaller READMEs)

Generate resized, compressed copies under `docs/screenshots/optimized/` (macOS-only; uses `sips`):

```bash
node scripts/optimize_screenshots.mjs --width 1400 --format jpg
```
