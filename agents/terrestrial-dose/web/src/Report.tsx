import { Triangle } from './Triangle';
import type { DoseResult } from './dose_core';

export function Report({ data }: { data: DoseResult | null }) {
  if (!data) return <div style={{ color: '#8b97b0', padding: 20, fontFamily: 'Inter, sans-serif' }}>Hover the map of Ireland to see dose</div>;
  const c = data.risk.tier === 'GREEN' ? '#22c55e' : data.risk.tier === 'AMBER' ? '#f59e0b' : '#ef4444';
  return (
    <div style={{ padding: 20, color: '#e6ebf5', fontFamily: 'Inter, sans-serif', height: '100%', overflowY: 'auto' }}>
      <div style={{ fontSize: 11, color: '#8b97b0' }}>Cell 100m · {data.lith} ({data.lithName})</div>
      <div style={{ display: 'inline-block', padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600, margin: '10px 0', background: `${c}22`, color: c, border: `1px solid ${c}44` }}>
        {data.risk.tier} — {data.total.toFixed(2)} mSv/yr
      </div>
      <Triangle arms={data.arms} size={220} />
      <div style={{ fontSize: 14, marginTop: 8 }}>Total: <b>{data.total.toFixed(2)}</b> mSv/yr</div>
      <div style={{ marginTop: 14 }}>
        <p style={{ fontSize: 13, marginBottom: 7 }}>{data.arms.radon > data.arms.thoron && data.arms.radon > data.arms.gamma ? 'Radon' : data.arms.thoron > data.arms.gamma ? 'Thoron' : 'Gamma'} is dominant.</p>
        <p style={{ fontSize: 13, marginBottom: 7 }}>{(data.total / 2.2).toFixed(1)}× UNSCEAR world average (2.2 mSv/yr).</p>
        <p style={{ fontSize: 13, marginBottom: 7 }}>Indoor radon: {data.C_Rn.toFixed(0)} Bq/m³ {data.C_Rn >= 200 ? '⚠ Irish action level' : ''}.</p>
        <p style={{ fontSize: 13, marginBottom: 7 }}>Ra-eq: {data.raeq.toFixed(0)} Bq/kg {data.raeq >= 370 ? '⚠ above threshold' : ''}.</p>
      </div>
      <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid #243049' }}>
        <h3 style={{ fontSize: 10, color: '#3b82f6', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 }}>Provenance</h3>
        {data.prov.map((p, i) => <div key={i} style={{ fontSize: 11, color: '#8b97b0', marginBottom: 2 }}>→ {p}</div>)}
      </div>
      <div style={{ marginTop: 14, fontSize: 11, color: '#8b97b0' }}>
        Confidence: {data.conf}% — {data.conf >= 75 ? 'high (measured)' : data.conf >= 50 ? 'medium-high' : 'geology prior'}
      </div>
      <div style={{ marginTop: 14 }}>
        <div style={{ fontSize: 10, color: '#8b97b0', marginBottom: 4 }}>
          <span style={{ display: 'inline-block', width: 7, height: 7, borderRadius: '50%', background: '#22c55e', marginRight: 6 }} />
          GREEN: ≤ 2.2 mSv/yr
        </div>
        <div style={{ fontSize: 10, color: '#8b97b0', marginBottom: 4 }}>
          <span style={{ display: 'inline-block', width: 7, height: 7, borderRadius: '50%', background: '#f59e0b', marginRight: 6 }} />
          AMBER: 2.2–6.6 mSv/yr
        </div>
        <div style={{ fontSize: 10, color: '#8b97b0', marginBottom: 4 }}>
          <span style={{ display: 'inline-block', width: 7, height: 7, borderRadius: '50%', background: '#ef4444', marginRight: 6 }} />
          RED: &gt; 6.6 mSv/yr or Rn ≥ 200 Bq/m³
        </div>
        <div style={{ fontSize: 10, color: '#8b97b0', marginTop: 6, opacity: 0.6 }}>
          Irish action level: 200 Bq/m³ (stricter than EU 300) · EU BSS 2013/59/Euratom
        </div>
      </div>
    </div>
  );
}
