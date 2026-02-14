# Marketplace / Listing Checklist (Sheets Approval + Audit Trail)

Use this when you’re about to publish the project as a **digital download** (Gumroad / Ko‑fi) or attach it to a **fixed‑price setup offer** (Upwork Project Catalog).

This repo intentionally supports **two modes**:

1) **DIY download** — user copies/pastes `Code.gs` (or uses the packaged zip)
2) **Done‑for‑you setup** — you install/customize it into their existing sheet

## 0) Decide the offer

- **DIY** (lowest friction): “Copy/paste Apps Script + demo template + docs”
- **Setup service** (higher $): “I install it, customize tracked fields, and verify the workflow live”

If you’re doing both, publish the DIY download and use it as an upsell into setup.

## 1) Make sure docs are coherent

- [ ] `README.md` is accurate and has the shortest path to success
- [ ] `QUICKSTART.md` works end‑to‑end in <2 minutes
- [ ] `DEMO.md` is a 2–5 minute talk‑track (what to click + what to say)
- [ ] `TROUBLESHOOTING.md` covers the common Apps Script gotchas (permissions, triggers)

## 2) Screenshots (real, if possible)

Recommended: capture these real screenshots (see `SCREENSHOTS.md` for the shot list).

### Check placeholder status

```bash
python3 scripts/check_screenshots.py
```

### Optional: helper pack for capturing “real” screenshots (recommended if you’re delegating)

```bash
python3 scripts/make_real_screenshot_capture_pack.py
```

This generates a zip under `dist/real-screenshots-capture-pack-<ts>.zip` that you can hand to yourself/another machine/VA.

After unzipping on the capture machine:

```bash
python3 scripts/install_real_screenshots.py --from ~/Desktop --open --check --optimize
python3 scripts/check_screenshots.py --require-real-screenshots
```

### Rebuild gallery + (optional) optimized JPGs + GIF

```bash
python3 scripts/screenshots_pipeline.py
# strict mode (fails if any placeholders remain)
python3 scripts/screenshots_pipeline.py --fail-on-placeholders
# macOS-only: also create docs/screenshots/optimized/*.jpg
python3 scripts/screenshots_pipeline.py --optimize --width 1400
# optional: generate small animated preview used in docs/screenshots/
python3 scripts/screenshots_pipeline.py --make-gif --gif-width 900 --gif-ms 900
```

## 3) Build the deliverable zip

You have two packaging options:

### A) “Client bundle” zip (simple)

```bash
python3 scripts/package_sheets_approval_appsscript.py
```

### B) “Marketplace pack” zip (listing‑oriented)

```bash
python3 scripts/make_marketplace_pack.py
```

The marketplace pack is designed to be uploaded as the downloadable artifact.

## 4) Listing copy

- [ ] Use `LISTING.md` as the canonical copy source (long-form)
- [ ] Use `MARKETPLACE-LISTING-COPY.md` for **copy/paste** titles, bullets, and FAQ snippets
- [ ] Confirm the “What it does” section matches the current feature set
- [ ] Decide if you are selling **MIT-licensed source** (this repo) or a curated download bundle

## 5) QA sanity checks (before you post)

- [ ] Validate marketplace pack contents (recommended):

```bash
python3 scripts/validate_marketplace_pack.py dist/marketplace-pack-*.zip
```

- [ ] `python3 scripts/package_sheets_approval_appsscript.py --check` (if supported)
- [ ] Landing page renders locally:

```bash
python3 scripts/serve_landing.py --open
```

- [ ] No placeholder screenshots (if you’re claiming “real” screenshots)

## 6) Optional: Done‑for‑you setup checklist

If you’re offering a setup service, use:

- `INTAKE_QUESTIONS.md`
- `CLIENT-HANDOFF.md`

And be explicit about what you will (and will not) customize:

- tracked headers allowlist
- status values
- notifications
- protections/locking mode

---

If you want, add a short “versioned changelog” section to your listing (buyers love this). A minimal approach is just a dated bullet list in `CHANGELOG.md`.
