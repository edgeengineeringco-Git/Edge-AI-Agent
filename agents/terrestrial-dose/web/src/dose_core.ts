/**
 * Terrestrial Dose Calculation Core — TypeScript port
 * Faithful port of dose_calculation_core.py (build-prompt version)
 * Standards: UNSCEAR 2024, ICRP 137, EU BSS 2013/59/Euratom, WHO 100 Bq/m³.
 *
 * DO NOT modify the dose formulas.
 */

// ── Constants ──
export const WORLD_AVG_DOSE = 2.2;
export const GAMMA_RATE_WORLD_AVG = 59.0;

export const BQ_PER_PPM_U = 12.22;
export const BQ_PER_PPM_TH = 4.06;
export const BQ_PER_PCT_K = 313.0;

export const DCC_RA = 0.462;
export const DCC_TH = 0.604;
export const DCC_K = 0.041;
export const HOURS_PER_YEAR = 8760.0;
export const CC_SV_PER_GY = 0.7;

export const RADON_EUBSS_FACTOR = 10.0 / 300.0;
export const PAEC_PER_BQ_EEC = 5.57e-6;
export const ICRP137_COEFF = 3.0;
export const DCF_ICRP137 = PAEC_PER_BQ_EEC * ICRP137_COEFF * 1e6;
export const DCF_UNSCEAR = 9.0;
export const DCF_ICRP65_RES = 6.1;
export const F_INDOOR = 0.4;
export const F_OUTDOOR = 0.6;
export const T_INDOOR = 7000.0;
export const T_OUTDOOR = 1760.0;

export const THORON_EMANATION_DEFAULT = 0.3;
export const THORON_TRANSFER_COEFF = 2.0;
export const F_THORON = 0.02;
export const DCF_THORON = 40.0;

export const RADON_ACTION_LEVEL = 300.0;
export const RADON_WHO_LEVEL = 100.0;
export const RAEQ_THRESHOLD = 370.0;
export const GAMMA_RATE_ICRP_SAFE = 1000.0;

// ── GLiM code → description ──
export const GLIM_CODE_NAMES: Record<string, string> = {
  Su: "unconsolidated sediments",
  Ss: "siliciclastic sedimentary",
  Sm: "mixed sedimentary",
  Sc: "carbonate sedimentary",
  Sb: "basic pyroclastic",
  Ev: "evaporite",
  Pa: "acid plutonic (granite)",
  Pi: "intermediate plutonic",
  Pb: "basic plutonic",
  Va: "acid volcanic",
  Vi: "intermediate volcanic",
  Vb: "basic volcanic",
  Mt: "metamorphic",
  Py: "pyroclastic",
  Wa: "water",
  Ice: "ice",
};

// ── Lithology activities (Bq/kg) ──
export const LITHOLOGY_ACTIVITIES: Record<string, [number, number, number]> = {
  Su: [30, 35, 450],
  Ss: [35, 35, 400],
  Sm: [35, 40, 500],
  Sc: [20, 12, 90],
  Sb: [25, 30, 600],
  Ev: [12, 8, 120],
  Pa: [60, 80, 1200],
  Pi: [30, 40, 800],
  Pb: [12, 18, 300],
  Va: [50, 70, 1100],
  Vi: [25, 35, 700],
  Vb: [15, 20, 350],
  Mt: [45, 55, 850],
  Py: [40, 45, 700],
  Wa: [0, 0, 0],
  Ice: [0, 0, 0],
  granite: [60, 80, 1200],
  monzogranite: [29, 34, 883],
  syenogranite: [31, 35, 890],
  rhyolite: [50, 70, 1100],
  pegmatite: [80, 100, 1400],
  diorite: [30, 40, 800],
  andesite: [25, 35, 700],
  syenite: [40, 60, 900],
  basalt: [15, 20, 350],
  gabbro: [12, 18, 300],
  dolerite: [15, 22, 380],
  peridotite: [8, 10, 100],
  serpentinite: [10, 12, 120],
  sandstone: [35, 35, 400],
  arkose: [40, 45, 600],
  shale: [40, 50, 700],
  mudstone: [35, 45, 650],
  siltstone: [30, 38, 500],
  limestone: [20, 12, 90],
  dolomite: [18, 10, 80],
  chalk: [15, 8, 70],
  gypsum: [12, 8, 120],
  halite: [5, 3, 40],
  phosphate: [1000, 50, 100],
  schist: [40, 45, 700],
  gneiss: [45, 55, 850],
  quartzite: [25, 28, 350],
  marble: [15, 10, 90],
  slate: [40, 48, 680],
  phyllite: [35, 42, 600],
  monazite_bearing: [100, 800, 300],
  carbonatite: [500, 400, 800],
  uranium_mineralised: [5000, 80, 800],
  coal_bearing: [60, 35, 200],
  black_shale: [150, 25, 600],
  alluvium: [30, 35, 450],
  world_average_soil: [35, 30, 420],
};

export const LITHOLOGY_FACTOR: Record<string, number> = {
  Su: 1.5, Ss: 1.4, Sm: 1.2, Sc: 0.7, Sb: 1.0, Ev: 0.4, Pa: 1.3, Pi: 1.0,
  Pb: 0.6, Va: 1.2, Vi: 0.9, Vb: 0.7, Mt: 1.2, Py: 1.1, Wa: 0.0, Ice: 0.0,
  granite: 1.3, monzogranite: 1.2, rhyolite: 1.2, pegmatite: 1.5, syenite: 1.3,
  diorite: 1.0, andesite: 0.9, basalt: 0.7, gabbro: 0.6, dolerite: 0.7,
  peridotite: 0.5, serpentinite: 0.6, sandstone: 1.4, arkose: 1.3, shale: 0.8,
  mudstone: 0.8, siltstone: 1.0, limestone: 0.7, dolomite: 0.7, chalk: 0.6,
  gypsum: 0.6, halite: 0.4, phosphate: 1.2, schist: 1.1, gneiss: 1.2,
  quartzite: 1.0, marble: 0.6, slate: 0.8, phyllite: 0.9,
  monazite_bearing: 2.0, carbonatite: 1.8, uranium_mineralised: 2.5,
  coal_bearing: 1.0, black_shale: 1.3, alluvium: 1.5, world_average_soil: 1.0,
};

export function glimName(code: string): string {
  return GLIM_CODE_NAMES[code] || code;
}

export function lithologyToActivities(lithology: string) {
  const entry = LITHOLOGY_ACTIVITIES[lithology];
  if (!entry) return null;
  return { A_Ra226: entry[0], A_Th232: entry[1], A_K40: entry[2] };
}

export function lithologyFactor(lithology: string, defaultVal = 1.0): number {
  return LITHOLOGY_FACTOR[lithology] ?? defaultVal;
}

export function ppmToBqkg(eU?: number | null, eTh?: number | null, K?: number | null) {
  const out: Record<string, number> = {};
  if (eU != null) out.A_Ra226 = eU * BQ_PER_PPM_U;
  if (eTh != null) out.A_Th232 = eTh * BQ_PER_PPM_TH;
  if (K != null) out.A_K40 = K * BQ_PER_PCT_K;
  return out;
}

export function externalGammaDoseRate(a: number, b: number, c: number): number {
  return DCC_RA * a + DCC_TH * b + DCC_K * c;
}

export function annualExternalDose(a: number, b: number, c: number, occupancy = 0.2, indoor = false): number {
  const dAir = externalGammaDoseRate(a, b, c);
  const of = indoor ? 0.8 : occupancy;
  return dAir * HOURS_PER_YEAR * of * CC_SV_PER_GY * 1e-6;
}

export function radonInhalationDose(C_Rn: number, method = "eubss", F = F_INDOOR, T = T_INDOOR): number {
  if (method === "eubss") return C_Rn * RADON_EUBSS_FACTOR;
  const dcfMap: Record<string, number> = { icrp137: DCF_ICRP137, unscear: DCF_UNSCEAR, icrp65: DCF_ICRP65_RES };
  const dcf = dcfMap[method] ?? DCF_ICRP137;
  return C_Rn * F * dcf * T * 1e-6;
}

export function geogenicRadonPotential(A_Ra226: number, permeability = 1e-13, distFaultM = 1000.0, lineamentDensity = 0.5, lf = 1.0): number {
  const permTerm = (permeability / 1e-13) ** 0.5;
  const faultTerm = Math.max(0.0, 1.0 - distFaultM / 2000.0);
  const lineTerm = Math.min(1.0, lineamentDensity / 2.0);
  return (A_Ra226 / 50.0) * permTerm * (1 + 0.3 * faultTerm) * (1 + 0.2 * lineTerm) * lf;
}

export function geogenicThoronPotential(A_Th232: number, emanation = THORON_EMANATION_DEFAULT, transferCoeff = THORON_TRANSFER_COEFF, lf = 1.0): number {
  return A_Th232 * emanation * transferCoeff * lf;
}

export function thoronInhalationDose(C_Tn_gas?: number | null, A_Th232?: number | null, emanation = THORON_EMANATION_DEFAULT, transferCoeff = THORON_TRANSFER_COEFF, lf = 1.0, F_Tn = F_THORON, DCF = DCF_THORON, T = T_INDOOR): number {
  let C_Tn: number;
  if (C_Tn_gas != null) {
    C_Tn = C_Tn_gas;
  } else {
    if (A_Th232 == null) throw new Error("Provide C_Tn_gas or A_Th232.");
    C_Tn = geogenicThoronPotential(A_Th232, emanation, transferCoeff, lf);
  }
  return C_Tn * F_Tn * DCF * T * 1e-6;
}

export function radiumEquivalent(a: number, b: number, c: number): number {
  return a + 1.43 * b + 0.077 * c;
}

export function gammaActivityIndex(a: number, b: number, c: number): number {
  return a / 300.0 + b / 200.0 + c / 3000.0;
}

export function excessLifetimeCancerRisk(E_annual_mSv: number, lifeExpectancy = 70.0, riskFactor = 0.05): number {
  return E_annual_mSv * 1e-3 * lifeExpectancy * riskFactor;
}

export function riskClass(E_terrestrial_mSv: number, C_Rn?: number | null, raeq?: number | null, gammaRate?: number | null) {
  const rationale: string[] = [];
  const flags: string[] = [];
  let tier: string;

  if (E_terrestrial_mSv <= WORLD_AVG_DOSE) {
    tier = "GREEN";
    rationale.push(`${E_terrestrial_mSv.toFixed(2)} <= ${WORLD_AVG_DOSE}`);
  } else if (E_terrestrial_mSv <= 3 * WORLD_AVG_DOSE) {
    tier = "AMBER";
    rationale.push(`${E_terrestrial_mSv.toFixed(2)} 1-3x avg`);
  } else {
    tier = "RED";
    rationale.push(`${E_terrestrial_mSv.toFixed(2)} > 3x avg`);
  }

  if (C_Rn != null && C_Rn >= RADON_ACTION_LEVEL) {
    flags.push(`RADON_ACTION ${C_Rn.toFixed(0)}>=300`);
    tier = "RED";
  } else if (C_Rn != null && C_Rn >= RADON_WHO_LEVEL) {
    flags.push(`RADON_ELEVATED ${C_Rn.toFixed(0)}>=100`);
    if (tier === "GREEN") tier = "AMBER";
  }

  if (raeq != null && raeq >= RAEQ_THRESHOLD) {
    flags.push(`RAEQ_HIGH ${raeq.toFixed(0)}>=370`);
    if (tier !== "RED") tier = "RED";
  }

  if (gammaRate != null && gammaRate >= GAMMA_RATE_ICRP_SAFE) {
    flags.push(`GAMMA_HIGH ${gammaRate.toFixed(0)}>=1000`);
    tier = "RED";
  }

  return { tier, rationale, flags };
}

// ── Main entry: polygon dose fingerprint ──
export interface DoseFingerprint {
  lithology: string;
  lithology_name: string;
  arms_mSv_yr: { radon: number; thoron: number; gamma: number };
  activities_Bq_kg: { A_Ra226: number; A_Th232: number; A_K40: number };
  gamma_rate_nGy_h: number;
  radon_Bq_m3_est: number;
  thoron_gas_Bq_m3_est: number;
  grp: number | null;
  gtp_thoron_gas: number | null;
  raeq_Bq_kg: number;
  i_gamma: number;
  total_terrestrial_mSv_yr: number;
  elcr: number;
  risk: { tier: string; rationale: string[]; flags: string[] };
  provenance: string[];
}

export function polygonDoseFingerprint(opts: {
  lithology?: string;
  eU_ppm?: number | null;
  eTh_ppm?: number | null;
  K_pct?: number | null;
  C_Rn?: number | null;
  C_Tn?: number | null;
  occupancy?: number;
  permeability?: number;
  dist_fault_m?: number;
  lineament_density?: number;
  radon_method?: string;
  thoron_emanation?: number;
} = {}): DoseFingerprint {
  const {
    lithology = "Su",
    eU_ppm = null,
    eTh_ppm = null,
    K_pct = null,
    C_Rn = null,
    C_Tn = null,
    occupancy = 0.2,
    permeability = 1e-13,
    dist_fault_m = 1000.0,
    lineament_density = 0.5,
    radon_method = "eubss",
    thoron_emanation = THORON_EMANATION_DEFAULT,
  } = opts;

  const prior = lithologyToActivities(lithology) || {};
  const lf = lithologyFactor(lithology);
  const sourceNote: string[] = [];
  const meas = ppmToBqkg(eU_ppm, eTh_ppm, K_pct);
  const acts: Record<string, number> = { ...prior };

  for (const k of ["A_Ra226", "A_Th232", "A_K40"] as const) {
    if (meas[k] != null) {
      acts[k] = meas[k];
      sourceNote.push(`${k}: measured`);
    } else if (prior[k] != null) {
      const src = lithology in GLIM_CODE_NAMES ? `GLiM ${glimName(lithology)}` : lithology;
      sourceNote.push(`${k}: geology prior (${src})`);
    }
  }

  const A_Ra = acts.A_Ra226 ?? 35.0;
  const A_Th = acts.A_Th232 ?? 30.0;
  const A_K = acts.A_K40 ?? 420.0;

  const eExt = annualExternalDose(A_Ra, A_Th, A_K, occupancy);
  const gammaRate = externalGammaDoseRate(A_Ra, A_Th, A_K);

  let C_Rn_est: number;
  let grp: number | null = null;
  if (C_Rn != null) {
    C_Rn_est = C_Rn;
    sourceNote.push("radon: measured");
  } else {
    grp = geogenicRadonPotential(A_Ra, permeability, dist_fault_m, lineament_density, lf);
    C_Rn_est = grp * 50.0;
    sourceNote.push("radon: geogenic GRP");
  }
  const eRn = radonInhalationDose(C_Rn_est, radon_method);

  let C_Tn_gas_est: number;
  let gtp: number | null = null;
  if (C_Tn != null) {
    C_Tn_gas_est = C_Tn;
    sourceNote.push("thoron: measured");
  } else {
    C_Tn_gas_est = geogenicThoronPotential(A_Th, thoron_emanation, THORON_TRANSFER_COEFF, lf);
    gtp = C_Tn_gas_est;
    sourceNote.push("thoron: geogenic GTP");
  }
  const eTn = thoronInhalationDose(C_Tn_gas_est, A_Th, thoron_emanation, THORON_TRANSFER_COEFF, lf);

  const raeq = radiumEquivalent(A_Ra, A_Th, A_K);
  const iGamma = gammaActivityIndex(A_Ra, A_Th, A_K);
  const eTotal = eExt + eRn + eTn;
  const elcr = excessLifetimeCancerRisk(eTotal);
  const risk = riskClass(eTotal, C_Rn_est, raeq, gammaRate);

  return {
    lithology,
    lithology_name: lithology in GLIM_CODE_NAMES ? glimName(lithology) : lithology,
    arms_mSv_yr: {
      radon: +eRn.toFixed(4),
      thoron: +eTn.toFixed(4),
      gamma: +eExt.toFixed(4),
    },
    activities_Bq_kg: {
      A_Ra226: +A_Ra.toFixed(1),
      A_Th232: +A_Th.toFixed(1),
      A_K40: +A_K.toFixed(1),
    },
    gamma_rate_nGy_h: +gammaRate.toFixed(1),
    radon_Bq_m3_est: +C_Rn_est.toFixed(1),
    thoron_gas_Bq_m3_est: +C_Tn_gas_est.toFixed(2),
    grp,
    gtp_thoron_gas: gtp,
    raeq_Bq_kg: +raeq.toFixed(1),
    i_gamma: +iGamma.toFixed(4),
    total_terrestrial_mSv_yr: +eTotal.toFixed(4),
    elcr: +elcr.toFixed(6),
    risk,
    provenance: sourceNote,
  };
}
