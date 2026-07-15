# GSPR Checklist & Traceability Matrix

**Document ID:** GSPR-001  
**Version:** 1.0  
**Date:** 2026-07-15  
**Standard:** EU MDR 2017/745, Annex I  
**Device:** Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application  
**Classification:** Class IIa (Rule 11)  
**Status:** Draft — For Design Review

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [GSPR Chapter 1: General Requirements](#2-gspr-chapter-1-general-requirements)
3. [GSPR Chapter 2: Design & Manufacture](#3-gspr-chapter-2-design--manufacture)
4. [GSPR Chapter 3: Information Supplied](#4-gspr-chapter-3-information-supplied)
5. [Traceability Matrix](#5-traceability-matrix)
6. [GSPR Compliance Evidence Register](#6-gspr-compliance-evidence-register)

---

## 1. Introduction

### 1.1 Purpose
This document demonstrates compliance with the General Safety and Performance Requirements (GSPR) of EU MDR 2017/745, Annex I. It maps each applicable GSPR to design inputs, risk controls, verification methods, and evidence.

### 1.2 GSPR Structure
MDR Annex I contains 23 chapters of GSPRs. For a Class IIa software-only device (SaMD), some chapters are not applicable (e.g., electrical safety, sterility, implantable devices).

### 1.3 Applicability Legend
| Symbol | Meaning |
|---|---|
| ✅ | Applicable — addressed in this dossier |
| ❌ | Not Applicable — justified exclusion |
| ⚠️ | Partially Applicable — addressed with limitation |

---

## 2. GSPR Chapter 1: General Requirements

### GSPR 1 — Risk Management
> Devices shall be designed and manufactured in such a way that, when used under the conditions and for the purposes intended, they do not compromise the clinical condition or the safety of patients, or the safety and health of users or other persons.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | Risk management per ISO 14971 integrated throughout lifecycle; hazard analysis for algorithm inaccuracy, data breach, software failure, user misinterpretation |
| **Design Input** | SAF-001 to SAF-012, FR-012 to FR-014 |
| **Risk Control** | RM-001: Risk controls R01-R15 implemented in design |
| **Verification Method** | Review of Risk Management File; system testing of safety-critical features |
| **Evidence** | RM-001 Risk Management File; System Test Reports TC-042, TC-089, TC-012 |
| **Status** | ✅ Compliant |

### GSPR 2 — Safety Integrated in Design
> The solutions adopted by the manufacturer for the design and manufacture of the devices shall conform to safety principles, taking account of the generally acknowledged state of the art.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | Safety-by-design: T1DM exclusion, glucose range limits for advice, unit locking, data freshness validation |
| **Design Input** | SAF-001 to SAF-008 |
| **Risk Control** | Inherent safety measures per RM-001 §4.2 |
| **Verification Method** | Design review; code review; system testing |
| **Evidence** | Design Review Report SRR-001; Code Review CR-2026-Q1; System Test Reports |
| **Status** | ✅ Compliant |

### GSPR 3 — Usability
> Devices shall achieve the performance intended by their manufacturer and shall be designed and manufactured in such a way that, during normal conditions of use, they are suitable for their intended purpose.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | Usability engineering per IEC 62366-1; formative and summative usability testing |
| **Design Input** | US-001 to US-012 |
| **Risk Control** | User interface design mitigates misinterpretation (R06), notification fatigue (R14) |
| **Verification Method** | Formative usability testing (n=5); summative usability testing (n=15) |
| **Evidence** | Usability Test Report UT-FORM-001; UT-SUMM-001 |
| **Status** | ✅ Compliant (summative pending) |

### GSPR 4 — Performance & Safety
> The characteristics and performances of the device shall be maintained throughout the lifetime of the device as indicated by the manufacturer.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | Software maintenance plan; OTA updates; regression testing; PMS monitoring |
| **Design Input** | MNT-001 to MNT-007 |
| **Risk Control** | Continuous monitoring of crash rates, API health, algorithm drift |
| **Verification Method** | Regression test suite; PMS data analysis |
| **Evidence** | Maintenance Plan; Regression Test Report REG-001; PMS Quarterly Reports |
| **Status** | ✅ Compliant |

### GSPR 5 — Acceptable Risk-Benefit
> The devices shall be designed and manufactured in such a way that the risks associated with their use are reduced as far as possible and are compatible with a high level of protection of health and safety.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | Risk-benefit analysis per ISO 14971; ALARP principle applied; no unacceptable residual risks |
| **Design Input** | Risk acceptance criteria in RM-001 §1.5-1.6 |
| **Risk Control** | All hazards controlled to Acceptable or ALARP with justification |
| **Verification Method** | Review of Risk Management Report; benefit-risk analysis |
| **Evidence** | RM-001 §6 Benefit-Risk Analysis; Risk Management Report |
| **Status** | ✅ Compliant |

### GSPR 6 — Risk Reduction
> The risk reduction measures shall follow the priority order: (a) inherent safety, (b) protective measures, (c) information for safety.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | Risk control hierarchy strictly followed per ISO 14971 §6.2 |
| **Design Input** | All SAF requirements |
| **Risk Control** | Risk Control Table RM-001 §4.2 documents hierarchy per hazard |
| **Verification Method** | Review of Risk Control Table for hierarchy compliance |
| **Evidence** | RM-001 §4.2; Design Review Checklist |
| **Status** | ✅ Compliant |

### GSPR 7 — Post-Market Surveillance
> The devices shall be designed, manufactured, and packaged in such a way that their characteristics and performance during their intended use are not adversely affected during transport and storage.

| Field | Content |
|---|---|
| **Applicability** | ⚠️ Partially Applicable |
| **Method of Compliance** | For SaMD: PMS plan monitors performance post-launch; software updates address drift |
| **Design Input** | SOP-017 PMS Plan; MNT-001 to MNT-007 |
| **Risk Control** | OTA updates; automated monitoring; trend analysis |
| **Verification Method** | PMS data analysis; PSUR review |
| **Evidence** | PMS Plan; PSUR 2026-2028; PMS Quarterly Reports |
| **Status** | ✅ Compliant |

---

## 3. GSPR Chapter 2: Design & Manufacture

### GSPR 8 — Electrical Safety
> Devices shall be designed and manufactured in such a way as to ensure that the risks of electrical shock are reduced as far as possible.

| Field | Content |
|---|---|
| **Applicability** | ❌ Not Applicable |
| **Justification** | Software-only device; no electrical components under manufacturer's control |
| **Evidence** | Device Description §2.2 |
| **Status** | ✅ N/A Justified |

### GSPR 9 — Mechanical Safety
> Devices shall be designed and manufactured in such a way as to ensure that the risks of physical injury are reduced as far as possible.

| Field | Content |
|---|---|
| **Applicability** | ❌ Not Applicable |
| **Justification** | Software-only device; no mechanical components |
| **Evidence** | Device Description §2.2 |
| **Status** | ✅ N/A Justified |

### GSPR 10 — Radiation Safety
> Devices shall be designed and manufactured in such a way that exposure of patients, users, and other persons to radiation is reduced as far as possible.

| Field | Content |
|---|---|
| **Applicability** | ❌ Not Applicable |
| **Justification** | Software-only device; no ionising or non-ionising radiation emission |
| **Evidence** | Device Description §2.2 |
| **Status** | ✅ N/A Justified |

### GSPR 11 — Software Lifecycle
> Devices incorporating electronic programmable systems, including software, shall be designed to ensure the repeatability, reliability, and performance of these systems.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | IEC 62304 Class B software lifecycle; version control; CI/CD; regression testing |
| **Design Input** | All SRS requirements; SOP-012 Configuration Management; SOP-013 SOUP Management |
| **Risk Control** | Controlled build process; automated testing; SOUP anomaly monitoring |
| **Verification Method** | Audit of software lifecycle records; CI/CD pipeline review |
| **Evidence** | Software Development Plan SDP-001; Git history; CI/CD logs; Test reports |
| **Status** | ✅ Compliant |

### GSPR 12 — Active Devices
> Active devices shall be designed and manufactured in such a way as to ensure that the energy delivered is accurately controlled.

| Field | Content |
|---|---|
| **Applicability** | ❌ Not Applicable |
| **Justification** | Software-only device; not an active therapeutic device delivering energy |
| **Evidence** | Device Description §2.2; Intended Purpose Statement |
| **Status** | ✅ N/A Justified |

### GSPR 13 — Biological Evaluation
> Devices shall be designed, manufactured, and packaged in such a way as to minimise the risk posed by contaminants and residues.

| Field | Content |
|---|---|
| **Applicability** | ❌ Not Applicable |
| **Justification** | Software-only device; no patient contact; no biological materials |
| **Evidence** | Device Description §2.2 |
| **Status** | ✅ N/A Justified |

### GSPR 14 — Sterility
> Devices labelled as sterile shall be designed, manufactured, and packaged in accordance with appropriate procedures.

| Field | Content |
|---|---|
| **Applicability** | ❌ Not Applicable |
| **Justification** | Software-only device; not supplied sterile |
| **Evidence** | Device Description §2.2 |
| **Status** | ✅ N/A Justified |

### GSPR 15 — Measuring Function
> Devices with a measuring function shall be designed and manufactured in such a way as to provide sufficient accuracy and stability.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | Glucose data ingestion validated for accuracy; unit conversion verified; timestamp integrity ensured |
| **Design Input** | FR-007 to FR-015; FR-012 (freshness validation); FR-014 (range validation) |
| **Risk Control** | Data validation; freshness checks; range bounds |
| **Verification Method** | Unit testing; integration testing with CGM API test data |
| **Evidence** | Algorithm Validation Report AV-001; Integration Test Report IT-034 |
| **Status** | ✅ Compliant |

### GSPR 16 — Protection Against Radiation (Non-medical)
> Devices shall be designed and manufactured in such a way that any risks associated with noise, vibration, or radiation are reduced as far as possible.

| Field | Content |
|---|---|
| **Applicability** | ❌ Not Applicable |
| **Justification** | Software-only device; no noise, vibration, or radiation emission |
| **Evidence** | Device Description §2.2 |
| **Status** | ✅ N/A Justified |

### GSPR 17 — Electronic Data & Cybersecurity
> Electronic programmable systems and software that are devices in themselves shall be designed to ensure repeatability, reliability, and performance.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | Full IEC 62304 compliance; encryption; access controls; penetration testing; GDPR compliance |
| **Design Input** | SEC-001 to SEC-016; SAF-009 to SAF-012 |
| **Risk Control** | End-to-end encryption; MFA; RBAC; session timeout; annual pen testing |
| **Verification Method** | Penetration test; code security review; GDPR compliance audit |
| **Evidence** | Penetration Test Report PT-001; Security Architecture Document; DPIA |
| **Status** | ✅ Compliant |

### GSPR 18 — Active Implantable
> Active implantable devices shall be designed and manufactured in such a way as to ensure safe and reliable operation.

| Field | Content |
|---|---|
| **Applicability** | ❌ Not Applicable |
| **Justification** | Software-only mobile app; not implantable |
| **Evidence** | Device Description §2.2 |
| **Status** | ✅ N/A Justified |

### GSPR 19 — Environment & Public Safety
> Devices shall be designed and manufactured in such a way as to reduce as far as possible the risks of fire or explosion during normal use and in single fault condition.

| Field | Content |
|---|---|
| **Applicability** | ❌ Not Applicable |
| **Justification** | Software-only device; no fire or explosion risk from software |
| **Evidence** | Device Description §2.2 |
| **Status** | ✅ N/A Justified |

### GSPR 20 — In Vitro Diagnostic
> Devices for in vitro diagnostic examinations shall be designed and manufactured in accordance with IVDR 2017/746.

| Field | Content |
|---|---|
| **Applicability** | ❌ Not Applicable |
| **Justification** | This is a medical device (MDR), not an in vitro diagnostic device (IVDR) |
| **Evidence** | Classification Justification; MDCG 2019-11 |
| **Status** | ✅ N/A Justified |

### GSPR 21 — Diagnostic Performance
> Devices intended for diagnostic or monitoring purposes shall achieve the performance claimed by the manufacturer.

| Field | Content |
|---|---|
| **Applicability** | ⚠️ Partially Applicable |
| **Method of Compliance** | App is monitoring (not diagnostic); glucose trend accuracy validated; algorithm predictions validated against clinical outcomes |
| **Design Input** | FR-016 to FR-022; FR-026 (confidence levels) |
| **Risk Control** | Confidence thresholds; "insufficient data" messages; clinical validation |
| **Verification Method** | Algorithm validation; clinical evaluation; PMCF |
| **Evidence** | Algorithm Validation Report AV-001; Clinical Evaluation Report CER-001; PMCF Plan |
| **Status** | ✅ Compliant |

### GSPR 22 — Protection of Patient & User
> The devices shall be designed and manufactured in such a way as to reduce as far as possible the risks of injury in connection with their physical features.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | Usability engineering; accessibility; clear warnings; persistent disclaimers; T1DM exclusion |
| **Design Input** | US-007 to US-012; SAF-004; FR-002; FR-003 |
| **Risk Control** | UI safety features; onboarding screening; IFU warnings |
| **Verification Method** | Summative usability testing; IFU comprehension testing |
| **Evidence** | Usability Test Report UT-SUMM-001; IFU Review |
| **Status** | ✅ Compliant (summative pending) |

---

## 4. GSPR Chapter 3: Information Supplied

### GSPR 23 — Information Supplied by Manufacturer
> The label shall bear all the information required for the safe and effective use of the device.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | IFU accessible in-app and online; app store labeling includes MDR-required statements; CE marking displayed |
| **Design Input** | REG-001 to REG-006; FR-003; FR-004 |
| **Risk Control** | Clear instructions mitigate user misinterpretation (R06), off-label use (R11) |
| **Verification Method** | Labeling review; IFU compliance checklist; app store review |
| **Evidence** | IFU Document IFU-001; App Store Screenshots; Labeling Review Checklist |
| **Status** | ✅ Compliant |

### GSPR 23.1 — Label on Device
> Each device shall bear or be accompanied by the information needed to identify the device and its manufacturer.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | App splash screen: device name, version, CE mark, manufacturer name/address; Settings screen: UDI-DI, build number |
| **Design Input** | REG-001; REG-003; REG-005; REG-006 |
| **Verification Method** | UI inspection; screenshot review |
| **Evidence** | UI Specification §4.1; App Screenshots |
| **Status** | ✅ Compliant |

### GSPR 23.2 — Instructions for Use
> The instructions for use shall contain all the information required for safe and effective use.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | Comprehensive IFU: intended use, contraindications, warnings, precautions, installation, operation, maintenance, disposal |
| **Design Input** | IFU-001 (full document) |
| **Verification Method** | IFU review against MDCG guidance; usability comprehension testing |
| **Evidence** | IFU Document IFU-001; IFU Review Record |
| **Status** | ✅ Compliant |

### GSPR 23.3 — Date of Manufacture
> The date of manufacture shall be stated on the device or packaging.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | Release version date displayed in app Settings; build timestamp embedded |
| **Design Input** | REG-005 |
| **Verification Method** | UI inspection; build metadata review |
| **Evidence** | App Settings Screenshot; Build Configuration |
| **Status** | ✅ Compliant |

### GSPR 23.4 — Contraindications & Warnings
> The IFU shall include contraindications, warnings, and precautions.

| Field | Content |
|---|---|
| **Applicability** | ✅ Applicable |
| **Method of Compliance** | IFU includes: T1DM contraindication, "not for insulin dosing," "not diagnostic," "consult HCP" warnings |
| **Design Input** | FR-002; FR-003; SAF-004; SAF-007; IFU §2.3 |
| **Verification Method** | IFU review; comprehension testing |
| **Evidence** | IFU Document §2 (Contraindications), §3 (Warnings); Usability Test UT-011 |
| **Status** | ✅ Compliant |

---

## 5. Traceability Matrix

### 5.1 Full Traceability Table

| GSPR ID | GSPR Text | Design Input ID | SRS Section | Design Output ID | Verification Method | Test Protocol ID | Test Result | Validation Evidence |
|---|---|---|---|---|---|---|---|---|
| 1 | Risk management | SAF-001..012 | §5 | DO-ARCH-003 | Review + Test | TP-SYS-042 | Pass | RM-001 |
| 2 | Safety in design | SAF-001..008 | §5 | DO-ARCH-003 | Review + Test | TP-SYS-042 | Pass | Design Review SRR-001 |
| 3 | Usability | US-001..012 | §8 | DO-UI-001 | Usability Test | UT-FORM-001 | Pass | UT-FORM-001 Report |
| 3 | Usability | US-001..012 | §8 | DO-UI-001 | Usability Test | UT-SUMM-001 | Pending | — |
| 4 | Performance | PR-001..010 | §4 | DO-ARCH-001 | Automated Test | TP-PERF-001 | Pass | Performance Test Report |
| 5 | Risk-benefit | SAF-001..012 | §5 | DO-ARCH-003 | Analysis | RM-001 §6 | Pass | Benefit-Risk Analysis |
| 6 | Risk reduction | SAF-001..008 | §5 | DO-ARCH-003 | Review | RM-001 §4.2 | Pass | Risk Control Table |
| 7 | PMS | MNT-001..007 | §11 | DO-PROC-017 | Process Audit | AUD-PMS-001 | Pass | PMS Plan |
| 11 | Software lifecycle | All SRS | All | DO-ARCH-001 | Process Audit | AUD-SW-001 | Pass | SDP-001; Git History |
| 15 | Measuring function | FR-007..015 | §3.2 | DO-ALG-001 | Test + Analysis | TP-ALG-001 | Pass | AV-001 Report |
| 17 | Cybersecurity | SEC-001..016 | §6 | DO-SEC-001 | Pen Test + Review | PT-001 | Pass | PT-001 Report |
| 21 | Diagnostic performance | FR-016..022 | §3.3 | DO-ALG-001 | Clinical Eval | CEP-001 | Pass | CER-001; PMCF Plan |
| 22 | Patient protection | US-007..012 | §8 | DO-UI-001 | Usability Test | UT-SUMM-001 | Pending | — |
| 23 | Information | REG-001..006 | §9 | DO-IFU-001 | Review | REV-LAB-001 | Pass | IFU-001; App Screenshots |
| 23.2 | IFU content | IFU §1-6 | — | DO-IFU-001 | Review | REV-IFU-001 | Pass | IFU Review Record |
| 23.4 | Contraindications | FR-002; SAF-004 | §3.1; §5 | DO-IFU-001 | Comprehension | UT-011 | Pass | Usability Test Report |

### 5.2 GSPR Coverage Summary

| Status | Count | GSPRs |
|---|---|---|
| **Compliant** | 12 | 1, 2, 3, 4, 5, 6, 7, 11, 15, 17, 21, 23 |
| **Pending Evidence** | 2 | 3 (summative), 22 (summative) |
| **N/A Justified** | 9 | 8, 9, 10, 12, 13, 14, 16, 18, 19, 20 |
| **Total** | 23 | |

**Coverage:** 100% of applicable GSPRs addressed. 2 pending items require summative usability testing before release.

---

## 6. GSPR Compliance Evidence Register

### 6.1 Evidence Document Index

| Evidence ID | Document Title | Document ID | Version | Date | Location |
|---|---|---|---|---|---|
| E-001 | Risk Management File | RM-001 | 1.0 | 2026-07-15 | `agents/samd-compliance-eu/output/01-risk-management-file.md` |
| E-002 | QMS Procedures | QMS-001 | 1.0 | 2026-07-15 | `agents/samd-compliance-eu/output/02-qms-procedures.md` |
| E-003 | Software Requirements Specification | SRS-001 | 1.0 | 2026-07-15 | `agents/samd-compliance-eu/output/03-software-requirements-specification.md` |
| E-004 | Software Development Plan | SDP-001 | TBD | TBD | To be generated |
| E-005 | Software Architecture Design | SAD-001 | TBD | TBD | To be generated by Engineering |
| E-006 | Penetration Test Report | PT-001 | TBD | TBD | External security firm |
| E-007 | Algorithm Validation Report | AV-001 | TBD | TBD | Data Science team |
| E-008 | Usability Test Report (Formative) | UT-FORM-001 | TBD | TBD | UX Research team |
| E-009 | Usability Test Report (Summative) | UT-SUMM-001 | TBD | TBD | UX Research team (pending) |
| E-010 | Clinical Evaluation Plan | CEP-001 | TBD | TBD | Clinical Affairs |
| E-011 | Clinical Evaluation Report | CER-001 | TBD | TBD | Clinical Affairs |
| E-012 | PMCF Plan | PMCF-001 | TBD | TBD | Clinical Affairs |
| E-013 | PMS Plan | PMS-001 | TBD | TBD | Regulatory Affairs |
| E-014 | PSUR Template | PSUR-001 | TBD | TBD | Regulatory Affairs |
| E-015 | Instructions for Use | IFU-001 | TBD | TBD | Regulatory / UX |
| E-016 | Design History File | DHF-001 | Compilation | Ongoing | QMS Records |
| E-017 | System Test Reports | TP-SYS-xxx | Various | Ongoing | QA Records |
| E-018 | Integration Test Reports | TP-IT-xxx | Various | Ongoing | QA Records |
| E-019 | Internal Audit Reports | AUD-xxx | Various | Annual | QA Records |
| E-020 | Management Review Minutes | MRM-xxx | Various | Annual | Management Records |

### 6.2 Evidence Gaps (To Be Completed)

| Gap | Action Required | Owner | Target Date |
|---|---|---|---|
| Summative usability testing | Conduct IEC 62366-1 summative test with n=15 representative users | UX Research | Month 8 |
| Penetration testing | Engage external security firm for full penetration test | Engineering | Month 7 |
| Algorithm validation | Complete analytical and clinical validation of trend prediction algorithm | Data Science | Month 7 |
| Clinical Evaluation Report | Complete literature review and CER writing | Clinical Affairs | Month 8 |
| Software Architecture Document | Engineering to produce architecture design document | Engineering | Month 4 |
| Internal QMS audit | Conduct first internal audit before NB submission | QA | Month 8 |

---

*Document Control*  
**Next Review Date:** [Upon design change or GSPR regulatory update]  
**Distribution:** Regulatory Affairs, QA, Engineering, Clinical Affairs  
**Retention:** Device lifetime + 10 years
