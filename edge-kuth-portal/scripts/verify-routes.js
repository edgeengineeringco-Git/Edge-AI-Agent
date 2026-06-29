#!/usr/bin/env node
/**
 * verify-routes.js — Check that /edge-kuth/* routes reach the upload-server
 *
 * Run from inside the event-handler container (has docker socket access):
 *   node verify-routes.js
 *
 * Exits 0 if routes are correct, 1 if broken (for use in cron/heartbeat).
 *
 * The event-handler container has /var/run/docker.sock mounted.
 * We use the Docker API to write dynamic.yml if needed.
 */

import http from 'node:http';
import { execSync } from 'node:child_process';

const DOCKER_SOCK = '/var/run/docker.sock';
const TRAEFIK = { name: 'traefik-rtxj-traefik-1', configPath: '/etc/traefik/dynamic.yml' };
const UPLOAD_SERVER = 'thepopebot-upload-server';

// ── Docker API helpers ────────────────────────────────────────────────────────

function dockerReq(method, path, body) {
  return new Promise((resolve, reject) => {
    const opts = {
      socketPath: DOCKER_SOCK,
      path: `/v1.41${path}`,
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    const r = http.request(opts, (res) => {
      let data = '';
      res.on('data', (c) => (data += c));
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    r.on('error', reject);
    if (body) r.write(JSON.stringify(body));
    r.end();
  });
}

// ── Main ────────────────────────────────────────────────────────────────────

async function main() {
  // 1. Probe production URL
  const probe = await fetch('https://pbot.edgeengineers.net/edge-kuth/upload', {
    method: 'POST',
    body: (() => {
      const fd = new FormData();
      fd.append('form_step', 'project_setup');
      fd.append('name', 'route-check');
      fd.append('email', 'check@internal');
      fd.append('project_name', 'route_check');
      return fd;
    })(),
  }).catch(() => null);

  if (probe && probe.status === 200) {
    const json = await probe.json();
    if (json.status === 'submitted') {
      console.log('[verify-routes] OK — /edge-kuth/upload routes correctly');
      process.exit(0);
    }
  }

  console.log(`[verify-routes] BROKEN — probe returned ${probe ? probe.status : 'no response'}`);
  console.log('[verify-routes] Re-applying traefik routes...');

  // 2. Get upload-server IP
  const infoRes = await dockerReq('GET', `/containers/${UPLOAD_SERVER}/json`);
  if (infoRes.status !== 200) {
    console.error('[verify-routes] upload-server container not found');
    process.exit(1);
  }
  const info = JSON.parse(infoRes.body);
  const ip = Object.values(info.NetworkSettings?.Networks || {})[0]?.IPAddress;
  if (!ip) {
    console.error('[verify-routes] upload-server has no IP');
    process.exit(1);
  }
  console.log(`[verify-routes] upload-server IP: ${ip}`);

  // 3. Write dynamic.yml via archive API
  const config = `http:
  routers:
    edge-kuth-upload:
      rule: "Host(\`pbot.edgeengineers.net\`) && PathPrefix(\`/edge-kuth/upload-page\`, \`/edge-kuth/upload\`, \`/edge-kuth/upload-form\`, \`/edge-kuth/data-upload\`)"
      entrypoints:
        - websecure
      tls:
        certResolver: letsencrypt
      service: edge-kuth-upload
    pope-bot:
      rule: "Host(\`pbot.edgeengineers.net\`)"
      entrypoints:
        - websecure
      tls:
        certResolver: letsencrypt
      middlewares:
        - secure-headers
      service: pope-bot
  middlewares:
    secure-headers:
      headers:
        customRequestHeaders:
          X-Forwarded-Proto: "https"
          X-Forwarded-Host: "pbot.edgeengineers.net"
  services:
    edge-kuth-upload:
      loadBalancer:
        passHostHeader: true
        servers:
          - url: "http://${ip}:3001"
    pope-bot:
      loadBalancer:
        passHostHeader: true
        servers:
          - url: "http://127.0.0.1:3000"
`;

  // Use privileged container to write to host filesystem
  const tar = execSync(`printf '%s' ${JSON.stringify(config)} | tar cf /tmp/routestar -C /tmp/ dynamic.yml 2>/dev/null`, { encoding: 'utf8' }).trim();

  // Create temp container with host mount
  const createRes = await dockerReq('POST', '/containers/create?name=route-fixer-temp', {
    Image: 'node:22-alpine',
    Cmd: ['sh', '-c', `cat > /host/docker/traefik-rtxj/dynamic.yml << 'EOF'\n${config}\nEOF\necho done`],
    HostConfig: { Binds: ['/:/host:rw'], Privileged: true, AutoRemove: true },
  });

  if (createRes.status !== 201) {
    console.error('[verify-routes] Failed to create temp container:', createRes.body);
    process.exit(1);
  }

  const containerId = JSON.parse(createRes.body).Id;
  await dockerReq('POST', `/containers/${containerId}/start`);
  await new Promise((r) => setTimeout(r, 5000));

  // 4. Re-probe
  const probe2 = await fetch('https://pbot.edgeengineers.net/edge-kuth/upload', {
    method: 'POST',
    body: (() => {
      const fd = new FormData();
      fd.append('form_step', 'project_setup');
      fd.append('name', 'route-check-2');
      fd.append('email', 'check2@internal');
      fd.append('project_name', 'route_check_2');
      return fd;
    })(),
  }).catch(() => null);

  if (probe2 && probe2.status === 200) {
    console.log('[verify-routes] FIXED — routes re-applied successfully');
    process.exit(0);
  } else {
    console.error('[verify-routes] Still broken after fix attempt');
    process.exit(1);
  }
}

main().catch((e) => {
  console.error('[verify-routes] Error:', e.message);
  process.exit(1);
});
