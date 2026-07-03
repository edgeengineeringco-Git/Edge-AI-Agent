/**
 * EDGE Intake Portal — Google Apps Script Backend
 *
 * Receives JSON+base64 form submissions from the intake portal HTML forms
 * and saves them to Google Drive + logs to a Google Sheet.
 *
 * Setup:
 *   1. Create a new Google Apps Script project: https://script.google.com
 *   2. Paste this entire file into the default Code.gs
 *   3. Set CONFIG values below (TARGET_FOLDER_ID, SHEET_ID, NOTIFY_EMAIL)
 *   4. Deploy → New deployment → Web app → Execute as: Me → Access: Anyone
 *   5. Copy the deployment URL and paste it into GAS_URL in both HTML files
 */

// ═══════════════════════════════════════════════════════════════════════════
// CONFIG — replace these with your actual IDs
// ═══════════════════════════════════════════════════════════════════════════

var CONFIG = {
  // Google Drive folder ID where submission sub-folders will be created
  TARGET_FOLDER_ID: '1iqhbAZOqb1G-vV8658Ih2bqXzyeU4puO',

  // Google Sheet ID for the submission log
  SHEET_ID: '1YkQyyYkaLQUmauiGMVYpfxEauSI17t4l',

  // Sheet tab name (will be created if it doesn't exist)
  SHEET_TAB_NAME: 'Submissions',

  // Email address for new-submission alerts (leave empty to disable)
  NOTIFY_EMAIL: '',
};

// ═══════════════════════════════════════════════════════════════════════════
// Entry Points
// ═══════════════════════════════════════════════════════════════════════════

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var result = processSubmission(data);
    return outputJSON(result);
  } catch (err) {
    Logger.log('doPost error: ' + err + '\nStack: ' + err.stack);
    return outputJSON({ ok: false, error: err.toString() });
  }
}

function doOptions(e) {
  return outputJSON({ ok: true });
}

// ═══════════════════════════════════════════════════════════════════════════
// Core Processing
// ═══════════════════════════════════════════════════════════════════════════

function processSubmission(data) {
  var fields = data.fields || {};
  var files = data.files || [];
  var formType = data.form_type || 'unknown';
  var ts = new Date();
  var tsStr = Utilities.formatDate(ts, 'GMT', 'yyyyMMdd_HHmmss');

  var projectName = fields.project_name || fields.project || fields.contact_name || ('Submission ' + tsStr);
  var safeName = projectName.replace(/[^a-zA-Z0-9 _-]/g, '').substring(0, 40).trim();
  var folderName = tsStr + ' — ' + safeName + ' (' + formType + ')';

  // ── Create Drive sub-folder ──
  var parentFolder = DriveApp.getFolderById(CONFIG.TARGET_FOLDER_ID);
  var subFolder = parentFolder.createFolder(folderName);

  // ── Save files ──
  var uploadedFiles = [];
  for (var i = 0; i < files.length; i++) {
    var f = files[i];
    if (!f.data) continue;
    try {
      var byteArr = Utilities.base64Decode(f.data);
      var blob = Utilities.newBlob(
        byteArr,
        f.mimeType || 'application/octet-stream',
        f.filename || ('file_' + i)
      );
      var driveFile = subFolder.createFile(blob);
      uploadedFiles.push({
        name: driveFile.getName(),
        link: driveFile.getUrl(),
        size: byteArr.length
      });
    } catch (fileErr) {
      Logger.log('File save failed: ' + fileErr);
      uploadedFiles.push({ name: f.filename, error: fileErr.toString() });
    }
  }

  // ── Log to Sheet ──
  var sheetLink = logToSheet(formType, fields, uploadedFiles, subFolder.getUrl(), ts);

  // ── Generate HTML summary ──
  try {
    var html = generateSummaryHtml(fields, uploadedFiles, ts, projectName, subFolder.getUrl());
    subFolder.createFile(Utilities.newBlob(html, 'text/html; charset=utf-8', 'submission-summary.html'));
  } catch (htmlErr) {
    Logger.log('HTML summary failed: ' + htmlErr);
  }

  // ── Email notification ──
  try {
    var recipient = CONFIG.NOTIFY_EMAIL;
    if (!recipient) {
      try { recipient = Session.getActiveUser().getEmail(); } catch (e) {}
    }
    if (recipient && recipient.indexOf('@') > 0) {
      MailApp.sendEmail({
        to: recipient,
        subject: 'EDGE Portal — New submission: ' + projectName,
        htmlBody:
          '<h2 style="color:#1b4332">New Portal Submission</h2>' +
          '<table style="border-collapse:collapse;font-size:0.9rem">' +
          rowToHtml('Project', projectName) +
          rowToHtml('Form', formType) +
          rowToHtml('Contact', fields.contact_name || '') +
          rowToHtml('Email', fields.email || '') +
          rowToHtml('Files', uploadedFiles.length) +
          '</table>' +
          '<p><a href="' + subFolder.getUrl() + '" style="background:#2d6a4f;color:#fff;padding:8px 16px;border-radius:6px;text-decoration:none">OPEN DRIVE FOLDER</a></p>'
      });
    }
  } catch (mailErr) {
    Logger.log('Email notification failed: ' + mailErr);
  }

  return {
    ok: true,
    folderUrl: subFolder.getUrl(),
    folderId: subFolder.getId(),
    fileCount: uploadedFiles.filter(function(f) { return !f.error; }).length,
    sheetLink: sheetLink,
    timestamp: ts.toISOString()
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Sheet Logging
// ═══════════════════════════════════════════════════════════════════════════

function logToSheet(formType, fields, uploadedFiles, folderUrl, ts) {
  try {
    var ss = SpreadsheetApp.openById(CONFIG.SHEET_ID);
    var sheet = ss.getSheetByName(CONFIG.SHEET_TAB_NAME);

    if (!sheet) {
      sheet = ss.insertSheet(CONFIG.SHEET_TAB_NAME);
      var headers = [
        'Timestamp', 'Form Type', 'Project Name', 'Organisation', 'Contact Name', 'Email',
        'Area', 'Country', 'Services', 'Detector Type', 'Detector Model',
        'Start Date', 'Referral', 'File Count', 'Drive Folder', 'Notes'
      ];
      sheet.getRange(1, 1, 1, headers.length).setValues([headers])
        .setFontWeight('bold').setBackground('#2d6a4f').setFontColor('#ffffff');
      sheet.setFrozenRows(1);
    }

    var row = [
      ts.toISOString(),
      formType,
      fields.project_name || '',
      fields.organisation || '',
      fields.contact_name || '',
      fields.email || '',
      fields.calculated_area || '',
      fields.country || '',
      fields.services || '',
      fields.detector_type || '',
      fields.detector_model || '',
      fields.start_date || '',
      fields.referral || '',
      uploadedFiles.filter(function(f) { return !f.error; }).length,
      folderUrl,
      fields.additional_notes || ''
    ];
    sheet.appendRow(row);
    return ss.getUrl();
  } catch (err) {
    Logger.log('logToSheet error: ' + err);
    return '';
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// HTML Summary Generator
// ═══════════════════════════════════════════════════════════════════════════

function generateSummaryHtml(fields, files, ts, projectName, folderUrl) {
  var fileRows = '';
  for (var i = 0; i < files.length; i++) {
    var f = files[i];
    var sizeStr = '';
    if (f.size) {
      sizeStr = f.size > 1048576 ? (f.size / 1048576).toFixed(1) + ' MB'
        : (f.size > 1024 ? (f.size / 1024).toFixed(0) + ' KB' : f.size + ' B');
    }
    fileRows += '<tr>' +
      '<td style="padding:8px 16px;border-bottom:1px solid #eaecf0;font-size:0.88rem">' +
        (f.link ? '<a href="' + f.link + '">' + escapeHtml(f.name) + '</a>' : escapeHtml(f.name)) +
      '</td>' +
      '<td style="padding:8px 16px;border-bottom:1px solid #eaecf0;font-size:0.88rem;color:#667085">' +
        (f.error ? '<span style="color:#b42318">Failed</span>' : sizeStr) +
      '</td></tr>';
  }

  function field(label, value) {
    return '<div style="margin-bottom:10px">' +
      '<div style="font-size:0.75rem;color:#667085;text-transform:uppercase;letter-spacing:0.05em;font-weight:600">' + escapeHtml(label) + '</div>' +
      '<div style="font-size:0.92rem;color:#101828;margin-top:2px">' + escapeHtml(value || '—') + '</div>' +
    '</div>';
  }

  return '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<title>EDGE Portal — ' + escapeHtml(projectName) + '</title>' +
    '<style>*{box-sizing:border-box}body{margin:0;font-family:Inter,Segoe UI,sans-serif;background:#f9fafb;color:#101828;line-height:1.6}' +
    '.header{background:linear-gradient(135deg,#1b4332 0%,#1e3a5f 100%);color:#fff;padding:32px 24px}' +
    '.header h1{margin:0;font-weight:700;font-size:1.4rem}.header p{margin:4px 0 0;opacity:0.8;font-size:0.9rem}' +
    'main{max-width:760px;margin:0 auto;padding:24px 16px 60px}' +
    '.card{background:#fff;border:1px solid #d0d5dd;border-radius:12px;box-shadow:0 1px 3px rgba(16,24,40,.08);padding:20px 24px;margin-bottom:16px}' +
    '.card h2{margin:0 0 14px;font-size:1.05rem;font-weight:600;color:#2d6a4f}' +
    'table{width:100%;border-collapse:collapse}' +
    'th{text-align:left;padding:8px 16px;font-size:0.75rem;color:#667085;text-transform:uppercase;letter-spacing:0.05em;border-bottom:2px solid #2d6a4f}' +
    '.footer{text-align:center;font-size:0.8rem;color:#667085;margin-top:32px;padding-top:16px;border-top:1px solid #eaecf0}' +
    '</style></head><body>' +
    '<div class="header"><h1>' + escapeHtml(projectName) + '</h1>' +
    '<p>' + escapeHtml(fields.organisation || '') + ' &middot; ' + ts.toISOString() + '</p>' +
    '<p><a href="' + folderUrl + '" style="color:#d8f3dc">View Drive Folder</a></p></div>' +
    '<main>' +
    '<div class="card"><h2>Contact</h2>' +
      field('Name', fields.contact_name) +
      field('Email', fields.email) +
      field('Organisation', fields.organisation) +
      field('Description', fields.project_description) + '</div>' +
    '<div class="card"><h2>Area of Interest</h2>' +
      field('Calculated Area', fields.calculated_area) +
      field('Country / Region', fields.country) + '</div>' +
    (files.length > 0 ? '<div class="card"><h2>Uploaded Files (' + files.length + ')</h2>' +
      '<table><thead><tr><th>File</th><th>Size</th></tr></thead><tbody>' + fileRows + '</tbody></table></div>' : '') +
    (fields.additional_notes ? '<div class="card"><h2>Additional Notes</h2>' +
      '<p style="white-space:pre-wrap;margin:0;font-size:0.9rem">' + escapeHtml(fields.additional_notes) + '</p></div>' : '') +
    '<div class="footer">EDGE GeoIntelligence &middot; Processed ' + ts.toISOString() + '</div>' +
    '</main></body></html>';
}

// ═══════════════════════════════════════════════════════════════════════════
// Utilities
// ═══════════════════════════════════════════════════════════════════════════

function outputJSON(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function rowToHtml(label, val) {
  return '<tr><td style="padding:4px 12px 4px 0;font-weight:600;color:#666">' + escapeHtml(label) + '</td>' +
    '<td style="padding:4px 0">' + escapeHtml(String(val)) + '</td></tr>';
}
