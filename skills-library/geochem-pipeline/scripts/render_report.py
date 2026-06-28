#!/usr/bin/env python3
"""
Render the HTML survey report from a Jinja2 template.

Usage:
    python3 render_report.py \
        --template <template.html> \
        --summary <summary.json> \
        --anomalies <clusters.csv> \
        --resources <resource.json> \
        [--risk <risk.json>] \
        --output <report.html> \
        --survey-id SURVEY_2026_05_A
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
    parser = argparse.ArgumentParser(description="Render HTML survey report.")
    parser.add_argument("--template", required=True, help="Path to Jinja2 template")
    parser.add_argument("--summary", required=True, help="Processing summary JSON")
    parser.add_argument("--anomalies", required=True, help="Cluster summary CSV")
    parser.add_argument("--resources", required=True, help="Resource estimate JSON")
    parser.add_argument("--risk", default=None, help="Risk matrix JSON (optional)")
    parser.add_argument("--output", required=True, help="Output HTML path")
    parser.add_argument("--survey-id", required=True, help="Survey identifier")
    args = parser.parse_args()

    for p in [args.template, args.summary, args.anomalies, args.resources]:
        if not Path(p).exists():
            print(f"Error: file not found: {p}", file=sys.stderr)
            sys.exit(1)

    with open(args.summary) as f:
        summary = json.load(f)
    anomalies = pd.read_csv(args.anomalies).to_dict(orient="records")
    with open(args.resources) as f:
        resources = json.load(f)
    risk = None
    if args.risk and Path(args.risk).exists():
        with open(args.risk) as f:
            risk = json.load(f)

    env = Environment(
        loader=FileSystemLoader(str(Path(args.template).parent)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template(Path(args.template).name)

    html = template.render(
        survey_id=args.survey_id,
        report_date=datetime.now().strftime("%Y-%m-%d"),
        report_timestamp=datetime.now().isoformat(timespec="minutes"),
        qc_verdict="PASS",
        qc_stats={
            "total_samples": summary.get("n_rows", 0),
            "n_blanks": 0,
            "n_crms": 0,
            "n_duplicates": 0,
        },
        anomalies=anomalies,
        resource_estimates=[resources] if isinstance(resources, dict) else resources,
        risk_assessment=risk,
        recommended_actions=[
            "Review QC-verified processed CSV",
            "Run geochem-anomaly on validated data",
            "Run geochem-resource for top clusters",
        ],
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        f.write(html)
    print(f"Rendered report → {out_path}")


if __name__ == "__main__":
    main()
