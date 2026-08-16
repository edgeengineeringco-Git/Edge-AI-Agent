/** D3 three-arm dose triangle — pure SVG, arms at 120° from centre */
export function Triangle({ arms, size = 200 }: {
  arms: { radon: number; thoron: number; gamma: number }; size?: number;
}) {
  const cx = size / 2, cy = size / 2 - 10, ml = size * 0.4;
  const md = Math.max(arms.radon, arms.thoron, arms.gamma, 0.01);
  const L = (d: number) => Math.max(15, d / md * ml);
  const r = L(arms.radon), t = L(arms.thoron), g = L(arms.gamma);
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <polygon
        points={`${cx},${cy - r} ${cx - 0.866 * t},${cy + 0.5 * t} ${cx + 0.866 * g},${cy + 0.5 * g}`}
        fill="rgba(59,130,246,0.1)" stroke="rgba(59,130,246,0.4)"
      />
      <line x1={cx} y1={cy} x2={cx} y2={cy - r} stroke="#3b82f6" strokeWidth="4" strokeLinecap="round" />
      <line x1={cx} y1={cy} x2={cx - 0.866 * t} y2={cy + 0.5 * t} stroke="#f97316" strokeWidth="4" strokeLinecap="round" />
      <line x1={cx} y1={cy} x2={cx + 0.866 * g} y2={cy + 0.5 * g} stroke="#22c55e" strokeWidth="4" strokeLinecap="round" />
      <circle cx={cx} cy={cy} r="3" fill="#e6ebf5" />
      <text x={cx} y={cy - r - 6} textAnchor="middle" fontSize="10" fill="#3b82f6">{`Rn ${arms.radon.toFixed(2)}`}</text>
      <text x={cx - 0.866 * t - 15} y={cy + 0.5 * t + 14} textAnchor="middle" fontSize="9" fill="#f97316">{`Tn ${arms.thoron.toFixed(2)}`}</text>
      <text x={cx + 0.866 * g + 15} y={cy + 0.5 * g + 14} textAnchor="middle" fontSize="9" fill="#22c55e">{`γ ${arms.gamma.toFixed(2)}`}</text>
    </svg>
  );
}
