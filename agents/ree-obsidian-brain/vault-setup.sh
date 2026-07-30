#!/bin/bash
# ============================================================
# REE Obsidian Brain — Vault Git Setup
# Run this script at the start of every agent job.
# It configures git credentials and verifies access to
# the Edge-Obsidian-Brain repo (the ONLY repo for Obsidian).
# ============================================================

VAULT_TOKEN="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"
VAULT_REPO="https://github.com/edgeengineeringco-Git/Edge-Obsidian-Brain.git"
VAULT_DIR="$(cd "$(dirname "$0")/vault" && pwd)"

echo "🔧 Setting up vault git access..."

# 1. Configure git credential helper (persists for this container)
git config --global credential.helper store

# 2. Write credentials to git-credentials store
echo "https://edgeengineeringco-Git:${VAULT_TOKEN}@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

# 3. Ensure vault directory has the correct remote
cd "$VAULT_DIR"

if [ ! -d ".git" ]; then
    echo "📥 Cloning vault repo (first time)..."
    cd "$(dirname "$VAULT_DIR")"
    git clone "$VAULT_REPO" vault
    cd vault
fi

# 4. Set the remote URL with embedded token
git remote set-url origin "https://edgeengineeringco-Git:${VAULT_TOKEN}@github.com/edgeengineeringco-Git/Edge-Obsidian-Brain.git"

# 5. Pull latest changes
echo "⬇️  Pulling latest from Edge-Obsidian-Brain..."
git pull origin main 2>&1

echo ""
echo "✅ Vault git access configured."
echo "   Repo: Edge-Obsidian-Brain"
echo "   Branch: main"
echo "   Directory: $VAULT_DIR"
