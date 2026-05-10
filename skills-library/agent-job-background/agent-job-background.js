#!/usr/bin/env node

const apiKey = process.env.AGENT_JOB_TOKEN;
const appUrl = process.env.APP_URL;

const args = process.argv.slice(2);
const [subcommand, ...rest] = args;

function usage() {
  console.error('Usage:');
  console.error('  agent-job-background create <description> [--llm-model M] [--agent-backend B] [--scope S]');
  console.error('  agent-job-background status [agent_job_id]');
  process.exit(1);
}

function requireAuth() {
  if (!apiKey) { console.error('AGENT_JOB_TOKEN not available'); process.exit(1); }
  if (!appUrl) { console.error('APP_URL not available'); process.exit(1); }
}

async function httpJson(method, path, body) {
  const url = `${appUrl}${path}`;
  const opts = { method, headers: { 'x-api-key': apiKey } };
  if (body !== undefined) {
    opts.headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(url, opts);
  if (!res.ok) {
    const text = await res.text();
    console.error(`${method} ${url} → ${res.status} ${text}`);
    process.exit(1);
  }
  return res.json();
}

if (!subcommand) usage();
requireAuth();

if (subcommand === 'create') {
  let description = null;
  const opts = {};
  let scopeExplicit = false;
  for (let i = 0; i < rest.length; i++) {
    const arg = rest[i];
    if (arg === '--llm-model') opts.llm_model = rest[++i];
    else if (arg === '--agent-backend') opts.agent_backend = rest[++i];
    else if (arg === '--scope') { opts.scope = rest[++i]; scopeExplicit = true; }
    else if (description === null) description = arg;
    else { console.error(`Unexpected arg: ${arg}`); usage(); }
  }
  if (!description) { console.error('Missing job description'); usage(); }

  if (!scopeExplicit && process.env.SCOPE) {
    opts.scope = process.env.SCOPE;
  }

  const body = { agent_job: description };
  if (opts.llm_model) body.llm_model = opts.llm_model;
  if (opts.agent_backend) body.agent_backend = opts.agent_backend;
  if (opts.scope) body.scope = opts.scope;
  if (process.env.USER_ID) body.user_id = process.env.USER_ID;

  const json = await httpJson('POST', '/api/create-agent-job', body);
  console.log(JSON.stringify(json, null, 2));
  process.exit(0);
}

if (subcommand === 'status') {
  const agentJobId = rest[0];
  const qs = agentJobId ? `?agent_job_id=${encodeURIComponent(agentJobId)}` : '';
  const json = await httpJson('GET', `/api/agent-jobs/status${qs}`);
  console.log(JSON.stringify(json, null, 2));
  process.exit(0);
}

console.error(`Unknown subcommand: ${subcommand}`);
usage();
