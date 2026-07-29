#!/bin/bash
# Run this in your Terminal (Mac/Linux) to connect Obsidian to GitHub
# One command — just copy-paste the whole thing

echo "Setting up Git for Obsidian sync..."

# Step 1: Store the GitHub token so you don't have to type it again
git config --global credential.helper store

# Step 2: Set the remote URL for the vault
cd "$(dirname "$0")"
git remote set-url origin https://github.com/edgeengineeringco-Git/Edge-AI-Agent

# Step 3: Pull the latest notes (this will prompt for the token once, then remember it)
git pull origin main --rebase

echo ""
echo "Done! Open Obsidian — the Git plugin will auto-pull changes now."
echo "If it asks for credentials, use:"
echo "  Username: edgeengineeringco-Git"
echo "  Password: (paste the token I give you)"
