"""
Terrestrial Radiation Dose Calculation Core
The SINGLE SOURCE OF TRUTH for all dose numbers. Import. Do not rewrite.
"""

BQ_PER_PPM_U = 12.22
BQ_PER_PPM_TH = 4.06
BQ_PER_PCT_K = 313.0

def ppm_to_bqkg(eU_ppm=None, eTh_ppm=None, K_pct=None):
    out = {}
    if eU_ppm is not None:  out["A_Ra226"] = eU_ppm * BQ_PER_PPM_U
    if eTh_ppm is not None: out["A_Th232"] = eTh_ppm * BQ_PER_PPM_TH
    if K_pct is not None:   out["A_K40"]   = K_pct * BQ_PER_PCT_K
    return out

LITHOLOGY_ACTIVITIES = {
    "Su":(30,35,450),"Ss":(35,35,400),"Sm":(35,40,500),"Sc":(20,12,90),
    "Sb":(25,30,600),"Ev":(12,8,120),"Pa":(60,80,1200),"Pi":(30,40,800),
    "Pb":(12,18,300),"Va":(50,70,1100),"Vi":(25,35,700),"Vb":(15,20,350),
    "Mt":(45,55,850),"Py":(40,45,700),"Wa":(0,0,0),"Ice":(0,0,0),
    "granite":(60,80,1200),"monzogranite":(29,34,883),"syenogranite":(31,35,890),
    "rhyolite":(50,70,1100),"pegmatite":(80,100,1400),"diorite":(30,40,800),
    "andesite":(25,35,700),"syenite":(40,60,900),"basalt":(15,20,350),
    "gabbro":(12,18,300),"dolerite":(15,22,380),"peridotite":(8,10,100),
    "serpentinite":(10,12,120),"sandstone":(35,35,400),"arkose":(40,45,600),
    "shale":(40,50,700),"mudstone":(35,45,650),"siltstone":(30,38,500),
    "limestone":(20,12,90),"dolomite":(18,10,80),"chalk":(15,8,70),
    "gypsum":(12,8,120),"halite":(5,3,40),"phosphate":(1000,50,100),
    "schist":(40,45,700),"gneiss":(45,55,850),"quartzite":(25,28,350),
    "marble":(15,10,90),"slate":(40,48,680),"phyllite":(35,42,600),
    "monazite_bearing":(100,800,300),"carbonatite":(500,400,800),
    "uranium_mineralised":(5000,80,800),"coal_bearing":(60,35,200),
    "black_shale":(150,25,600),"alluvium":(30,35,450),
    "world_average_soil":(35,30,420),
}
GLIM_CODE_NAMES = {
    "Su":"unconsolidated sediments","Ss":"siliciclastic sedimentary",
    "Sm":"mixed sedimentary","Sc":"carbonate sedimentary","Sb":"basic pyroclastic",
    "Ev":"evaporite","Pa":"acid plutonic (granite)","Pi":"intermediate plutonic",
    "Pb":"basic plutonic","Va":"acid volcanic","Vi":"intermediate volcanic",
    "Vb":"basic volcanic","Mt":"metamorphic","Py":"pyroclastic",
    "Wa":"water","Ice":"ice",
}
LITHOLOGY_FACTOR = {
    "Su":1.5,"Ss":1.4,"Sm":1.2,"Sc":0.7,"Sb":1.0,"Ev":0.4,"Pa":1.3,"Pi":1.0,
    "Pb":0.6,"Va":1.2,"Vi":0.9,"Vb":0.7,"Mt":1.2,"Py":1.1,"Wa":0.0,"Ice":0.0,
    "granite":1.3,"monzogranite":1.2,"rhyolite":1.2,"pegmatite":1.5,"syenite":1.3,
    "diorite":1.0,"andesite":0.9,"basalt":0.7,"gabbro":0.6,"dolerite":0.7,
    "peridotite":0.5,"serpentinite":0.6,"sandstone":1.4,"arkose":1.3,"shale":0.8,
    "mudstone":0.8,"siltstone":1.0,"limestone":0.7,"dolomite":0.7,"chalk":0.6,
    "gypsum":0.6,"halite":0.4,"phosphate":1.2,"schist":1.1,"gneiss":1.2,
    "quartzite":1.0,"marble":0.6,"slate":0.8,"phyllite":0.9,
    "monazite_bearing":2.0,"carbonatite":1.8,"uranium_mineralised":2.5,
    "coal_bearing":1.0,"black_shale":1.3,"alluvium":1.5,"world_average_soil":1.0,
}

def lithology_to_activities(lithology):
    if lithology in LITHOLOGY_ACTIVITIES:
        ra,th,k = LITHOLOGY_ACTIVITIES[lithology]
        return {"A_Ra226":ra,"A_Th232":th,"A_K40":k}
    return None

def lithology_factor(lithology, default=1.0):
    return LITHOLOGY_FACTOR.get(lithology, default)

def glim_name(code):
    return GLIM_CODE_NAMES.get(code, code)

WORLD_AVG_DOSE = 2.2
GAMMA_RATE_WORLD_AVG = 59.0

DCC_RA = 0.462; DCC_TH = 0.604; DCC_K = 0.041
HOURS_PER_YEAR = 8760.0; CC_SV_PER_GY = 0.7

def external_gamma_dose_rate(A_Ra226, A_Th232, A_K40):
    return DCC_RA*A_Ra226 + DCC_TH*A_Th232 + DCC_K*A_K40

def annual_external_dose(A_Ra226, A_Th232, A_K40, occupancy=0.2, indoor=False):
    d_air = external_gamma_dose_rate(A_Ra226, A_Th232, A_K40)
    of = 0.8 if indoor else occupancy
    return d_air * HOURS_PER_YEAR * of * CC_SV_PER_GY * 1e-6

RADON_EUBSS_FACTOR = 10.0 / 300.0
PAEC_PER_BQ_EEC = 5.57e-6
ICRP137_COEFF = 3.0
DCF_ICRP137 = PAEC_PER_BQ_EEC * ICRP137_COEFF * 1e6
DCF_UNSCEAR = 9.0; DCF_ICRP65_RES = 6.1
F_INDOOR = 0.4; F_OUTDOOR = 0.6
T_INDOOR = 7000.0; T_OUTDOOR = 1760.0

def radon_inhalation_dose(C_Rn, method="eubss", F=F_INDOOR, T=T_INDOOR):
    if method == "eubss": return C_Rn * RADON_EUBSS_FACTOR
    dcf = {"icrp137":DCF_ICRP137,"unscear":DCF_UNSCEAR,"icrp65":DCF_ICRP65_RES}[method]
    return C_Rn * F * dcf * T * 1e-6

def geogenic_radon_potential(A_Ra226, permeability=1e-13, dist_fault_m=1000.0,
                             lineament_density=0.5, lithology_factor=1.0):
    perm_term = (permeability / 1e-13) ** 0.5
    fault_term = max(0.0, 1.0 - dist_fault_m / 2000.0)
    line_term = min(1.0, lineament_density / 2.0)
    return (A_Ra226 / 50.0) * perm_term * (1 + 0.3*fault_term) * (1 + 0.2*line_term) * lithology_factor

THORON_EMANATION_DEFAULT = 0.3; THORON_TRANSFER_COEFF = 2.0
F_THORON = 0.02; DCF_THORON = 40.0

def geogenic_thoron_potential(A_Th232, emanation=THORON_EMANATION_DEFAULT,
                              transfer_coeff=THORON_TRANSFER_COEFF, lithology_factor=1.0):
    return A_Th232 * emanation * transfer_coeff * lithology_factor

def thoron_inhalation_dose(C_Tn_gas=None, A_Th232=None, emanation=THORON_EMANATION_DEFAULT,
                           transfer_coeff=THORON_TRANSFER_COEFF, lithology_factor=1.0,
                           F_Tn=F_THORON, DCF=DCF_THORON, T=T_INDOOR):
    if C_Tn_gas is None:
        if A_Th232 is None: raise ValueError("Provide C_Tn_gas or A_Th232.")
        C_Tn_gas = geogenic_thoron_potential(A_Th232, emanation, transfer_coeff, lithology_factor)
    return C_Tn_gas * F_Tn * DCF * T * 1e-6

def radium_equivalent(A_Ra226, A_Th232, A_K40):
    return A_Ra226 + 1.43*A_Th232 + 0.077*A_K40

def gamma_activity_index(A_Ra226, A_Th232, A_K40):
    return A_Ra226/300.0 + A_Th232/200.0 + A_K40/3000.0

def excess_lifetime_cancer_risk(E_annual_mSv, life_expectancy=70.0, risk_factor=0.05):
    return E_annual_mSv * 1e-3 * life_expectancy * risk_factor

RADON_ACTION_LEVEL = 300.0; RADON_WHO_LEVEL = 100.0
RAEQ_THRESHOLD = 370.0; GAMMA_RATE_ICRP_SAFE = 1000.0

def risk_class(E_terrestrial_mSv, C_Rn=None, raeq=None, gamma_rate=None):
    rationale = []; flags = []
    if E_terrestrial_mSv <= WORLD_AVG_DOSE:
        tier = "GREEN"; rationale.append(f"{E_terrestrial_mSv:.2f} <= {WORLD_AVG_DOSE}")
    elif E_terrestrial_mSv <= 3*WORLD_AVG_DOSE:
        tier = "AMBER"; rationale.append(f"{E_terrestrial_mSv:.2f} 1-3x avg")
    else:
        tier = "RED"; rationale.append(f"{E_terrestrial_mSv:.2f} > 3x avg")
    if C_Rn is not None and C_Rn >= RADON_ACTION_LEVEL:
        flags.append(f"RADON_ACTION {C_Rn:.0f}>=300"); tier = "RED"
    elif C_Rn is not None and C_Rn >= RADON_WHO_LEVEL:
        flags.append(f"RADON_ELEVATED {C_Rn:.0f}>=100")
        if tier == "GREEN": tier = "AMBER"
    if raeq is not None and raeq >= RAEQ_THRESHOLD:
        flags.append(f"RAEQ_HIGH {raeq:.0f}>=370")
        if tier != "RED": tier = "RED"
    if gamma_rate is not None and gamma_rate >= GAMMA_RATE_ICRP_SAFE:
        flags.append(f"GAMMA_HIGH {gamma_rate:.0f}>=1000"); tier = "RED"
    return {"tier": tier, "rationale": rationale, "flags": flags}

def polygon_dose_fingerprint(lithology="Su", eU_ppm=None, eTh_ppm=None, K_pct=None,
                             C_Rn=None, C_Tn=None, occupancy=0.2,
                             permeability=1e-13, dist_fault_m=1000.0,
                             lineament_density=0.5, radon_method="eubss",
                             thoron_emanation=THORON_EMANATION_DEFAULT):
    prior = lithology_to_activities(lithology) or {}
    lf = lithology_factor(lithology); source_note = []
    meas = ppm_to_bqkg(eU_ppm, eTh_ppm, K_pct); acts = dict(prior)
    for k in ("A_Ra226","A_Th232","A_K40"):
        if k in meas: acts[k] = meas[k]; source_note.append(f"{k}: measured")
        elif k in prior:
            src = f"GLiM {glim_name(lithology)}" if lithology in GLIM_CODE_NAMES else lithology
            source_note.append(f"{k}: geology prior ({src})")
    A_Ra = acts.get("A_Ra226",35.0); A_Th = acts.get("A_Th232",30.0); A_K = acts.get("A_K40",420.0)
    e_ext = annual_external_dose(A_Ra, A_Th, A_K, occupancy=occupancy)
    gamma_rate = external_gamma_dose_rate(A_Ra, A_Th, A_K)
    if C_Rn is None:
        grp = geogenic_radon_potential(A_Ra, permeability, dist_fault_m, lineament_density, lf)
        C_Rn_est = grp * 50.0; source_note.append("radon: geogenic GRP")
    else: C_Rn_est = C_Rn; grp = None; source_note.append("radon: measured")
    e_rn = radon_inhalation_dose(C_Rn_est, method=radon_method)
    if C_Tn is None:
        C_Tn_gas_est = geogenic_thoron_potential(A_Th, thoron_emanation, THORON_TRANSFER_COEFF, lf)
        gtp = C_Tn_gas_est; source_note.append("thoron: geogenic GTP")
    else: C_Tn_gas_est = C_Tn; gtp = None; source_note.append("thoron: measured")
    e_tn = thoron_inhalation_dose(C_Tn_gas=C_Tn_gas_est, A_Th232=A_Th,
                                   emanation=thoron_emanation, lithology_factor=lf)
    raeq = radium_equivalent(A_Ra, A_Th, A_K)
    i_gamma = gamma_activity_index(A_Ra, A_Th, A_K)
    e_total = e_ext + e_rn + e_tn
    elcr = excess_lifetime_cancer_risk(e_total)
    risk = risk_class(e_total, C_Rn_est, raeq, gamma_rate)
    return {
        "lithology": lithology,
        "lithology_name": glim_name(lithology) if lithology in GLIM_CODE_NAMES else lithology,
        "arms_mSv_yr": {"radon": e_rn, "thoron": e_tn, "gamma": e_ext},
        "activities_Bq_kg": acts, "gamma_rate_nGy_h": gamma_rate,
        "radon_Bq_m3_est": C_Rn_est, "thoron_gas_Bq_m3_est": C_Tn_gas_est,
        "grp": grp, "gtp_thoron_gas": gtp, "raeq_Bq_kg": raeq,
        "i_gamma": i_gamma, "total_terrestrial_mSv_yr": e_total,
        "elcr": elcr, "risk": risk, "provenance": source_note,
    }
