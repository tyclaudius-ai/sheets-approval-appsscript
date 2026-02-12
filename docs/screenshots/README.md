# Screenshots

These images are what the landing page (and a product listing) should reference.

If you haven’t captured real screenshots yet, you have two options:

- **Mock (“real-ish”) screenshots**: run `python3 scripts/generate_realish_screenshots.py --optimize` to generate *non-identical* PNGs that look like screenshots (adds simple browser chrome + fake Sheets header). This helps the README/landing page look real without requiring a Google login.
  - Note: this writes `docs/screenshots/realish-hashes.json` so we can later detect whether the repo is still using generated mocks.
- **True screenshots**: capture from a real Google Sheet and overwrite `docs/screenshots/*.png` 1:1 (preferred for a real product listing).

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

Follow: [`REAL_SCREENSHOTS_GUIDE.md`](../../REAL_SCREENSHOTS_GUIDE.md)

After capturing, verify none are still placeholders:

```bash
python3 scripts/check_screenshots.py
```

Optional: regenerate this README + the HTML gallery from the manifest:

```bash
python3 scripts/render_screenshots_gallery.py
```
