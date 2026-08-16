"""
Terrestrial Radiation Dose Calculation Core — SINGLE SOURCE OF TRUTH.
All mSv/nGy/Bq numbers come from here. Import. Do not rewrite.
Standards: UNSCEAR 2024, ICRP 137, EU BSS 2013/59/Euratom.
"""

BQ_PER_PPM_U = 12.22
BQ_PER_PPM_TH = 4.06
BQ_PER_PCT_K = 313.0


def ppm_to_bqkg(eU_ppm=None, eTh_ppm=None, K_pct=None):
    out = {}
    if eU_ppm is not None:
        out["A_Ra226"] = eU_ppm * BQ_PER_PPM_U
    if eTh_ppm is not None:
        out["A_Th232"] = eTh_ppm * BQ_PER_PPM_TH
    if K_pct is not None:
        out["A_K40"] = K_pct * BQ_PER_PCT_K
    return out


LITHOLOGY_ACTIVITIES = {
    "Su": (30, 35, 450), "Ss": (35, 35, 400), "Sm": (35, 40, 500),
    "Sc": (20, 12, 90), "Sb": (25, 30, 600), "Ev": (12, 8, 120),
    "Pa": (60, 80, 1200), "Pi": (30, 40, 800), "Pb": (12, 18, 300),
    "Va": (50, 70, 1100), "Vi": (25, 35, 700), "Vb": (15, 20, 350),
    "Mt": (45, 55, 850), "Py": (40, 45, 700), "Wa": (0, 0, 0), "Ice": (0, 0, 0),
    "granite": (60, 80, 1200), "monzogranite": (29, 34, 883),
    "syenogranite": (31, 35, 890), "rhyolite": (50, 70, 1100),
    "pegmatite": (80, 100, 1400), "diorite": (30, 40, 800),
    "andesite": (25, 35, 700), "syenite": (40, 60, 900),
    "basalt": (15, 20, 350), "gabbro": (12, 18, 300),
    "dolerite": (15, 22, 380), "peridotite": (8, 10, 100),
    "serpentinite": (10, 12, 120), "sandstone": (35, 35, 400),
    "arkose": (40, 45, 600), "shale": (40, 50, 700),
    "mudstone": (35, 45, 650), "siltstone": (30, 38, 500),
    "limestone": (20, 12, 90), "dolomite": (18, 10, 80),
    "chalk": (15, 8, 70), "gypsum": (12, 8, 120),
    "halite": (5, 3, 40), "phosphate": (1000, 50, 100),
    "schist": (40, 45, 700), "gneiss": (45, 55, 850),
    "quartzite": (25, 28, 350), "marble": (15, 10, 90),
    "slate": (40, 48, 680), "phyllite": (35, 42, 600),
    "monazite_bearing": (100, 800, 300), "carbonatite": (500, 400, 800),
    "uranium_mineralised": (5000, 80, 800), "coal_bearing": (60, 35, 200),
    "black_shale": (150, 25, 600), "alluvium": (30, 35, 450),
    "world_average_soil": (35, 30, 420),
}

GLIM_CODE_NAMES = {
    "Su": "unconsolidated sediments", "Ss": "siliciclastic sedimentary",
    "Sm": "mixed sedimentary", "Sc": "carbonate sedimentary",
    "Sb": "basic pyroclastic", "Ev": "evaporite",
    "Pa": "acid plutonic (granite)", "Pi": "intermediate plutonic",
    "Pb": "basic plutonic", "Va": "acid volcanic",
    "Vi": "intermediate volcanic", "Vb": "basic volcanic",
    "Mt": "metamorphic", "Py": "pyroclastic", "Wa": "water", "Ice": "ice",
}

LITHOLOGY_FACTOR = {
    "Su": 1.5, "Ss": 1.4, "Sm": 1.2, "Sc": 0.7, "Sb": 1.0, "Ev": 0.4,
    "Pa": 1.3, "Pi": 1.0, "Pb": 0.6, "Va": 1.2, "Vi": 0.9, "Vb": 0.7,
    "Mt": 1.2, "Py": 1.1, "Wa": 0.0, "Ice": 0.0,
    "granite": 1.3, "monzogranite": 1.2, "rhyolite": 1.2,
    "pegmatite": 1.5, "syenite": 1.3, "diorite": 1.0,
    "andesite": 0.9, "basalt": 0.7, "gabbro": 0.6,
    "dolerite": 0.7, "peridotite": 0.5, "serpentinite": 0.6,
    "sandstone": 1.4, "arkose": 1.3, "shale": 0.8,
    "mudstone": 0.8, "siltstone": 1.0, "limestone": 0.7,
    "dolomite": 0.7, "chalk": 0.6, "gypsum": 0.6,
    "halite": 0.4, "phosphate": 1.2, "schist": 1.1,
    "gneiss": 1.2, "quartzite": 1.0, "marble": 0.6,
    "slate": 0.8, "phyllite": 0.9, "monazite_bearing": 2.0,
    "carbonatite": 1.8, "uranium_mineralised": 2.5,
    "coal_bearing": 1.0, "black_shale": 1.3, "alluvium": 1.5,
    "world_average_soil": 1.0,
}


def lithology_to_activities(l):
    if l in LITHOLOGY_ACTIVITIES:
        ra, th, k = LITHOLOGY_ACTIVITIES[l]
        return {"A_Ra226": ra, "A_Th232": th, "A_K40": k}
    return None


def lithology_factor(l, d=1.0):
    return LITHOLOGY_FACTOR.get(l, d)


def glim_name(c):
    return GLIM_CODE_NAMES.get(c, c)


WORLD_AVG_DOSE = 2.2
DCC_RA = 0.462
DCC_TH = 0.604
DCC_K = 0.041
HOURS_PER_YEAR = 8760.0
CC_SV_PER_GY = 0.7


def external_gamma_dose_rate(A_Ra, A_Th, A_K):
    return DCC_RA * A_Ra + DCC_TH * A_Th + DCC_K * A_K


def annual_external_dose(A_Ra, A_Th, A_K, occupancy=0.2, indoor=False):
    d = external_gamma_dose_rate(A_Ra, A_Th, A_K)
    return d * HOURS_PER_YEAR * (0.8 if indoor else occupancy) * CC_SV_PER_GY * 1e-6


RADON_EUBSS_FACTOR = 10.0 / 300.0
PAEC_PER_BQ_EEC = 5.57e-6
ICRP137_COEFF = 3.0
DCF_ICRP137 = PAEC_PER_BQ_EEC * ICRP137_COEFF * 1e6
DCF_UNSCEAR = 9.0
DCF_ICRP65_RES = 6.1
F_INDOOR = 0.4
T_INDOOR = 7000.0


def radon_inhalation_dose(C_Rn, method="eubss", F=F_INDOOR, T=T_INDOOR):
    if method == "eubss":
        return C_Rn * RADON_EUBSS_FACTOR
    return C_Rn * F * {
        "icrp137": DCF_ICRP137,
        "unscear": DCF_UNSCEAR,
        "icrp65": DCF_ICRP65_RES,
    }[method] * T * 1e-6


def geogenic_radon_potential(A_Ra, perm=1e-13, dist_fault=1000.0, lin=0.5, lf=1.0):
    return (
        (A_Ra / 50.0)
        * ((perm / 1e-13) ** 0.5)
        * (1 + 0.3 * max(0, 1 - dist_fault / 2000.0))
        * (1 + 0.2 * min(1, lin / 2.0))
        * lf
    )


THORON_EMANATION = 0.3
THORON_TRANSFER = 2.0
F_THORON = 0.02
DCF_THORON = 40.0


def geogenic_thoron_potential(A_Th, em=THORON_EMANATION, tc=THORON_TRANSFER, lf=1.0):
    return A_Th * em * tc * lf


def thoron_inhalation_dose(
    C_Tn_gas=None, A_Th232=None, em=THORON_EMANATION,
    tc=THORON_TRANSFER, lf=1.0, F_Tn=F_THORON, DCF=DCF_THORON, T=T_INDOOR,
):
    if C_Tn_gas is None:
        if A_Th232 is None:
            raise ValueError("Provide C_Tn_gas or A_Th232")
        C_Tn_gas = geogenic_thoron_potential(A_Th232, em, tc, lf)
    return C_Tn_gas * F_Tn * DCF * T * 1e-6


def radium_equivalent(A_Ra, A_Th, A_K):
    return A_Ra + 1.43 * A_Th + 0.077 * A_K


def gamma_activity_index(A_Ra, A_Th, A_K):
    return A_Ra / 300.0 + A_Th / 200.0 + A_K / 3000.0


def excess_lifetime_cancer_risk(E, le=70.0, rf=0.05):
    return E * 1e-3 * le * rf


RADON_ACTION_LEVEL = 300.0
RADON_WHO_LEVEL = 100.0
RAEQ_THRESHOLD = 370.0
GAMMA_RATE_ICRP_SAFE = 1000.0


def risk_class(E, C_Rn=None, raeq=None, gamma_rate=None):
    r = []
    f = []
    if E <= WORLD_AVG_DOSE:
        t = "GREEN"
        r.append(f"{E:.2f}<={WORLD_AVG_DOSE}")
    elif E <= 3 * WORLD_AVG_DOSE:
        t = "AMBER"
        r.append(f"{E:.2f} 1-3x")
    else:
        t = "RED"
        r.append(f"{E:.2f}>3x")
    if C_Rn is not None and C_Rn >= RADON_ACTION_LEVEL:
        f.append(f"RADON_ACTION {C_Rn:.0f}>=300")
        t = "RED"
    elif C_Rn is not None and C_Rn >= RADON_WHO_LEVEL:
        f.append(f"RADON_ELEVATED {C_Rn:.0f}>=100")
    if C_Rn is not None and C_Rn >= RADON_WHO_LEVEL and t == "GREEN":
        t = "AMBER"
    if raeq is not None and raeq >= RAEQ_THRESHOLD:
        f.append(f"RAEQ_HIGH {raeq:.0f}>=370")
    if raeq is not None and raeq >= RAEQ_THRESHOLD and t != "RED":
        t = "RED"
    if gamma_rate is not None and gamma_rate >= GAMMA_RATE_ICRP_SAFE:
        f.append(f"GAMMA_HIGH {gamma_rate:.0f}>=1000")
        t = "RED"
    return {"tier": t, "rationale": r, "flags": f}


def polygon_dose_fingerprint(
    lithology="Su", eU_ppm=None, eTh_ppm=None, K_pct=None,
    C_Rn=None, C_Tn=None, occupancy=0.2, permeability=1e-13,
    dist_fault_m=1000.0, lineament_density=0.5,
    radon_method="eubss", thoron_emanation=THORON_EMANATION,
):
    prior = lithology_to_activities(lithology) or {}
    lf = lithology_factor(lithology)
    sn = []
    meas = ppm_to_bqkg(eU_ppm, eTh_ppm, K_pct)
    acts = dict(prior)
    for k in ("A_Ra226", "A_Th232", "A_K40"):
        if k in meas:
            acts[k] = meas[k]
            sn.append(f"{k}: measured")
        elif k in prior:
            sn.append(f"{k}: prior ({glim_name(lithology)})")
    A_Ra = acts.get("A_Ra226", 35.0)
    A_Th = acts.get("A_Th232", 30.0)
    A_K = acts.get("A_K40", 420.0)
    e_ext = annual_external_dose(A_Ra, A_Th, A_K, occupancy=occupancy)
    gr = external_gamma_dose_rate(A_Ra, A_Th, A_K)
    if C_Rn is None:
        grp = geogenic_radon_potential(A_Ra, permeability, dist_fault_m, lineament_density, lf)
        C_Rn_est = grp * 50.0
        sn.append("radon: GRP")
    else:
        C_Rn_est = C_Rn
        grp = None
        sn.append("radon: measured")
    e_rn = radon_inhalation_dose(C_Rn_est, method=radon_method)
    if C_Tn is None:
        C_Tn_est = geogenic_thoron_potential(A_Th, thoron_emanation, THORON_TRANSFER, lf)
        gtp = C_Tn_est
        sn.append("thoron: GTP")
    else:
        C_Tn_est = C_Tn
        gtp = None
        sn.append("thoron: measured")
    e_tn = thoron_inhalation_dose(
        C_Tn_gas=C_Tn_est, A_Th232=A_Th,
        em=thoron_emanation, lf=lf,
    )
    raeq = radium_equivalent(A_Ra, A_Th, A_K)
    ig = gamma_activity_index(A_Ra, A_Th, A_K)
    e_total = e_ext + e_rn + e_tn
    elcr = excess_lifetime_cancer_risk(e_total)
    risk = risk_class(e_total, C_Rn_est, raeq, gr)
    return {
        "lithology": lithology,
        "lithology_name": glim_name(lithology) if lithology in GLIM_CODE_NAMES else lithology,
        "arms_mSv_yr": {"radon": e_rn, "thoron": e_tn, "gamma": e_ext},
        "activities_Bq_kg": acts,
        "gamma_rate_nGy_h": gr,
        "radon_Bq_m3_est": C_Rn_est,
        "thoron_gas_Bq_m3_est": C_Tn_est,
        "grp": grp,
        "gtp_thoron_gas": gtp,
        "raeq_Bq_kg": raeq,
        "i_gamma": ig,
        "total_terrestrial_mSv_yr": e_total,
        "elcr": elcr,
        "risk": risk,
        "provenance": sn,
    }
