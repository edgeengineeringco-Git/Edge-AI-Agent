#!/usr/bin/env python3
"""
EDGE Prospector AI — Live Demo
Generates synthetic survey data, runs full QC→Anomaly→Resource→Report pipeline.
"""
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime

# ─── 1. Generate Synthetic Survey Data ───
def generate_survey(n_samples=200, seed=42):
    rng = np.random.RandomState(seed)
    
    # Background REE levels (low)
    base = {
        'La': 30, 'Ce': 60, 'Pr': 6.7, 'Nd': 27, 'Sm': 5.3,
        'Eu': 1.3, 'Gd': 4.0, 'Tb': 0.65, 'Dy': 3.0, 'Ho': 0.8,
        'Er': 2.3, 'Tm': 0.4, 'Yb': 2.2, 'Lu': 0.4, 'Y': 21
    }
    
    data = []
    for i in range(n_samples):
        # Grid coordinates
        x = rng.uniform(1000, 5000)
        y = rng.uniform(2000, 6000)
        
        # 3 anomaly clusters
        cluster = None
        if (x-2500)**2 + (y-3500)**2 < 400**2:
            cluster = 'carbonatite'
            multiplier = rng.uniform(80, 200)
        elif (x-4000)**2 + (y-4500)**2 < 300**2:
            cluster = 'hydrothermal'
            multiplier = rng.uniform(60, 120)
        elif (x-1800)**2 + (y-5000)**2 < 350**2:
            cluster = 'ion_adsorption'
            multiplier = rng.uniform(50, 100)
        else:
            multiplier = rng.uniform(0.5, 2.0)
        
        sample = {
            'sample_id': f'S-2026-{i+1:04d}',
            'easting': round(x, 1),
            'northing': round(y, 1),
            'cluster_true': cluster,
            'moisture_pct': rng.uniform(5, 35),
            'Fe_pct': rng.uniform(1, 12)
        }
        
        for elem, base_ppm in base.items():
            noise = rng.lognormal(0, 0.3)
            sample[f'{elem}_ppm'] = round(base_ppm * multiplier * noise, 2)
        
        data.append(sample)
    
    return pd.DataFrame(data)

# ─── 2. QC Engine ───
def run_qc(df):
    issues = []
    
    # Check moisture
    high_moisture = df['moisture_pct'] > 25
    if high_moisture.sum() > 0:
        issues.append(f"{high_moisture.sum()} samples with moisture > 25%")
    
    # Check Fe matrix for pXRF suppression
    high_fe = df['Fe_pct'] > 15
    if high_fe.sum() > 0:
        issues.append(f"{high_fe.sum()} samples with Fe > 15% (matrix suppression)")
    
    # Check for negatives
    ree_cols = [c for c in df.columns if c.endswith('_ppm')]
    negatives = (df[ree_cols] < 0).any().any()
    if negatives:
        issues.append("Negative values detected in REE data")
    
    # Missing values
    missing = df[ree_cols].isnull().sum().sum()
    if missing > 0:
        issues.append(f"{missing} missing REE values")
    
    verdict = "PASS" if len(issues) == 0 else "CONDITIONAL" if len(issues) <= 2 else "FAIL"
    return verdict, issues

# ─── 3. TREO / HREO Computation ───
def compute_grades(df):
    ree_cols = ['La','Ce','Pr','Nd','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Y']
    
    # Oxide conversion factors
    factors = {
        'La': 1.1728, 'Ce': 1.2284, 'Pr': 1.2082, 'Nd': 1.1664, 'Sm': 1.1596,
        'Eu': 1.1579, 'Gd': 1.1526, 'Tb': 1.1762, 'Dy': 1.1477, 'Ho': 1.1455,
        'Er': 1.1435, 'Tm': 1.1421, 'Yb': 1.1387, 'Lu': 1.1371, 'Y': 1.2699
    }
    
    # TREO in %
    df['TREO_pct'] = sum(df[f'{e}_ppm'] * factors[e] for e in ree_cols) / 10000
    
    # HREO:TREO
    hree = ['Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Y']
    hree_sum = sum(df[f'{e}_ppm'] * factors[e] for e in hree)
    treo_sum = sum(df[f'{e}_ppm'] * factors[e] for e in ree_cols)
    df['HREO_TREO'] = hree_sum / treo_sum
    
    # CREO (critical REE oxides: Nd, Pr, Dy, Tb, Eu)
    creo_elements = ['Nd','Pr','Dy','Tb','Eu']
    df['CREO_pct'] = sum(df[f'{e}_ppm'] * factors[e] for e in creo_elements) / 10000
    
    return df

# ─── 4. Anomaly Detection (DBSCAN) ───
from sklearn.cluster import DBSCAN

def detect_anomalies(df, eps=300, min_samples=5):
    # Only cluster high-grade samples
    high_grade = df[df['TREO_pct'] > 0.05].copy()
    
    if len(high_grade) < min_samples:
        return pd.DataFrame()
    
    coords = high_grade[['easting', 'northing']].values
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
    high_grade['cluster_id'] = clustering.labels_
    
    # Summarize clusters (-1 = noise)
    clusters = []
    for cid in sorted(high_grade['cluster_id'].unique()):
        if cid == -1:
            continue
        members = high_grade[high_grade['cluster_id'] == cid]
        
        # Classify deposit type
        avg_hreo = members['HREO_TREO'].mean()
        if avg_hreo > 0.35:
            deposit_type = 'hydrothermal_hree'
        elif avg_hreo > 0.20:
            deposit_type = 'ion_adsorption'
        else:
            deposit_type = 'carbonatite'
        
        clusters.append({
            'cluster_id': int(cid),
            'n_samples': len(members),
            'mean_treo_pct': round(members['TREO_pct'].mean(), 3),
            'max_treo_pct': round(members['TREO_pct'].max(), 3),
            'mean_hreo_treo': round(avg_hreo, 3),
            'mean_creo_pct': round(members['CREO_pct'].mean(), 3),
            'deposit_type': deposit_type,
            'center_x': round(members['easting'].mean(), 1),
            'center_y': round(members['northing'].mean(), 1)
        })
    
    return pd.DataFrame(clusters)

# ─── 5. Resource Estimation ───
def estimate_resources(clusters_df, bulk_density=2.5, depth=50):
    results = []
    for _, row in clusters_df.iterrows():
        # Assume circular area based on sample spread + 100m buffer per sample
        area_m2 = np.pi * (100 + row['n_samples'] * 20) ** 2
        tonnage = area_m2 * depth * bulk_density
        
        treo_tonnes = tonnage * row['mean_treo_pct'] / 100
        creo_tonnes = tonnage * row['mean_creo_pct'] / 100
        
        # Confidence
        if row['n_samples'] >= 10:
            confidence = 'Medium'
        elif row['n_samples'] >= 5:
            confidence = 'Low'
        else:
            confidence = 'Unreliable'
        
        # Economic status
        if row['mean_treo_pct'] > 1.0:
            economic = 'Potentially Economic'
        elif row['mean_treo_pct'] > 0.5:
            economic = 'Marginal'
        else:
            economic = 'Subeconomic'
        
        results.append({
            'cluster_id': row['cluster_id'],
            'area_m2': int(area_m2),
            'tonnage_t': int(tonnage),
            'mean_treo_pct': row['mean_treo_pct'],
            'treo_tonnes': round(treo_tonnes, 1),
            'creo_tonnes': round(creo_tonnes, 1),
            'deposit_type': row['deposit_type'],
            'confidence_tier': confidence,
            'economic_status': economic
        })
    
    return pd.DataFrame(results)

# ─── 6. Report Generation ───
def generate_report(survey_id, qc, anomalies, resources, output_path):
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>EDGE Survey Report — {survey_id}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; }}
h1 {{ color: #1a1a2e; border-bottom: 3px solid #e94560; padding-bottom: 10px; }}
h2 {{ color: #16213e; margin-top: 30px; }}
.status-pass {{ color: green; font-weight: bold; }}
.status-conditional {{ color: orange; font-weight: bold; }}
table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
th {{ background: #16213e; color: white; padding: 10px; text-align: left; }}
td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
tr:hover {{ background: #f5f5f5; }}
.metric {{ background: #f0f0f0; padding: 15px; border-radius: 8px; margin: 10px 0; }}
.footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 0.85em; color: #666; }}
</style>
</head>
<body>
<h1>🌍 EDGE Prospector AI — Survey Report</h1>
<p><strong>Survey ID:</strong> {survey_id}<br>
<strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}<br>
<strong>System:</strong> EDGE Platform v1.0</p>

<h2>📊 Quality Control</h2>
<div class="metric">
<p><strong>Verdict:</strong> <span class="status-{qc[0].lower()}">{qc[0]}</span></p>
<p><strong>Issues:</strong> {qc[1] if qc[1] else 'None detected'}</p>
</div>

<h2>🔍 Anomaly Clusters</h2>
{anomalies.to_html(index=False, classes='data') if len(anomalies) > 0 else '<p>No significant anomalies detected.</p>'}

<h2>💎 Resource Estimates</h2>
{resources.to_html(index=False, classes='data') if len(resources) > 0 else '<p>No resources estimated.</p>'}

<div class="footer">
<p><em>This is an AI-assisted analysis. Final interpretation requires Competent Person review per JORC 2012.</em></p>
<p>EDGE Critical Minerals Intelligence Platform</p>
</div>
</body>
</html>"""
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    return output_path

# ─── MAIN ───
if __name__ == '__main__':
    print("=" * 60)
    print("  🌍 EDGE PROSPECTOR AI — FULL PIPELINE DEMO")
    print("=" * 60)
    
    # Step 1: Generate data
    print("\n[1/6] Generating synthetic survey data (200 samples)...")
    df = generate_survey(n_samples=200, seed=42)
    print(f"      ✓ {len(df)} samples created")
    
    # Step 2: Compute grades
    print("\n[2/6] Computing TREO / HREO:TREO / CREO...")
    df = compute_grades(df)
    print(f"      ✓ TREO range: {df['TREO_pct'].min():.3f}% - {df['TREO_pct'].max():.3f}%")
    print(f"      ✓ Mean TREO: {df['TREO_pct'].mean():.3f}%")
    print(f"      ✓ Mean HREO:TREO: {df['HREO_TREO'].mean():.3f}")
    
    # Step 3: QC
    print("\n[3/6] Running QC checks...")
    qc_verdict, qc_issues = run_qc(df)
    print(f"      ✓ Verdict: {qc_verdict}")
    for issue in qc_issues:
        print(f"      ⚠ {issue}")
    
    # Step 4: Anomaly detection
    print("\n[4/6] Detecting anomaly clusters (DBSCAN)...")
    anomalies = detect_anomalies(df, eps=300, min_samples=5)
    print(f"      ✓ {len(anomalies)} clusters found")
    for _, row in anomalies.iterrows():
        print(f"      • Cluster {row['cluster_id']}: {row['deposit_type']}, {row['n_samples']} samples, max TREO {row['max_treo_pct']}%")
    
    # Step 5: Resource estimation
    print("\n[5/6] Estimating resources...")
    resources = estimate_resources(anomalies)
    total_treo = resources['treo_tonnes'].sum() if len(resources) > 0 else 0
    print(f"      ✓ Total contained TREO: {total_treo:,.1f} tonnes")
    for _, row in resources.iterrows():
        print(f"      • Cluster {row['cluster_id']}: {row['tonnage_t']:,}t rock, {row['treo_tonnes']:,.1f}t TREO, {row['confidence_tier']} confidence")
    
    # Step 6: Report
    print("\n[6/6] Generating HTML report...")
    report_path = '/tmp/edge_survey_report.html'
    generate_report('DEMO_2026_07', (qc_verdict, qc_issues), anomalies, resources, report_path)
    print(f"      ✓ Report saved: {report_path}")
    
    # Summary JSON
    summary = {
        'survey_id': 'DEMO_2026_07',
        'n_samples': len(df),
        'qc_verdict': qc_verdict,
        'n_anomalies': len(anomalies),
        'total_treo_tonnes': round(total_treo, 1),
        'clusters': anomalies.to_dict('records') if len(anomalies) > 0 else [],
        'resources': resources.to_dict('records') if len(resources) > 0 else []
    }
    
    with open('/tmp/edge_survey_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"      ✓ Summary JSON: /tmp/edge_survey_summary.json")
    
    print("\n" + "=" * 60)
    print("  ✅ PIPELINE COMPLETE")
    print("=" * 60)
    print(f"\n  Samples processed: {len(df)}")
    print(f"  Anomalies found:   {len(anomalies)}")
    print(f"  Total TREO metal:  {total_treo:,.1f} tonnes")
    print(f"  Report:            {report_path}")
    print("\n  Next: Review report, then advance to drilling or gather more data.")
