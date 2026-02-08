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
};

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Approvals')
    .addItem('Approve row', 'approveSelectedRow')
    .addItem('Reject row', 'rejectSelectedRow')
    .addSeparator()
    .addItem('Reset to pending', 'resetSelectedRowToPending')
    .addSeparator()
    .addItem('Create demo setup', 'createDemoSetup')
    .addSeparator()
    .addItem('Help / Docs', 'showHelpSidebar')
    .addToUi();
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
      if (status !== CFG.STATUS.APPROVED) continue;

      const requestId = ensureRequestId_(sheet, headers, r, rowObj);

      // Force back to pending + clear decision fields.
      setCellByHeader_(sheet, headers, r, 'Status', CFG.STATUS.PENDING);
      setCellByHeader_(sheet, headers, r, 'Approver', '');
      setCellByHeader_(sheet, headers, r, 'DecisionAt', '');
      setCellByHeader_(sheet, headers, r, 'DecisionNotes', `Auto: re-approval required (edited: ${editedHeaders.join(', ')})`);

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
          priorStatus: CFG.STATUS.APPROVED,
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

function approveSelectedRow() {
  decideOnSelectedRow_(CFG.STATUS.APPROVED);
}

function rejectSelectedRow() {
  decideOnSelectedRow_(CFG.STATUS.REJECTED);
}

function resetSelectedRowToPending() {
  decideOnSelectedRow_(CFG.STATUS.PENDING);
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

    const headers = getHeaders_(reqSheet);
    const rowValues = reqSheet.getRange(row, 1, 1, headers.length).getValues()[0];
    const rowObj = rowToObject_(headers, rowValues);

    const requestId = ensureRequestId_(reqSheet, headers, row, rowObj);

    const ui = SpreadsheetApp.getUi();
    const promptTitle = status === CFG.STATUS.APPROVED
      ? 'Approve request'
      : status === CFG.STATUS.REJECTED
        ? 'Reject request'
        : 'Reset to pending';

    let notes = '';
    if (status !== CFG.STATUS.PENDING) {
      const resp = ui.prompt(promptTitle, 'Optional decision notes:', ui.ButtonSet.OK_CANCEL);
      if (resp.getSelectedButton() !== ui.Button.OK) return;
      notes = (resp.getResponseText() || '').trim();
    }

    const now = new Date();
    const userEmail = getUserEmail_();

    // Write decision back to row
    setCellByHeader_(reqSheet, headers, row, 'Status', status);
    setCellByHeader_(reqSheet, headers, row, 'Approver', userEmail);
    setCellByHeader_(reqSheet, headers, row, 'DecisionAt', now);
    setCellByHeader_(reqSheet, headers, row, 'DecisionNotes', notes);

    // Refresh snapshot for audit log
    const newValues = reqSheet.getRange(row, 1, 1, headers.length).getValues()[0];
    const newObj = rowToObject_(headers, newValues);

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
  } finally {
    lock.releaseLock();
  }
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
  const headers = ['EventAt', 'Actor', 'Action', 'RequestId', 'RowNumber', 'SnapshotJSON', 'SnapshotHash'];

  if (audit.getLastRow() === 0) {
    audit.getRange(1, 1, 1, headers.length).setValues([headers]);
  } else if (audit.getLastRow() === 1) {
    // ensure headers exist
    const existing = audit.getRange(1, 1, 1, headers.length).getValues()[0];
    const needs = existing.some((v, i) => (v || '').toString().trim() !== headers[i]);
    if (needs) audit.getRange(1, 1, 1, headers.length).setValues([headers]);
  }

  audit.appendRow([
    evt.eventAt,
    evt.actor,
    evt.action,
    evt.requestId,
    evt.rowNumber,
    evt.snapshotJson,
    evt.snapshotHash,
  ]);
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
 * Demo helper: creates the required sheets, headers, and a couple example requests.
 * Safe to run multiple times; it will not overwrite existing data rows.
 */
function createDemoSetup() {
  const ss = SpreadsheetApp.getActive();

  const requestsHeaders = ['RequestId', 'Title', 'Requester', 'Status', 'Approver', 'DecisionAt', 'DecisionNotes'];
  const req = ensureSheetWithHeaders_(ss, CFG.REQUESTS_SHEET, requestsHeaders);

  // Seed a couple rows if sheet is empty (besides header).
  if (req.getLastRow() <= CFG.HEADER_ROW) {
    req.appendRow(['', 'Purchase approval: lab supplies', 'alex@example.com', CFG.STATUS.PENDING, '', '', '']);
    req.appendRow(['', 'Access request: shared drive', 'sam@example.com', CFG.STATUS.PENDING, '', '', '']);
  }

  // Ensure audit sheet exists + headers are correct.
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

  SpreadsheetApp.getUi().alert('Demo setup complete. Select a row in “Requests” and use Approvals → Approve/Reject.');
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
