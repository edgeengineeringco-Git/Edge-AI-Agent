#!/usr/bin/env node
/**
 * Gamma–Flight Join Portal — Multipart Upload Receiver
 *
 * A lightweight Node.js HTTP endpoint that:
 *   - Serves the branded upload form (index.html + assets) for the portal.
 *   - Receives the client's multipart POST with one spectrogram (.txt) and one
 *     Airdata flight log (.csv), saves them into a per-job directory, and
 *     triggers the scoped agent (agents/gamma-flight-join) for processing.
 *
 * Uses ONLY Node.js built-in modules — zero npm dependencies.
 *
 * Usage:  node agents/gamma-flight-join/scripts/upload-server.mjs
 *
 * Environment:
 *   PORT                  — listen port (default: 3002)
 *   APP_HOSTNAME          — thepopebot host for agent trigger (default: event-handler)
 *   CREATE_AGENT_JOB_URL  — override full create-agent-job URL
 *   UPLOAD_API_KEY        — optional x-api-key for the create-agent-job call
 *   UPLOAD_PASSWORD       — access password required on the form (default: Edge12345)
 *   JOBS_DIR              — where to write per-job dirs (default: <repo>/data/gamma-flight-join/jobs)
 *   MAX_UPLOAD_BYTES      — max request body size (default: 209715200 = 200 MB)
 */

import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// scripts/ -> gamma-flight-join/ -> agents/ -> repo root
const REPO_ROOT = path.resolve(__dirname, "..", "..", "..");
const WEB_DIR = path.resolve(__dirname, "..", "web");

const PORT = parseInt(process.env.PORT || "3002", 10);
const JOBS_DIR =
  process.env.JOBS_DIR || path.join(REPO_ROOT, "data", "gamma-flight-join", "jobs");
const UPLOAD_PASSWORD = process.env.UPLOAD_PASSWORD || "Edge12345";
const MAX_UPLOAD_BYTES = parseInt(process.env.MAX_UPLOAD_BYTES || "209715200", 10);

fs.mkdirSync(JOBS_DIR, { recursive: true });

// ── Multipart/form-data parser (zero-dependency) ──────────────────────────

function parseMultipart(buffer, boundary) {
  const parts = [];
  const delimiter = `--${boundary}`;
  const delimiterBuf = Buffer.from(delimiter);

  let start = 0;
  while (start < buffer.length) {
    const delimStart = buffer.indexOf(delimiterBuf, start);
    if (delimStart === -1) break;

    let partStart = delimStart + delimiterBuf.length;
    if (buffer[partStart] === 0x0d && buffer[partStart + 1] === 0x0a) partStart += 2;
    if (buffer[partStart] === 0x0d && buffer[partStart + 1] === 0x0a) partStart += 2;

    const nextDelim = buffer.indexOf(Buffer.from(`\r\n${delimiter}`), partStart);
    if (nextDelim === -1) break;

    let partEnd = nextDelim;
    if (buffer[partEnd - 2] === 0x0d && buffer[partEnd - 1] === 0x0a) partEnd -= 2;

    const rawPart = buffer.subarray(partStart, partEnd);
    if (rawPart.length === 0) break;

    const headerEnd = rawPart.indexOf("\r\n\r\n");
    if (headerEnd === -1) {
      start = nextDelim + 2;
      continue;
    }

    const headerBlock = rawPart.subarray(0, headerEnd).toString("utf-8");
    const body = rawPart.subarray(headerEnd + 4);

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

    start = nextDelim + 2;
  }
  return parts;
}

// ── Static form serving ─────────────────────────────────────────────────────

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
};

function serveStatic(req, res) {
  let urlPath = decodeURIComponent((req.url || "").split("?")[0]);
  if (
    urlPath === "/" ||
    urlPath === "/gamma-join" ||
    urlPath === "/gamma-join/" ||
    urlPath === "/gamma-join/upload-page"
  ) {
    urlPath = "/index.html";
  } else {
    // strip the routing prefix so /gamma-join/style.css maps to WEB_DIR/style.css
    urlPath = urlPath.replace(/^\/gamma-join\/?/, "/");
  }

  const safePath = path.normalize(path.join(WEB_DIR, urlPath));
  if (!safePath.startsWith(WEB_DIR)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }
  fs.readFile(safePath, (err, data) => {
    if (err) {
      res.writeHead(404, { "Content-Type": "text/plain" });
      res.end("Not found");
      return;
    }
    const ext = path.extname(safePath).toLowerCase();
    res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
    res.end(data);
  });
}

// ── Trigger the scoped agent via create-agent-job ────────────────────────────

async function triggerAgent(metadata) {
  const createJobUrl =
    process.env.CREATE_AGENT_JOB_URL ||
    `http://${process.env.APP_HOSTNAME || "event-handler"}/api/create-agent-job`;
  const apiKey = process.env.UPLOAD_API_KEY || "";

  const jobDesc = `A client submitted a job to the Gamma–Flight Join Portal. Process it immediately. Read agents/gamma-flight-join/jobs/process-join.md and execute all steps using this payload:

job_id=${metadata.job_id}
project_name=${metadata.project_name}
client_name=${metadata.client_name}
email=${metadata.email}
time_tolerance=${metadata.time_tolerance}
factory_a0=${metadata.factory_a0}
factory_a1=${metadata.factory_a1}
factory_a2=${metadata.factory_a2}
factory_a3=${metadata.factory_a3}
spectrogram_file=${metadata.spectrogram_file}
flightlog_file=${metadata.flightlog_file}

The input files are already saved to data/gamma-flight-join/jobs/${metadata.job_id}/input/ by the upload server. Do not ask for input — execute all steps autonomously.`;

  const body = JSON.stringify({
    agent_job: jobDesc,
    scope: "agents/gamma-flight-join",
    agent_backend: "claude-code",
    llm_model: "deepseek-chat",
  });
  const headers = { "Content-Type": "application/json" };
  if (apiKey) headers["x-api-key"] = apiKey;

  const response = await fetch(createJobUrl, { method: "POST", headers, body });
  console.log(`[upload] Agent job create status: ${response.status}`);
  if (response.ok) {
    const result = await response.json().catch(() => ({}));
    console.log(`[upload] Agent job id: ${result.agent_job_id} branch: ${result.branch}`);
  } else {
    const text = await response.text().catch(() => "");
    console.error(`[upload] Create job response: ${text.slice(0, 200)}`);
  }
}

// ── HTTP server ──────────────────────────────────────────────────────────────

const server = http.createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  if (req.method === "GET" || req.method === "HEAD") {
    if ((req.url || "").split("?")[0] === "/health") {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ status: "ok" }));
      return;
    }
    serveStatic(req, res);
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
    const chunks = [];
    let total = 0;
    for await (const chunk of req) {
      total += chunk.length;
      if (total > MAX_UPLOAD_BYTES) {
        res.writeHead(413, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Upload too large" }));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    }
    const buffer = Buffer.concat(chunks);
    const parts = parseMultipart(buffer, boundaryMatch[1]);

    const fields = {};
    let spectrogram = null;
    let flightlog = null;

    for (const part of parts) {
      if (part.filename) {
        const lower = part.filename.toLowerCase();
        if (lower.endsWith(".csv")) {
          flightlog = { filename: part.filename, data: part.body };
        } else if (lower.endsWith(".txt") || lower.endsWith(".spe") || lower.endsWith(".dat")) {
          spectrogram = { filename: part.filename, data: part.body };
        }
      } else if (part.name) {
        fields[part.name] = part.body.toString("utf-8").trim();
      }
    }

    if (fields.password !== UPLOAD_PASSWORD) {
      res.writeHead(403, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Invalid access password" }));
      return;
    }

    if (!spectrogram) {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Missing spectrogram file (.txt)" }));
      return;
    }
    if (!flightlog) {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Missing Airdata flight log (.csv)" }));
      return;
    }

    const ts = new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 15);
    const projectSafe = (fields.project_name || "project").replace(/[^a-zA-Z0-9_-]/g, "_");
    const jobId = `${projectSafe}_${ts}`;

    const inputDir = path.join(JOBS_DIR, jobId, "input");
    fs.mkdirSync(inputDir, { recursive: true });

    const spectroName = spectrogram.filename.replace(/[^a-zA-Z0-9._-]/g, "_");
    const flightName = flightlog.filename.replace(/[^a-zA-Z0-9._-]/g, "_");
    fs.writeFileSync(path.join(inputDir, spectroName), spectrogram.data);
    fs.writeFileSync(path.join(inputDir, flightName), flightlog.data);

    const metadata = {
      job_id: jobId,
      project_name: fields.project_name || projectSafe,
      client_name: fields.client_name || "",
      email: fields.email || "",
      time_tolerance: parseFloat(fields.time_tolerance) || 5.0,
      factory_a0: parseFloat(fields.factory_a0) || 0.0,
      factory_a1: parseFloat(fields.factory_a1) || 0.739863,
      factory_a2: parseFloat(fields.factory_a2) || 0.0,
      factory_a3: parseFloat(fields.factory_a3) || 0.0,
      spectrogram_file: spectroName,
      flightlog_file: flightName,
      timestamp: new Date().toISOString(),
    };
    fs.writeFileSync(
      path.join(JOBS_DIR, jobId, "webhook-payload.json"),
      JSON.stringify(metadata, null, 2),
    );

    console.log(
      `[upload] Job ${jobId}: spectrogram=${spectroName} flightlog=${flightName} project=${metadata.project_name}`,
    );

    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(
      JSON.stringify({
        status: "received",
        job_id: jobId,
        message: `Job ${jobId} received. Your joined CSV and calibration metadata will be delivered to a "${jobId}" folder in Google Drive and announced via Telegram.`,
      }),
    );

    // Fire-and-forget agent trigger
    triggerAgent(metadata).catch((err) =>
      console.error(`[upload] Trigger agent failed: ${err.message}`),
    );
  } catch (err) {
    console.error(`[upload] Error: ${err.message}`);
    res.writeHead(500, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: err.message }));
  }
});

server.listen(PORT, () => {
  console.log(`[upload] Gamma–Flight Join upload receiver on port ${PORT}`);
  console.log(`[upload] Jobs dir: ${JOBS_DIR}`);
  console.log(`[upload] Web dir:  ${WEB_DIR}`);
});

process.on("SIGINT", () => {
  console.log("\n[upload] Shutting down");
  server.close();
  process.exit(0);
});
process.on("SIGTERM", () => {
  server.close();
  process.exit(0);
});
