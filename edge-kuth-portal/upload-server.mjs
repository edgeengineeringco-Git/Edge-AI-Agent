#!/usr/bin/env node
/**
 * EDGE K/U/Th Portal — Multipart Upload Receiver
 *
 * A lightweight Node.js HTTP endpoint that receives the client form POST
 * with .spc files, saves them, and triggers the agent for processing.
 *
 * Uses ONLY Node.js built-in modules — zero npm dependencies.
 *
 * Usage:
 *   node edge-kuth-portal/upload-server.mjs
 *
 * Environment:
 *   PORT              — listen port (default: 3001)
 *   APP_HOSTNAME      — thepopebot host for agent trigger (default: localhost)
 *   EVENT_HANDLER_URL — override full event-handler URL
 *   UPLOAD_DIR        — where to save incoming files (default: edge-kuth-portal/incoming)
 *   JOBS_DIR          — where to write job metadata (default: edge-kuth-portal/jobs)
 *   BREVO_API_KEY    — Brevo API key for confirmation email (free, no DNS needed)
 *   SENDGRID_API_KEY — SendGrid API key (alternative to Brevo)
 *   FROM_EMAIL        — sender email address (default: noreply@edgeengineers.net)
 *   FROM_NAME         — sender display name (default: EDGE K/U/Th Portal)
 */

import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import crypto from "node:crypto";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

const PORT = parseInt(process.env.PORT || "3001", 10);
const UPLOAD_DIR = process.env.UPLOAD_DIR || path.join(__dirname, "incoming");
const JOBS_DIR = process.env.JOBS_DIR || path.join(__dirname, "jobs");

// Password — matches client form (set via env or default)
const UPLOAD_PASSWORD = process.env.UPLOAD_PASSWORD || "Edge12345";

// Ensure directories exist
fs.mkdirSync(UPLOAD_DIR, { recursive: true });

// ── Multipart/form-data parser (zero-dependency) ──────────────────────────

function parseMultipart(buffer, boundary) {
  const parts = [];
  const delimiter = `--${boundary}`;
  const delimiterBuf = Buffer.from(delimiter);
  const endDelimiter = `--${boundary}--`;

  let start = 0;
  while (start < buffer.length) {
    // Find the next delimiter
    const delimStart = buffer.indexOf(delimiterBuf, start);
    if (delimStart === -1) break;

    // Skip past the delimiter + \r\n
    let partStart = delimStart + delimiterBuf.length;
    // Skip past optional \r\n
    if (buffer[partStart] === 0x0d && buffer[partStart + 1] === 0x0a) partStart += 2;
    if (buffer[partStart] === 0x0d && buffer[partStart + 1] === 0x0a) partStart += 2;

    // Find next delimiter to get end of this part
    const nextDelim = buffer.indexOf(Buffer.from(`\r\n${delimiter}`), partStart);
    if (nextDelim === -1) break;

    let partEnd = nextDelim;
    // Trim trailing \r\n from part content
    if (buffer[partEnd - 2] === 0x0d && buffer[partEnd - 1] === 0x0a) partEnd -= 2;

    const rawPart = buffer.subarray(partStart, partEnd);
    if (rawPart.length === 0) break;

    // Parse headers and body
    const headerEnd = rawPart.indexOf("\r\n\r\n");
    if (headerEnd === -1) break;

    const headerBlock = rawPart.subarray(0, headerEnd).toString("utf-8");
    const bodyStart = headerEnd + 4;  // skip \r\n\r\n
    const body = rawPart.subarray(bodyStart);

    const headers = {};
    for (const line of headerBlock.split("\r\n")) {
      const colon = line.indexOf(":");
      if (colon === -1) continue;
      headers[line.slice(0, colon).trim().toLowerCase()] = line.slice(colon + 1).trim();
    }

    const cd = headers["content-disposition"] || "";
    const nameMatch = cd.match(/name="([^"]*)"/);
    const filenameMatch = cd.match(/filename="([^"]*)"/);

    parts.push({
      name: nameMatch ? nameMatch[1] : null,
      filename: filenameMatch ? filenameMatch[1] : null,
      contentType: headers["content-type"] || null,
      body,
    });

    start = nextDelim + 2; // skip \r\n before next delimiter
  }

  return parts;
}

// ── Email notification (Brevo or SendGrid) ──────────────────────────────────

async function sendConfirmationEmail(metadata, fileCount) {
  const apiKey = process.env.BREVO_API_KEY || process.env.SENDGRID_API_KEY;
  const provider = process.env.BREVO_API_KEY ? "brevo" : process.env.SENDGRID_API_KEY ? "sendgrid" : null;

  if (!apiKey || !provider) {
    console.log("[email] No API key (BREVO_API_KEY or SENDGRID_API_KEY) — skipping confirmation");
    return;
  }
  const to = metadata.email;
  if (!to) {
    console.log("[email] No client email — skipping confirmation");
    return;
  }

  const fromEmail = process.env.FROM_EMAIL || "edgeengineering.co@gmail.com";
  const fromName = process.env.FROM_NAME || "EDGE K/U/Th Portal";
  // NOTE: Change to info@edgeengineers.net once sender is verified in Brevo
  const project = metadata.project || metadata.client_name || "Unnamed";

  const body = `Dear Client,

Your gamma spectrum files have been received successfully by the EDGE K/U/Th Portal.

  Job ID:      ${metadata.job_id}
  Project:     ${project}
  Files:       ${fileCount} .spc file(s)

Your results CSV containing K (%), U (ppm) and Th (ppm) estimates
for all measurement points will be sent to this email automatically
once processing is complete.

Best regards,
EDGE Geointelligence`;

  try {
    if (provider === "brevo") {
      const response = await fetch("https://api.brevo.com/v3/smtp/email", {
        method: "POST",
        headers: { "api-key": apiKey, "Content-Type": "application/json" },
        body: JSON.stringify({
          sender: { name: fromName, email: fromEmail },
          to: [{ email: to }],
          subject: `EDGE K/U/Th Portal — Files Received (${metadata.job_id})`,
          textContent: body,
        }),
      });
      if (response.status === 201 || response.status === 200) {
        console.log(`[email] Confirmation sent to ${to} via Brevo`);
      } else {
        const text = await response.text();
        console.error(`[email] Brevo returned ${response.status}: ${text}`);
      }
    } else {
      // SendGrid
      const response = await fetch("https://api.sendgrid.com/v3/mail/send", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          personalizations: [{ to: [{ email: to }] }],
          from: { email: fromEmail, name: fromName },
          subject: `EDGE K/U/Th Portal — Files Received (${metadata.job_id})`,
          content: [{ type: "text/plain", value: body }],
        }),
      });
      if (response.status === 202) {
        console.log(`[email] Confirmation sent to ${to} via SendGrid`);
      } else {
        const text = await response.text();
        console.error(`[email] SendGrid returned ${response.status}: ${text}`);
      }
    }
  } catch (err) {
    console.error(`[email] Confirmation failed: ${err.message}`);
  }
}

// ── HTTP Server ───────────────────────────────────────────────────────────

const server = http.createServer(async (req, res) => {
  // CORS headers
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method !== "POST") {
    res.writeHead(405, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Method not allowed" }));
    return;
  }

  const contentType = req.headers["content-type"] || "";
  const boundaryMatch = contentType.match(/boundary=([^;]+)/);
  if (!boundaryMatch) {
    res.writeHead(400, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Expected multipart/form-data with boundary" }));
    return;
  }

  try {
    // Read the entire request body
    const chunks = [];
    for await (const chunk of req) {
      chunks.push(chunk);
    }
    const buffer = Buffer.concat(chunks);

    // Parse multipart parts
    const parts = parseMultipart(buffer, boundaryMatch[1]);

    // Extract form fields and files
    const fields = {};
    const files = [];
    let doseCsv = null;

    for (const part of parts) {
      if (part.filename) {
        // It's a file
        const entry = { field: part.name, filename: part.filename, data: part.body };
        if (part.filename.endsWith(".spc")) {
          files.push(entry);
        } else if (part.filename.endsWith(".csv")) {
          doseCsv = entry;
        }
      } else if (part.name) {
        fields[part.name] = part.body.toString("utf-8").trim();
      }
    }

    // Validate password
    if (fields.password !== UPLOAD_PASSWORD) {
      res.writeHead(403, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Invalid access password" }));
      return;
    }

    // Validate files
    if (files.length === 0) {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "No .spc files found in upload" }));
      return;
    }

    // Generate job ID
    const ts = new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 15);
    const clientSafe = (fields.project || "client").replace(/[^a-zA-Z0-9_-]/g, "_");
    const jobId = `${clientSafe}_${ts}`;

    // Create job directory
    const jobDir = path.join(JOBS_DIR, jobId, "spectra");
    fs.mkdirSync(jobDir, { recursive: true });

    // Save .spc files
    const savedFiles = [];
    for (const f of files) {
      const dest = path.join(jobDir, f.filename);
      fs.writeFileSync(dest, f.data);
      savedFiles.push(f.filename);
    }

    // Save dose CSV if provided
    if (doseCsv) {
      const doseDir = path.join(JOBS_DIR, jobId);
      fs.writeFileSync(path.join(doseDir, doseCsv.filename), doseCsv.data);
    }

    // Save metadata as JSON
    const metadata = {
      job_id: jobId,
      client_name: clientSafe,
      project: fields.project || "",
      email: fields.email || "",
      roi_half_width: parseFloat(fields.roi_half_width) || 20,
      normalize_live_time: fields.normalize_live_time === "true",
      normalize_total_counts: fields.normalize_total_counts === "true",
      measurement_id_column: fields.measurement_id_column || "measurement_id",
      spectra_files: savedFiles,
      dose_csv_file: doseCsv ? doseCsv.filename : null,
      timestamp: new Date().toISOString(),
    };

    fs.writeFileSync(
      path.join(JOBS_DIR, jobId, "webhook-payload.json"),
      JSON.stringify(metadata, null, 2),
    );

    // Also save .spc files to incoming/ as fallback (for backward compat)
    for (const f of files) {
      const dest = path.join(UPLOAD_DIR, f.filename);
      if (!fs.existsSync(dest)) {
        fs.writeFileSync(dest, f.data);
      }
    }

    console.log(`[upload] Job ${jobId}: ${savedFiles.length} files from ${fields.project || "anonymous"}`);

    // Send confirmation email (fire-and-forget, non-blocking)
    sendConfirmationEmail(metadata, savedFiles.length);

    // Respond to client
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({
      status: "received",
      job_id: jobId,
      files: savedFiles.length,
      message: `Job ${jobId} received. Processing results will be sent to ${fields.email || "the registered email"}.`,
    }));

    // Trigger agent job creation via create-agent-job API (bypasses broken trigger mechanism)
    const createJobUrl = process.env.CREATE_AGENT_JOB_URL
      || `http://${process.env.APP_HOSTNAME || "event-handler"}/api/create-agent-job`;
    const apiKey = process.env.UPLOAD_API_KEY || "";

    try {
      const jobDesc = `A client submitted a form to the EDGE K/U/Th Portal. Process the upload immediately. Read agents/edge-kuth-portal/jobs/process-spectra.md and execute all steps using the webhook payload:

job_id=${metadata.job_id}
client_name=${metadata.client_name}
email=${metadata.email}
project=${metadata.project}
roi_half_width=${metadata.roi_half_width}
normalize_live_time=${metadata.normalize_live_time}
normalize_total_counts=${metadata.normalize_total_counts}
measurement_id_column=${metadata.measurement_id_column}
spectra_files=${JSON.stringify(metadata.spectra_files)}
dose_csv_file=${metadata.dose_csv_file ?? "null"}

The .spc files are already saved to edge-kuth-portal/jobs/${metadata.job_id}/spectra/ by the upload server. Do not ask for input — execute all steps autonomously.`;

      const body = JSON.stringify({
        agent_job: jobDesc,
        scope: "agents/edge-kuth-portal",
      });
      const headers = { "Content-Type": "application/json" };
      if (apiKey) headers["x-api-key"] = apiKey;
      const response = await fetch(createJobUrl, {
        method: "POST",
        headers,
        body,
      });
      console.log(`[upload] Agent job created: ${response.status}`);
      if (response.ok) {
        const result = await response.json();
        console.log(`[upload] Agent job ID: ${result.agent_job_id} branch: ${result.branch}`);
      } else {
        const text = await response.text().catch(() => "");
        console.error(`[upload] Create job response: ${text.slice(0, 200)}`);
      }
    } catch (err) {
      console.error(`[upload] Create agent job failed: ${err.message}`);
    }

  } catch (err) {
    console.error(`[upload] Error: ${err.message}`);
    res.writeHead(500, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: err.message }));
  }
});

server.listen(PORT, () => {
  console.log(`[upload] EDGE K/U/Th upload receiver on port ${PORT}`);
  console.log(`[upload] Upload dir: ${UPLOAD_DIR}`);
});

// Handle graceful shutdown
process.on("SIGINT", () => { console.log("\n[upload] Shutting down"); server.close(); process.exit(0); });
process.on("SIGTERM", () => { server.close(); process.exit(0); });
