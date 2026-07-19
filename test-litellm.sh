#!/usr/bin/env bash
# Test script for thepopebot LiteLLM proxy
# Usage: ./test-litellm.sh [model_name]
# Defaults to testing deepseek-chat if no arg provided

set -e

MODEL="${1:-deepseek-chat}"
LITELLM_URL="${LITELLM_URL:-http://localhost:4000}"

echo "=== LiteLLM Proxy Test ==="
echo "Testing model: $MODEL"
echo "Proxy URL: $LITELLM_URL"
echo ""

# Health / model list check
echo "--- 1. Checking available models ---"
curl -s "$LITELLM_URL/v1/models" | python3 -m json.tool 2>/dev/null || curl -s "$LITELLM_URL/v1/models"
echo ""

# Chat completion test
echo "--- 2. Testing chat completion ---"
curl -s "$LITELLM_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Say 'LiteLLM is working' and nothing else.\"}],
    \"max_tokens\": 20
  }" | python3 -m json.tool 2>/dev/null || curl -s "$LITELLM_URL/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [{\"role\": \"user\", \"content\": \"Say 'LiteLLM is working' and nothing else.\"}],
    \"max_tokens\": 20
  }"
echo ""

echo "=== Test complete ==="
