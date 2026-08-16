"""
models/point_table.py

The fixed raw data table schema. Every hovered point fills this table with RAW values only.
No derived values, no analysis, no dose math. Missing = None.
"""

RAW_TABLE_SCHEMA = {
    # Location
    "lat": float,
    "lon": float,
    "map_scale": str,
    # Geology (raw mapped class — NOT activities)
    "lithology_code": str,
    "lithology_description": str,
    "geology_age": str,
    # Soil (raw SoilGrids — NOT permeability estimate)
    "soil_clay_pct": float,
    "soil_sand_pct": float,
    "soil_silt_pct": float,
    "soil_bulk_density": float,
    "depth_to_bedrock_m": float,
    "soil_ph": float,
    # Terrain (raw DEM — NOT lineament density)
    "elevation_m": float,
    "slope_deg": float,
    "aspect_deg": float,
    # Structural (raw fault geometry)
    "nearest_fault_name": str,
    "nearest_fault_type": str,
    "dist_nearest_fault_m": float,
    # Sentinel-2 (raw band reflectances — NOT indices)
    "s2_b2_blue": float,
    "s2_b3_green": float,
    "s2_b4_red": float,
    "s2_b8_nir": float,
    "s2_b11_swir1": float,
    "s2_b12_swir2": float,
    # Sentinel-1 (raw backscatter)
    "s1_vv_db": float,
    "s1_vh_db": float,
    # Soil moisture (raw satellite)
    "soil_moisture_m3m3": float,
    # Land cover (raw code)
    "corine_code": str,
    "corine_label": str,
    # Meteorology (raw ERA5)
    "era5_temp_c": float,
    "era5_pressure_hpa": float,
    "era5_humidity_pct": float,
    "era5_precip_mm": float,
    "era5_wind_ms": float,
    # Geophysics (raw anomaly)
    "emag2_magnetic_nt": float,
    "wgm_gravity_mgal": float,
    # Population (raw census)
    "population_count": int,
    # Measured radiation (raw — for validation only; None if not nearby)
    "foregs_eU_ppm": float,
    "foregs_eTh_ppm": float,
    "foregs_K_pct": float,
    "jrc_indoor_rn": float,
    "jrc_gamma_rate": float,
    "jrc_soil_K": float,
    "jrc_soil_U": float,
    "jrc_soil_Th": float,
}


def empty_raw_table(lat: float, lon: float) -> dict:
    """Return a raw table with all fields set to None, plus lat/lon."""
    table = {k: None for k in RAW_TABLE_SCHEMA}
    table["lat"] = lat
    table["lon"] = lon
    return table

