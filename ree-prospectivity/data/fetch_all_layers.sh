#!/usr/bin/env bash
# ============================================================================
# fetch_all_layers.sh  —  Reproducible data acquisition for the
# National REE Prospectivity System for Ireland (L1–L18).
#
#   bash data/fetch_all_layers.sh [OUTDIR]
#
# Each block pulls ONE layer from its authoritative OPEN source.
# Status (see layer_confirmation.csv / data_access_report.md):
#   OK       = fetched successfully this session
#   BLOCKED  = source requires GSI auth token or is not openly published
#   PENDING  = requires Copernicus auth + scene compositing (heavy)
# The 13 OK layers below are reproducible on demand; the 5 BLOCKED/PENDING
# are documented with their exact barriers so they can be closed later.
# ============================================================================
set -u
OUT="${1:-data/raw}"; mkdir -p "$OUT"
G="https://gsi.geodata.gov.ie"

dl(){ curl -s -L -o "$2" "$1" -w "  -> %{http_code} %{size_download}B  $2\n"; }

echo "=== L1-L3  Airborne radiometrics eTh/eU/K (genuine GSI Tellus, resampled grid) ==="
dl "https://raw.githubusercontent.com/edgeengineeringco-Git/edge-ai-agent-site/main/data/radiometrics/values.bin" "$OUT/values.bin"

echo "=== L4  Magnetics TMI  [BLOCKED: GSI ImageServer 499 Token Required; no ROI magnetic REST service] ==="
echo "  Closure: obtain a GSI token (generateToken) OR use BGS Tellus NI-border magnetic grid."

echo "=== L5 / L6  Tellus stream SEDIMENT / WATER geochemistry (XLSX) ==="
dl "$G/downloads/Geochemistry/Data/GSI_Tellus_C_stream_sediment_geochemistry.zip" "$OUT/L5_stream_sediment.zip"
dl "$G/downloads/Geochemistry/Data/GSI_Tellus_W_stream_water_geochemistry.zip"    "$OUT/L6_stream_water.zip"

echo "=== L7 / L9 / L10 / L11  GSI FeatureServers (real geometry + attributes) ==="
fs(){ python3 - "$1" "$2" <<'PY'
import requests,json,sys,time
svc,out=sys.argv[1],sys.argv[2]
base=f"https://gsi.geodata.gov.ie/server/rest/services/{svc}/FeatureServer/0"
mrc=requests.get(base,params={"f":"json"},timeout=30).json().get("maxRecordCount",1000); step=min(1000,mrc)
cnt=requests.get(base+"/query",params={"where":"1=1","returnCountOnly":"true","f":"json"},timeout=30).json().get("count",0)
print(f"  {svc}: {cnt} features")
feats=[]; off=0
while True:
    g=requests.get(base+"/query",params={"where":"1=1","outFields":"*","returnGeometry":"true",
        "f":"geojson","resultOffset":off,"resultRecordCount":step},timeout=120).json()
    fs=g.get("features",[]); feats.extend(fs)
    if len(fs)<step: break
    off+=step; time.sleep(0.02)
json.dump({"type":"FeatureCollection","features":feats},open(out,"w"))
print(f"  saved {out} ({len(feats)})")
PY
}
fs "Geochemistry/IE_GSI_Geochemistry_Deeper_Topsoil_S_XRFS_IE26_ITM" "$OUT/L7_soil_xrfs.geojson"
fs "Quaternary/IE_GSI_Quaternary_Sediments_50K_IE26_ITM"           "$OUT/L9_quaternary.geojson"
fs "Minerals/IE_GSI_Mineral_Locations_IE26_ITM"                    "$OUT/L10_mineral_locations.geojson"
fs "Minerals/IE_GSI_MINERAL_EXPLORATION_BOREHOLES_50K_IE26_ITM"     "$OUT/L11_boreholes.geojson"

echo "=== L8  Bedrock 1:100k (SHP) ==="
dl "$G/downloads/Bedrock/Data/IE_GSI_Bedrock_Geology_Datasets_100K_IE26_ITM.zip" "$OUT/bedrock_100k.zip"

echo "=== L12 / L13  MPM soils 345k / lineaments  [BLOCKED: not openly published; L13 depends on L4] ==="

echo "=== L14  Copernicus DEM GLO-30 (AWS, national mosaic of N5xW0xx tiles) ==="
for t in N51W006 N51W009 N52W006 N52W009 N53W006 N53W009 N54W006 N54W009 N55W006 N55W009 N56W006 N56W009; do
  dl "https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_${t}_00_DEM/Copernicus_DSM_COG_10_${t}_00_DEM.tif" "$OUT/DEM_${t}.tif"
done

echo "=== L15  ESA WorldCover 10m 2021 v200 (AWS, Ireland tiles) ==="
for t in N51W006 N51W009 N52W006 N52W009 N53W006 N53W009 N54W006 N54W009 N55W006 N55W009; do
  dl "https://esa-worldcover.s3.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_${t}_Map.tif" "$OUT/WC_${t}.tif"
done

echo "=== L16  Sentinel-2 L2A  [PENDING: needs Copernicus auth + cloud-masked compositing] ==="

echo "=== L17  GSRO prospecting licences  [BLOCKED: onshore licences not openly published] ==="
echo "  Offshore petroleum authorisations (if needed):"
echo "    atlas.marine.ie/midata/EnergyResourcesExploration/Current_Authorisations.shapezip.zip"

echo "=== L18  NPWS SAC / SPA / pNHA ==="
dl "https://www.npws.ie/sites/default/files/files/SAC_datasheets_20231017.zip" "$OUT/SAC_datasheets_20231017.zip"
dl "https://www.npws.ie/sites/default/files/files/SPA_datasheets_20231017.zip" "$OUT/SPA_datasheets_20231017.zip"
dl "https://www.npws.ie/sites/default/files/files/pNHA_ITM_2015_11.zip"        "$OUT/pNHA_ITM_2015_11.zip"
echo "DONE. Cross-check against layer_confirmation.csv + data_access_report.md."
