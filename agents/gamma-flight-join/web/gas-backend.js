/**
 * Gamma / Flight-Log Join Portal — Google Apps Script Backend (v3)
 *
 * Serverless receiver for the Gamma/Flight-Log Join upload page.
 * NO Docker, NO server — runs entirely on Google's infrastructure.
 *
 * v3 changes:
 *   - Input files saved to a TEMPORARY _pending folder (DELETED by agent after processing)
 *   - Only processed OUTPUT files persist in Google Drive
 *   - Processing starts IMMEDIATELY via thepopebot webhook trigger
 *
 * ═══════════════════════════════════════════════════════════════════════════
 * SETUP (one-time, 2 minutes):
 *   1. Go to https://script.google.com → New project
 *   2. Delete the default code, paste this entire file
 *   3. Deploy → New deployment → Web app
 *      - Execute as: Me
 *      - Who has access: Anyone
 *   4. Authorize when Google asks (needs Drive access)
 *   5. Copy the Web App URL and paste it into DEFAULT_ENDPOINT in index.html
 *   6. Set WEBHOOK_URL below to your thepopebot server URL (e.g. https://bot.example.com/gamma-join/upload)
 * ═══════════════════════════════════════════════════════════════════════════
 */

var CONFIG = {
  // Main project Drive folder — ONLY output files go here after processing.
  TARGET_FOLDER_ID: '18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3',

  // thepopebot webhook URL for immediate processing.
  // Set this to your thepopebot server's public URL + /gamma-join/upload
  WEBHOOK_URL: 'https://pbot.edgeengineers.net/gamma-join/upload',

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

  // ── Save inputs to a TEMPORARY _pending folder (DELETED by agent after processing) ──
  var parentFolder = DriveApp.getFolderById(CONFIG.TARGET_FOLDER_ID);

  // Get or create the _pending container folder
  var pendingFolders = parentFolder.getFoldersByName('_pending');
  var pendingContainer = pendingFolders.hasNext() ? pendingFolders.next() : parentFolder.createFolder('_pending');

  // Create per-job temp folder
  var tempFolder = pendingContainer.createFolder(jobId);

  // Save both input files to the temp folder
  var uploaded = [];
  [spectro, flight].forEach(function (f) {
    var bytes = Utilities.base64Decode(f.data);
    var blob = Utilities.newBlob(bytes, f.mimeType || 'application/octet-stream', f.filename);
    var driveFile = tempFolder.createFile(blob);
    uploaded.push({ name: driveFile.getName(), size: bytes.length });
  });

  // Write manifest to the temp folder (agent reads this to know what to process)
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
  tempFolder.createFile(
    Utilities.newBlob(JSON.stringify(manifest, null, 2), 'application/json', 'job-manifest.json')
  );

  // ── Trigger thepopebot webhook for IMMEDIATE processing ──
  var webhookResult = triggerWebhook(jobId, projectName, fields, spectro, flight, tempFolder.getId());

  // ── Telegram notify (fire-and-forget) ──
  sendTelegram(jobId, projectName, fields, webhookResult.ok);

  if (webhookResult.ok) {
    return {
      ok: true,
      job_id: jobId,
      message:
        'Job ' + jobId + ' received and processing has started. ' +
        'You will be notified when the joined CSV and calibration are ready.',
    };
  } else {
    return {
      ok: false,
      job_id: jobId,
      error: 'Webhook trigger failed: ' + webhookResult.error + '. Processing did not start.',
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Webhook Trigger
// ═══════════════════════════════════════════════════════════════════════════

function triggerWebhook(jobId, projectName, fields, spectro, flight, pendingFolderId) {
  if (!CONFIG.WEBHOOK_URL || CONFIG.WEBHOOK_URL.indexOf('PASTE_YOUR') !== -1) {
    return { ok: false, error: 'WEBHOOK_URL not configured' };
  }

  try {
    var payload = {
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
      pending_folder_id: pendingFolderId,
    };

    var resp = UrlFetchApp.fetch(CONFIG.WEBHOOK_URL, {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      muteHttpExceptions: true,
    });

    var code = resp.getResponseCode();
    if (code >= 200 && code < 300) {
      return { ok: true };
    } else {
      return { ok: false, error: 'HTTP ' + code + ': ' + resp.getContentText().substring(0, 200) };
    }
  } catch (e) {
    return { ok: false, error: e.toString() };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════════

function sendTelegram(jobId, projectName, fields, processingStarted) {
  if (!CONFIG.TELEGRAM_BOT_TOKEN) return;
  try {
    var status = processingStarted ? '⚡ Processing started' : '❌ Processing failed to start';
    var text =
      '📡 *Gamma/Flight Join — New Job*\n\n' +
      '*Job:* ' + jobId + '\n' +
      '*Project:* ' + projectName + '\n' +
      (fields.client_name ? '*Client:* ' + fields.client_name + '\n' : '') +
      '*Status:* ' + status;
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
