/**
 * Gamma / Flight-Log Join Portal — Google Apps Script Backend
 *
 * Serverless receiver for the Gamma/Flight-Log Join upload page.
 * NO Docker, NO server — runs entirely on Google's infrastructure.
 *
 * Receives a JSON+base64 submission (one gamma spectrogram .txt + one Airdata
 * flight-log .csv), creates a per-job subfolder inside the project Drive
 * folder, saves both files, and (optionally) notifies Telegram.
 *
 * ═══════════════════════════════════════════════════════════════════════════
 * SETUP (one-time, 2 minutes — identical to the intake portal backend):
 *   1. Go to https://script.google.com → New project
 *   2. Delete the default code, paste this entire file
 *   3. Deploy → New deployment → Web app
 *      - Execute as: Me
 *      - Who has access: Anyone
 *   4. Authorize when Google asks (needs Drive access)
 *   5. Copy the Web App URL and paste it into GAS_URL in gamma-flight-join/index.html
 * ═══════════════════════════════════════════════════════════════════════════
 */

var CONFIG = {
  // The user's gamma project Drive folder — every job gets a subfolder here.
  TARGET_FOLDER_ID: '18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3',

  // Shared access password required on the form (change for production).
  ACCESS_PASSWORD: 'Edge12345',

  // Telegram notifications (leave token empty to disable).
  TELEGRAM_BOT_TOKEN: '8997616081:AAGAIusYm98JuLx59n1XIt4Xc2ThhgmNcsc',
  TELEGRAM_CHAT_ID: '466297056',
};

// ═══════════════════════════════════════════════════════════════════════════
// Entry Points
// ═══════════════════════════════════════════════════════════════════════════

function doGet(e) {
  return outputJSON({
    ok: true,
    service: 'Gamma / Flight-Log Join Portal',
    folderId: CONFIG.TARGET_FOLDER_ID,
    time: new Date().toISOString(),
  });
}

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var result = processSubmission(data);
    return outputJSON(result);
  } catch (err) {
    return outputJSON({ ok: false, error: err.toString() });
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Core
// ═══════════════════════════════════════════════════════════════════════════

function processSubmission(data) {
  var fields = data.fields || {};
  var files = data.files || [];

  // Access control
  if (CONFIG.ACCESS_PASSWORD && fields.password !== CONFIG.ACCESS_PASSWORD) {
    return { ok: false, error: 'Invalid access password' };
  }

  // Validate: exactly one spectrogram (.txt) and one flight log (.csv)
  var spectro = null, flight = null;
  for (var i = 0; i < files.length; i++) {
    var fn = (files[i].filename || '').toLowerCase();
    if (fn.match(/\.(txt|spe|dat)$/)) spectro = files[i];
    else if (fn.match(/\.csv$/)) flight = files[i];
  }
  if (!spectro) return { ok: false, error: 'Missing spectrogram file (.txt)' };
  if (!flight) return { ok: false, error: 'Missing Airdata flight log (.csv)' };

  var ts = new Date();
  var tsStr = Utilities.formatDate(ts, 'GMT', 'yyyyMMdd_HHmmss');
  var projectName = fields.project_name || 'project';
  var safeName = projectName.replace(/[^a-zA-Z0-9 _-]/g, '').substring(0, 40).trim() || 'project';
  var jobId = safeName.replace(/\s+/g, '_') + '_' + tsStr;

  // ── Per-job subfolder under the gamma project folder ──
  var parentFolder = DriveApp.getFolderById(CONFIG.TARGET_FOLDER_ID);
  var jobFolder = parentFolder.createFolder(jobId);

  // ── Save both files ──
  var uploaded = [];
  [spectro, flight].forEach(function (f) {
    var bytes = Utilities.base64Decode(f.data);
    var blob = Utilities.newBlob(bytes, f.mimeType || 'application/octet-stream', f.filename);
    var driveFile = jobFolder.createFile(blob);
    uploaded.push({ name: driveFile.getName(), link: driveFile.getUrl(), size: bytes.length });
  });

  // ── Write a job manifest so the processing agent can pick it up ──
  var manifest = {
    job_id: jobId,
    project_name: projectName,
    client_name: fields.client_name || '',
    email: fields.email || '',
    time_tolerance: parseFloat(fields.time_tolerance) || 1.0,
    factory_a0: parseFloat(fields.factory_a0) || 0.0,
    factory_a1: parseFloat(fields.factory_a1) || 0.739863,
    factory_a2: parseFloat(fields.factory_a2) || 0.0,
    factory_a3: parseFloat(fields.factory_a3) || 0.0,
    spectrogram_file: spectro.filename,
    flightlog_file: flight.filename,
    submitted_utc: ts.toISOString(),
    status: 'pending',
  };
  jobFolder.createFile(
    Utilities.newBlob(JSON.stringify(manifest, null, 2), 'application/json', 'job-manifest.json')
  );

  // ── Telegram notify (fire-and-forget) ──
  sendTelegram(jobId, projectName, fields, jobFolder.getUrl());

  return {
    ok: true,
    job_id: jobId,
    folderUrl: jobFolder.getUrl(),
    fileCount: uploaded.length,
    message:
      'Job ' + jobId + ' received. Files saved to your Google Drive folder "' + jobId +
      '". You will be notified when the joined CSV and calibration are ready.',
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════

function sendTelegram(jobId, projectName, fields, folderUrl) {
  if (!CONFIG.TELEGRAM_BOT_TOKEN) return;
  try {
    var text =
      '📡 *Gamma/Flight Join — New Job*\n\n' +
      '*Job:* ' + jobId + '\n' +
      '*Project:* ' + projectName + '\n' +
      (fields.client_name ? '*Client:* ' + fields.client_name + '\n' : '') +
      '*Drive folder:* ' + folderUrl;
    UrlFetchApp.fetch('https://api.telegram.org/bot' + CONFIG.TELEGRAM_BOT_TOKEN + '/sendMessage', {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({
        chat_id: CONFIG.TELEGRAM_CHAT_ID,
        text: text,
        parse_mode: 'Markdown',
      }),
      muteHttpExceptions: true,
    });
  } catch (e) {
    // non-fatal
  }
}

function outputJSON(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON
  );
}
