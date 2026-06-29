#!/bin/sh
# fix-traefik-routes.sh — Re-apply Traefik routes for EDGE K/U/Th Portal
#
# Problem: The custom SSL traefik (traefik-rtxj) uses a static dynamic.yml file.
# All traffic routes to the event-handler (NextAuth) which requires login.
# The upload-server container handles /edge-kuth/* forms but is unreachable
# unless traefik has explicit routes for it.
#
# This script:
# 1. Writes the correct dynamic.yml (with edge-kuth → upload-server routes)
# 2. Traefik auto-reloads the file (no restart needed)
#
# Run this on the production host if form submissions stop working
# (e.g., after `thepopebot init` or traefik container restart)

set -e

DYNAMIC_YML="/docker/traefik-rtxj/dynamic.yml"
CONTAINER_NAME="traefik-rtxj-traefik-1"

cat > /tmp/dynamic-portal-routes.yml << 'YAML'
http:
  routers:
    edge-kuth-upload:
      rule: "Host(`pbot.edgeengineers.net`) && PathPrefix(`/edge-kuth`)"
      entrypoints:
        - websecure
      tls:
        certResolver: letsencrypt
      service: edge-kuth-upload
    pope-bot:
      rule: "Host(`pbot.edgeengineers.net`) && !PathPrefix(`/edge-kuth`)"
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
          - url: "http://thepopebot-upload-server:3001"
    pope-bot:
      loadBalancer:
        passHostHeader: true
        servers:
          - url: "http://127.0.0.1:3000"
YAML

# Get upload-server container IP (in case it changed)
UPLOAD_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' thepopebot-upload-server 2>/dev/null)
if [ -z "$UPLOAD_IP" ]; then
  echo "ERROR: upload-server container not found. Start it first: docker start thepopebot-upload-server"
  exit 1
fi

# Substitute actual IP
sed -i "s|http://thepopebot-upload-server:3001|http://${UPLOAD_IP}:3001|g" /tmp/dynamic-portal-routes.yml

# Write to traefik config location
cp /tmp/dynamic-portal-routes.yml "$DYNAMIC_YML"

echo "[fix-traefik-routes] Written to $DYNAMIC_YML"
echo "[fix-traefik-routes] Upload-server target: http://${UPLOAD_IP}:3001"
echo "[fix-traefik-routes] Traefik will auto-reload within a few seconds"

# Verify
sleep 3
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST https://pbot.edgeengineers.net/edge-kuth/upload -F "form_step=project_setup" -F "name=verify" -F "email=v@v.com" -F "project_name=route_verify")
if [ "$STATUS" = "200" ]; then
  echo "[fix-traefik-routes] OK — form submission returns HTTP $STATUS"
else
  echo "[fix-traefik-routes] WARNING — form submission returns HTTP $STATUS (expected 200)"
fi
