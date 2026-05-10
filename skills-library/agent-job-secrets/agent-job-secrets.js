#!/usr/bin/env node

const apiKey = process.env.AGENT_JOB_TOKEN;
const appUrl = process.env.APP_URL;

const args = process.argv.slice(2);
const [subcommand, ...rest] = args;

function usage() {
  console.error('Usage:');
  console.error('  agent-job-secrets list');
  console.error('  agent-job-secrets get <key>');
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

if (subcommand === 'list') {
  const json = await httpJson('GET', '/api/agent-job-list-secrets');
  const secrets = json.secrets;
  if (!secrets || secrets.length === 0) {
    console.log('No agent secrets configured.');
  } else {
    console.log('Available secrets:');
    secrets.forEach(s => {
      const hint = s.secretType === 'oauth2' ? '  (OAuth — use get to fetch access token)'
                 : s.secretType === 'oauth_token' ? '  (OAuth token — use get to fetch)'
                 : '';
      console.log(`  - ${s.key}${hint}`);
    });
    console.log('\nUse: agent-job-secrets get KEY_NAME');
    console.log('If a fetched value stops working, call get again for a fresh one.');
  }
  process.exit(0);
}

if (subcommand === 'get') {
  const key = rest[0];
  if (!key) { console.error('Usage: agent-job-secrets get KEY_NAME'); process.exit(1); }
  const json = await httpJson('GET', `/api/get-agent-job-secret?key=${encodeURIComponent(key)}`);
  console.log(json.value);
  process.exit(0);
}

console.error(`Unknown subcommand: ${subcommand}`);
usage();
