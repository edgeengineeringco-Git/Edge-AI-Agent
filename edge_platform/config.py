#!/usr/bin/env python3
"""
EDGE Platform Configuration — reads secrets from environment.
"""
import os

# ─── LLM / API Keys ───
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CUSTOM_API_KEY = os.getenv("CUSTOM_API_KEY")
CUSTOM_OPENAI_BASE_URL = os.getenv("CUSTOM_OPENAI_BASE_URL")

# ─── Communication ───
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

# ─── Cloud Storage ───
GOOGLE_DRIVE_OAUTH = os.getenv("GOOGLE_DRIVE_OAUTH")

# ─── GitHub ───
GH_TOKEN = os.getenv("GH_TOKEN")

# ─── Platform ───
AGENT_JOB_TOKEN = os.getenv("AGENT_JOB_TOKEN")
APP_URL = os.getenv("APP_URL", "")

def check_secrets():
    """Return available vs missing secrets"""
    secrets = {
        "Moonshot (Kimi)": bool(MOONSHOT_API_KEY),
        "Telegram Bot": bool(TELEGRAM_BOT_TOKEN),
        "Google Drive OAuth": bool(GOOGLE_DRIVE_OAUTH),
        "GitHub": bool(GH_TOKEN),
        "Brevo (Email)": bool(BREVO_API_KEY),
        "Custom LLM": bool(CUSTOM_API_KEY and CUSTOM_OPENAI_BASE_URL),
    }
    return secrets
