#!/bin/bash
set -e

# Apply the voice input fix to the running popebot
# Run this on the HOST where docker-compose is managed (e.g., /docker/pope-bot-new)

cd /docker/pope-bot-new

echo "=== Popebot Voice Input Fix ==="
echo ""

# Step 1: Verify docker is available
if ! command -v docker &> /dev/null; then
    echo "ERROR: docker not found. Run this on the host machine."
    exit 1
fi

# Step 2: Add NEXTAUTH_URL to .env if missing
if ! grep -q "^NEXTAUTH_URL=" .env 2>/dev/null; then
    echo "Adding NEXTAUTH_URL to .env..."
    echo 'NEXTAUTH_URL=https://pbot.edgeengineers.net' >> .env
else
    echo "NEXTAUTH_URL already in .env, updating..."
    sed -i 's|^NEXTAUTH_URL=.*|NEXTAUTH_URL=https://pbot.edgeengineers.net|' .env
fi

# Step 3: Recreate the event-handler container (picks up env_file changes)
echo "Recreating event-handler container with new env vars..."
docker-compose -f docker-compose.custom.yml up -d --force-recreate event-handler

# Step 4: Wait for healthy
echo "Waiting for event-handler to become healthy..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:3000/api/ping > /dev/null 2>&1; then
        echo "✓ event-handler is up"
        break
    fi
    sleep 2
done

# Step 5: Verify the redirect
echo ""
echo "Testing HTTPS redirect..."
REDIRECT=$(curl -skI https://pbot.edgeengineers.net/ 2>/dev/null | grep -i "^location:" | head -1)
echo "  HTTPS redirect: $REDIRECT"

echo ""
echo "=== FIX APPLIED ==="
echo ""
echo "The microphone button requires HTTPS to work (browser security)."
echo ""
echo "IMPORTANT: Access popebot via:"
echo "  https://pbot.edgeengineers.net"
echo ""
echo "Do NOT use http://187.124.210.124:3000 - the mic won't work on HTTP."
echo ""
echo "After logging in, the mic button in the chat should work."
