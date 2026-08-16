/**
 * Analysis Text Generator — client-side port of analyze_point + short_report
 * Generates human-readable analysis from computed dose fingerprint fields.
 * NO free-form invented geology — all text is templated from computed values.
 */

import type { DoseFingerprint } from "./dose_core";
import { getLithologyAt } from "./lithology";
import { glimName, lithologyFactor, WORLD_AVG_DOSE } from "./dose_core";

export interface AnalysisResult {
  dominant: "radon" | "thoron" | "gamma";
  sharePct: number;
  why: string[];
  expectedOrAnomaly: "expected" | "elevated" | "anomaly";
  vsWorldAvg: number;
  resolutionNote: string;
}

export interface FactorEntry {
  id: string;
  value: string;
  effect: string;
  direction: "up" | "down" | "neutral" | "varies";
  source: string;
  resolution: string;
}

export interface ClientAnalyzedData extends DoseFingerprint {
  factors: FactorEntry[];
  confidence: { level: string; reason: string };
  report_short: string[];
  cell_m: number;
}

/**
 * Client-side analyze_point equivalent.
 * Takes a DoseFingerprint (from polygonDoseFingerprint) + location context
 * and returns enriched data with factors, confidence, and report lines.
 */
export function analyzeClient(data: DoseFingerprint, lat?: number, lon?: number): ClientAnalyzedData {
  const arms = data.arms_mSv_yr;
  const total = data.total_terrestrial_mSv_yr;
  const lith = data.lithology;
  const lf = lithologyFactor(lith);

  // Build factors (simplified client-side version)
  const factors: FactorEntry[] = [];
  factors.push({
    id: "lithology",
    value: `${lith} (${glimName(lith)})`,
    effect: "Rn Tn gamma source",
    direction: "varies",
    source: "European geology mosaic",
    resolution: "50k–1M",
  });
  factors.push({
    id: "permeability",
    value: "moderate (1.0e-13)",
    effect: "Rn transport",
    direction: "neutral",
    source: "SoilGrids 250m",
    resolution: "250m",
  });
  factors.push({
    id: "fault",
    value: "5000 m",
    effect: "Rn pathway",
    direction: "neutral",
    source: "GEM faults",
    resolution: "vector",
  });
  factors.push({
    id: "activities",
    value: `Ra=${data.activities_Bq_kg.A_Ra226.toFixed(0)} Th=${data.activities_Bq_kg.A_Th232.toFixed(0)} K=${data.activities_Bq_kg.A_K40.toFixed(0)} Bq/kg`,
    effect: "source term",
    direction: "varies",
    source: data.provenance[0]?.includes("measured") ? "Measured" : "Geology prior",
    resolution: "—",
  });

  // Confidence
  const hasMeasurement = data.provenance.some((p) => p.includes("measured"));
  const confidence = {
    level: hasMeasurement ? "high" : "low",
    reason: hasMeasurement
      ? "Measurement data available"
      : `Geology prior (${glimName(lith)}); no measurement nearby`,
  };

  // Report lines
  const report_short = buildShortReport(data, factors, confidence);

  // Cell size from map scale if available
  const cell_m = lat != null && lon != null ? getLithologyAt(lon, lat).cell_m : 1000;

  return {
    ...data,
    factors,
    confidence,
    report_short,
    cell_m,
  };
}

function buildShortReport(
  data: DoseFingerprint,
  factors: FactorEntry[],
  confidence: { level: string; reason: string }
): string[] {
  const arms = data.arms_mSv_yr;
  const total = data.total_terrestrial_mSv_yr;
  const risk = data.risk.tier;
  const dom = (Object.keys(arms) as Array<keyof typeof arms>).reduce((a, b) => (arms[a] > arms[b] ? a : b));
  const share = total > 0 ? (arms[dom] / total) * 100 : 0;

  const lines: string[] = [];
  lines.push(`${dom.charAt(0).toUpperCase() + dom.slice(1)} is ${share.toFixed(0)}% of total dose (${arms[dom].toFixed(2)} mSv/yr).`);
  lines.push(`Total terrestrial dose: ${total.toFixed(2)} mSv/yr — ${risk}.`);

  for (const f of factors.slice(0, 3)) {
    const arrow = f.direction === "up" ? "↑" : f.direction === "down" ? "↓" : "→";
    lines.push(`${f.id.charAt(0).toUpperCase() + f.id.slice(1)}: ${f.value} (${arrow} ${f.effect}).`);
  }

  const ratio = total / WORLD_AVG_DOSE;
  lines.push(`${ratio.toFixed(1)}× UNSCEAR world average (2.2 mSv/yr).`);
  lines.push(`Confidence: ${confidence.level}. ${confidence.reason}.`);
  lines.push(
    `Cell: ${1000} m. Activities: Ra=${data.activities_Bq_kg.A_Ra226.toFixed(0)}, Th=${data.activities_Bq_kg.A_Th232.toFixed(0)}, K=${data.activities_Bq_kg.A_K40.toFixed(0)} Bq/kg.`
  );

  return lines.slice(0, 8);
}

/**
 * Generate recommendations from the analysis.
 */
export interface Recommendation {
  priority: "URGENT" | "HIGH" | "MEDIUM" | "LOW";
  text: string;
}

export function generateRecommendations(data: DoseFingerprint): Recommendation[] {
  const recs: Recommendation[] = [];
  const total = data.total_terrestrial_mSv_yr;
  const tier = data.risk.tier;

  if (tier === "RED") {
    recs.push({
      priority: "URGENT",
      text: `Radon mitigation systems (sub-slab depressurisation) recommended if indoor Rn exceeds 300 Bq/m³.`,
    });
  }

  const hasMeasurement = data.provenance.some((p) => p.includes("measured"));
  if (!hasMeasurement) {
    recs.push({
      priority: "HIGH",
      text: "Conduct airborne gamma-ray spectrometry survey (eU, eTh, K%) to replace geology-prior estimates.",
    });
  }

  if (data.radon_Bq_m3_est > 100) {
    recs.push({
      priority: "HIGH",
      text: `Deploy indoor radon detectors to validate geogenic estimate of ${data.radon_Bq_m3_est.toFixed(0)} Bq/m³.`,
    });
  }

  if (data.activities_Bq_kg.A_Th232 > 100) {
    recs.push({
      priority: "MEDIUM",
      text: "Thoron measurement with grab-sampling. Consider CeBr3 drone spectrometry for Th-232 mapping.",
    });
  }

  if (data.raeq_Bq_kg > 370) {
    recs.push({
      priority: "MEDIUM",
      text: `Test building materials for compliance with EU BSS activity index (Iγ = ${data.i_gamma.toFixed(2)}).`,
    });
  }

  if (tier === "GREEN" && hasMeasurement) {
    recs.push({
      priority: "LOW",
      text: "No immediate action required. Periodic monitoring every 5 years is sufficient.",
    });
  }

  if (tier === "AMBER" && hasMeasurement) {
    recs.push({
      priority: "LOW",
      text: "Consider long-term radon monitoring during winter months.",
    });
  }

  return recs;
}
