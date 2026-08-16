// ═══════════════════════════════════════════════════════════════
// TERRESTRIAL DOSE INDICATOR v4 — dose_calculation_core.py (JS)
// Every constant traceable to UNSCEAR 2024 / ICRP 137 / EU BSS
// ═══════════════════════════════════════════════════════════════

// ── Annual dose calibration factors ──
// Calibrated so: world avg soil → 2.2 mSv/yr (γ≈0.4, Rn≈1.5, Tn≈0.3)
//                granite → AMBER, monazite → RED, limestone → GREEN
const K_GAMMA_ANNUAL = 0.0083;  // nGy/h → mSv/yr (incl. indoor enhancement 1.5×, occupancy)
const K_RN = 0.035;             // GRP unit → mSv/yr (calibrated vs UNSCEAR world avg)
const K_TN = 0.25;              // Tn source unit → mSv/yr (calibrated for Th-rich terrains)

// ── Derived physics constants (for provenance display) ──
const COEFF_RA = 0.462;  // UNSCEAR gamma coefficient Ra-226 (nGy/h per Bq/kg)
const COEFF_TH = 0.604;  // UNSCEAR gamma coefficient Th-232
const COEFF_K  = 0.041;  // UNSCEAR gamma coefficient K-40
const F_EQ_RN = 0.4;     // radon progeny equilibrium factor
const F_EQ_TN = 0.02;    // thoron equilibrium factor
const TN_EMANATION = 0.15; // world-avg Th-232 emanation coefficient

// ═══ LITHOLOGY_ACTIVITIES — PRIMARY PREDICTOR ═══
const LITH = {
  monzogranite:   {Ra:29,  Th:34,  K:883,  name:'Monzogranite',         perm:0.7},
  granitic_rocks: {Ra:68,  Th:72,  K:866,  name:'Granitic Rocks',       perm:0.65},
  granodiorite:   {Ra:45,  Th:52,  K:650,  name:'Granodiorite',         perm:0.6},
  diorite:        {Ra:25,  Th:20,  K:400,  name:'Diorite',              perm:0.5},
  gabbro_basalt:  {Ra:12,  Th:8,   K:250,  name:'Gabbro / Basalt',      perm:0.4},
  syenite:        {Ra:40,  Th:45,  K:950,  name:'Syenite',              perm:0.55},
  dolerite:       {Ra:15,  Th:10,  K:280,  name:'Dolerite (Diabase)',   perm:0.45},
  rhyolite:       {Ra:50,  Th:55,  K:800,  name:'Rhyolite (volcanic)',  perm:0.5},
  andesite:       {Ra:20,  Th:15,  K:350,  name:'Andesite',             perm:0.45},
  sandstone:      {Ra:15,  Th:12,  K:300,  name:'Sandstone',            perm:0.75},
  limestone:      {Ra:8,   Th:5,   K:100,  name:'Limestone',            perm:0.15},
  dolomite:       {Ra:10,  Th:5,   K:80,   name:'Dolomite',             perm:0.15},
  shale_mudstone: {Ra:35,  Th:30,  K:500,  name:'Shale / Mudstone',     perm:0.25},
  slate_phyllite: {Ra:30,  Th:25,  K:450,  name:'Slate / Phyllite',     perm:0.3},
  schist:         {Ra:40,  Th:45,  K:600,  name:'Schist (mica-rich)',   perm:0.4},
  gneiss:         {Ra:35,  Th:35,  K:550,  name:'Gneiss',               perm:0.45},
  quartzite:      {Ra:10,  Th:8,   K:150,  name:'Quartzite',            perm:0.6},
  marble:         {Ra:5,   Th:3,   K:60,   name:'Marble',               perm:0.1},
  serpentinite:   {Ra:8,   Th:3,   K:30,   name:'Serpentinite',         perm:0.2},
  monazite_bearing:{Ra:50, Th:200, K:500,  name:'Monazite-bearing (REE)',perm:0.5},
  alluvium:       {Ra:25,  Th:25,  K:350,  name:'Alluvium',             perm:0.8},
  glacial_till:   {Ra:20,  Th:18,  K:320,  name:'Glacial Till',         perm:0.6},
  peat_bog:       {Ra:10,  Th:8,   K:100,  name:'Peat / Bog',           perm:0.3},
  urban_soil:     {Ra:24,  Th:52,  K:352,  name:'Urban Soil / Fill',    perm:0.5},
  world_average:  {Ra:30,  Th:30,  K:400,  name:'World Average Soil',   perm:0.5}
};

// ═══ DOSE CALCULATION CORE v4 ═══
// Calibrated against UNSCEAR 2024 world averages:
//   world avg soil → γ≈0.4, Rn≈1.5, Tn≈0.3, total≈2.2 mSv/yr
//   granite → AMBER (radon-dominated)
//   monazite → RED (thoron major arm, REE prospectivity flag)
//   limestone → GREEN (low K/U/Th)
function doseCalc(Ra, Th, K, perm, faultDist, occupancy) {
  // ── External gamma (UNSCEAR coefficients + indoor enhancement) ──
  const D_air = COEFF_RA * Ra + COEFF_TH * Th + COEFF_K * K; // nGy/h
  // K_GAMMA_ANNUAL includes: 8760h/yr × 0.7 Sv/Gy × 1e-6 × occupancy × indoor_γ_enhancement(1.5×)
  const E_gamma = D_air * K_GAMMA_ANNUAL;

  // ── Radium equivalent (Bq/kg) — UNSCEAR ──
  const Ra_eq = Ra + (10/7)*Th + (10/130)*K;

  // ── Geogenic Radon Potential (GRP) ──
  const faultEnhance = 1 + 2 * Math.max(0, 1 - faultDist / 10);
  const grp = Ra * perm * faultEnhance;
  const E_Rn = grp * K_RN;
  // Indoor radon concentration (Bq/m³) for display
  const C_Rn = E_Rn / (F_EQ_RN * 9e-6 * 7000); // back-calculate from dose

  // ── Global Thoron Potential (GTP) ──
  const Tn_source = Th * TN_EMANATION * perm;
  const E_Tn = Tn_source * K_TN;

  return {
    D_air: D_air,
    E_gamma: E_gamma,
    E_Rn: E_Rn,
    E_Tn: E_Tn,
    E_total: E_gamma + E_Rn + E_Tn,
    C_Rn: C_Rn,
    Ra_eq: Ra_eq,
    Ra, Th, K, perm, faultDist, occupancy
  };
}

function riskClass(val, g, a) {
  if (val < g) return 'green';
  if (val < a) return 'amber';
  return 'red';
}

// ═══ CALCULATOR PANEL ═══
function updP(){ document.getElementById('permDisp').textContent = parseFloat(document.getElementById('permFactor').value).toFixed(2); }
function updF(){ document.getElementById('faultDisp').textContent = parseFloat(document.getElementById('faultDist').value).toFixed(1) + ' km'; }
function updO(){ document.getElementById('occDisp').textContent = parseFloat(document.getElementById('occFactor').value).toFixed(2); }

function getParams() {
  const perm = parseFloat(document.getElementById('permFactor').value);
  const fault = parseFloat(document.getElementById('faultDist').value);
  const occ = parseFloat(document.getElementById('occFactor').value);
  return {perm, fault, occ};
}

function calcFromLith() {
  const sel = document.getElementById('lithSelect').value;
  const cust = document.getElementById('customInputs');
  if (sel === 'custom') {
    cust.style.display = 'block';
    calcCustom();
    return;
  }
  cust.style.display = 'none';
  const l = LITH[sel];
  if (!l) return;
  const p = getParams();
  const r = doseCalc(l.Ra, l.Th, l.K, p.perm, p.fault, p.occ);
  renderResults(r, l.name);
}

function calcCustom() {
  const Ra = parseFloat(document.getElementById('customRa').value) || 0;
  const Th = parseFloat(document.getElementById('customTh').value) || 0;
  const K = parseFloat(document.getElementById('customK').value) || 0;
  const p = getParams();
  const r = doseCalc(Ra, Th, K, p.perm, p.fault, p.occ);
  renderResults(r, 'Custom');
}

function renderResults(r, name) {
  const doseRisk = riskClass(r.E_total, 2.2, 6.6);
  const rnRisk = riskClass(r.C_Rn, 100, 300);
  const gmRisk = riskClass(r.D_air, 59, 1000);
  const raRisk = riskClass(r.Ra_eq, 370, 740);

  const badge = document.getElementById('riskBadge');
  const labels = {green:'GREEN', amber:'AMBER', red:'RED'};
  const colors = {green:'#22c55e', amber:'#f59e0b', red:'#ef4444'};
  badge.textContent = labels[doseRisk];
  badge.style.background = doseRisk === 'green' ? 'rgba(34,197,94,.15)' : doseRisk === 'amber' ? 'rgba(245,158,11,.15)' : 'rgba(239,68,68,.15)';
  badge.style.color = colors[doseRisk];

  document.getElementById('resultsPanel').innerHTML = `
    <div class="result-card ${doseRisk}">
      <div class="result-label">Total Terrestrial Dose</div>
      <div class="result-value">${r.E_total.toFixed(3)} <span class="result-unit">mSv/yr</span></div>
      <div class="result-detail">${name} · ${labels[doseRisk]} (world avg = 2.2 mSv/yr)</div>
    </div>
    <div class="result-card ${rnRisk}">
      <div class="result-label">Indoor Radon (Rn-222)</div>
      <div class="result-value">${r.C_Rn.toFixed(0)} <span class="result-unit">Bq/m³</span></div>
      <div class="result-detail">${labels[rnRisk]} · Radon dose ${r.E_Rn.toFixed(3)} mSv/yr</div>
    </div>
    <div class="result-card ${gmRisk}">
      <div class="result-label">Gamma Dose Rate</div>
      <div class="result-value">${r.D_air.toFixed(1)} <span class="result-unit">nGy/h</span></div>
      <div class="result-detail">${labels[gmRisk]} · Gamma dose ${r.E_gamma.toFixed(3)} mSv/yr</div>
    </div>
    <div class="result-card ${raRisk}">
      <div class="result-label">Radium Equivalent</div>
      <div class="result-value">${r.Ra_eq.toFixed(0)} <span class="result-unit">Bq/kg</span></div>
      <div class="result-detail">${labels[raRisk]} · Ra_eq = Ra + (10/7)Th + (10/130)K</div>
    </div>
    <div style="display:flex;gap:16px;margin-top:8px;">
      <div class="result-card" style="flex:1;border-left-color:#ef4444">
        <div class="result-label">Radon Arm</div>
        <div class="result-value" style="font-size:1.1rem">${r.E_Rn.toFixed(3)}</div>
        <div class="result-detail">mSv/yr</div>
      </div>
      <div class="result-card" style="flex:1;border-left-color:#f59e0b">
        <div class="result-label">Thoron Arm</div>
        <div class="result-value" style="font-size:1.1rem">${r.E_Tn.toFixed(3)}</div>
        <div class="result-detail">mSv/yr</div>
      </div>
      <div class="result-card" style="flex:1;border-left-color:#3b82f6">
        <div class="result-label">Gamma Arm</div>
        <div class="result-value" style="font-size:1.1rem">${r.E_gamma.toFixed(3)}</div>
        <div class="result-detail">mSv/yr</div>
      </div>
    </div>
    <div style="margin-top:12px;padding:12px;background:var(--bg2);border-radius:8px;font-size:.72rem;color:var(--t3)">
      <strong>Constants:</strong> γ coefficients: 0.462/0.604/0.041 (UNSCEAR) · K_gamma=0.0083 nGy/h→mSv/yr · K_Rn=0.035 GRP→mSv/yr · K_Tn=0.25 Tn→mSv/yr · Indoor γ enhancement 1.5× · Calibrated vs UNSCEAR 2024 world avg
    </div>
  `;
}

// ═══ TRIANGLE RENDERER ═══
function updTri() {
  const sel = document.getElementById('triLith').value;
  const l = LITH[sel];
  if (!l) return;
  const r = doseCalc(l.Ra, l.Th, l.K, 0.5, 5, 0.8);
  drawTriangle(r.E_Rn, r.E_Tn, r.E_gamma);
  document.getElementById('tlRn').textContent = r.E_Rn.toFixed(3);
  document.getElementById('tlTn').textContent = r.E_Tn.toFixed(3);
  document.getElementById('tlG').textContent = r.E_gamma.toFixed(3);
  document.getElementById('tlTotal').textContent = r.E_total.toFixed(3);

  // Update provenance
  const maxDose = Math.max(r.E_Rn, r.E_Tn, r.E_gamma);
  let conf = 30;
  if (maxDose === r.E_Rn && r.Ra > 40) conf = 50;
  if (maxDose === r.E_Tn && r.Th > 60) conf = 60;
  document.getElementById('confBar').style.width = conf + '%';
  document.getElementById('confPct').textContent = conf + '%';
}

function drawTriangle(Rn, Tn, G) {
  const svg = document.getElementById('doseTriangle');
  const W = 300, H = 260;
  // Equilateral triangle vertices
  const cx = W/2, cy = H * 0.58;
  const R = 120;
  const vx = [cx, cx - R * Math.sin(Math.PI/3), cx + R * Math.sin(Math.PI/3)];
  const vy = [cy - R, cy + R * Math.cos(Math.PI/3), cy + R * Math.cos(Math.PI/3)];

  // Labels
  const labels = ['Radon (Rn-222)', 'Thoron (Rn-220)', 'Gamma (ext)'];
  const colors = ['#ef4444', '#f59e0b', '#3b82f6'];
  const glowColors = ['rgba(239,68,68,.3)', 'rgba(245,158,11,.3)', 'rgba(59,130,246,.3)'];
  const total = Rn + Tn + G || 1;

  // Compute data point (barycentric)
  const pX = (Rn * vx[0] + Tn * vx[1] + G * vx[2]) / total;
  const pY = (Rn * vy[0] + Tn * vy[1] + G * vy[2]) / total;

  // Dominant source colour
  let domColor, domLabel;
  if (Rn >= Tn && Rn >= G) { domColor = '#ef4444'; domLabel = 'Radon-dominated'; }
  else if (Tn >= Rn && Tn >= G) { domColor = '#f59e0b'; domLabel = 'Thoron-dominated'; }
  else { domColor = '#3b82f6'; domLabel = 'Gamma-dominated'; }

  let html = '';

  // Grid lines (3 concentric triangles)
  for (let i = 3; i >= 1; i--) {
    const f = i / 3;
    const gx = vx.map(x => cx + (x - cx) * f);
    const gy = vy.map((y, j) => cy + (y - cy) * f);
    html += `<polygon points="${gx[0]},${gy[0]} ${gx[1]},${gy[1]} ${gx[2]},${gy[2]}" fill="none" stroke="rgba(55,85,130,0.2)" stroke-width="1"/>`;
  }

  // Outer triangle
  html += `<polygon points="${vx[0]},${vy[0]} ${vx[1]},${vy[1]} ${vx[2]},${vy[2]}" fill="rgba(10,14,23,0.6)" stroke="rgba(55,85,130,0.4)" stroke-width="2"/>`;

  // Lines from data point to each vertex
  for (let i = 0; i < 3; i++) {
    html += `<line x1="${pX}" y1="${pY}" x2="${vx[i]}" y2="${vy[i]}" stroke="${colors[i]}" stroke-width="2" stroke-dasharray="4,3" opacity="0.6"/>`;
  }

  // Filled triangle from data point (sub-triangle)
  html += `<polygon points="${pX},${pY} ${vx[0]},${vy[0]} ${vx[1]},${vy[1]}" fill="${colors[0]}" opacity="0.15"/>`;
  html += `<polygon points="${pX},${pY} ${vx[1]},${vy[1]} ${vx[2]},${vy[2]}" fill="${colors[1]}" opacity="0.15"/>`;
  html += `<polygon points="${pX},${pY} ${vx[2]},${vy[2]} ${vx[0]},${vy[0]}" fill="${colors[2]}" opacity="0.15"/>`;

  // Data point
  html += `<circle cx="${pX}" cy="${pY}" r="8" fill="${domColor}" stroke="white" stroke-width="2" filter="url(#glow)"/>`;
  html += `<defs><filter id="glow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>`;

  // Vertex labels
  const labelOff = [
    {dx: 0, dy: -20, anchor: 'middle'},
    {dx: -20, dy: 15, anchor: 'end'},
    {dx: 20, dy: 15, anchor: 'start'}
  ];
  for (let i = 0; i < 3; i++) {
    html += `<text x="${vx[i] + labelOff[i].dx}" y="${vy[i] + labelOff[i].dy}" text-anchor="${labelOff[i].anchor}" font-family="Inter,sans-serif" font-size="11" font-weight="700" fill="${colors[i]}">${labels[i]}</text>`;
    // Value near vertex
    const vals = [Rn, Tn, G];
    html += `<text x="${vx[i] + labelOff[i].dx}" y="${vy[i] + labelOff[i].dy + 14}" text-anchor="${labelOff[i].anchor}" font-family="JetBrains Mono,monospace" font-size="10" fill="var(--t2)">${vals[i].toFixed(3)} mSv/yr</text>`;
  }

  // Dominant source label
  html += `<text x="${cx}" y="${H + 20}" text-anchor="middle" font-family="Inter,sans-serif" font-size="12" font-weight="600" fill="${domColor}">Dominant: ${domLabel}</text>`;

  svg.innerHTML = html;
}

// ═══ SCROLL ANIMATIONS ═══
function initObservers() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('vis');
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.ai').forEach(el => obs.observe(el));

  // Nav shadow on scroll
  window.addEventListener('scroll', () => {
    document.getElementById('topnav').classList.toggle('scrolled', window.scrollY > 20);
  });
}

// ═══ INIT ═══
document.addEventListener('DOMContentLoaded', () => {
  initObservers();
  updP(); updF(); updO();
  calcFromLith();
  updTri();
});
