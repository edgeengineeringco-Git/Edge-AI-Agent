#!/usr/bin/env python3
"""
EDGE Notification Engine — Telegram + future channels.
"""
import os
import json
import httpx
from .config import TELEGRAM_BOT_TOKEN

class TelegramNotifier:
    def __init__(self, token=None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.base = f"https://api.telegram.org/bot{self.token}"
    
    async def send_message(self, chat_id, text, parse_mode="HTML"):
        if not self.token:
            return {"error": "No TELEGRAM_BOT_TOKEN configured"}
        
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                timeout=30
            )
            return r.json()
    
    async def send_document(self, chat_id, file_path, caption=""):
        if not self.token:
            return {"error": "No TELEGRAM_BOT_TOKEN configured"}
        
        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as f:
                r = await client.post(
                    f"{self.base}/sendDocument",
                    data={"chat_id": chat_id, "caption": caption},
                    files={"document": (os.path.basename(file_path), f)},
                    timeout=60
                )
            return r.json()
    
    async def broadcast_admins(self, text):
        """Send to all admin users (requires user DB lookup)"""
        # For now, broadcast to a default channel or list of IDs
        # In production, this reads from thepopebot user database
        return await self.send_message("@edge_critical_minerals", text)

def format_survey_alert(survey_id, qc_verdict, n_anomalies, total_treo_tonnes):
    """Format a survey completion alert for Telegram"""
    status_emoji = "✅" if qc_verdict == "PASS" else "⚠️" if qc_verdict == "CONDITIONAL" else "❌"
    
    return f"""<b>🌍 EDGE Survey Complete</b>

<b>Survey:</b> <code>{survey_id}</code>
<b>QC:</b> {status_emoji} {qc_verdict}
<b>Anomalies:</b> {n_anomalies} clusters found
<b>Contained TREO:</b> {total_treo_tonnes:,.0f} tonnes

<i>Full report available on platform.</i>"""
