#!/bin/bash
# Fix popebot voice input (microphone button)
# Run this on the HOST where docker-compose is managed

set -e

cd /docker/pope-bot-new

echo "=== Fixing popebot voice input ==="

# 1. Add NEXTAUTH_URL to .env if not present (forces HTTPS redirects)
if ! grep -q "NEXTAUTH_URL" .env 2>/dev/null; then
    echo "Adding NEXTAUTH_URL to .env..."
    echo 'NEXTAUTH_URL=https://pbot.edgeengineers.net' >> .env
else
    echo "NEXTAUTH_URL already in .env"
fi

# 2. Recreate the event-handler container to pick up env_file + NEXTAUTH_URL
echo "Recreating event-handler container..."
docker-compose -f docker-compose.custom.yml up -d --force-recreate event-handler

# 3. Wait for it to be healthy
echo "Waiting for event-handler to start..."
sleep 10

# 4. Verify
echo "Testing..."
curl -s http://localhost:3000/api/ping && echo " - event-handler is up"

echo ""
echo "=== FIX APPLIED ==="
echo "Access popebot via HTTPS: https://pbot.edgeengineers.net"
echo "The microphone button requires HTTPS to work."
echo "If you access via HTTP, the browser blocks microphone access."
