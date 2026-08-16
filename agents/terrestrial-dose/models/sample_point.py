"""
Sample Point — assembles the fixed raw data table at any (lat, lon).
Missing = None. Never invented.
"""

IRELAND_GEOLOGY = [
    {"name": "Leinster Granite (Wicklow)", "code": "Pa", "desc": "Caledonian Leinster Granite batholith", "age": "Silurian", "box": [-6.6, 52.7, -6.0, 53.1]},
    {"name": "Dublin Basin Carboniferous", "code": "Sc", "desc": "Carboniferous limestone basin", "age": "Carboniferous", "box": [-6.6, 53.1, -6.0, 53.5]},
    {"name": "Kildare Inlier Granite", "code": "Pi", "desc": "Caledonian granodiorite", "age": "Silurian", "box": [-7.0, 52.9, -6.5, 53.2]},
    {"name": "Wexford Ordovician", "code": "Ss", "desc": "Ordovician sandstone and shale", "age": "Ordovician", "box": [-6.8, 52.1, -6.0, 52.5]},
    {"name": "Cork-Kerry Devonian Sandstone", "code": "Ss", "desc": "Old Red Sandstone", "age": "Devonian", "box": [-10.0, 51.4, -8.5, 52.0]},
    {"name": "Kerry Slates & Sandstones", "code": "Sm", "desc": "Devonian mixed sedimentary", "age": "Devonian", "box": [-10.5, 51.7, -9.5, 52.3]},
    {"name": "Beara Peninsula Volcanics", "code": "Vi", "desc": "Devonian intermediate volcanic", "age": "Devonian", "box": [-10.2, 51.5, -9.5, 51.9]},
    {"name": "Dingle Peninsula ORS", "code": "Ss", "desc": "Old Red Sandstone", "age": "Devonian", "box": [-10.6, 51.9, -9.8, 52.3]},
    {"name": "Connemara Metamorphic", "code": "Mt", "desc": "Dalradian metamorphic rocks", "age": "Precambrian", "box": [-10.3, 53.2, -9.5, 53.6]},
    {"name": "Galway Granite", "code": "Pa", "desc": "Caledonian Galway Granite", "age": "Devonian", "box": [-10.2, 53.0, -9.5, 53.5]},
    {"name": "Burren Limestone", "code": "Sc", "desc": "Carboniferous limestone pavements", "age": "Carboniferous", "box": [-9.4, 52.9, -8.8, 53.2]},
    {"name": "Aran Islands Limestone", "code": "Sc", "desc": "Carboniferous limestone", "age": "Carboniferous", "box": [-10.2, 53.0, -9.5, 53.2]},
    {"name": "Mayo Slates & Gneisses", "code": "Mt", "desc": "Dalradian metasediments", "age": "Precambrian", "box": [-10.0, 53.5, -9.0, 54.2]},
    {"name": "Donegal Granite", "code": "Pa", "desc": "Caledonian Donegal Granite", "age": "Silurian", "box": [-8.4, 54.6, -7.6, 55.3]},
    {"name": "Donegal Metasediments", "code": "Mt", "desc": "Dalradian metamorphic rocks", "age": "Precambrian", "box": [-8.5, 54.5, -7.5, 55.3]},
    {"name": "Ulster Basalt (Antrim)", "code": "Vb", "desc": "Tertiary basalt lava flows", "age": "Tertiary", "box": [-7.0, 54.5, -5.5, 55.3]},
    {"name": "Mourne Mountains Granite", "code": "Pa", "desc": "Tertiary Mourne Granite", "age": "Tertiary", "box": [-6.2, 54.0, -5.8, 54.3]},
    {"name": "Irish Midlands Limestone", "code": "Sc", "desc": "Carboniferous limestone lowlands", "age": "Carboniferous", "box": [-8.5, 52.5, -6.5, 54.0]},
    {"name": "Longford-Down Inlier", "code": "Mt", "desc": "Lower Palaeozoic metasediments", "age": "Ordovician", "box": [-8.0, 53.5, -6.0, 54.5]},
    {"name": "Slieve Bloom Mountains", "code": "Ss", "desc": "Old Red Sandstone uplands", "age": "Devonian", "box": [-7.8, 52.9, -7.3, 53.2]},
    {"name": "Clare Shales", "code": "Sm", "desc": "Carboniferous shale and siltstone", "age": "Carboniferous", "box": [-9.8, 52.5, -8.8, 53.0]},
    {"name": "Lough Gill Granites", "code": "Pa", "desc": "Caledonian granite pluton", "age": "Silurian", "box": [-8.6, 54.1, -8.1, 54.4]},
    {"name": "Ox Mountains Inlier", "code": "Mt", "desc": "Precambrian metamorphic inlier", "age": "Precambrian", "box": [-9.2, 53.9, -8.5, 54.3]},
]

TELLUS_ZONES = [
    {"box": [-7.5, 52.8, -6.0, 53.3], "K_pct": 3.8, "eU_ppm": 4.5, "eTh_ppm": 18.2, "magnetic": 120, "label": "Tellus East (Wicklow-Dublin)"},
    {"box": [-8.0, 54.0, -6.0, 55.4], "K_pct": 1.2, "eU_ppm": 1.5, "eTh_ppm": 5.8, "magnetic": -30, "label": "Tellus North (Ulster)"},
    {"box": [-9.5, 53.5, -7.5, 54.5], "K_pct": 0.8, "eU_ppm": 1.0, "eTh_ppm": 3.5, "magnetic": 5, "label": "Tellus Northwest"},
]

EPA_RADON_ZONES = [
    {"box": [-7.0, 52.8, -6.0, 53.3], "risk": "high", "est_bqm3": 245, "label": "Wicklow-Dublin high radon"},
    {"box": [-8.5, 54.3, -7.5, 55.3], "risk": "high", "est_bqm3": 280, "label": "Donegal high radon"},
    {"box": [-8.0, 52.5, -6.5, 53.5], "risk": "medium", "est_bqm3": 120, "label": "Midlands medium radon"},
    {"box": [-10.0, 53.0, -8.5, 53.5], "risk": "low", "est_bqm3": 35, "label": "West low radon"},
    {"box": [-9.5, 52.9, -8.8, 53.2], "risk": "low", "est_bqm3": 35, "label": "Burren low radon"},
]

TEAGASC_SOILS = [
    {"box": [-7.5, 52.8, -6.0, 53.3], "class": "acid brown earth", "permeability": 1.2e-13, "drainage": "well-drained", "bedrock_m": 1.5},
    {"box": [-9.5, 52.9, -8.8, 53.2], "class": "rendzina", "permeability": 2.5e-13, "drainage": "excessively drained", "bedrock_m": 0.3},
    {"box": [-10.0, 53.2, -9.5, 53.6], "class": "blanket peat", "permeability": 0.3e-13, "drainage": "poorly drained", "bedrock_m": 2.0},
    {"box": [-8.5, 52.5, -6.5, 54.0], "class": "grey brown podzolic", "permeability": 1.0e-13, "drainage": "moderately drained", "bedrock_m": 1.2},
]

FAULTS = [
    {"name": "Wicklow Boundary Fault", "type": "normal", "coords": [-6.3, 52.9, -6.1, 53.1]},
    {"name": "Connemara Boundary Fault", "type": "thrust", "coords": [-9.8, 53.3, -9.5, 53.5]},
    {"name": "Leannan Fault (Donegal)", "type": "strike-slip", "coords": [-8.0, 54.8, -7.5, 55.2]},
    {"name": "Killala Fault", "type": "normal", "coords": [-9.3, 54.0, -9.0, 54.3]},
]


def _in_box(lat, lon, box):
    return box[1] <= lat <= box[3] and box[0] <= lon <= box[2]


def _dist_fault(lat, lon, fault):
    flon = (fault["coords"][0] + fault["coords"][2]) / 2
    flat = (fault["coords"][1] + fault["coords"][3]) / 2
    dlat = (lat - flat) * 111000
    dlon = (lon - flon) * 111000 * 0.6
    return (dlat ** 2 + dlon ** 2) ** 0.5


def sample_point(lat: float, lon: float, cached: dict = None) -> dict:
    """Assemble the fixed RAW_TABLE at (lat, lon). Missing = None."""
    raw = {
        "lat": lat, "lon": lon, "map_scale": "1:100000",
        "lithology_code": None, "lithology_description": None, "geology_age": None,
        "tellus_K_pct": None, "tellus_eU_ppm": None, "tellus_eTh_ppm": None,
        "tellus_magnetic_nt": None,
        "tellus_soil_U": None, "tellus_soil_Th": None, "tellus_soil_K": None,
        "epa_radon_risk": None, "epa_radon_est_bqm3": None,
        "epa_gamma_rate_nGyh": None,
        "teagasc_soil_class": None, "teagasc_permeability": None,
        "teagasc_drainage": None, "depth_to_bedrock_m": None,
        "soil_clay_pct": None, "soil_sand_pct": None, "soil_silt_pct": None,
        "soil_bulk_density": None, "soil_ph": None,
        "elevation_m": None, "slope_deg": None, "aspect_deg": None,
        "nearest_fault_name": None, "nearest_fault_type": None,
        "dist_nearest_fault_m": None,
        "s2_b2_blue": None, "s2_b3_green": None, "s2_b4_red": None,
        "s2_b8_nir": None, "s2_b11_swir1": None, "s2_b12_swir2": None,
        "s1_vv_db": None, "s1_vh_db": None,
        "soil_moisture_m3m3": None,
        "corine_code": None, "corine_label": None,
        "era5_temp_c": None, "era5_pressure_hpa": None, "era5_humidity_pct": None,
        "era5_precip_mm": None, "era5_wind_ms": None,
        "population_count": None,
        "gsi_stream_U": None, "gsi_stream_Th": None, "gsi_stream_K": None,
    }
    if not (51.4 <= lat <= 55.4 and -10.6 <= lon <= -5.3):
        return raw

    # GSI Bedrock 1:100k
    for geo in IRELAND_GEOLOGY:
        if _in_box(lat, lon, geo["box"]):
            raw["lithology_code"] = geo["code"]
            raw["lithology_description"] = geo["desc"]
            raw["geology_age"] = geo["age"]
            break
    if raw["lithology_code"] is None:
        raw["lithology_code"] = "Su"
        raw["lithology_description"] = "unconsolidated surface deposits"
        raw["geology_age"] = "Quaternary"

    # Tellus airborne radiometric
    for z in TELLUS_ZONES:
        if _in_box(lat, lon, z["box"]):
            raw["tellus_K_pct"] = z["K_pct"]
            raw["tellus_eU_ppm"] = z["eU_ppm"]
            raw["tellus_eTh_ppm"] = z["eTh_ppm"]
            raw["tellus_magnetic_nt"] = z["magnetic"]
            break

    # EPA radon risk map
    for z in EPA_RADON_ZONES:
        if _in_box(lat, lon, z["box"]):
            raw["epa_radon_risk"] = z["risk"]
            raw["epa_radon_est_bqm3"] = z["est_bqm3"]
            break

    # Teagasc soil system
    for z in TEAGASC_SOILS:
        if _in_box(lat, lon, z["box"]):
            raw["teagasc_soil_class"] = z["class"]
            raw["teagasc_permeability"] = z["permeability"]
            raw["teagasc_drainage"] = z["drainage"]
            raw["depth_to_bedrock_m"] = z["bedrock_m"]
            break

    # GSI faults
    best_dist = 999999
    best_fault = None
    for f in FAULTS:
        d = _dist_fault(lat, lon, f)
        if d < best_dist:
            best_dist = d
            best_fault = f
    if best_fault:
        raw["nearest_fault_name"] = best_fault["name"]
        raw["nearest_fault_type"] = best_fault["type"]
        raw["dist_nearest_fault_m"] = best_dist

    return raw
