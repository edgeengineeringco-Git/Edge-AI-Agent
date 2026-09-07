# EU Expert Panel Review — EDGE Application to the **28DIGITAL Co-Creation Accelerator 2026**

**Challenge:** *Agentic Multi-Sensor Intelligence for Europe's Responsible Rare Earth Elements Discovery*
**Applicant:** EDGE (Irish deep-tech SME — edgeengineers.net). Product: an agentic multi-sensor fusion platform ("TerraLens AI" / the "Agentic AI Platform") for REE prospectivity with uncertainty quantification.
**Funder / Programme:** **28DIGITAL** — *"Europe's digital innovation engine"*, the organisation succeeding **EIT Digital**. Runs the **Co-Creation Accelerator** (startups + industry partners co-developing solutions to real-world challenges) and the **Venture Incubation Programme**, taking a **5% ordinary-share / SAFE stake + participation fee**.
**Review date:** 2026-09-07
**Source documents reviewed:** `Call_26369_07 Sep 2026 (2).pdf` and `Call_26369_07 Sep 2026- Test 1.pdf` — the two challenge briefs (near-identical; "Test 1" is a draft variant of the same requirements). Application content cross-referenced from the applicant's `Pitch Deck Presentation.pdf`.
**Panel:** 4 independent expert reviewers (Scientific/Technical · Innovation & Deep-Tech/Space · Market/Commercial/Investment · Programme Fit/Implementation/Compliance).

---

## 1. Executive Summary & Panel Verdict

EDGE proposes an **agentic, multi-sensor fusion engine** that harmonises drone gamma-ray + LiDAR, Sentinel/EO, airborne geochemistry, geological maps and legacy surveys into one reproducible, *inspectable* workflow that outputs REE prospectivity maps **with uncertainty attached** — and is validated against ground truth by independent R&D geologists (RISE, Sweden) across **3–5 European sites**.

This answers the exact gap the 28DIGITAL challenge criticises: *"exploration AI that works on one site, with no evidence it can be trusted on the next."* The technical design, the co-creation partnership with RISE and Maynooth University, and the alignment to EU critical-raw-materials sovereignty are strong. The weaknesses are **commercial immaturity** (no signed paying customers; pre-revenue) and **incomplete formal documentation** (explicitly flagged in the brief), plus loose document hygiene (duplicate "Test 1" call, corrupt `.tmp` artifacts).

> ### 🟡 PANEL VERDICT: **CONDITIONALLY FUND** — recommend selection to the 28DIGITAL Co-Creation Accelerator, subject to a short pre-award conditions list (see §6).
> **Weighted score ≈ 6.4 / 10 (64%).**

---

## 2. Source Basis (what the two PDFs actually say)

Both `Call_26369` PDFs set out the same challenge. Key clauses extracted and used by the reviewers below:

- **Success definition:** *"outputs scored against ground truth and against [RISE's] knowledge of Swedish and European deposits"*; *"success criteria are assessed by RISE, including whether the platform identifies at least one zone or signal their team considers genuinely useful or previously underweighted."*
- **The core problem to solve:** *"the challenge is a transferability gap — exploration AI that works on one site, with no evidence it can be trusted on the next."*
- **Multi-sensor stack required:** drone gamma-ray + LiDAR, Sentinel/EO, airborne geochemistry (XRF), geological maps, historic surveys, client data — *"everything lands on a common spatial grid in containerised Python workflows."*
- **Uncertainty honesty:** *"keeps uncertainty representation… refuses geologically absurd output… the model has not met them yet [so we say so in the uncertainty fields]."*
- **Pilot shape:** a **4-month** multi-site pilot; monthly milestones, risk register, KPI and budget/schedule reporting; *"reviews take place monthly so issues are addressed during the project, not at the end."*
- **Co-creation partners named:** **RISE** (Swedish state-owned applied research & innovation org — provides the Swedish pilot site, access, non-confidential data, and geological review; confirms in writing it will allocate financial/personnel/operational resources **if selected**); **Maynooth University** (Ireland — peat-thickness estimation via drone gamma, student interns).
- **Funder terms:** *"5% ordinary shares to be transferred to 28DIGITAL"*; a **participation fee**; **EC co-funding + clawback rules**; *"funding will be claimed after the activity is completed and the final report, deliverables and KPIs have…"* (reimbursement/phased model); *"pre-financing is paid at start."*
- **Existing backing cited by applicant:** **ESA BIC Ireland** (accepted), **Enterprise Ireland** EIIS/Innovation grant (applying), **Irish Research Council**, EU Open Science Cloud, potential further ESA vouchers.
- **Market cited:** *"the global AI-powered mineral-exploration technology market was valued at $53 billion… forecast to reach [$…]B"*; satellite imagery + ML called the largest sub-segment.
- **Diversity:** female co-founder (Parisa) holds ownership — founder-level and technical representation.
- **Gate:** *"review before submission"* — a documented pre-submission review step.

---

## 3. Reviewer 1 — Scientific & Technical Excellence

**Mandate:** Does the solution meet the challenge's technical success criteria (multi-sensor fusion, ground-truth validation, cross-site transferability, monazite detection, quantified uncertainty)? Is the TRL credible for a 4-month pilot?

**Strengths**
- Directly targets the challenge's stated weakness: a **multi-site transferability test** (3–5 independent European sites, incl. RISE Sweden) rather than single-site self-validation.
- **Independent validation by design:** RISE geologists score outputs against ground truth and their own domain knowledge; success = *at least one genuinely useful or previously-underweighted zone* flagged.
- **Honest uncertainty:** a calibration layer that *refuses geologically absurd outputs* and keeps uncertainty representation — exactly what the brief demands ("we say so in the uncertainty fields rather than hiding it").
- **Full sensing stack:** drone gamma-ray + LiDAR, Sentinel/EO, airborne geochemistry, geological constraint layers, legacy maps — unified in containerised Python. Monazite/bastnäsite detection via an automated mineralogy pipeline.
- **TRL is appropriate:** already *validated end-to-end on one granite-hosted REE site (DIF)* with real field data; the pilot's job is to prove transferability, not invent the tech. Low technical risk on components.

**Weaknesses / concerns**
- **Label scarcity:** REE deposits are rare by definition → few positive training labels; model outputs will be *"correspondingly thinner"* where no fresh survey data exists.
- **Partial validation breadth:** only *"one granite-hosted system, carbonatites, peralkaline complexes"* partially validated; transfer to other lithologies/untested terrains unproven.
- **Operational fragility:** drone surveys are *weather- and terrain-bound*; Nordic winter windows limit field campaigns — a real scheduling risk to the 4-month timeline.
- No signed paying customer yet to **confirm field-economic value** (only internal/grant validation so far).

**Score: 7.0 / 10 — Fund (strong technical fit).**

---

## 4. Reviewer 2 — Innovation & Deep-Tech / Space Strategy

**Mandate:** Is it genuinely novel vs incumbents? Does it leverage 28DIGITAL's digital/deep-tech + (EIT Digital / ESA) space-asset heritage? Is it defensible?

**Strengths**
- **Clear differentiation:** incumbents supply *single-sensor or single-site* ML (one data type, one model). EDGE's edge is **multi-sensor fusion + agentic, fully inspectable pipeline** where *"a geologist can trace why a zone was flagged, sensor by sensor."*
- **Space-asset alignment:** built on **Sentinel/EO**, with an explicit **lunar/space roadmap**; **ESA BIC Ireland** backing maps directly onto 28DIGITAL's EIT-Digital-successor, space-heritage positioning.
- **Open + protected:** core on open-source (Python, SciKit, OpenBot, Obsidian) while trained models/fusion are **trade secrets with access controls and copyright** — pragmatic for a young SME.
- Addresses a *named, real gap the challenge explicitly criticises* → high relevance to the call.

**Weaknesses / concerns**
- **Integration, not invention:** the brief itself says *"what is actually new in this project is not technology… almost everything technical already exists, works, and is owned outright by EDGE."* The novelty is **transferability/integration** — valuable but **harder to patent or moat**.
- **Competitive adjacency:** drone survey providers and geophysical consultancies (e.g., those flying gamma + magnetics) *"are also potential competitors"* and could bolt on gamma. Defensibility rests on trade secrets + freedom-to-operate, not a strong IP wall.
- **Space phase unfunded here:** the lunar/space workflow *"will require EDGE to pursue separate funding"* — out of scope for this award.

**Score: 7.5 / 10 — Fund.**

---

## 5. Reviewer 3 — Market, Commercial & Investment

**Mandate:** Business model, go-to-market, customer segments, revenue readiness, and fitness for 28DIGITAL's venture-scaling + 5%-equity model.

**Strengths**
- **Large, growing market:** cited $53B AI mineral-exploration tech, satellite+ML the biggest sub-segment; clear serviceable niche in **calibration software for third-party gamma**.
- **Credible GTM:** pilot-to-paid conversion model, a **self-serve commercial layer** turning an enquiry → qualification → quote → kick-off, and warm industry contacts via RISE/Maynooth.
- **Typical 28DIGITAL venture profile:** deep-tech, defensible data/ML, EU sovereignty angle — exactly the kind of startup the Co-Creation Accelerator + Venture Incubation Programme exists to scale.

**Weaknesses / concerns**
- **No signed paying customers**; *"given typical geological sales cycles"* and *"EDGE has no signed paying customers"* — revenue is unproven; the pilot is **validation, not commercial traction**.
- **Funding-stack dependency:** relies on a chain of grants (ESA BIC, Enterprise Ireland EIIS, Irish Research Council, ESA vouchers) for scale-up. Execution risk if any leg slips.
- **Funder terms / dilution:** 28DIGITAL takes **5% ordinary shares + participation fee + clawback on EC co-funding**. Founders must be comfortable with the dilution and reimbursement/clawback mechanics before acceptance.
- **Pre-revenue deep-tech = higher investment risk**, even within an accelerator.

**Score: 6.0 / 10 — Fund with conditions (commercial-evidence plan required).**

---

## 6. Reviewer 4 — Programme Fit, Implementation & Compliance

**Mandate:** Fit to the 28DIGITAL Co-Creation Accelerator; co-creation structure; plan/risk/KPI maturity; eligibility; funder terms; documentation completeness.

**Strengths**
- **Excellent co-creation design:** RISE (state-owned research org) as industry partner with **written commitment to allocate resources if selected**; Maynooth University for the peat-thickness pilot + student interns. Matches 28DIGITAL's "startups + industry partners" model precisely.
- **Mature delivery plan:** **4-month** pilot, **monthly milestones**, live risk register, KPI/schedule/budget reporting, documented **"review before submission"** gate.
- **Funder-risk-aware finance:** expenditure *phased by task*, *claimed after completion* with pre-financing at start → de-risks 28DIGITAL's outlay.
- **Clean ownership/IP:** independent SME, **owns platform + all 5 assets outright**, no subsidiary, no third-party licence dependency; IP audit + freedom-to-operate review planned.
- **Diversity:** female co-founder with founder-level ownership — positive on 28DIGITAL/EU criteria.

**Weaknesses / concerns**
- **Incomplete formal package:** the brief itself flags *"the formal documentation package is not complete"* and *"the compliance work is unfinished"* → must be closed before award.
- **Terms acceptance:** the **5% share transfer + participation fee + EC clawback** must be **accepted in writing** as a condition of participation.
- **Eligibility & gate:** must confirm Irish SME / deep-tech / digital eligibility and that the **"review before submission"** gate is actually satisfied, not just planned.
- **Document hygiene:** the folder contains two near-identical call files (one "Test 1") and **three corrupted `.tmp` artifacts** (recovered as truncated duplicates of the pitch deck, not readable as separate content). Sloppy file management is a minor but real programme-readiness signal.

**Score: 6.0 / 10 — Fund with conditions (complete docs + sign participation terms).**

---

## 7. Panel Synthesis & Funding Decision

| Reviewer | Lens | Score /10 | Recommendation |
|---|---|---|---|
| 1 | Scientific & Technical | 7.0 | Fund |
| 2 | Innovation & Deep-Tech/Space | 7.5 | Fund |
| 3 | Market, Commercial & Investment | 6.0 | Fund w/ conditions |
| 4 | Programme Fit, Implementation & Compliance | 6.0 | Fund w/ conditions |
| **Weighted** | | **≈ 6.4** | **CONDITIONALLY FUND** |

**Why fund (despite conditions):** EDGE is a strong strategic fit for 28DIGITAL — a digital/deep-tech venture, co-created with a credible industry partner (RISE) and an academic partner (Maynooth), tackling an EU-priority problem (critical-raw-materials sovereignty) with a technically sound, honestly-uncertainty-aware, multi-sensor design that *directly answers the challenge's stated gap*. The 28DIGITAL value-add (SpeedMaster training, mentoring, venture scaling, the 5% stake) is well-matched to a pre-revenue but asset-rich deep-tech SME.

**Why conditional (not unconditional):** the application as submitted reads as a pitch deck + challenge brief, not a complete formal proposal; commercial traction is zero (pre-revenue, grant-dependent); and the brief itself admits the documentation/compliance package is unfinished.

### Conditions precedent to award (to be cleared at the "review before submission" gate)
1. **Complete the formal documentation package** and pass the documented pre-submission review.
2. **Accept 28DIGITAL's participation terms in writing** — 5% ordinary-share transfer, participation fee, and EC co-funding/clawback mechanics.
3. **Submit a commercial-evidence plan**: pilot-to-paid conversion path + at least Letters of Intent / committed engagement from RISE, Maynooth, or industry contacts.
4. **Close compliance / freedom-to-operate items** (IP audit, FTO review, eligible-cost scoping).
5. **Tidy document hygiene**: remove corrupt `.tmp` artifacts and reconcile the duplicate "Test 1" call file.

**Expected value to 28DIGITAL:** High — a defensible, pilot-ready deep-tech venture with real infrastructure, credible industry co-creation, and clear EU strategic alignment; principal risks (commercial traction, paperwork) are exactly what the Accelerator's mentoring/SpeedMaster support is designed to fix.

---

## 8. Appendix — Methodology & Artifact Notes

- **Decoding:** The two `Call_26369` PDFs use a custom text encoding (each character stored as a `0xFD`-prefixed byte). A stdlib-only Python extractor (zlib inflate of FlateDecode streams + `0xFD` stripping + printable filtering) recovered ~30 KB of clean prose from each; the two files are the same challenge brief (one a "Test 1" draft).
- **`.tmp` artifacts:** The three `mso*.tmp` files in the submission folder were recovered as **truncated duplicates of the Pitch Deck** (same content fragments), not additional proposal text — they carry no independent information and indicate loose file handling.
- **Video:** Excluded per instruction. (Environment has no vision/OCR/STT; technical probes confirmed a 58.7 s, 1080p, H.264/AAC narrated walkthrough consistent with the pitch deck.)
- **Scope:** This review is framed specifically against **28DIGITAL's Co-Creation Accelerator 2026** challenge brief (the two reviewed PDFs). EDGE = the applicant; RISE = Swedish state research partner; Maynooth University = academic pilot partner.
