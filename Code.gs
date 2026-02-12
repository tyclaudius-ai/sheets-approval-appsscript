/**
 * Sheets Approval + Audit Trail (MVP)
 *
 * Bind this script to a Google Sheet.
 * Creates an "Approvals" custom menu.
 * Works on the currently selected row in the Requests sheet.
 */

const CFG = {
  REQUESTS_SHEET: 'Requests',
  AUDIT_SHEET: 'Audit',
  HEADER_ROW: 1,
  STATUS: {
    PENDING: 'PENDING',
    APPROVED: 'APPROVED',
    REJECTED: 'REJECTED',
  },
  // RequestId is generated if empty
  REQUEST_ID_HEADER: 'RequestId',

  // Optional: store a sha256 hash of the last approved *meaningful* snapshot on the row.
  // If you add a column with this header, the script will write the hash on APPROVED
  // and the menu action `Scan approved rows for changes` can detect drift even when
  // changes happen outside a user edit (imports, other scripts, copy/paste that bypasses triggers, etc.).
  APPROVED_HASH_HEADER: 'ApprovedHash',

  // If an already-approved row is edited, automatically revert it to PENDING.
  //
  // Behavior:
  // - Only runs for user edits (simple trigger).
  // - Re-approval is required if the edited cells include at least one header that is:
  //   - NOT in REAPPROVAL_EXEMPT_HEADERS, AND
  //   - (if REAPPROVAL_TRACKED_HEADERS is non-empty) IS included in REAPPROVAL_TRACKED_HEADERS
  REAPPROVAL_ON_CHANGE: true,

  // Optional allowlist: when set, ONLY edits to these columns can trigger re-approval.
  // Leave empty to treat any non-exempt column as meaningful.
  REAPPROVAL_TRACKED_HEADERS: [],

  // Which statuses should revert to PENDING when a meaningful edit occurs.
  // Default: only APPROVED rows require re-approval.
  // You may include 'REJECTED' if you want edits to rejected requests to re-open them.
  REAPPROVAL_FROM_STATUSES: ['APPROVED'],

  // Columns that will NOT trigger re-approval (decision + meta columns).
  REAPPROVAL_EXEMPT_HEADERS: [
    'RequestId',
    'Status',
    'Approver',
    'DecisionAt',
    'DecisionNotes',
  ],

  // Optional: lock the entire row after approval using a range Protection.
  // Note: consumer accounts / some domains may restrict protection editors. WARNING_ONLY avoids hard-blocks.
  LOCK_ROW_ON_APPROVE: true,
  LOCK_WARNING_ONLY: true,
  LOCK_DESCRIPTION_PREFIX: 'ApprovalsLock',

  // Optional: add a simple “hash chain” to the Audit sheet so tampering is easier to detect.
  // Each audit row stores PrevChainHash + ChainHash where:
  //   ChainHash = sha256(prevChainHash + "\n" + SnapshotHash)
  // This gives you a spreadsheet-friendly, blockchain-ish integrity check.
  AUDIT_HASH_CHAIN: true,
};

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Approvals')
    .addItem('Approve row', 'approveSelectedRow')
    .addItem('Reject row', 'rejectSelectedRow')
    .addItem('Approve selected rows…', 'approveSelectedRows')
    .addItem('Reject selected rows…', 'rejectSelectedRows')
    .addSeparator()
    .addItem('Reset to pending', 'resetSelectedRowToPending')
    .addItem('Reset selected rows to pending', 'resetSelectedRowsToPending')
    .addSeparator()
    .addItem('Scan approved rows for changes', 'scanForReapprovalNeeded')
    .addSeparator()
    .addItem('Create demo setup', 'createDemoSetup')
    .addItem('Screenshot tour (capture helper)', 'showScreenshotTourSidebar')
    .addSeparator()
    .addItem('Install re-approval trigger (optional)', 'installReapprovalTrigger')
    .addItem('Remove installed triggers', 'removeInstalledApprovalTriggers')
    .addSeparator()
    .addItem('Help / Docs', 'showHelpSidebar')
    .addToUi();
}

/**
 * Optional: install an installable onEdit trigger.
 *
 * Why:
 * - Simple triggers can be constrained in some domains.
 * - Installable triggers run under the authorizing user and can be easier to debug/permission.
 *
 * Note: if you keep the simple `onEdit(e)` function, Sheets will still call it.
 * Installing this trigger creates an additional handler `onEditInstallable(e)`.
 */
function installReapprovalTrigger() {
  const ss = SpreadsheetApp.getActive();
  const existing = ScriptApp.getProjectTriggers().filter(t => {
    return t.getEventType && t.getEventType() === ScriptApp.EventType.ON_EDIT && t.getHandlerFunction && t.getHandlerFunction() === 'onEditInstallable';
  });

  if (existing.length > 0) {
    SpreadsheetApp.getUi().alert('Re-approval trigger already installed.');
    return;
  }

  ScriptApp.newTrigger('onEditInstallable')
    .forSpreadsheet(ss)
    .onEdit()
    .create();

  SpreadsheetApp.getUi().alert('Installed installable re-approval trigger (onEditInstallable).');
}

function removeInstalledApprovalTriggers() {
  const triggers = ScriptApp.getProjectTriggers();
  let removed = 0;
  triggers.forEach(t => {
    const handler = t.getHandlerFunction && t.getHandlerFunction();
    const type = t.getEventType && t.getEventType();
    if (type === ScriptApp.EventType.ON_EDIT && (handler === 'onEditInstallable')) {
      ScriptApp.deleteTrigger(t);
      removed++;
    }
  });

  SpreadsheetApp.getUi().alert(`Removed ${removed} installed trigger(s).`);
}

/**
 * Installable trigger handler.
 * Delegates to the simple trigger logic.
 */
function onEditInstallable(e) {
  // Best-effort: if anything fails, we don't want to break the user's edit.
  try {
    onEdit(e);
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('onEditInstallable error:', err);
  }
}

/**
 * Simple trigger: if someone edits a previously-approved request,
 * the request is forced back to PENDING to require re-approval.
 *
 * Note: Simple triggers run only for user edits (not edits made by scripts).
 */
function onEdit(e) {
  if (!CFG.REAPPROVAL_ON_CHANGE) return;
  if (!e || !e.range) return;

  const sheet = e.range.getSheet();
  if (!sheet || sheet.getName() !== CFG.REQUESTS_SHEET) return;

  const startRow = e.range.getRow();
  const numRows = e.range.getNumRows();
  if (startRow <= CFG.HEADER_ROW) return;

  const lock = LockService.getDocumentLock();
  lock.waitLock(30 * 1000);

  try {
    const ss = SpreadsheetApp.getActive();
    const headers = getHeaders_(sheet);

    // Identify which headers were edited (might be a multi-cell paste).
    const startCol = e.range.getColumn();
    const numCols = e.range.getNumColumns();
    const editedHeaders = [];
    for (let i = 0; i < numCols; i++) {
      editedHeaders.push(headers[startCol - 1 + i] || `Col${startCol + i}`);
    }

    const tracked = (CFG.REAPPROVAL_TRACKED_HEADERS || []).map(h => (h || '').toString().trim()).filter(Boolean);
    const exempt = (CFG.REAPPROVAL_EXEMPT_HEADERS || []).map(h => (h || '').toString().trim()).filter(Boolean);

    const meaningful = editedHeaders.some(h => exempt.indexOf(h) === -1 && (tracked.length === 0 || tracked.indexOf(h) !== -1));
    if (!meaningful) return;

    const now = new Date();
    const userEmail = getUserEmail_();

    // Apply to every affected row (multi-row paste/edit).
    for (let r = startRow; r < startRow + numRows; r++) {
      if (r <= CFG.HEADER_ROW) continue;

      // Read current row state *after* the user edit.
      const rowValues = sheet.getRange(r, 1, 1, headers.length).getValues()[0];
      const rowObj = rowToObject_(headers, rowValues);

      const status = (rowObj.Status || '').toString().trim();
      const reapprovalStatuses = (CFG.REAPPROVAL_FROM_STATUSES || [CFG.STATUS.APPROVED])
        .map(x => (x || '').toString().trim())
        .filter(Boolean);
      if (reapprovalStatuses.indexOf(status) === -1) continue;

      const requestId = ensureRequestId_(sheet, headers, r, rowObj);

      // Force back to pending + clear decision fields.
      setCellByHeader_(sheet, headers, r, 'Status', CFG.STATUS.PENDING);
      setCellByHeader_(sheet, headers, r, 'Approver', '');
      setCellByHeader_(sheet, headers, r, 'DecisionAt', '');
      setCellByHeader_(sheet, headers, r, 'DecisionNotes', `Auto: re-approval required (was ${status}; edited: ${editedHeaders.join(', ')})`);

      // Remove row lock if present.
      if (CFG.LOCK_ROW_ON_APPROVE) {
        unprotectRow_(sheet, r);
      }

      // Snapshot after forcing pending.
      const newValues = sheet.getRange(r, 1, 1, headers.length).getValues()[0];
      const newObj = rowToObject_(headers, newValues);

      const snapshotJson = JSON.stringify({
        ...newObj,
        _reapproval: {
          editedHeaders,
          priorStatus: status,
        },
      });

      appendAuditEvent_(ss, {
        eventAt: now,
        actor: userEmail,
        action: 'REAPPROVAL_REQUIRED',
        requestId,
        rowNumber: r,
        snapshotJson,
        snapshotHash: sha256Hex_(snapshotJson),
      });
    }
  } finally {
    lock.releaseLock();
  }
}

function computeMeaningfulSnapshotJson_(headers, rowValues) {
  const obj = rowToObject_(headers, rowValues);

  const tracked = (CFG.REAPPROVAL_TRACKED_HEADERS || []).map(h => (h || '').toString().trim()).filter(Boolean);
  const exempt = (CFG.REAPPROVAL_EXEMPT_HEADERS || []).map(h => (h || '').toString().trim()).filter(Boolean);

  // Build a stable, minimal snapshot of only the fields that matter for re-approval.
  // - If tracked is set: only include tracked headers (minus exempt)
  // - Else: include all headers (minus exempt)
  const keys = [];
  for (let i = 0; i < headers.length; i++) {
    const h = (headers[i] || `Col${i + 1}`).toString().trim();
    if (!h) continue;
    if (exempt.indexOf(h) !== -1) continue;
    if (tracked.length > 0 && tracked.indexOf(h) === -1) continue;
    keys.push(h);
  }
  keys.sort();

  const out = {};
  keys.forEach(k => { out[k] = obj[k]; });
  return JSON.stringify(out);
}

function computeMeaningfulHash_(headers, rowValues) {
  return sha256Hex_(computeMeaningfulSnapshotJson_(headers, rowValues));
}

/**
 * Menu action: scan approved rows to detect “drift” from the last approved snapshot.
 *
 * Why this exists:
 * - `onEdit(e)` only fires for user edits.
 * - Rows can still change via imports, other scripts, API writes, copy/paste edge cases, etc.
 *
 * If you add a column named `ApprovedHash` (CFG.APPROVED_HASH_HEADER),
 * this tool will:
 * - on APPROVED rows with empty ApprovedHash: set it to the current meaningful hash (and audit it)
 * - on APPROVED rows with a mismatched ApprovedHash: revert to PENDING and log REAPPROVAL_REQUIRED
 */
function scanForReapprovalNeeded() {
  const lock = LockService.getDocumentLock();
  lock.waitLock(30 * 1000);

  try {
    const ss = SpreadsheetApp.getActive();
    const reqSheet = ss.getSheetByName(CFG.REQUESTS_SHEET);
    if (!reqSheet) throw new Error(`Missing sheet: ${CFG.REQUESTS_SHEET}`);

    const headers = getHeaders_(reqSheet);
    const idxStatus = headers.indexOf('Status');
    const idxApprovedHash = headers.indexOf(CFG.APPROVED_HASH_HEADER);

    if (idxStatus == -1) throw new Error('Missing required header: Status');
    if (idxApprovedHash == -1) {
      SpreadsheetApp.getUi().alert(`No column named “${CFG.APPROVED_HASH_HEADER}” found. Add it to Requests to enable drift scanning.`);
      return;
    }

    const lastRow = reqSheet.getLastRow();
    if (lastRow <= CFG.HEADER_ROW) {
      SpreadsheetApp.getUi().alert('No data rows to scan.');
      return;
    }

    const values = reqSheet.getRange(CFG.HEADER_ROW + 1, 1, lastRow - CFG.HEADER_ROW, headers.length).getValues();

    const now = new Date();
    const userEmail = getUserEmail_();
    let setCount = 0;
    let reapprovalCount = 0;

    for (let i = 0; i < values.length; i++) {
      const rowNumber = CFG.HEADER_ROW + 1 + i;
      const rowValues = values[i];
      const status = (rowValues[idxStatus] || '').toString().trim();
      if (status !== CFG.STATUS.APPROVED) continue;

      const requestId = ensureRequestId_(reqSheet, headers, rowNumber, rowToObject_(headers, rowValues));
      const computed = computeMeaningfulHash_(headers, rowValues);
      const stored = (rowValues[idxApprovedHash] || '').toString().trim();

      if (!stored) {
        // First-time: set it, but do not force re-approval.
        reqSheet.getRange(rowNumber, idxApprovedHash + 1).setValue(computed);
        setCount++;

        appendAuditEvent_(ss, {
          eventAt: now,
          actor: userEmail,
          action: 'APPROVAL_HASH_SET',
          requestId,
          rowNumber,
          snapshotJson: JSON.stringify({ rowNumber, computedMeaningfulHash: computed }),
          snapshotHash: sha256Hex_(`set:${computed}`),
        });
        continue;
      }

      if (stored !== computed) {
        // Drift detected: revert to pending + clear decision fields.
        setCellByHeader_(reqSheet, headers, rowNumber, 'Status', CFG.STATUS.PENDING);
        setCellByHeader_(reqSheet, headers, rowNumber, 'Approver', '');
        setCellByHeader_(reqSheet, headers, rowNumber, 'DecisionAt', '');
        setCellByHeader_(reqSheet, headers, rowNumber, 'DecisionNotes', 'Auto: re-approval required (hash mismatch; run scan)');

        if (CFG.LOCK_ROW_ON_APPROVE) unprotectRow_(reqSheet, rowNumber);

        const postValues = reqSheet.getRange(rowNumber, 1, 1, headers.length).getValues()[0];
        const postObj = rowToObject_(headers, postValues);
        const snapshotJson = JSON.stringify({
          ...postObj,
          _reapproval: {
            reason: 'hash_mismatch',
            storedMeaningfulHash: stored,
            computedMeaningfulHash: computed,
          },
        });

        appendAuditEvent_(ss, {
          eventAt: now,
          actor: userEmail,
          action: 'REAPPROVAL_REQUIRED',
          requestId,
          rowNumber,
          snapshotJson,
          snapshotHash: sha256Hex_(snapshotJson),
        });

        reapprovalCount++;
      }
    }

    SpreadsheetApp.getUi().alert(`Scan complete. Set ApprovedHash on ${setCount} row(s). Re-opened ${reapprovalCount} row(s) for re-approval.`);
  } finally {
    lock.releaseLock();
  }
}

function approveSelectedRow() {
  decideOnSelectedRow_(CFG.STATUS.APPROVED);
}

function rejectSelectedRow() {
  decideOnSelectedRow_(CFG.STATUS.REJECTED);
}

function approveSelectedRows() {
  decideOnSelectedRows_(CFG.STATUS.APPROVED);
}

function rejectSelectedRows() {
  decideOnSelectedRows_(CFG.STATUS.REJECTED);
}

function resetSelectedRowToPending() {
  decideOnSelectedRow_(CFG.STATUS.PENDING);
}

function resetSelectedRowsToPending() {
  decideOnSelectedRows_(CFG.STATUS.PENDING);
}

function decideOnSelectedRow_(status) {
  const lock = LockService.getDocumentLock();
  lock.waitLock(30 * 1000);

  try {
    const ss = SpreadsheetApp.getActive();
    const reqSheet = ss.getSheetByName(CFG.REQUESTS_SHEET);
    if (!reqSheet) throw new Error(`Missing sheet: ${CFG.REQUESTS_SHEET}`);

    const range = reqSheet.getActiveRange();
    if (!range) throw new Error('No active selection');

    const row = range.getRow();
    if (row <= CFG.HEADER_ROW) throw new Error('Select a data row (not the header).');

    decideOnRowsImpl_({ ss, reqSheet, status, rows: [row] });
  } finally {
    lock.releaseLock();
  }
}

function decideOnSelectedRows_(status) {
  const lock = LockService.getDocumentLock();
  lock.waitLock(30 * 1000);

  try {
    const ss = SpreadsheetApp.getActive();
    const reqSheet = ss.getSheetByName(CFG.REQUESTS_SHEET);
    if (!reqSheet) throw new Error(`Missing sheet: ${CFG.REQUESTS_SHEET}`);

    const range = reqSheet.getActiveRange();
    if (!range) throw new Error('No active selection');

    const startRow = range.getRow();
    const numRows = range.getNumRows();

    const rows = [];
    for (let r = startRow; r < startRow + numRows; r++) {
      if (r > CFG.HEADER_ROW) rows.push(r);
    }

    if (rows.length === 0) throw new Error('Select at least one data row (not the header).');

    decideOnRowsImpl_({ ss, reqSheet, status, rows });
  } finally {
    lock.releaseLock();
  }
}

function decideOnRowsImpl_({ ss, reqSheet, status, rows }) {
  if (!ss) throw new Error('Missing ss');
  if (!reqSheet) throw new Error('Missing reqSheet');
  if (!Array.isArray(rows) || rows.length === 0) throw new Error('No rows selected');

  const headers = getHeaders_(reqSheet);
  const ui = SpreadsheetApp.getUi();

  const promptTitle = status === CFG.STATUS.APPROVED
    ? 'Approve request(s)'
    : status === CFG.STATUS.REJECTED
      ? 'Reject request(s)'
      : 'Reset to pending';

  let notes = '';
  if (status === CFG.STATUS.APPROVED || status === CFG.STATUS.REJECTED) {
    const resp = ui.prompt(promptTitle, `Optional decision notes (applied to ${rows.length} row(s)):` , ui.ButtonSet.OK_CANCEL);
    if (resp.getSelectedButton() !== ui.Button.OK) return;
    notes = (resp.getResponseText() || '').trim();
  }

  const now = new Date();
  const userEmail = getUserEmail_();

  rows.forEach(row => {
    if (row <= CFG.HEADER_ROW) return;

    const rowValues = reqSheet.getRange(row, 1, 1, headers.length).getValues()[0];
    const rowObj = rowToObject_(headers, rowValues);
    const requestId = ensureRequestId_(reqSheet, headers, row, rowObj);

    // Write decision back to row
    setCellByHeader_(reqSheet, headers, row, 'Status', status);

    if (status === CFG.STATUS.PENDING) {
      // Reset: clear decision metadata (do NOT attribute to a user/time).
      setCellByHeader_(reqSheet, headers, row, 'Approver', '');
      setCellByHeader_(reqSheet, headers, row, 'DecisionAt', '');
      setCellByHeader_(reqSheet, headers, row, 'DecisionNotes', '');
    } else {
      setCellByHeader_(reqSheet, headers, row, 'Approver', userEmail);
      setCellByHeader_(reqSheet, headers, row, 'DecisionAt', now);
      setCellByHeader_(reqSheet, headers, row, 'DecisionNotes', notes);
    }

    // Refresh snapshot for audit log
    const newValues = reqSheet.getRange(row, 1, 1, headers.length).getValues()[0];
    const newObj = rowToObject_(headers, newValues);

    // If APPROVED, store a hash of the meaningful fields on the row (optional column).
    if (status === CFG.STATUS.APPROVED) {
      const mh = computeMeaningfulHash_(headers, newValues);
      setCellByHeader_(reqSheet, headers, row, CFG.APPROVED_HASH_HEADER, mh);
    }

    const snapshotJson = JSON.stringify(newObj);
    appendAuditEvent_(ss, {
      eventAt: now,
      actor: userEmail,
      action: status,
      requestId,
      rowNumber: row,
      snapshotJson,
      snapshotHash: sha256Hex_(snapshotJson),
    });

    // Optional row locking
    if (CFG.LOCK_ROW_ON_APPROVE) {
      if (status === CFG.STATUS.APPROVED) {
        protectRow_(reqSheet, row, requestId);
      } else {
        // On reject/reset, remove prior locks created by this script.
        unprotectRow_(reqSheet, row);
      }
    }
  });
}

function getHeaders_(sheet) {
  const lastCol = sheet.getLastColumn();
  if (lastCol < 1) throw new Error('No headers found');
  const headers = sheet.getRange(CFG.HEADER_ROW, 1, 1, lastCol).getValues()[0]
    .map(h => (h || '').toString().trim());

  if (headers.every(h => !h)) throw new Error('Header row is empty');
  return headers;
}

function rowToObject_(headers, values) {
  const obj = {};
  for (let i = 0; i < headers.length; i++) {
    const key = headers[i] || `Col${i + 1}`;
    obj[key] = values[i];
  }
  return obj;
}

function ensureRequestId_(sheet, headers, row, rowObj) {
  const idx = headers.indexOf(CFG.REQUEST_ID_HEADER);
  if (idx === -1) {
    throw new Error(`Missing required header: ${CFG.REQUEST_ID_HEADER}`);
  }
  const existing = (rowObj[CFG.REQUEST_ID_HEADER] || '').toString().trim();
  if (existing) return existing;

  const gen = `REQ-${Utilities.getUuid()}`;
  sheet.getRange(row, idx + 1).setValue(gen);
  return gen;
}

function setCellByHeader_(sheet, headers, row, headerName, value) {
  const idx = headers.indexOf(headerName);
  if (idx === -1) return; // allow extra columns / optional fields
  sheet.getRange(row, idx + 1).setValue(value);
}

function appendAuditEvent_(ss, evt) {
  const audit = getOrCreateAuditSheet_(ss);

  const baseHeaders = ['EventAt', 'Actor', 'Action', 'RequestId', 'RowNumber', 'SnapshotJSON', 'SnapshotHash'];
  const headers = CFG.AUDIT_HASH_CHAIN
    ? baseHeaders.concat(['PrevChainHash', 'ChainHash'])
    : baseHeaders;

  // Ensure header row exists/updated.
  if (audit.getLastRow() === 0) {
    audit.getRange(1, 1, 1, headers.length).setValues([headers]);
  } else {
    const existing = audit.getRange(1, 1, 1, Math.max(headers.length, audit.getLastColumn())).getValues()[0]
      .slice(0, headers.length)
      .map(v => (v || '').toString().trim());
    const needs = existing.length !== headers.length || existing.some((v, i) => v !== headers[i]);
    if (needs) {
      audit.getRange(1, 1, 1, headers.length).setValues([headers]);
    }
  }

  let prevChainHash = '';
  let chainHash = '';
  if (CFG.AUDIT_HASH_CHAIN) {
    // Get previous chain hash from the last data row (best-effort).
    const lastRow = audit.getLastRow();
    const idxChain = headers.indexOf('ChainHash');
    if (lastRow >= 2 && idxChain !== -1) {
      try {
        prevChainHash = (audit.getRange(lastRow, idxChain + 1).getValue() || '').toString().trim();
      } catch (e) {
        prevChainHash = '';
      }
    }
    chainHash = sha256Hex_(`${prevChainHash}\n${evt.snapshotHash}`);
  }

  const row = [
    evt.eventAt,
    evt.actor,
    evt.action,
    evt.requestId,
    evt.rowNumber,
    evt.snapshotJson,
    evt.snapshotHash,
  ];

  if (CFG.AUDIT_HASH_CHAIN) {
    row.push(prevChainHash, chainHash);
  }

  audit.appendRow(row);
}

function sha256Hex_(str) {
  const bytes = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, str, Utilities.Charset.UTF_8);
  return bytes.map(b => {
    const v = (b < 0 ? b + 256 : b);
    return (v < 16 ? '0' : '') + v.toString(16);
  }).join('');
}

function getOrCreateAuditSheet_(ss) {
  let sheet = ss.getSheetByName(CFG.AUDIT_SHEET);
  if (!sheet) sheet = ss.insertSheet(CFG.AUDIT_SHEET);
  return sheet;
}

function getUserEmail_() {
  try {
    const email = Session.getActiveUser().getEmail();
    return email || 'unknown';
  } catch (e) {
    return 'unknown';
  }
}

function protectRow_(sheet, row, requestId) {
  const lastCol = Math.max(1, sheet.getLastColumn());
  const range = sheet.getRange(row, 1, 1, lastCol);

  // Avoid duplicate protections for the same row.
  const existing = sheet.getProtections(SpreadsheetApp.ProtectionType.RANGE)
    .filter(p => {
      const r = p.getRange();
      return r.getRow() === row && r.getNumRows() === 1 && (p.getDescription() || '').startsWith(CFG.LOCK_DESCRIPTION_PREFIX + ':');
    });
  if (existing.length) return;

  const p = range.protect();
  p.setDescription(`${CFG.LOCK_DESCRIPTION_PREFIX}:${requestId}:row=${row}`);
  p.setWarningOnly(!!CFG.LOCK_WARNING_ONLY);

  // Best-effort: restrict editors to just the script runner.
  // If this throws (domain policy), we still keep warning-only protection as a soft guardrail.
  try {
    if (!CFG.LOCK_WARNING_ONLY) {
      p.removeEditors(p.getEditors());
      if (p.canDomainEdit()) p.setDomainEdit(false);
      const me = Session.getEffectiveUser();
      if (me) p.addEditor(me);
    }
  } catch (e) {
    // ignore
  }
}

function unprotectRow_(sheet, row) {
  const protections = sheet.getProtections(SpreadsheetApp.ProtectionType.RANGE);
  protections.forEach(p => {
    const desc = (p.getDescription() || '');
    if (!desc.startsWith(CFG.LOCK_DESCRIPTION_PREFIX + ':')) return;
    const r = p.getRange();
    if (r.getRow() === row && r.getNumRows() === 1) {
      try { p.remove(); } catch (e) { /* ignore */ }
    }
  });
}

/**
 * Demo helper: creates the required sheets, headers, and a screenshot-friendly
 * set of example requests.
 *
 * Safe to run multiple times:
 * - It will NOT overwrite existing data rows.
 * - It WILL apply light formatting (freeze header row, set widths, header style).
 */
function createDemoSetup() {
  const ss = SpreadsheetApp.getActive();

  const requestsHeaders = ['RequestId', 'Title', 'Requester', 'Status', 'Approver', 'DecisionAt', 'DecisionNotes', CFG.APPROVED_HASH_HEADER];
  const req = ensureSheetWithHeaders_(ss, CFG.REQUESTS_SHEET, requestsHeaders);

  // Apply formatting even if there is already data.
  try {
    formatRequestsSheetForScreenshots_(req, requestsHeaders);
  } catch (e) {
    // Best-effort; formatting isn't critical.
  }

  // Seed only when sheet is empty (besides header).
  if (req.getLastRow() <= CFG.HEADER_ROW) {
    // Deterministic, screenshot-ready rows.
    // Note: use explicit RequestIds so screenshots remain stable.
    const now = new Date();
    const iso = Utilities.formatDate(now, ss.getSpreadsheetTimeZone(), 'yyyy-MM-dd HH:mm');

    // Row 2: pending
    req.appendRow(['REQ-0001', 'Purchase approval: lab supplies', 'alex@example.com', CFG.STATUS.PENDING, '', '', '', '']);

    // Row 3: approved (clean)
    req.appendRow(['REQ-0002', 'Vendor onboarding: ACME Co.', 'sam@example.com', CFG.STATUS.APPROVED, 'approver@example.com', iso, 'Approved for Q1; within budget.', '']);

    // Row 4: rejected
    req.appendRow(['REQ-0003', 'Access request: finance drive', 'taylor@example.com', CFG.STATUS.REJECTED, 'approver@example.com', iso, 'Rejected: least privilege — request specific folder.', '']);

    // Row 5: approved (drift example) — stored hash will mismatch after we mutate the Title.
    req.appendRow(['REQ-0004', 'Equipment purchase: thermal camera', 'jordan@example.com', CFG.STATUS.APPROVED, 'approver@example.com', iso, 'Approved: use preferred vendor.', '']);

    // Set ApprovedHash on APPROVED rows, then introduce drift on REQ-0004.
    const headers = getHeaders_(req);
    const idxApprovedHash = headers.indexOf(CFG.APPROVED_HASH_HEADER);
    if (idxApprovedHash !== -1) {
      // Set hashes for rows 3 and 5.
      [3, 5].forEach(r => {
        const rowValues = req.getRange(r, 1, 1, headers.length).getValues()[0];
        const computed = computeMeaningfulHash_(headers, rowValues);
        req.getRange(r, idxApprovedHash + 1).setValue(computed);
      });

      // Mutate Title on REQ-0004 after hashing so scanForReapprovalNeeded() will catch it.
      // (Simulates drift from imports/other scripts.)
      req.getRange(5, headers.indexOf('Title') + 1).setValue('Equipment purchase: thermal camera (spec updated)');
    }

    // Cosmetic: auto-fit rows/columns around seeded data.
    try {
      req.autoResizeColumns(1, requestsHeaders.length);
    } catch (e) {
      // ignore
    }
  }

  // Ensure audit sheet exists + log setup event.
  getOrCreateAuditSheet_(ss);
  appendAuditEvent_(ss, {
    eventAt: new Date(),
    actor: getUserEmail_(),
    action: 'DEMO_SETUP',
    requestId: 'n/a',
    rowNumber: 0,
    snapshotJson: JSON.stringify({ sheet: CFG.REQUESTS_SHEET, seededRows: Math.max(0, req.getLastRow() - 1) }),
    snapshotHash: sha256Hex_('demo'),
  });

  SpreadsheetApp.getUi().alert(
    'Demo setup complete.\n\n' +
    'Suggested screenshots:\n' +
    '1) Select REQ-0001 and Approvals → Approve row.\n' +
    '2) Run Approvals → Scan approved rows for changes (REQ-0004 will reopen).\n' +
    '3) Open Approvals → Help / Docs.'
  );
}

function formatRequestsSheetForScreenshots_(sheet, headers) {
  // Freeze header row.
  sheet.setFrozenRows(1);

  // Header style.
  const headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange
    .setFontWeight('bold')
    .setBackground('#f1f3f4')
    .setHorizontalAlignment('center');

  // Set some reasonable default widths for clean screenshots.
  const widths = {
    RequestId: 110,
    Title: 320,
    Requester: 220,
    Status: 110,
    Approver: 220,
    DecisionAt: 160,
    DecisionNotes: 360,
    ApprovedHash: 220,
  };

  headers.forEach((h, i) => {
    const w = widths[h] || 160;
    try { sheet.setColumnWidth(i + 1, w); } catch (e) { /* ignore */ }
  });

  // Wrap notes for nicer screenshots.
  const idxNotes = headers.indexOf('DecisionNotes');
  if (idxNotes !== -1) {
    sheet.getRange(2, idxNotes + 1, Math.max(1, sheet.getMaxRows() - 1), 1).setWrap(true);
  }

  // Conditional formatting for Status (makes screenshots immediately readable).
  const idxStatus = headers.indexOf('Status');
  if (idxStatus !== -1) {
    const statusRange = sheet.getRange(2, idxStatus + 1, Math.max(1, sheet.getMaxRows() - 1), 1);

    // Keep any existing rules that do NOT apply to the Status column.
    const existing = sheet.getConditionalFormatRules() || [];
    const keep = existing.filter(rule => {
      try {
        const ranges = rule.getRanges ? rule.getRanges() : [];
        return !ranges.some(r => r.getColumn() === idxStatus + 1);
      } catch (e) {
        // If introspection fails, keep the rule.
        return true;
      }
    });

    const rules = [
      SpreadsheetApp.newConditionalFormatRule()
        .whenTextEqualTo(CFG.STATUS.APPROVED)
        .setBackground('#d9ead3')
        .setFontColor('#0b8043')
        .setRanges([statusRange])
        .build(),
      SpreadsheetApp.newConditionalFormatRule()
        .whenTextEqualTo(CFG.STATUS.PENDING)
        .setBackground('#fff2cc')
        .setFontColor('#7a4f01')
        .setRanges([statusRange])
        .build(),
      SpreadsheetApp.newConditionalFormatRule()
        .whenTextEqualTo(CFG.STATUS.REJECTED)
        .setBackground('#f4cccc')
        .setFontColor('#a61c00')
        .setRanges([statusRange])
        .build(),
    ];

    sheet.setConditionalFormatRules(keep.concat(rules));
  }
}

function ensureSheetWithHeaders_(ss, name, headers) {
  let sheet = ss.getSheetByName(name);
  if (!sheet) sheet = ss.insertSheet(name);

  const lastCol = Math.max(headers.length, sheet.getLastColumn());
  if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    return sheet;
  }

  // If headers row is empty or mismatched, write the expected headers (but do not wipe data rows).
  const existing = sheet.getRange(CFG.HEADER_ROW, 1, 1, lastCol).getValues()[0]
    .slice(0, headers.length)
    .map(v => (v || '').toString().trim());

  const needs = existing.length !== headers.length || existing.some((v, i) => v !== headers[i]);
  if (needs) {
    sheet.getRange(CFG.HEADER_ROW, 1, 1, headers.length).setValues([headers]);
  }

  return sheet;
}

function showHelpSidebar() {
  const html = HtmlService.createHtmlOutputFromFile('Docs')
    .setTitle('Approvals Help')
    .setWidth(360);

  SpreadsheetApp.getUi().showSidebar(html);
}

/**
 * Screenshot tour sidebar: guides you through staging consistent UI states
 * for capturing the README/landing page screenshots.
 */
function showScreenshotTourSidebar() {
  const html = HtmlService.createHtmlOutputFromFile('Tour')
    .setTitle('Screenshot tour')
    .setWidth(360);

  SpreadsheetApp.getUi().showSidebar(html);
}

/**
 * Server-side helper for the screenshot tour.
 *
 * Note: The sidebar runs client-side; it calls this function via google.script.run.
 */
function screenshotTourAction_(action) {
  const ss = SpreadsheetApp.getActive();
  const ui = SpreadsheetApp.getUi();

  // Ensure demo is present so buttons do something predictable.
  ensureDemoSetupForTour_(ss);

  const req = ss.getSheetByName(CFG.REQUESTS_SHEET);
  const audit = ss.getSheetByName(CFG.AUDIT_SHEET);
  if (!req || !audit) {
    ui.alert('Demo sheets missing. Run Approvals → Create demo setup first.');
    return;
  }

  if (action === 'go_requests') {
    ss.setActiveSheet(req);
    req.setActiveSelection('A1');
    return;
  }

  if (action === 'open_menu_hint') {
    // No programmatic menu-open in Sheets; this is just a no-op action the UI can call.
    return;
  }

  if (action === 'select_first_pending') {
    const headers = getHeaders_(req);
    const statusCol = headers.indexOf('Status') + 1;
    if (statusCol <= 0) {
      ui.alert('Could not find Status column in Requests.');
      return;
    }

    const lastRow = req.getLastRow();
    if (lastRow <= CFG.HEADER_ROW) {
      ui.alert('No data rows found in Requests. Click “Reset demo” in the tour.');
      return;
    }

    const statuses = req.getRange(CFG.HEADER_ROW + 1, statusCol, lastRow - CFG.HEADER_ROW, 1).getValues();
    let targetRow = null;
    for (let i = 0; i < statuses.length; i++) {
      const v = (statuses[i][0] || '').toString().trim();
      if (v === CFG.STATUS.PENDING) {
        targetRow = CFG.HEADER_ROW + 1 + i;
        break;
      }
    }

    if (!targetRow) {
      ui.alert('No PENDING rows found. Click “Reset demo” in the tour.');
      return;
    }

    ss.setActiveSheet(req);
    req.setActiveSelection(req.getRange(targetRow, 1, 1, Math.max(6, req.getLastColumn())));
    return;
  }

  if (action === 'approve_active_row') {
    ss.setActiveSheet(req);
    // Uses current selection.
    approveSelectedRow();
    return;
  }

  if (action === 'trigger_reapproval') {
    const headers = getHeaders_(req);
    const statusCol = headers.indexOf('Status') + 1;
    if (statusCol <= 0) {
      ui.alert('Could not find Status column in Requests.');
      return;
    }

    // Find first APPROVED row.
    const lastRow = req.getLastRow();
    const statuses = req.getRange(CFG.HEADER_ROW + 1, statusCol, Math.max(0, lastRow - CFG.HEADER_ROW), 1).getValues();
    let targetRow = null;
    for (let i = 0; i < statuses.length; i++) {
      const v = (statuses[i][0] || '').toString().trim();
      if (v === CFG.STATUS.APPROVED) {
        targetRow = CFG.HEADER_ROW + 1 + i;
        break;
      }
    }

    if (!targetRow) {
      ui.alert('No APPROVED rows found. Click “Approve active row” first.');
      return;
    }

    // Pick a "meaningful" column to edit: first non-exempt header.
    const exempt = (CFG.REAPPROVAL_EXEMPT_HEADERS || []).map(h => (h || '').toString().trim());
    let editCol = null;
    for (let c = 1; c <= headers.length; c++) {
      const h = (headers[c - 1] || '').toString().trim();
      if (!h) continue;
      if (exempt.indexOf(h) !== -1) continue;
      editCol = c;
      break;
    }

    if (!editCol) {
      ui.alert('Could not find a meaningful (non-exempt) column to edit for re-approval.');
      return;
    }

    ss.setActiveSheet(req);
    const cell = req.getRange(targetRow, editCol);
    const cur = cell.getValue();
    const next = `${cur || ''}`.trim() ? `${cur} (edited)` : 'Edited';
    cell.setValue(next);

    // onEdit won't fire for script edits; call the core handler manually to simulate.
    // We pass a minimal event object shape.
    try {
      onEdit({ range: cell });
    } catch (err) {
      // Best-effort; if it fails, still leave the edit.
      console.error('trigger_reapproval onEdit simulation failed:', err);
    }

    req.setActiveSelection(req.getRange(targetRow, 1, 1, Math.max(6, req.getLastColumn())));
    return;
  }

  if (action === 'go_audit_last') {
    ss.setActiveSheet(audit);
    const lastRow = audit.getLastRow();
    if (lastRow <= CFG.HEADER_ROW) {
      audit.setActiveSelection('A1');
      return;
    }
    audit.setActiveSelection(audit.getRange(lastRow, 1, 1, Math.max(6, audit.getLastColumn())));
    return;
  }

  if (action === 'open_help') {
    showHelpSidebar();
    return;
  }

  if (action === 'reset_demo') {
    createDemoSetup();
    ss.setActiveSheet(req);
    req.setActiveSelection('A1');
    return;
  }

  ui.alert(`Unknown screenshot tour action: ${action}`);
}

function ensureDemoSetupForTour_(ss) {
  const req = ss.getSheetByName(CFG.REQUESTS_SHEET);
  const audit = ss.getSheetByName(CFG.AUDIT_SHEET);
  if (!req || !audit) {
    createDemoSetup();
  }
}
