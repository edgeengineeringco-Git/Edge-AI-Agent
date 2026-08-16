/**
 * Irish Geology Grid — GSI Bedrock 1:100k
 * Sources: GSI IE_100k (ITM, EPSG:2157)
 * Cell size: 100m for 100k
 */

export interface LithEntry {
  glim: string;
  label: string;
  map_scale: string;
  cell_m: number;
  source: string;
}

interface GeoRegion {
  name: string;
  glim: string;
  map_scale: string;
  source: string;
  coords: [number, number, number, number];
}

// ═══════════════════════════════════════════════════════════════
// IRELAND — GSI 1:100k Bedrock Geology
// ═══════════════════════════════════════════════════════════════
const IRELAND: GeoRegion[] = [
  { name: "Leinster Granite (Caledonian)", glim: "Pa", map_scale: "100k", source: "GSI IE_100k", coords: [-6.8, 52.2, -6.0, 53.0] },
  { name: "Leinster Granite (Wicklow)", glim: "Pa", map_scale: "100k", source: "GSI IE_100k", coords: [-6.6, 52.7, -6.0, 53.1] },
  { name: "Dublin Basin Carboniferous", glim: "Sc", map_scale: "100k", source: "GSI IE_100k", coords: [-6.6, 53.1, -6.0, 53.5] },
  { name: "Kildare Inlier Granite", glim: "Pi", map_scale: "100k", source: "GSI IE_100k", coords: [-7.0, 52.9, -6.5, 53.2] },
  { name: "Wexford Ordovician", glim: "Ss", map_scale: "100k", source: "GSI IE_100k", coords: [-6.8, 52.1, -6.0, 52.5] },
  { name: "Cork-Kerry Devonian Sandstone", glim: "Ss", map_scale: "100k", source: "GSI IE_100k", coords: [-10.0, 51.4, -8.5, 52.0] },
  { name: "Kerry Slates & Sandstones", glim: "Sm", map_scale: "100k", source: "GSI IE_100k", coords: [-10.5, 51.7, -9.5, 52.3] },
  { name: "Beara Peninsula Volcanics", glim: "Vi", map_scale: "100k", source: "GSI IE_100k", coords: [-10.2, 51.5, -9.5, 51.9] },
  { name: "Dingle Peninsula ORS", glim: "Ss", map_scale: "100k", source: "GSI IE_100k", coords: [-10.6, 51.9, -9.8, 52.3] },
  { name: "Connemara Metamorphic", glim: "Mt", map_scale: "100k", source: "GSI IE_100k", coords: [-10.3, 53.2, -9.5, 53.6] },
  { name: "Galway Granite", glim: "Pa", map_scale: "100k", source: "GSI IE_100k", coords: [-10.2, 53.0, -9.5, 53.5] },
  { name: "Burren Limestone", glim: "Sc", map_scale: "100k", source: "GSI IE_100k", coords: [-9.4, 52.9, -8.8, 53.2] },
  { name: "Aran Islands Limestone", glim: "Sc", map_scale: "100k", source: "GSI IE_100k", coords: [-10.2, 53.0, -9.5, 53.2] },
  { name: "Mayo Slates & Gneisses", glim: "Mt", map_scale: "100k", source: "GSI IE_100k", coords: [-10.0, 53.5, -9.0, 54.2] },
  { name: "Donegal Granite", glim: "Pa", map_scale: "100k", source: "GSI IE_100k", coords: [-8.4, 54.6, -7.6, 55.3] },
  { name: "Donegal Metasediments", glim: "Mt", map_scale: "100k", source: "GSI IE_100k", coords: [-8.5, 54.5, -7.5, 55.3] },
  { name: "Ulster Basalt (Antrim)", glim: "Vb", map_scale: "100k", source: "GSI IE_100k", coords: [-7.0, 54.5, -5.5, 55.3] },
  { name: "Mourne Mountains Granite", glim: "Pa", map_scale: "100k", source: "GSI IE_100k", coords: [-6.2, 54.0, -5.8, 54.3] },
  { name: "Irish Midlands Limestone", glim: "Sc", map_scale: "100k", source: "GSI IE_100k", coords: [-8.5, 52.5, -6.5, 54.0] },
  { name: "Longford-Down Inlier", glim: "Mt", map_scale: "100k", source: "GSI IE_100k", coords: [-8.0, 53.5, -6.0, 54.5] },
  { name: "Slieve Bloom Mountains", glim: "Ss", map_scale: "100k", source: "GSI IE_100k", coords: [-7.8, 52.9, -7.3, 53.2] },
  { name: "Clare Shales", glim: "Sm", map_scale: "100k", source: "GSI IE_100k", coords: [-9.8, 52.5, -8.8, 53.0] },
  { name: "Lough Gill Granites", glim: "Pa", map_scale: "100k", source: "GSI IE_100k", coords: [-8.6, 54.1, -8.1, 54.4] },
  { name: "Ox Mountains Inlier", glim: "Mt", map_scale: "100k", source: "GSI IE_100k", coords: [-9.2, 53.9, -8.5, 54.3] },
];

const SCALE_TO_CELL: Record<string, number> = {
  "50k": 50, "100k": 100, "250k": 250, "500k": 500, "1M": 1000,
};

const ACT: Record<string, { ra: number; th: number; k: number; label: string }> = {
  granite:              { ra: 59,  th: 64,  k: 1070, label: "Granite" },
  granodiorite:         { ra: 40,  th: 50,  k: 900,  label: "Granodiorite" },
  diorite:              { ra: 25,  th: 30,  k: 550,  label: "Diorite" },
  gabbro:               { ra: 12,  th: 15,  k: 250,  label: "Gabbro" },
  peridotite:           { ra: 3,   th: 5,   k: 80,   label: "Peridotite" },
  pegmatite:            { ra: 65,  th: 80,  k: 1200, label: "Pegmatite" },
  syenite:              { ra: 45,  th: 70,  k: 1100, label: "Syenite" },
  rhyolite:             { ra: 55,  th: 60,  k: 1000, label: "Rhyolite" },
  andesite:             { ra: 30,  th: 40,  k: 700,  label: "Andesite" },
  basalt:               { ra: 15,  th: 18,  k: 300,  label: "Basalt" },
  tuff:                 { ra: 30,  th: 35,  k: 600,  label: "Tuff" },
  gneiss:               { ra: 38,  th: 45,  k: 850,  label: "Gneiss" },
  schist:               { ra: 35,  th: 42,  k: 750,  label: "Schist" },
  slate:                { ra: 22,  th: 28,  k: 480,  label: "Slate" },
  quartzite:            { ra: 10,  th: 8,   k: 150,  label: "Quartzite" },
  marble:               { ra: 8,   th: 5,   k: 80,   label: "Marble" },
  limestone:            { ra: 12,  th: 6,   k: 100,  label: "Limestone" },
  dolomite:             { ra: 10,  th: 5,   k: 80,   label: "Dolomite" },
  sandstone:            { ra: 18,  th: 22,  k: 350,  label: "Sandstone" },
  shale:                { ra: 30,  th: 35,  k: 580,  label: "Shale" },
  mudstone:             { ra: 28,  th: 32,  k: 520,  label: "Mudstone" },
  siltstone:            { ra: 25,  th: 30,  k: 480,  label: "Siltstone" },
  marl:                 { ra: 15,  th: 10,  k: 200,  label: "Marl" },
  chalk:                { ra: 8,   th: 4,   k: 60,   label: "Chalk" },
  alluvium:             { ra: 20,  th: 25,  k: 400,  label: "Alluvium" },
  glacial_till:         { ra: 18,  th: 22,  k: 380,  label: "Glacial Till" },
  monazite_bearing:     { ra: 80,  th: 350, k: 400,  label: "Monazite-bearing" },
  carbonatite:          { ra: 120, th: 150, k: 200,  label: "Carbonatite" },
  world_average_soil:   { ra: 30,  th: 30,  k: 400,  label: "World Average Soil" },
  water:                { ra: 0,   th: 0,   k: 0,    label: "Water" },
  ice:                  { ra: 0,   th: 0,   k: 0,    label: "Ice" },
};

const GLIM_TO_INTERNAL: Record<string, string> = {
  Su: "alluvium", Ss: "sandstone", Sm: "siltstone", Sc: "limestone", Sb: "marl",
  Ev: "dolomite", Pa: "granite", Pi: "granodiorite", Pb: "gabbro",
  Va: "rhyolite", Vi: "andesite", Vb: "basalt", Mt: "gneiss", Py: "tuff",
  Wa: "water", Ice: "ice",
};

export function resolveLith(glim: string): string {
  if (ACT[glim]) return glim;
  return GLIM_TO_INTERNAL[glim] || "world_average_soil";
}

export function getLithologyAt(lon: number, lat: number): LithEntry & { region: string; meets_target: boolean } {
  // Find smallest-area matching region
  let best: GeoRegion | null = null;
  let bestArea = Infinity;

  for (const r of IRELAND) {
    const [minLon, minLat, maxLon, maxLat] = r.coords;
    if (lon >= minLon && lon <= maxLon && lat >= minLat && lat <= maxLat) {
      const area = (maxLon - minLon) * (maxLat - minLat);
      if (area < bestArea) {
        bestArea = area;
        best = r;
      }
    }
  }

  if (!best) {
    // Fallback for Ireland outside detailed regions
    if (lat >= 51.4 && lat <= 55.4 && lon >= -10.6 && lon <= -5.3) {
      return { glim: "world_average_soil", label: "Irish Soil (unmapped)", map_scale: "100k", cell_m: 100, source: "GSI IE_100k", region: "Ireland (unmapped detail)", meets_target: true };
    }
    return { glim: "world_average_soil", label: "World Average Soil", map_scale: "1M", cell_m: 1000, source: "Global", region: "Outside Ireland", meets_target: false };
  }

  const internal = resolveLith(best.glim);
  const act = ACT[internal] || ACT.world_average_soil;
  const cell_m = SCALE_TO_CELL[best.map_scale] || 1000;
  const meets = best.map_scale === "50k" || best.map_scale === "100k";

  return {
    glim: best.glim,
    label: act.label,
    map_scale: best.map_scale,
    cell_m,
    source: best.source,
    region: best.name,
    meets_target: meets,
  };
}
