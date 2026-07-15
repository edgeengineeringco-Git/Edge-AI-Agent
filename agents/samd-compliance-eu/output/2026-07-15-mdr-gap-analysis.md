# EU MDR SaMD Compliance Audit & Gap Analysis

**Date:** 2026-07-15  
**Device:** Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application  
**Target Market:** European Union (EU MDR 2017/745)  
**Report Version:** 1.0

---

## Executive Summary

Your wellness application — which monitors glucose fluctuations and delivers personalised weight-loss insights — is classified as **Class IIa** Software as a Medical Device (SaMD) under EU MDR Annex VIII, Rule 11. You currently have **zero regulatory documentation** and **no Quality Management System (QMS)**. This report identifies the critical gaps and provides a prioritised 12-month roadmap to CE marking.

**Critical Path:**
1. Finalise Intended Purpose and select Notified Body (Month 1)
2. Implement ISO 13485 QMS + IEC 62304 software lifecycle (Months 1-3)
3. Generate Technical Documentation (Months 3-6)
4. Complete Clinical Evaluation + Algorithm Validation (Months 6-9)
5. Notified Body Audit + CE Marking (Months 9-12)

**Estimated External Costs:** €80,000 – €150,000 (Notified Body fees, regulatory consultant, clinical evaluation support, testing).  
**Internal Effort:** 1.0 – 1.5 FTEs for 12 months.

---

## 1. Device Classification Justification

### 1.1 Regulatory Basis
**MDR 2017/745, Annex VIII, Chapter III, Rule 11:**
> "Software intended to provide information which is used to take decisions with diagnosis or therapeutic purposes is classified as **Class IIa**, except if such decisions have an impact that may cause death or an irreversible deterioration of a person's state of health (Class III), or a serious deterioration of a person's state of health or a surgical intervention (Class IIb)."

### 1.2 Classification Determination

| Attribute | Determination |
|---|---|
| **Device Name** | [Your App Name] |
| **Intended Purpose** | Software for monitoring glucose fluctuations and providing personalised lifestyle insights to support weight management in adults with prediabetes, type 2 diabetes, or metabolic syndrome. |
| **Patient Population** | Adults (18+) with prediabetes, type 2 diabetes, or metabolic syndrome. Not intended for paediatric use or Type 1 diabetes management without clinician oversight. |
| **MDR Rule** | Annex VIII, Rule 11 |
| **Classification** | **Class IIa** |
| **Conformity Route** | Annex IX (QMS + Technical Documentation Review) |
| **Notified Body Required** | **Yes** |

### 1.3 Rationale
The software processes physiological data (glucose values, either user-entered or from CGM APIs) and provides information used to take **therapeutic decisions** (dietary modifications, exercise recommendations, lifestyle changes). The decisions are:
- Non-invasive and managed through user discretion
- Intended to be used under healthcare-provider oversight
- Do not directly control drug delivery or acute life-support interventions
- Do not cause death, irreversible deterioration, or surgical intervention when followed

### 1.4 Reclassification Triggers
**The following feature additions would trigger reclassification:**

| Feature Change | New Classification | Regulatory Impact |
|---|---|---|
| Insulin dosing calculations or recommendations | Class IIb (Rule 11) | Significantly higher clinical evidence, stricter NB audit |
| Severe hypoglycaemia emergency alerts (auto-dial 112, etc.) | Class IIb or III | Life-support critical software, Class C per IEC 62304 |
| Automated meal-plan generation for diabetic ketoacidosis prevention | Class IIb | Clinical investigation likely required |
| Diagnostic claim ("detects diabetes") | Class IIa / IIb depending on claim | May fall under IVDR if screening |

**Recommendation:** Freeze feature scope for CE marking. Document all "intended use" exclusions explicitly in the IFU.

---

## 2. QMS Gap Analysis (ISO 13485:2016)

### 2.1 Overall Assessment
**Current State:** No formal QMS. Likely using agile sprints with basic git/version control.  
**Target State:** Full ISO 13485 QMS with documented procedures, records, and design controls.

### 2.2 Clause-by-Clause Gap Matrix

| ISO 13485 Clause | Requirement | Current State | Gap Severity | Remediation Effort |
|---|---|---|---|---|
| **4.1** — Quality Manual | Documented QMS scope, exclusions, process interactions | Missing | **Critical** | 1-2 weeks |
| **4.2** — Document Control | Formal approval, distribution, revision history, archival | Basic git only | **Critical** | 2-3 weeks |
| **5.1** — Management Commitment | Quality policy, objectives, management reviews | Informal | **High** | 1 week |
| **5.2** — Customer Focus | Feedback mechanisms, complaint handling | App store reviews only | **High** | 2 weeks |
| **6.1** — Risk-Based Approach | Risk management integrated across all processes | Missing | **Critical** | Ongoing |
| **7.1** — Planning of Product Realization | Design plans, reviews, verification/validation planning | Agile sprints | **Critical** | 3-4 weeks |
| **7.3** — Design & Development | DHF, design inputs/outputs, reviews, traceability | Missing | **Critical** | 8-12 weeks |
| **7.5** — Production & Service Provision | Controlled build, release, installation | CI/CD uncontrolled | **High** | 3-4 weeks |
| **7.5.6** — Validation of Computer Software | Validate software used in QMS (Jira, GitHub, test tools) | Missing | **High** | 2-3 weeks |
| **8.2** — Monitoring & Measurement | Feedback, complaint handling, reporting to authorities | Crashlytics only | **Critical** | 4-6 weeks |
| **8.2.2** — Complaint Handling | Formal complaint log, investigation, MDR vigilance reporting | Missing | **Critical** | 2-3 weeks |
| **8.2.3** — Reporting to Authorities | Serious incident reporting to competent authorities | Missing | **Critical** | 1 week (procedure) |
| **8.3** — Nonconforming Product | NCR log, investigation, corrective action | Bug backlog only | **High** | 2-3 weeks |
| **8.4** — Data Analysis | Trend analysis, KPIs, PMS data analysis | Missing | **High** | 2-3 weeks |
| **8.5** — Improvement | CAPA system, preventive actions | Missing | **High** | 3-4 weeks |

### 2.3 Priority Remediation Plan

**Phase 1 (Months 1-2): Foundation**
1. Draft Quality Manual and 15 core SOPs
2. Implement document control system (e-signature + version control, e.g., Greenlight Guru, MatrixALM, or paper-based initially)
3. Establish management review schedule
4. Define quality policy and measurable objectives

**Phase 2 (Months 2-3): Design Controls**
1. Implement design planning template
2. Create Design History File (DHF) structure
3. Establish design review gates
4. Build traceability matrix template (GSPR ↔ Design Input ↔ Verification ↔ Evidence)

**Phase 3 (Months 3-4): Production & PMS**
1. Formalise release checklist and build control
2. Implement complaint handling procedure
3. Establish vigilance reporting procedure
4. Create CAPA form and log

---

## 3. Technical Documentation Roadmap (Annex III)

### 3.1 Document List & Effort Estimate

| # | Document | MDR Basis | Priority | Effort | Owner |
|---|---|---|---|---|---|
| 1 | Device Description & Specification | Annex III, 1 | Critical | 2-3 weeks | Regulatory / Product |
| 2 | Basic UDI-DI Assignment | Annex VI | Critical | 1 day | Regulatory |
| 3 | Intended Purpose Statement | Annex III, 1.1 | Critical | 2 days | Regulatory |
| 4 | Patient Population & Contraindications | Annex III, 1.1 | Critical | 3 days | Clinical / Regulatory |
| 5 | Software Architecture Document | Annex III, 2 | Critical | 2 weeks | Engineering |
| 6 | SOUP / Third-Party Inventory | Annex III, 2 | Critical | 1 week | Engineering |
| 7 | General Safety & Performance Requirements (GSPR) | Annex I | Critical | 3-4 weeks | Regulatory |
| 8 | GSPR Traceability Matrix | Annex I | Critical | 2 weeks | Regulatory / QA |
| 9 | Risk Management Plan (ISO 14971) | Annex III, 3 | Critical | 1 week | Regulatory |
| 10 | Risk Analysis & FMEA | Annex III, 3 | Critical | 3 weeks | Regulatory / Engineering |
| 11 | Risk Management Report | Annex III, 3 | Critical | 1 week | Regulatory |
| 12 | Software Requirements Specification (SRS) | Annex III, 2 / IEC 62304 | Critical | 2-3 weeks | Engineering |
| 13 | Software Architecture Design | IEC 62304 | Critical | 2 weeks | Engineering |
| 14 | Software Detailed Design | IEC 62304 | High | 2-3 weeks | Engineering |
| 15 | Software Unit Verification | IEC 62304 | High | 2 weeks | QA / Engineering |
| 16 | Software Integration Testing | IEC 62304 | High | 2 weeks | QA / Engineering |
| 17 | Software System Testing | IEC 62304 | High | 2 weeks | QA / Engineering |
| 18 | Usability Engineering File (IEC 62366-1) | Annex I, GSPR 5 | High | 3-4 weeks | UX / Regulatory |
| 19 | Cybersecurity Assessment | Annex I, GSPR 17.2 | High | 2-3 weeks | Engineering |
| 20 | Clinical Evaluation Plan (CEP) | MDR Art. 61 | Critical | 1-2 weeks | Clinical / Regulatory |
| 21 | Clinical Literature Review | MDR Art. 61 | Critical | 4-6 weeks | Clinical |
| 22 | Clinical Evaluation Report (CER) | MDR Art. 61 | Critical | 2-3 weeks | Clinical / Regulatory |
| 23 | PMCF Plan | MDR Art. 74 | Critical | 1-2 weeks | Clinical |
| 24 | Post-Market Surveillance (PMS) Plan | MDR Art. 84 | Critical | 1 week | Regulatory |
| 25 | PSUR Template | MDR Art. 86 | High | 3 days | Regulatory |
| 26 | Instructions for Use (IFU) | Annex I, GSPR 23 | Critical | 2 weeks | Regulatory / UX |
| 27 | Labeling (App Store, In-App) | Annex I, GSPR 23 | High | 1 week | Product / Regulatory |
| 28 | Declaration of Conformity | Annex IV | Critical | 1 day | Regulatory |

**Total Documentation Effort:** ~40-50 weeks of work (parallelised across 2-3 FTEs = 4-6 months elapsed)

---

## 4. Risk Management Foundation (ISO 14971)

### 4.1 Top 10 Hazards for Glucose + Weight-Loss SaMD

| ID | Hazard | Hazardous Situation | Potential Harm | Probability | Severity | Risk Control |
|---|---|---|---|---|---|
| R01 | Algorithm inaccuracy | App predicts stable glucose but user experiences hyperglycaemia | Missed medical intervention, diabetic complications | Medium | High | Clinical validation, disclaimer, HCP oversight prompt |
| R02 | Data breach | Unauthorised access to glucose/health data | Privacy violation, discrimination, GDPR fines | Low | High | Encryption (at rest + in transit), access controls, penetration testing |
| R03 | Software crash / freeze | App crashes during glucose spike event | Loss of monitoring, missed trend | Medium | Medium | Offline caching, background sync, crash monitoring, redundancy |
| R04 | Algorithmic bias | Model trained on non-representative population | Ineffective/dangerous advice for ethnic minorities, elderly | Medium | High | Training data diversity audit, stratified validation, fairness metrics |
| R05 | CGM integration failure | API downtime or stale data feed | Decisions based on outdated glucose values | Medium | High | Data freshness checks, stale-data alerts, fallback to manual entry |
| R06 | User misinterpretation | Lay user interprets "stable" as "no diabetes risk" | Dangerous self-treatment, delayed diagnosis | High | Medium | Clear IFU, graded warnings, explicit "not a diagnostic tool" statements |
| R07 | Inappropriate advice for T1DM | T1DM user follows weight-loss advice without insulin adjustment | Ketoacidosis, severe hypoglycaemia | Medium | Critical | Contraindication screening, user onboarding questionnaire, T1DM exclusion |
| R08 | Over-reliance on app | User stops consulting healthcare provider | Delayed professional care, unmanaged comorbidities | High | Medium | Periodic HCP reminder, usage limit nudges, "consult your doctor" prompts |
| R09 | Incorrect unit display | mg/dL vs mmol/L confusion | Wrong interpretation of glucose values | Low | Critical | Locked unit preference, prominent unit display, onboarding confirmation |
| R10 | Update failure | OTA update bricks app or resets data | Loss of historical data, missed monitoring | Low | Medium | Staged rollout, rollback capability, automated backup, update validation |

### 4.2 Risk Acceptance Criteria
- **Unacceptable:** Any risk with Severity = Critical AND Probability ≠ Negligible
- **As Low As Reasonably Possible (ALARP):** Risks with Severity = High must have risk controls reducing probability to Low or Negligible
- **Acceptable:** All residual risks must be documented in the Risk Management Report with benefit-risk justification

### 4.3 Recommended Risk Control Hierarchy
1. **Inherent safety by design:** Exclude high-risk populations (e.g., Type 1 diabetes without clinician oversight)
2. **Protective measures:** Data validation, stale-data alerts, unit-locking
3. **Information for safety:** Clear IFU, contraindications, "consult your doctor" prompts

---

## 5. Clinical Evaluation Strategy

### 5.1 Route Selection
**Recommended: Route B — Literature Review + Bench/Algorithm Validation + PMCF**

Justification:
- Your device is a lifestyle management tool, not a drug-delivery or diagnostic device
- Significant published literature exists on CGM-based lifestyle interventions for T2DM and weight loss
- A full clinical investigation (Route A) would cost €300k+ and delay launch by 12-18 months
- PMCF can gather real-world outcome data post-launch to strengthen the clinical evidence base

### 5.2 Clinical Evidence Requirements

| Evidence Type | Purpose | Approach | Effort |
|---|---|---|---|
| **Analytical Validation** | Does the app accurately ingest and display glucose data? | Verify CGM API data fidelity, unit conversion accuracy, timestamp integrity | 1-2 weeks |
| **Algorithm Validation** | Do the personalised insights correlate with expected outcomes? | Retrospective cohort simulation, sensitivity/specificity of trend predictions vs. clinical outcomes | 3-4 weeks |
| **Clinical Validation** | Do users actually achieve weight loss / glycaemic improvement? | Literature synthesis + PMCF prospective study | 4-6 weeks (lit) + 12 months (PMCF) |
| **Usability Validation** | Can the intended user population operate the app safely? | IEC 62366-1 usability testing (formative + summative) | 3-4 weeks |

### 5.3 Predicate / Equivalent Device Search
Search EUDAMED and FDA 510(k) database for:
- MyFitnessPal / Noom (wellness, not SaMD — limited equivalence)
- Livongo / Teladoc diabetes management platforms (Class II, closest equivalent)
- Omada Health (CDC-recognised DPP, but not CE marked as SaMD)
- Roche Diabetes Care apps (Accu-Chek, mySugr — Class IIb in EU)

**Note:** Equivalence under MDR (MDCG 2020-5) is stricter than FDA 510(k). You must demonstrate equivalence in **clinical, technical, AND biological** characteristics. For software, "biological" is interpreted as physiological interaction. Full equivalence may be difficult to claim — plan for a hybrid approach (some equivalence + some own data).

### 5.4 PMCF Plan Outline
- Collect anonymised user outcome data (weight change, HbA1c trends if available)
- Monitor adverse events and app-related safety incidents
- Track algorithm performance drift across demographics
- Annual PMCF evaluation report
- Update CER with PMCF findings annually

---

## 6. Applicable Standards & Guidance Mapping

| Standard / Guidance | Scope | Lifecycle Phase | Status |
|---|---|---|---|
| **MDR 2017/745** | Overall regulatory framework | All | Required |
| **EN ISO 13485:2016** | QMS | All | Required |
| **EN IEC 62304:2006 + Amd 1:2015** | Software lifecycle | Design, Development, Maintenance | Required |
| **EN ISO 14971:2019** | Risk management | Design, Post-market | Required |
| **EN IEC 62366-1:2015** | Usability engineering | Design, Validation | Required |
| **EN ISO 10993-17** | Biological evaluation (if patient contact) | Design | Unlikely for pure software |
| **MDCG 2019-11** | Qualification & classification of software | Classification | Required |
| **MDCG 2020-1** | Clinical evaluation — MD software | Clinical | Required |
| **MDCG 2020-5** | Clinical equivalence | Clinical | Required |
| **MDCG 2020-13** | Clinical evaluation — legacy devices | Clinical (if applicable) | If applicable |
| **MDCG 2022-21** | Notified Body audits | Certification | Guidance |
| **NIST CSF / EU CRA** | Cybersecurity | Design, Post-market | Strongly recommended |
| **GDPR 2016/679** | Data protection | All | Legally required |
| **ISO 27001** | Information security | All | Recommended |

---

## 7. 12-Month Compliance Roadmap

### Phase 1 — Foundation (Months 1-3)
| Week | Activity | Deliverable | Owner |
|---|---|---|---|
| 1-2 | Finalise Intended Purpose, patient population, contraindications | Intended Purpose Statement | Regulatory |
| 1-2 | Select Notified Body (MDSW scope) | NB contract / quotation | Management |
| 2-3 | Draft Quality Manual + 15 core SOPs | QMS v1.0 | Regulatory / QA |
| 3-4 | Implement document control system | Controlled document repository | QA |
| 3-6 | Map current SDLC to IEC 62304 | Gap analysis + remediation plan | Engineering |
| 4-6 | Initiate ISO 14971 Risk Management File | Risk Management Plan + preliminary HAZID | Regulatory |
| 6-8 | Complete GSPR checklist (Annex I) | GSPR checklist + traceability matrix skeleton | Regulatory |
| 8-10 | Draft Software Requirements Specification | SRS v1.0 | Engineering |
| 10-12 | Establish SOUP inventory + maintenance plan | SOUP register | Engineering |

**Milestone:** QMS operational, design controls active, risk management initiated.

### Phase 2 — Documentation & Validation (Months 4-6)
| Week | Activity | Deliverable | Owner |
|---|---|---|---|
| 12-14 | Finalise Software Architecture & Detailed Design | Architecture document, module specs | Engineering |
| 14-16 | Complete Risk Analysis (FMEA) + Risk Controls | Risk Analysis Table, Risk Management Report | Regulatory |
| 16-18 | Conduct formative usability evaluation | Usability Engineering File (formative) | UX / Regulatory |
| 18-20 | Execute Software V&V (unit, integration, system testing) | V&V reports, test protocols | QA / Engineering |
| 20-22 | Cybersecurity assessment + penetration testing | Security assessment report | Engineering |
| 22-24 | Draft Instructions for Use (IFU) + Labeling | IFU v1.0, app store labeling | Regulatory / UX |

**Milestone:** Technical Documentation 80% complete, software validated.

### Phase 3 — Clinical & Finalisation (Months 7-9)
| Week | Activity | Deliverable | Owner |
|---|---|---|---|
| 24-26 | Finalise Clinical Evaluation Plan (CEP) | CEP signed | Clinical / Regulatory |
| 26-30 | Conduct literature review + equivalence assessment | Literature review report | Clinical |
| 28-30 | Summative usability testing | Usability validation report | UX / Regulatory |
| 30-32 | Draft Clinical Evaluation Report (CER) | CER v1.0 | Clinical / Regulatory |
| 32-34 | Finalise PMCF Plan + PMS Plan | PMCF Plan, PMS Plan | Clinical / Regulatory |
| 34-36 | Internal QMS audit + CAPA closure | Internal audit report, CAPA log | QA |
| 36-38 | Compile full Technical Documentation | Annex III dossier complete | Regulatory |

**Milestone:** Technical Documentation complete, ready for Notified Body submission.

### Phase 4 — Certification & Launch (Months 10-12)
| Week | Activity | Deliverable | Owner |
|---|---|---|---|
| 38-40 | Submit Technical Documentation to Notified Body | NB submission dossier | Regulatory |
| 40-42 | Notified Body Stage 1 Audit (QMS documentation) | Stage 1 findings, action plan | QA / Regulatory |
| 42-44 | Address Stage 1 findings | CAPA closure evidence | QA |
| 44-46 | Notified Body Stage 2 Audit (on-site / remote) | Stage 2 findings | QA / Regulatory |
| 46-48 | Address Stage 2 findings + TD review comments | Final CAPA closure | QA / Regulatory |
| 48-50 | Receive CE certificate + EUDAMED registration | CE certificate, SRN, UDI registration | Regulatory |
| 50-52 | Launch with active PMS/PMCF | Market release, PSUR schedule active | All |

**Milestone:** CE marked, EUDAMED registered, market launch.

---

## 8. Next Actions — Immediate 30-Day Priorities

### Week 1
- [ ] **Select Notified Body:** Contact 3 Notified Bodies with MDSW scope (e.g., TÜV SÜD, BSI, DEKRA). Request quotation and timeline for Class IIa software audit.
- [ ] **Hire/appoint Regulatory Lead:** You need at least 0.5 FTE dedicated to MDR compliance. Consider external regulatory consultant (€5k-€10k/month).
- [ ] **Freeze Feature Scope:** Document current intended use. Any new features (especially dosing, alerts, diagnostics) must go through change control.

### Week 2
- [ ] **Draft Intended Purpose Statement:** One paragraph that will appear in your IFU, technical documentation, and EUDAME. This is the regulatory anchor for everything.
- [ ] **Appoint Management Representative:** ISO 13485 requires a management rep with defined authority for QMS. Name this person in your Quality Manual.
- [ ] **Purchase QMS / ALM Tool:** Consider Greenlight Guru, MatrixALM, or Jira + Confluence with validation packages. Budget €500-€2,000/month.

### Week 3
- [ ] **Draft Quality Manual:** Define QMS scope (design, development, distribution, servicing of SaMD). Justify any exclusions.
- [ ] **Begin SOUP Inventory:** List every third-party library, cloud service, and API. Include version numbers and maintenance plans.
- [ ] **Initiate Risk Management Plan:** Define risk acceptability criteria, risk management team, and evaluation methods.

### Week 4
- [ ] **GSPR Workshop:** Walk through MDR Annex I GSPRs. For each requirement, determine applicability, method of compliance, and evidence needed.
- [ ] **Traceability Matrix Skeleton:** Create the spreadsheet/framework that will track GSPR ↔ Design Input ↔ Verification ↔ Evidence for the entire project.
- [ ] **Engage Clinical Consultant:** For CEP/CER and literature review support. Budget €10k-€20k.

---

## 9. Budget Estimate

| Category | Estimated Cost (€) | Notes |
|---|---|---|
| **Notified Body Fees** | 25,000 – 40,000 | Class IIa audit + TD review + annual surveillance |
| **Regulatory Consultant** | 30,000 – 60,000 | 6-12 months support, documentation drafting |
| **QMS / ALM Tooling** | 6,000 – 24,000 | Annual subscription (€500-€2,000/month) |
| **Clinical Evaluation** | 15,000 – 30,000 | Literature review + CER writing + PMCF design |
| **Usability Testing** | 8,000 – 15,000 | Formative + summative (IEC 62366-1) |
| **Cybersecurity / Pen Testing** | 5,000 – 12,000 | External penetration testing + vulnerability assessment |
| **Internal FTE Cost** | 60,000 – 90,000 | 1.0-1.5 FTE for 12 months (loaded cost) |
| **Testing & Validation** | 5,000 – 10,000 | Test environment, automated testing tools |
| **Contingency (15%)** | 22,000 – 42,000 | NB findings, scope changes, delays |
| **TOTAL** | **€176,000 – €323,000** | |

**Minimum Viable Budget:** €80,000-€100,000 (if internal team is strong, heavy use of templates, single-market EU, no major NB findings).

---

## 10. Key Contacts & Resources

### Notified Bodies (MDSW Scope)
- **TÜV SÜD Product Service GmbH** (DE) — strong software expertise
- **BSI Group** (UK/NL) — large capacity, English-language friendly
- **DEKRA Certification B.V.** (NL) — competitive pricing for software
- **SGS Belgium NV** (BE) — EU-wide presence

### Regulatory Consultants (EU MDR SaMD Specialisation)
- Search EUROPAMED and RAPS directories for consultants with IEC 62304 + MDR software experience.

### Guidance Documents
- [MDCG 2019-11: Qualification and Classification of Software](https://health.ec.europa.eu/medical-devices-sector/new-regulations/guidance-mdcg-endorsed-documents-and-other-guidance_en)
- [MDCG 2020-1: Clinical Evaluation — MD Software](https://health.ec.europa.eu/medical-devices-sector/new-regulations/guidance-mdcg-endorsed-documents-and-other-guidance_en)
- [IMDRF SaMD Guidance](https://www.imdrf.org/documents)

---

## Disclaimer

This report provides regulatory guidance based on EU MDR 2017/745 and applicable harmonised standards as of the report date. It does not constitute legal advice. Final classification, conformity assessment routes, and technical documentation requirements must be confirmed with your selected Notified Body and qualified regulatory affairs personnel. The agent cannot guarantee NB acceptance of any document or approach.

---

*Report generated by SaMD EU MDR Compliance Agent*  
*Scope: agents/samd-compliance-eu*  
*Skill: samd-eu-mdr*
