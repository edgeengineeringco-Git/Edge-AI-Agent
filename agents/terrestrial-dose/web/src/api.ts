/**
 * API client for the Euro-Dose backend.
 * Falls back to client-side computation when the API is unreachable
 * (e.g. static GitHub Pages deployment).
 */

import type { DoseFingerprint } from "./dose_core";
import { polygonDoseFingerprint } from "./dose_core";
import { getLithologyAt } from "./lithology";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function fetchDose(lat: number, lon: number): Promise<DoseFingerprint> {
  try {
    const resp = await fetch(`${API_BASE}/dose?lat=${lat}&lon=${lon}`, {
      signal: AbortSignal.timeout(3000),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    // Map API response shape to DoseFingerprint
    return {
      lithology: data.glim ?? "Su",
      lithology_name: data.lithology_name ?? data.region ?? "Unknown",
      arms_mSv_yr: data.arms_mSv_yr,
      activities_Bq_kg: data.activities ?? data.activities_Bq_kg,
      gamma_rate_nGy_h: data.gamma_rate_nGy_h,
      radon_Bq_m3_est: data.radon_Bq_m3_est ?? 0,
      thoron_gas_Bq_m3_est: data.thoron_gas_Bq_m3_est ?? 0,
      grp: data.grp ?? null,
      gtp_thoron_gas: data.gtp_thoron_gas ?? null,
      raeq_Bq_kg: data.raeq_Bq_kg ?? 0,
      i_gamma: data.i_gamma ?? 0,
      total_terrestrial_mSv_yr: data.total_terrestrial_mSv_yr,
      elcr: data.elcr ?? 0,
      risk: data.risk,
      provenance: data.provenance ?? [],
    };
  } catch {
    // Fallback: client-side computation
    const lith = getLithologyAt(lon, lat);
    return polygonDoseFingerprint({ lithology: lith.glim, lat, lon });
  }
}

export async function fetchDoseGrid(
  south: number,
  west: number,
  north: number,
  east: number,
  step: number
): Promise<{ lat: number; lon: number; tier: string; total: number }[]> {
  try {
    const resp = await fetch(
      `${API_BASE}/dose/bbox?south=${south}&west=${west}&north=${north}&east=${east}&step=${step}`,
      { signal: AbortSignal.timeout(8000) }
    );
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    return data.features.map((f: any) => ({
      lat: f.geometry.coordinates[1],
      lon: f.geometry.coordinates[0],
      tier: f.properties.tier,
      total: f.properties.dose,
    }));
  } catch {
    return [];
  }
}
