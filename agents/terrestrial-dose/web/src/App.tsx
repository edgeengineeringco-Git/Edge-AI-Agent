/**
 * App.tsx — Irish Terrestrial Dose Indicator
 * Left: satellite map of Ireland with floating triangle
 * Right: report panel (pinned on click)
 */

import { useState, useCallback } from "react";
import MapComponent from "./Map";
import Panel from "./Panel";
import type { DoseFingerprint } from "./dose_core";

const PRESETS = [
  { name: "Dublin", lat: 53.3498, lon: -6.2603 },
  { name: "Cork", lat: 51.8985, lon: -8.4756 },
  { name: "Galway", lat: 53.2707, lon: -9.0568 },
  { name: "Limerick", lat: 52.6638, lon: -8.6267 },
  { name: "Belfast", lat: 54.5973, lon: -5.9301 },
  { name: "Wicklow Granite", lat: 52.98, lon: -6.35 },
  { name: "Burren Limestone", lat: 53.05, lon: -9.15 },
  { name: "Connemara", lat: 53.35, lon: -9.55 },
  { name: "Donegal Granite", lat: 54.95, lon: -8.0 },
  { name: "Kerry", lat: 52.06, lon: -9.55 },
];

export default function App() {
  const [pinnedData, setPinnedData] = useState<DoseFingerprint | null>(null);
  const [pinnedName, setPinnedName] = useState("");
  const [panelVisible, setPanelVisible] = useState(false);
  const [flyTo, setFlyTo] = useState<{ lat: number; lon: number; name: string } | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const handleHover = useCallback(() => {}, []);

  const handleClick = useCallback((data: DoseFingerprint, name: string) => {
    setPinnedData(data);
    setPinnedName(name);
    setPanelVisible(true);
  }, []);

  const handlePreset = (p: typeof PRESETS[0]) => {
    setFlyTo({ lat: p.lat, lon: p.lon, name: p.name });
    import("./dose_core").then(({ polygonDoseFingerprint }) => {
      import("./lithology").then(({ getLithologyAt }) => {
        const lith = getLithologyAt(p.lon, p.lat);
        const fp = polygonDoseFingerprint({ lithology: lith.glim, lat: p.lat, lon: p.lon });
        setPinnedData(fp);
        setPinnedName(p.name);
        setPanelVisible(true);
      });
    });
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      const resp = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchQuery + ", Ireland")}&limit=1`);
      const data = await resp.json();
      if (data?.[0]) {
        const lat = parseFloat(data[0].lat);
        const lon = parseFloat(data[0].lon);
        if (lat >= 51.4 && lat <= 55.4 && lon >= -10.6 && lon <= -5.3) {
          setFlyTo({ lat, lon, name: data[0].display_name.split(",")[0] });
        } else {
          alert("Location outside Ireland. Please search within Ireland.");
        }
      }
    } catch (e) {
      console.error("Search failed:", e);
    }
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="topbar-brand">
          <span className="topbar-logo">◈</span>
          <h1 className="topbar-title">Irish-Dose</h1>
          <span className="topbar-subtitle">Irish Terrestrial Dose Indicator</span>
        </div>
        <div className="topbar-controls">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search Ireland…"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            />
            <button onClick={handleSearch}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
              </svg>
            </button>
          </div>
          <select className="preset-select" onChange={(e) => {
            const p = PRESETS.find((x) => x.name === e.target.value);
            if (p) handlePreset(p);
          }} value="">
            <option value="" disabled>Jump to location…</option>
            {PRESETS.map((p) => <option key={p.name} value={p.name}>{p.name}</option>)}
          </select>
        </div>
      </header>

      <main className="main">
        <div className="map-pane">
          <MapComponent onHover={handleHover} onClick={handleClick} flyTo={flyTo} />
        </div>
        <div className={`panel-pane ${panelVisible ? "visible" : ""}`}>
          <Panel data={pinnedData} name={pinnedName} visible={panelVisible} onClose={() => setPanelVisible(false)} />
        </div>
      </main>
    </div>
  );
}
