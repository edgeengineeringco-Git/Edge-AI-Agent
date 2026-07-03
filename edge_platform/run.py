#!/usr/bin/env python3
"""
EDGE Platform CLI — entry point for survey processing and intel.
"""
import asyncio
import argparse
from .orchestrator import EDGEPlatform

async def main():
    parser = argparse.ArgumentParser(description="EDGE Prospector AI Platform")
    parser.add_argument("command", choices=["status", "process", "intel"])
    parser.add_argument("--survey-id", default="SURVEY_001")
    parser.add_argument("--samples", type=int, default=200)
    
    args = parser.parse_args()
    
    platform = EDGEPlatform()
    
    if args.command == "status":
        platform.status()
    
    elif args.command == "process":
        await platform.process_survey(
            survey_id=args.survey_id,
            data_source="synthetic",
            n_samples=args.samples,
            seed=42
        )
    
    elif args.command == "intel":
        intel = await platform.run_intel_briefing()
        if intel:
            for query, results in intel.items():
                print(f"\n  📰 {query}")
                for r in results[:2]:
                    print(f"     • {r.get('title', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(main())
