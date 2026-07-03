#!/usr/bin/env python3
"""
EDGE Platform Orchestrator — runs the full survey processing pipeline.
"""
import json
import asyncio
from datetime import datetime

from .demo import generate_survey, run_qc, compute_grades, detect_anomalies, estimate_resources, generate_report
from .notify import TelegramNotifier, format_survey_alert
from .search import WebSearchEngine
from .config import check_secrets

class EDGEPlatform:
    """
    Main orchestrator for REE exploration workflows.
    """
    
    def __init__(self):
        self.secrets = check_secrets()
        self.notifier = TelegramNotifier()
        self.search = WebSearchEngine()
    
    async def process_survey(self, survey_id, data_source="synthetic", **kwargs):
        """
        Full pipeline: data → QC → grades → anomalies → resources → report → notify.
        """
        print(f"\n{'='*60}")
        print(f"  🌍 EDGE PLATFORM — Processing {survey_id}")
        print(f"{'='*60}")
        
        # Step 1: Load / generate data
        if data_source == "synthetic":
            df = generate_survey(**kwargs)
        else:
            raise NotImplementedError("File ingestion coming next")
        
        # Step 2: Compute grades
        df = compute_grades(df)
        
        # Step 3: QC
        qc_verdict, qc_issues = run_qc(df)
        
        # Step 4: Anomalies
        anomalies = detect_anomalies(df)
        
        # Step 5: Resources
        resources = estimate_resources(anomalies)
        total_treo = resources['treo_tonnes'].sum() if len(resources) > 0 else 0
        
        # Step 6: Report
        report_path = f"/tmp/edge_report_{survey_id}.html"
        generate_report(survey_id, (qc_verdict, qc_issues), anomalies, resources, report_path)
        
        # Step 7: Summary JSON
        summary = {
            'survey_id': survey_id,
            'timestamp': datetime.utcnow().isoformat(),
            'n_samples': len(df),
            'qc_verdict': qc_verdict,
            'n_anomalies': len(anomalies),
            'total_treo_tonnes': round(float(total_treo), 1),
            'clusters': anomalies.to_dict('records') if len(anomalies) > 0 else [],
            'resources': resources.to_dict('records') if len(resources) > 0 else []
        }
        
        summary_path = f"/tmp/edge_summary_{survey_id}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Step 8: Notify (if Telegram configured)
        if self.secrets.get("Telegram Bot"):
            alert = format_survey_alert(survey_id, qc_verdict, len(anomalies), total_treo)
            # Demo: print instead of sending to avoid spam
            print(f"\n  📤 Telegram alert prepared:")
            print(f"  {alert[:200]}...")
        
        print(f"\n{'='*60}")
        print(f"  ✅ SURVEY COMPLETE")
        print(f"{'='*60}")
        print(f"  Report:  {report_path}")
        print(f"  Summary: {summary_path}")
        print(f"  TREO:    {total_treo:,.1f} tonnes")
        
        return summary
    
    async def run_intel_briefing(self):
        """
        Fetch live REE intelligence and compile briefing.
        """
        print("\n  🔍 Fetching live REE intelligence...")
        
        if not any([self.secrets.get("Moonshot (Kimi)"), self.secrets.get("Custom LLM")]):
            print("  ⚠️ No search API keys configured. Skipping intel.")
            return {}
        
        try:
            intel = await self.search.fetch_ree_intel()
            print(f"  ✓ Fetched {len(intel)} intelligence queries")
            return intel
        except Exception as e:
            print(f"  ⚠️ Intel fetch failed: {e}")
            return {}
    
    def status(self):
        """Print platform status"""
        print(f"\n{'='*60}")
        print(f"  🌍 EDGE PROSPECTOR AI — Platform Status")
        print(f"{'='*60}")
        for name, available in self.secrets.items():
            status = "✅" if available else "❌"
            print(f"  {status} {name}")
        print(f"{'='*60}")
