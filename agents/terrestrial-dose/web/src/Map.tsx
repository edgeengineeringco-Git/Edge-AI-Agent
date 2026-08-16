import maplibregl from 'maplibre-gl';
import { useEffect, useRef } from 'react';

const SAT = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
const OSM = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';

export function MapView({ onHover, onPin }: {
  onHover: (lat: number, lon: number) => void;
  onPin: (lat: number, lon: number) => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const map = new maplibregl.Map({
      container: ref.current!,
      style: {
        version: 8,
        sources: {
          satellite: { type: 'raster', tiles: [SAT], tileSize: 256, attribution: '© Esri' },
          streets: { type: 'raster', tiles: [OSM], tileSize: 256, attribution: '© OSM' },
        },
        layers: [{ id: 'satellite', type: 'raster', source: 'satellite' }],
      },
      center: [-8.5, 53.3],
      zoom: 7,
      maxBounds: [[-10.7, 51.3], [-5.2, 55.5]],
    });
    map.addControl(new maplibregl.ScaleControl({ maxWidth: 100 }), 'bottom-left');
    map.addControl(new maplibregl.NavigationControl(), 'top-right');
    let t: number;
    map.on('mousemove', (e) => {
      clearTimeout(t);
      t = window.setTimeout(() => onHover(e.lngLat.lat, e.lngLat.lng), 100);
    });
    map.on('click', (e) => onPin(e.lngLat.lat, e.lngLat.lng));
    return () => map.remove();
  }, []);
  return <div ref={ref} style={{ width: '100%', height: '100%' }} />;
}
