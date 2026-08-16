/** TypeScript port of dose_calculation_core.py — SINGLE SOURCE OF TRUTH. */
export const WORLD_AVG_DOSE = 2.2;
export const IRISH_RN_ACTION = 200;
const RADON_IRISH_FACTOR = 6.7 / 200.0;
const DCC_RA = 0.462, DCC_TH = 0.604, DCC_K = 0.041, HOURS = 8760, CC = 0.7;

export interface DoseResult {
  arms: { radon: number; thoron: number; gamma: number };
  total: number; gr: number; raeq: number; C_Rn: number;
  activities: { Ra: number; Th: number; K: number };
  risk: { tier: 'GREEN' | 'AMBER' | 'RED'; flags: string[] };
  prov: string[]; conf: number; lith: string; lithName: string;
}

export function doseFingerprint(o: {
  lithology: string; eU_ppm?: number | null; eTh_ppm?: number | null;
  K_pct?: number | null; C_Rn?: number | null; permeability?: number;
  dist_fault?: number; lineament?: number;
}): DoseResult {
  const LA: Record<string, [number, number, number]> = {
    Pa: [60, 80, 1200], Pi: [30, 40, 800], Pb: [12, 18, 300], Vb: [15, 20, 350],
    Vi: [25, 35, 700], Va: [50, 70, 1100], Mt: [45, 55, 850], Py: [40, 45, 700],
    Ss: [35, 35, 400], Sm: [35, 40, 500], Sc: [20, 12, 90], Sb: [25, 30, 600],
    Ev: [12, 8, 120], Su: [30, 35, 450], Wa: [0, 0, 0], Ice: [0, 0, 0],
    granite: [60, 80, 1200], limestone: [20, 12, 90], world_average_soil: [35, 30, 420],
    monazite_bearing: [100, 800, 300], carbonatite: [500, 400, 800],
  };
  const LF: Record<string, number> = {
    Pa: 1.3, Sc: 0.7, Mt: 1.2, Ss: 1.4, Su: 1.5, granite: 1.3,
    limestone: 0.7, world_average_soil: 1.0, monazite_bearing: 2.0, carbonatite: 1.8,
  };
  const GN: Record<string, string> = {
    Pa: "acid plutonic (granite)", Sc: "carbonate sedimentary", Mt: "metamorphic",
    Ss: "siliciclastic sedimentary", Su: "unconsolidated sediments",
  };
  const prior = LA[o.lithology] || LA.world_average_soil;
  const lf = LF[o.lithology] ?? 1.0;
  let A_Ra = prior[0], A_Th = prior[1], A_K = prior[2];
  const prov: string[] = [];
  if (o.eU_ppm != null) { A_Ra = o.eU_ppm * 12.22; prov.push("A_Ra226: measured"); }
  if (o.eTh_ppm != null) { A_Th = o.eTh_ppm * 4.06; prov.push("A_Th232: measured"); }
  if (o.K_pct != null) { A_K = o.K_pct * 313; prov.push("A_K40: measured"); }
  const gr = DCC_RA * A_Ra + DCC_TH * A_Th + DCC_K * A_K;
  const eG = gr * HOURS * 0.8 * CC * 1e-6;
  let C_Rn = o.C_Rn;
  if (C_Rn == null) {
    const perm = o.permeability ?? 1e-13, df = o.dist_fault ?? 1000, lin = o.lineament ?? 0.5;
    const grp = (A_Ra / 50) * Math.sqrt(perm / 1e-13) * (1 + 0.3 * Math.max(0, 1 - df / 2000)) * (1 + 0.2 * Math.min(1, lin / 2)) * lf;
    C_Rn = grp * 50; prov.push("radon: GRP");
  } else { prov.push("radon: measured"); }
  const eRn = C_Rn * RADON_IRISH_FACTOR;
  const gtp = A_Th * 0.3 * 2.0 * lf;
  const eTn = gtp * 0.02 * 40 * 7000 * 1e-6;
  const raeqV = A_Ra + 1.43 * A_Th + 0.077 * A_K;
  const eTotal = eG + eRn + eTn;
  let tier: 'GREEN' | 'AMBER' | 'RED' = eTotal <= 2.2 ? 'GREEN' : eTotal <= 6.6 ? 'AMBER' : 'RED';
  const flags: string[] = [];
  if (C_Rn >= 200) { flags.push(`RADON_ACTION: ${C_Rn.toFixed(0)}>=Irish 200`); tier = 'RED'; }
  else if (C_Rn >= 100) { flags.push(`RADON_ELEVATED: ${C_Rn.toFixed(0)}>=WHO 100`); if (tier === 'GREEN') tier = 'AMBER'; }
  if (raeqV >= 370) { flags.push(`RAEQ_HIGH: ${raeqV.toFixed(0)}>=370`); if (tier !== 'RED') tier = 'RED'; }
  if (gr >= 1000) { flags.push(`GAMMA_HIGH: ${gr.toFixed(0)}>=1000`); tier = 'RED'; }
  const conf = o.eU_ppm != null ? 90 : o.eTh_ppm != null ? 75 : o.K_pct != null ? 60 : 20;
  return { arms: { radon: eRn, thoron: eTn, gamma: eG }, total: eTotal, gr, raeq: raeqV, C_Rn,
    activities: { Ra: A_Ra, Th: A_Th, K: A_K }, risk: { tier, flags }, prov, conf,
    lith: o.lithology, lithName: GN[o.lithology] || o.lithology };
}
