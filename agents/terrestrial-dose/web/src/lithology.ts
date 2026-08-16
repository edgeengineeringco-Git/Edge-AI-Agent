/** Ireland-specific geological provinces — GSI Bedrock 1:100k simplified */
export interface GeoRegion {
  name: string; code: string; desc: string; age: string;
  box: [number, number, number, number];
}

export const IRELAND_GEOLOGY: GeoRegion[] = [
  { name: "Leinster Granite (Wicklow)", code: "Pa", desc: "Caledonian Leinster Granite batholith", age: "Silurian", box: [-6.6, 52.7, -6.0, 53.1] },
  { name: "Dublin Basin Carboniferous", code: "Sc", desc: "Carboniferous limestone basin", age: "Carboniferous", box: [-6.6, 53.1, -6.0, 53.5] },
  { name: "Kildare Inlier Granite", code: "Pi", desc: "Caledonian granodiorite", age: "Silurian", box: [-7.0, 52.9, -6.5, 53.2] },
  { name: "Wexford Ordovician", code: "Ss", desc: "Ordovician sandstone", age: "Ordovician", box: [-6.8, 52.1, -6.0, 52.5] },
  { name: "Cork-Kerry Devonian Sandstone", code: "Ss", desc: "Old Red Sandstone", age: "Devonian", box: [-10.0, 51.4, -8.5, 52.0] },
  { name: "Kerry Slates & Sandstones", code: "Sm", desc: "Devonian mixed sedimentary", age: "Devonian", box: [-10.5, 51.7, -9.5, 52.3] },
  { name: "Beara Peninsula Volcanics", code: "Vi", desc: "Devonian intermediate volcanic", age: "Devonian", box: [-10.2, 51.5, -9.5, 51.9] },
  { name: "Dingle Peninsula ORS", code: "Ss", desc: "Old Red Sandstone", age: "Devonian", box: [-10.6, 51.9, -9.8, 52.3] },
  { name: "Connemara Metamorphic", code: "Mt", desc: "Dalradian metamorphic rocks", age: "Precambrian", box: [-10.3, 53.2, -9.5, 53.6] },
  { name: "Galway Granite", code: "Pa", desc: "Caledonian Galway Granite", age: "Devonian", box: [-10.2, 53.0, -9.5, 53.5] },
  { name: "Burren Limestone", code: "Sc", desc: "Carboniferous limestone pavements", age: "Carboniferous", box: [-9.4, 52.9, -8.8, 53.2] },
  { name: "Aran Islands Limestone", code: "Sc", desc: "Carboniferous limestone", age: "Carboniferous", box: [-10.2, 53.0, -9.5, 53.2] },
  { name: "Mayo Slates & Gneisses", code: "Mt", desc: "Dalradian metasediments", age: "Precambrian", box: [-10.0, 53.5, -9.0, 54.2] },
  { name: "Donegal Granite", code: "Pa", desc: "Caledonian Donegal Granite", age: "Silurian", box: [-8.4, 54.6, -7.6, 55.3] },
  { name: "Donegal Metasediments", code: "Mt", desc: "Dalradian metamorphic rocks", age: "Precambrian", box: [-8.5, 54.5, -7.5, 55.3] },
  { name: "Ulster Basalt (Antrim)", code: "Vb", desc: "Tertiary basalt lava flows", age: "Tertiary", box: [-7.0, 54.5, -5.5, 55.3] },
  { name: "Mourne Mountains Granite", code: "Pa", desc: "Tertiary Mourne Granite", age: "Tertiary", box: [-6.2, 54.0, -5.8, 54.3] },
  { name: "Irish Midlands Limestone", code: "Sc", desc: "Carboniferous limestone lowlands", age: "Carboniferous", box: [-8.5, 52.5, -6.5, 54.0] },
  { name: "Longford-Down Inlier", code: "Mt", desc: "Lower Palaeozoic metasediments", age: "Ordovician", box: [-8.0, 53.5, -6.0, 54.5] },
  { name: "Slieve Bloom Mountains", code: "Ss", desc: "Old Red Sandstone uplands", age: "Devonian", box: [-7.8, 52.9, -7.3, 53.2] },
  { name: "Clare Shales", code: "Sm", desc: "Carboniferous shale", age: "Carboniferous", box: [-9.8, 52.5, -8.8, 53.0] },
  { name: "Lough Gill Granites", code: "Pa", desc: "Caledonian granite pluton", age: "Silurian", box: [-8.6, 54.1, -8.1, 54.4] },
  { name: "Ox Mountains Inlier", code: "Mt", desc: "Precambrian metamorphic inlier", age: "Precambrian", box: [-9.2, 53.9, -8.5, 54.3] },
];

export function inBox(lat: number, lon: number, box: [number, number, number, number]): boolean {
  return lat >= box[1] && lat <= box[3] && lon >= box[0] && lon <= box[2];
}

export function getLithologyAt(lon: number, lat: number): GeoRegion | null {
  let best: GeoRegion | null = null, bestArea = Infinity;
  for (const r of IRELAND_GEOLOGY) {
    if (inBox(lat, lon, r.box)) {
      const area = (r.box[2] - r.box[0]) * (r.box[3] - r.box[1]);
      if (area < bestArea) { bestArea = area; best = r; }
    }
  }
  return best;
}
