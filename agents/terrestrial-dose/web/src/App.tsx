import { useState, useCallback } from 'react';
import { MapView } from './Map';
import { Report } from './Report';
import { doseFingerprint, type DoseResult } from './dose_core';
import { getLithologyAt } from './lithology';

export default function App() {
  const [data, setData] = useState<DoseResult | null>(null);
  const [pinned, setPinned] = useState(false);

  const onHover = useCallback(async (lat: number, lon: number) => {
    if (pinned) return;
    const geo = getLithologyAt(lon, lat);
    if (!geo) { setData(null); return; }
    const fp = doseFingerprint({ lithology: geo.code });
    setData(fp);
  }, [pinned]);

  const onPin = useCallback(async (lat: number, lon: number) => {
    const geo = getLithologyAt(lon, lat);
    if (!geo) return;
    const fp = doseFingerprint({ lithology: geo.code });
    setData(fp);
    setPinned(true);
  }, []);

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0a0e1a' }}>
      <div style={{ flex: 1.3 }}><MapView onHover={onHover} onPin={onPin} /></div>
      <div style={{ flex: 0.7, minWidth: 380, background: '#111726', borderLeft: '1px solid #243049' }}>
        <Report data={data} />
      </div>
    </div>
  );
}
