#!/usr/bin/env node

const apiKey = process.env.AGENT_JOB_TOKEN;
const appUrl = process.env.APP_URL;
const defaultUserId = process.env.USER_ID || null;

const args = process.argv.slice(2);
const [subcommand, ...rest] = args;

function usage() {
  console.error('Usage:');
  console.error('  agent-job-dm list');
  console.error('  agent-job-dm send <message>                      # to the originating user (USER_ID)');
  console.error('  agent-job-dm send --user-id <id> <message>       # to a specific user');
  console.error('  agent-job-dm send <message> --broadcast          # to all subscribed admins');
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
  const json = await httpJson('GET', '/api/users');
  console.log(JSON.stringify(json.users, null, 2));
  process.exit(0);
}

if (subcommand === 'send') {
  let userId = undefined;
  let broadcast = false;
  let message = null;
  for (let i = 0; i < rest.length; i++) {
    const arg = rest[i];
    if (arg === '--user-id') userId = rest[++i];
    else if (arg === '--broadcast') broadcast = true;
    else if (message === null) message = arg;
    else { console.error(`Unexpected arg: ${arg}`); usage(); }
  }
  if (!message) {
    console.error('Missing message.');
    usage();
  }
  // Recipient resolution: explicit --user-id wins. Otherwise --broadcast routes to subscribed admins.
  // Default: the originating user (USER_ID env), set when this job was created.
  const body = { message };
  if (userId !== undefined) body.user_id = userId;
  else if (!broadcast) {
    if (!defaultUserId) {
      console.error('No USER_ID in env and no --user-id/--broadcast specified. Either pass --user-id <id> or --broadcast.');
      process.exit(1);
    }
    body.user_id = defaultUserId;
  }
  const json = await httpJson('POST', '/api/send-dm', body);
  console.log(JSON.stringify(json, null, 2));
  process.exit(0);
}

console.error(`Unknown subcommand: ${subcommand}`);
usage();
