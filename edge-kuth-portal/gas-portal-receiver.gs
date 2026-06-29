/**
 * EDGE Portal — Google Apps Script Web App
 *
 * Receives form submissions DIRECTLY from GitHub Pages (browser → Apps Script → Drive).
 * No server, no Docker, no auth wall, no redeploy.
 *
 * ── DEPLOY INSTRUCTIONS ───────────────────────────────────────────────────────── * 1. Go to https://script.google.com
 * 2. New Project
 * 3. Paste this entire file
 * 4. Click Deploy → New deployment → Type: Web app
 *    - Execute as: Me (your Google account)
 *    - Who has access: Anyone
 * 5. Authorize the script (needs Drive + Mail permissions)
 * 6. Copy the Web App URL and paste it into the HTML forms as the form action
 *
 * The script:
 *   - Creates a timestamped subfolder for each submission
 *   - Uploads all attached files to that folder
 *   - Appends a row to an Excel (Google Sheets) log
 *   - Generates an HTML summary page
 *   - Sends an email notification to you
 */

var SUBMISSIONS_FOLDER_ID = '1iqhbAZOqb1G-vV8658Ih2bqXzyeU4puO';
var EXCEL_NAME = 'EDGE_Portal_Submissions';
var NOTIFICATION_EMAIL = ''; // leave empty = use your own email (the script owner)

/**
 * Health check
 */
function doGet(e) {
  return jsonResponse({ ok: true, service: 'EDGE Portal GAS Receiver', time: new Date().toISOString() });
}

/**
 * Handle CORS preflight (OPTIONS) — safety net for browsers that send it
 */
function doOptions() {
  return ContentService.createTextOutput('')
    .setMimeType(ContentService.MimeType.JSON)
    .setHeader('Access-Control-Allow-Origin', '*')
    .setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
    .setHeader('Access-Control-Allow-Headers', '*');
}

/**
 * Main entry — receive form submission from browser
 *
 * The browser sends JSON with this shape:
 *   {
 *     "fields": { "contact_name": "...", "email": "...", ... },
 *     "files": [
 *       { "name": "data.csv", "mimeType": "text/csv", "data": "<base64>" },
 *       ...
 *     ]
 *   }
 *
 * We use JSON (not multipart) because Apps Script handles it natively
 * and we avoid fragile multipart parsing.
 */
function doPost(e) {
  try {
    var body = e.postData && e.postData.contents ? e.postData.contents : '{}';
    var payload = JSON.parse(body);
    var result = processSubmission(payload);
    return jsonResponse(result);
  } catch (err) {
    return jsonResponse({ ok: false, error: err.toString(), stack: err.stack });
  }
}

function processSubmission(payload) {
  var ts = new Date();
  var tsStr = Utilities.formatDate(ts, 'GMT', 'yyyyMMdd_HHmmss');

  var fields = payload.fields || {};
  var fileInfos = payload.files || [];

  var projectName = fields.project_name || fields.project || fields.contact_name || ('Submission ' + tsStr);
  var safeName = projectName.replace(/[^a-zA-Z0-9 _-]/g, '').substring(0, 40).trim();
  var subFolderName = tsStr + '_' + safeName;

  // ── Create submission subfolder ───────────────────────────────────────
  var rootFolder = DriveApp.getFolderById(SUBMISSIONS_FOLDER_ID);
  var subFolder = rootFolder.createFolder(subFolderName);
  var subFolderId = subFolder.getId();
  var subFolderUrl = subFolder.getUrl();

  // ── Upload files to Drive ────────────────────────────────────────────
  var uploadedFiles = [];
  for (var i = 0; i < fileInfos.length; i++) {
    var fi = fileInfos[i];
    try {
      var byteArr = Utilities.base64Decode(fi.data || '');
      var blob = Utilities.newBlob(
        byteArr,
        fi.mimeType || 'application/octet-stream',
        fi.name || ('file_' + i)
      );
      var file = subFolder.createFile(blob);
      uploadedFiles.push({
        name: file.getName(),
        link: file.getUrl(),
        size: byteArr.length
      });
    } catch (fileErr) {
      uploadedFiles.push({ name: fi.name, error: fileErr.toString() });
    }
  }

  // ── Update/Create Excel log (as Google Sheets) ────────────────────────
  var rowData = [
    ts.toISOString(),
    fields.contact_name || '',
    fields.email || '',
    fields.organisation || '',
    fields.project_name || '',
    fields.calculated_area || '',
    fields.country || '',
    fields.services || '',
    fields.detector_type || '',
    fields.detector_model || '',
    fields.start_date || '',
    uploadedFiles.length,
    uploadedFiles.map(function(f) { return f.name; }).join('; ').substring(0, 300),
    (fields.additional_notes || '').substring(0, 1000),
    fields.confirmation === 'confirmed' ? 'Confirmed' : 'Pending',
    subFolderUrl
  ];

  var headers = [
    'Timestamp', 'Contact Name', 'Email', 'Organisation', 'Project Name',
    'Area', 'Country', 'Services', 'Detector Type', 'Detector Model',
    'Start Date', 'File Count', 'File Names', 'Notes', 'Confirmation', 'Drive Folder'
  ];

  var excelLink = updateExcelLog(rootFolder, headers, rowData);

  // ── Generate HTML summary ────────────────────────────────────────────
  var html = generateSummaryHtml(fields, uploadedFiles, ts, projectName, subFolderUrl);
  subFolder.createFile(
    Utilities.newBlob(html, 'text/html; charset=utf-8', 'submission-summary.html')
  );

  // ── Send notification email ──────────────────────────────────────────
  try {
    var recipient = NOTIFICATION_EMAIL || Session.getActiveUser().getEmail();
    if (recipient && !recipient.match(/your-own-google-account/i)) {
      MailApp.sendEmail({
        to: recipient,
        subject: 'EDGE Portal — New submission: ' + projectName,
        htmlBody:
          '<h2 style="color:#1b4332">New Portal Submission</h2>' +
          '<table style="border-collapse:collapse;font-size:0.9rem">' +
          rowToHtml('Project', projectName) +
          rowToHtml('Contact', fields.contact_name || '') +
          rowToHtml('Email', fields.email || '') +
          rowToHtml('Time', ts.toISOString()) +
          rowToHtml('Files received', uploadedFiles.length) +
          '</table>' +
          '<p><a href="' + subFolderUrl + '" style="background:#2d6a4f;color:#fff;padding:8px 16px;border-radius:6px;text-decoration:none">OPEN DRIVE FOLDER</a></p>' +
          '<hr style="border:none;border-top:1px solid #ddd">' +
          '<pre style="background:#f5f5f5;padding:12px;border-radius:6px;font-size:0.8rem;white-space:pre-wrap">' +
          escapeHtml(JSON.stringify(fields, null, 2)) + '</pre>'
      });
    }
  } catch (mailErr) {
    // Non-fatal
  }

  return {
    ok: true,
    message: 'Submission received — ' + uploadedFiles.length + ' file(s) saved',
    folderUrl: subFolderUrl,
    folderId: subFolderId,
    fileCount: uploadedFiles.length,
    excelLink: excelLink,
    timestamp: ts.toISOString()
  };

  function rowToHtml(label, val) {
    return '<tr><td style="padding:4px 12px 4px 0;font-weight:660;color:#666">' + escapeHtml(label) + '</td>' +
      '<td style="padding:4px 0">' + escapeHtml(String(val)) + '</td></tr>';
  }
}

/**
 * Append a row to the Excel log spreadsheet (create if not exists)
 */
function updateExcelLog(folder, headers, rowData) {
  var files = folder.getFilesByName(EXCEL_NAME);

  if (files.hasNext()) {
    var file = files.next();
    try {
      var ss = SpreadsheetApp.openById(file.getId());
      var sheet = ss.getSheets()[0];
      var lastRow = sheet.getLastRow();

      // Ensure headers exist
      if (lastRow === 0) {
        sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
        sheet.getRange(1, 1, 1, headers.length)
          .setFontWeight('bold')
          .setBackground('#2d6a4f')
          .setFontColor('#ffffff');
      }

      // Append data row
      var targetRow = lastRow + 1;
      sheet.getRange(targetRow, 1, 1, rowData.length).setValues([rowData]);
      return file.getUrl();
    } catch (err) {
      // Will create new below
    }
  }

  // Create new spreadsheet
  var ss = SpreadsheetApp.create(EXCEL_NAME);
  var sheet = ss.getSheets()[0];

  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length)
    .setFontWeight('bold')
    .setBackground('#2d6a4f')
    .setFontColor('#ffffff');
  sheet.getRange(2, 1, 1, rowData.length).setValues([rowData]);

  // Move from root into the submissions folder
  var driveFile = DriveApp.getFileById(ss.getId());
  folder.addFile(driveFile);
  DriveApp.getRootFolder().removeFile(driveFile);

  return driveFile.getUrl();
}

/**
 * Generate an HTML summary of the submission
 */
function generateSummaryHtml(fields, files, ts, projectName, folderUrl) {
  var fileRows = '';
  for (var i = 0; i < files.length; i++) {
    var f = files[i];
    var size = f.size || 0;
    var sizeStr = size > 1048576
      ? (size / 1048576).toFixed(1) + ' MB'
      : (size > 1024 ? (size / 1024).toFixed(0) + ' KB' : size + ' B');
    fileRows += '<tr>' +
      '<td style="padding:8px 16px;border-bottom:1px solid #eaecf0;font-size:0.88rem">' +
        (f.link ? '<a href="' + f.link + '">' + escapeHtml(f.name) + '</a>' : escapeHtml(f.name)) +
      '</td>' +
      '<td style="padding:8px 16px;border-bottom:1px solid #eaecf0;font-size:0.88rem;color:#667085">' +
        (f.error ? '<span style="color:#b42318">Failed: ' + escapeHtml(f.error) + '</span>' : sizeStr) +
      '</td>' +
    '</tr>';
  }

  function field(label, value) {
    return '<div style="margin-bottom:10px">' +
      '<div style="font-size:0.75rem;color:#667085;text-transform:uppercase;letter-spacing:0.05em;font-weight:600">' +
        escapeHtml(label) + '</div>' +
      '<div style="font-size:0.92rem;color:#101828;margin-top:2px">' + escapeHtml(value || '—') + '</div>' +
    '</div>';
  }

  return '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<title>EDGE Portal — ' + escapeHtml(projectName) + '</title>' +
    '<style>*{box-sizing:border-box}body{margin:0;font-family:Inter,Segoe UI,sans-serif;' +
    'background:#f9fafb;color:#101828;line-height:1.6}' +
    '.header{background:linear-gradient(135deg,#1b4332 0%,#1e3a5f 100%);color:#fff;padding:32px 24px}' +
    '.header h1{margin:0;font-weight:700;font-size:1.4rem}' +
    '.header p{margin:4px 0 0;opacity:0.8;font-size:0.9rem}' +
    'main{max-width:760px;margin:0 auto;padding:24px 16px 60px}' +
    '.card{background:#fff;border:1px solid #d0d5dd;border-radius:12px;' +
    'box-shadow:0 1px 3px rgba(16,24,40,.08);padding:20px 24px;margin-bottom:16px}' +
    '.card h2{margin:0 0 14px;font-size:1.05rem;font-weight:600;color:#2d6a4f}' +
    'table{width:100%;border-collapse:collapse}' +
    'th{text-align:left;padding:8px 16px;font-size:0.75rem;color:#667085;text-transform:uppercase;' +
    'letter-spacing:0.05em;border-bottom:2px solid #2d6a4f}' +
    '.badge{display:inline-block;padding:2px 10px;border-radius:100px;font-size:0.78rem;font-weight:600}' +
    '.badge-green{background:#d8f3dc;color:#1b4332}' +
    '.footer{text-align:center;font-size:0.8rem;color:#667085;margin-top:32px;' +
    'padding-top:16px;border-top:1px solid #eaecf0}' +
    '</style></head><body>' +
    '<div class="header">' +
      '<h1>' + escapeHtml(projectName) + '</h1>' +
      '<p>' + escapeHtml(fields.organisation || '') + ' &middot; ' + ts.toISOString() + '</p>' +
      '<p><a href="' + folderUrl + '" style="color:#d8f3dc">View Drive Folder</a></p>' +
    '</div>' +
    '<main>' +
      '<div class="card"><h2>Contact</h2>' +
        field('Name', fields.contact_name) +
        field('Email', fields.email) +
        field('Organisation', fields.organisation) +
        field('Description', fields.project_description) +
      '</div>' +
      '<div class="card"><h2>Area of Interest</h2>' +
        field('Calculated Area', fields.calculated_area) +
        field('Country / Region', fields.country) +
      '</div>' +
      (files.length > 0 ? '<div class="card"><h2>Uploaded Files (' + files.length + ')</h2>' +
        '<table><thead><tr><th>File</th><th>Size</th></tr></thead><tbody>' +
        fileRows + '</tbody></table></div>' : '') +
      (fields.additional_notes ? '<div class="card"><h2>Additional Notes</h2>' +
        '<p style="white-space:pre-wrap;margin:0;font-size:0.9rem">' +
          escapeHtml(fields.additional_notes) + '</p></div>' : '') +
      '<div class="footer">EDGE GeoIntelligence &middot; Processed ' + ts.toISOString() + '</div>' +
    '</main></body></html>';
}

// ── Helpers ──────────────────────────────────────────────────────────────────────

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function escapeHtml(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
