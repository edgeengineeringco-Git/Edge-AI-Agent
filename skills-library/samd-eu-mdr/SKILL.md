# SaMD EU MDR Compliance Skill

## Purpose
Transform a wellness application into a compliant Software as a Medical Device (SaMD) under EU MDR 2017/745. Covers classification, technical documentation, risk management, software lifecycle, clinical evaluation, QMS gaps, and post-market surveillance.

## Scope
- EU MDR 2017/745 (not IVDR — this is medical device software, not IVD)
- Applicable harmonised standards: EN ISO 13485, EN IEC 62304, EN ISO 14971, EN IEC 62366-1, EN ISO 10993-17 (if patient contact), EN 62304/Amendment 1
- MDCG guidance: 2019-11 (qualification/classification), 2020-1 (clinical evaluation), 2020-13 (clinical evaluation — legacy devices), 2022-21 (Notified Body audits)

## Device Classification (EU MDR Rule 11)

### Rule 11 Logic
> Software intended to provide information which is used to take decisions with diagnosis or therapeutic purposes is classified as **Class IIa**, except if such decisions have an impact that may cause:
> - death or an irreversible deterioration of a person's state of health (Class III)
> - a serious deterioration of a person's state of health or a surgical intervention (Class IIb)

### Your Device Profile
**Intended Use:** Monitor glucose fluctuations and deliver personalized insights to support weight-loss decisions.

**Likely Classification: Class IIa**
- Provides information used for therapeutic decisions (lifestyle/dietary modifications)
- Does not directly control drug delivery or acute life-support
- If future versions add insulin-dosing recommendations or severe-hypoglycaemia alerts → Class IIb

**Justification template:**
```
Device Name: [App Name]
Intended Purpose: Software for monitoring glucose fluctuations and providing 
  personalized lifestyle insights to support weight management in adults with 
  prediabetes, type 2 diabetes, or metabolic syndrome.
Rule Applied: MDR Annex VIII, Rule 11
Classification: Class IIa
Rationale: The software processes physiological data (glucose) and provides 
  information used to take therapeutic decisions (dietary/exercise modifications). 
  The decisions do not cause death, irreversible deterioration, or surgical 
  intervention. The impact is managed through lifestyle changes under user 
  discretion and healthcare-provider oversight.
```

### Class IIa Implications
- **Conformity route:** Annex IX (QMS + technical documentation) OR Annex X (EU type-examination) + Annex XI (production quality assurance). Most SaMD uses **Annex IX Chapter I + III**.
- **Notified Body required:** Yes. NB must audit QMS and review technical documentation.
- **Clinical evidence:** Clinical evaluation report (CER) required per MDR Article 61.
- **Post-market surveillance:** PSUR every 2 years for Class IIa (Article 86).

## Technical Documentation (Annex III)

### Required Documents
1. **Device Description & Specification**
   - UDI-DI, basic UDI-DI
   - Intended purpose, patient population, contraindications
   - Hardware/software dependencies (OS versions, CGM integration APIs)
   - Architecture diagram (mobile app, backend, ML inference pipeline)

2. **Information Supplied by Manufacturer**
   - Instructions for Use (IFU) — must include MDR-required statements
   - Labeling (app store screenshots are labeling)
   - Patient user interface warnings and precautions

3. **Design & Manufacturing**
   - Software development lifecycle records (IEC 62304)
   - Design reviews, verification & validation reports
   - Version control and configuration management
   - Third-party / SOUP (Software of Unknown Provenance) inventory

4. **General Safety & Performance Requirements (GSPR)**
   - Annex I checklist (all 23 chapters)
   - Traceability matrix: GSPR ↔ Design Input ↔ Verification Method ↔ Evidence

5. **Benefit-Risk Analysis**
   - ISO 14971 risk management file
   - Residual risk acceptance criteria
   - Risk control measures implemented in software

6. **Verification & Validation**
   - Software V&V per IEC 62304
   - Usability engineering per IEC 62366-1
   - Cybersecurity (NIST / EU CRA alignment)
   - Algorithm validation (if ML/AI: MDCG 2019-9, Good Machine Learning Practice)

7. **Clinical Evaluation**
   - Clinical evaluation plan (CEP)
   - Literature review (if equivalence claimed, MDCG 2020-5)
   - Clinical data (if own studies conducted)
   - Clinical evaluation report (CER)
   - PMCF plan (Post-Market Clinical Follow-up)

8. **Post-Market Surveillance**
   - PMS plan
   - PSUR template (every 2 years)
   - Trend reporting procedure

## Risk Management (ISO 14971)

### SaMD-Specific Hazards
| Hazard | Potential Harm | Risk Control |
|---|---|---|
| Incorrect glucose trend prediction | Wrong dietary advice → hyper/hypoglycaemia | Algorithm validation, disclaimer, clinician oversight |
| Data breach (PHI) | Privacy violation, discrimination | Encryption, access controls, GDPR + MDR dual compliance |
| Software failure / crash | Loss of monitoring, missed trends | Redundancy, offline caching, error handling |
| Algorithmic bias | Ineffective advice for certain demographics | Training data diversity validation, stratified testing |
| Integration failure (CGM API) | Stale or missing data | API health checks, data freshness validation, user alert |
| Misinterpretation by lay user | Dangerous self-treatment | Clear IFU, graded warnings, escalation to HCP |

### Risk Management File Structure
```
Risk Management File/
├── Risk Management Plan
├── Risk Analysis (HAZID, FMEA)
├── Risk Evaluation (acceptance criteria)
├── Risk Control Measures
├── Residual Risk Evaluation
├── Benefit-Risk Analysis
├── Risk Management Report
└── Production & Post-Production Monitoring
```

## Software Lifecycle (IEC 62304)

### Safety Classification
Class IIa SaMD is typically **Class B** (software can contribute to hazardous situations but serious injury is not probable) or **Class C** (if failure could cause serious injury). 

For glucose monitoring + lifestyle advice:
- **Likely Class B** if no acute dosing recommendations
- **Upgrade to Class C** if insulin-dosing or emergency alerts added

### Required Processes
1. **Software Development Plan**
2. **Software Requirements Analysis** (traceable to GSPR)
3. **Software Architecture Design**
4. **Software Detailed Design** (for Class B/C)
5. **Software Unit Implementation & Verification**
6. **Software Integration & Integration Testing**
7. **Software System Testing**
8. **Software Release**
9. **Software Maintenance** (problem resolution, change control)
10. **Software Risk Management** (linked to ISO 14971)
11. **Software Configuration Management**
12. **SOUP Management** (third-party libraries, OS, cloud services)

### SOUP Inventory Template
| Component | Version | Manufacturer | Safety Class | Anomaly List | Maintenance Plan |
|---|---|---|---|---|---|
| React Native | 0.73 | Meta | N/A | CVE monitoring | Quarterly review |
| Firebase Auth | latest | Google | N/A | Google security bulletins | Monthly review |
| HealthKit API | iOS 17+ | Apple | N/A | Apple release notes | Per iOS release |
| [CGM SDK] | [v] | [Manufacturer] | N/A | Manufacturer advisories | Per manufacturer notice |

## Clinical Evaluation (MDR Article 61)

### Route Selection
For Class IIa SaMD with no equivalent predicate:
- **Route A:** Clinical investigation (prospective study)
- **Route B:** Literature review + bench testing/algorithm validation + PMCF
- Most glucose-monitoring lifestyle apps use **Route B** with PMCF to gather real-world outcome data

### Clinical Evidence Needed
1. **Analytical Validation:** Does the software accurately process glucose inputs?
2. **Clinical Validation:** Do the personalized insights actually improve weight-loss outcomes or glycaemic control?
3. **Usability Validation:** Can the intended user population safely operate the app?

### PMCF Plan (Mandatory for Class IIa)
- Real-world performance monitoring
- User outcome data collection (with consent)
- Adverse event monitoring
- Algorithm performance drift detection
- Update schedule: minimum annually

## QMS Gap Analysis (ISO 13485)

### Major Gaps for Software Startups
| ISO 13485 Clause | Typical Wellness App State | Required State |
|---|---|---|
| 4.1 (Quality Manual) | Missing | Documented QMS scope, exclusions justified |
| 4.2 (Document Control) | Basic git | Formal DHR/DHF, approval signatures, version control |
| 5.3 (Quality Policy) | Informal | Signed policy, objectives, KPIs |
| 7.1 (Resources) | Ad-hoc | Competency records, training matrix |
| 7.3 (Design & Development) | Agile sprints | Design plan, reviews, traceability, DHF |
| 7.5 (Production) | CI/CD | Controlled build, release checklist, SOUP management |
| 8.2 (Monitoring & Measurement) | Crashlytics | PMS system, complaint handling, adverse event reporting |
| 8.5 (Improvement) | Bug backlog | CAPA system, risk-based prioritization |

## EUDAMED & Registration

### Steps
1. **Actor Registration:** Manufacturer SRN (Single Registration Number)
2. **Device Registration:** Basic UDI-DI, UDI-DI per version/platform
3. **Notified Body:** Select NB with MDR code MDSW (medical device software)
4. **Certificate:** Upload NB certificate to EUDAMED
5. **Vigilance:** Report serious incidents within 10 days (Article 87)

### UDI Requirements for SaMD
- **Basic UDI-DI:** One per device model/family
- **UDI-DI:** Per platform (iOS, Android) and per major version if safety-relevant changes
- **UDI-PI:** Production identifier (version/build number)
- Issuing entities: GS1, HIBCC, ICCBBA

## Cybersecurity & GDPR

### MDR + Cybersecurity
- MDR Annex I GSPR 17.2: Protection against unauthorised access
- MDCG 2019-16: Guidance on cybersecurity
- NIST Cybersecurity Framework alignment recommended
- EU Cyber Resilience Act (CRA) 2024: Applies to software with digital elements

### GDPR Overlap
- Health data = Special category data (Article 9)
- Lawful basis: Explicit consent or substantial public interest (healthcare)
- DPIA (Data Protection Impact Assessment) mandatory
- DPO likely required if core activity is health data processing at scale

## Action Plan: 12-Month Roadmap

### Phase 1 — Foundation (Months 1-3)
- [ ] Finalize intended use and patient population
- [ ] Complete MDR classification justification (Class IIa)
- [ ] Select Notified Body and confirm scope
- [ ] Draft Quality Manual and QMS procedures
- [ ] Initiate ISO 14971 risk management file
- [ ] Map current software lifecycle to IEC 62304

### Phase 2 — Documentation (Months 3-6)
- [ ] Complete GSPR checklist and traceability matrix
- [ ] Finalize Software Requirements Specification
- [ ] Complete risk analysis and risk controls
- [ ] Draft Clinical Evaluation Plan (CEP)
- [ ] Conduct usability engineering (IEC 62366-1)
- [ ] Implement formal configuration management

### Phase 3 — Validation (Months 6-9)
- [ ] Software verification & validation (IEC 62304)
- [ ] Algorithm validation (analytical + clinical)
- [ ] Cybersecurity penetration testing
- [ ] Complete Clinical Evaluation Report (CER)
- [ ] Finalize IFU and labeling
- [ ] Internal QMS audit

### Phase 4 — Certification & Launch (Months 9-12)
- [ ] Notified Body QMS audit (Stage 1 + Stage 2)
- [ ] Technical documentation review by NB
- [ ] EUDAMED actor and device registration
- [ ] CE marking affixed (app store badges, splash screens)
- [ ] Launch with PMS/PMCF systems active
- [ ] PSUR schedule established (every 2 years)

## Quick-Start Templates

When the agent is asked to generate documentation, it should produce:
1. **Classification Justification Document** (1-2 pages)
2. **GSPR Checklist** (spreadsheet format)
3. **Risk Analysis Table** (ISO 14971 format)
4. **Software Development Plan** (IEC 62304 aligned)
5. **Clinical Evaluation Plan** (MDCG 2020-1 aligned)
6. **QMS Gap Analysis Report** (ISO 13485 checklist)
7. **PMS Plan & PSUR Template**

## Invocation
Trigger this skill when the user asks about:
- EU MDR classification for their app
- SaMD compliance, CE marking, Notified Body preparation
- ISO 13485, IEC 62304, ISO 14971 documentation
- Technical documentation, GSPR, clinical evaluation
- Gap analysis between current state and MDR readiness
- Post-market surveillance or vigilance requirements
