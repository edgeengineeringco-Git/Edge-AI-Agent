/**
 * Gamma / Flight-Log Join Portal — Google Apps Script Backend (v4)
 *
 * Serverless receiver for the Gamma/Flight-Log Join upload page.
 * NO Docker, NO server — runs entirely on Google's infrastructure.
 *
 * Architecture (same as edge-kuth-portal):
 *   1. Form posts files as base64 to this GAS backend
 *   2. GAS saves input files to a TEMPORARY _pending folder in Drive
 *   3. GAS calls /api/create-agent-job with x-api-key (bypasses auth)
 *   4. Agent downloads inputs, processes, uploads ONLY outputs, deletes _pending
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
 *   6. Set API_KEY below to match your .env UPLOAD_API_KEY
 * ═══════════════════════════════════════════════════════════════════════════
 */

var CONFIG = {
  // Main project Drive folder — outputs go here, inputs go to _pending (temporary).
  TARGET_FOLDER_ID: '18fSXEOVp8D039BUXWMiYrPuIeIXOxgt3',

  // thepopebot API endpoint for creating agent jobs (same as edge-kuth-portal uses)
  API_URL: 'https://pbot.edgeengineers.net/api/create-agent-job',

  // API key for authentication (AGENT_JOB_TOKEN from .env)
  API_KEY: 'tpb_3cb2a23a075a917f69b344f7d9aa34cb2879e05716cdfec027ea06036270961b',

  // Agent's Drive email — GAS shares _pending folders with this account
  AGENT_DRIVE_EMAIL: 'edgeengineering.co@gmail.com',

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

  var pendingFolders = parentFolder.getFoldersByName('_pending');
  var pendingContainer = pendingFolders.hasNext() ? pendingFolders.next() : parentFolder.createFolder('_pending');

  var tempFolder = pendingContainer.createFolder(jobId);

  // Share the temp folder with the agent's Drive account so it can download files
  if (CONFIG.AGENT_DRIVE_EMAIL) {
    tempFolder.addEditor(CONFIG.AGENT_DRIVE_EMAIL);
  }

  var uploaded = [];
  [spectro, flight].forEach(function (f) {
    var bytes = Utilities.base64Decode(f.data);
    var blob = Utilities.newBlob(bytes, f.mimeType || 'application/octet-stream', f.filename);
    var driveFile = tempFolder.createFile(blob);
    uploaded.push({ name: driveFile.getName(), size: bytes.length });
  });

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

  // ── Create agent job via /api/create-agent-job (same as edge-kuth-portal) ──
  var agentResult = createAgentJob(jobId, projectName, fields, spectro.filename, flight.filename, tempFolder.getId());

  // ── Telegram notify (fire-and-forget) ──
  sendTelegram(jobId, projectName, fields, agentResult.ok);

  if (agentResult.ok) {
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
      error: 'Agent job creation failed: ' + agentResult.error + '.',
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Agent Job Creation (same pattern as edge-kuth-portal)
// ═══════════════════════════════════════════════════════════════════════════

function createAgentJob(jobId, projectName, fields, spectroFilename, flightFilename, pendingFolderId) {
  if (!CONFIG.API_URL) {
    return { ok: false, error: 'API_URL not configured' };
  }

  try {
    var jobDesc =
      'A client submitted a gamma/flight-log join job via the web form. Process IMMEDIATELY.\n\n' +
      'Read jobs/process-join.md and execute all steps using these parameters:\n\n' +
      'job_id=' + jobId + '\n' +
      'project_name=' + projectName + '\n' +
      'client_name=' + (fields.client_name || '') + '\n' +
      'email=' + (fields.email || '') + '\n' +
      'time_tolerance=' + (parseFloat(fields.time_tolerance) || 1.0) + '\n' +
      'factory_a0=' + (parseFloat(fields.factory_a0) || 0.0) + '\n' +
      'factory_a1=' + (parseFloat(fields.factory_a1) || 0.739863) + '\n' +
      'factory_a2=' + (parseFloat(fields.factory_a2) || 0.0) + '\n' +
      'factory_a3=' + (parseFloat(fields.factory_a3) || 0.0) + '\n' +
      'spectrogram_file=' + spectroFilename + '\n' +
      'flightlog_file=' + flightFilename + '\n' +
      'pending_folder_id=' + pendingFolderId + '\n\n' +
      'The input files are in a temporary _pending Drive folder (pending_folder_id). ' +
      'Download them, run the join, upload ONLY the output files (joined CSV, calibration.txt, summary.json) ' +
      'to a new job folder in the main project Drive, then delete the entire _pending folder. ' +
      'Do not ask for input — execute all steps autonomously.';

    var payload = {
      agent_job: jobDesc,
      scope: 'agents/gamma-flight-join',
      // No agent_backend or llm_model — use the instance defaults
      // (configured in thepopebot admin UI under CODING_AGENT)
    };

    var headers = {
      'Content-Type': 'application/json',
    };
    if (CONFIG.API_KEY) {
      headers['x-api-key'] = CONFIG.API_KEY;
    }

    var resp = UrlFetchApp.fetch(CONFIG.API_URL, {
      method: 'post',
      headers: headers,
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
