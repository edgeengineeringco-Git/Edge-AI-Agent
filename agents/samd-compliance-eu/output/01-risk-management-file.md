# Risk Management File

**Document ID:** RM-001  
**Version:** 1.0  
**Date:** 2026-07-15  
**Device:** Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application  
**Classification:** EU MDR Class IIa (Rule 11)  
**Standard:** EN ISO 14971:2019  
**Status:** Draft — For Internal Review

---

## Table of Contents
1. [Risk Management Plan](#1-risk-management-plan)
2. [Risk Analysis](#2-risk-analysis)
3. [Risk Evaluation](#3-risk-evaluation)
4. [Risk Control Measures](#4-risk-control-measures)
5. [Residual Risk Evaluation](#5-residual-risk-evaluation)
6. [Benefit-Risk Analysis](#6-benefit-risk-analysis)
7. [Risk Management Report](#7-risk-management-report)
8. [Production & Post-Production Monitoring](#8-production--post-production-monitoring)

---

## 1. Risk Management Plan

### 1.1 Scope
This Risk Management Plan applies to the Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application, a Class IIa Software as a Medical Device (SaMD) under EU MDR 2017/745. The plan covers all lifecycle phases: design, development, verification, validation, release, and post-market surveillance.

### 1.2 Regulatory Basis
- **MDR 2017/745, Annex I, GSPR 1-3:** Risk management as part of the overall QMS
- **EN ISO 14971:2019:** Application of risk management to medical devices
- **EN IEC 62304:2006 + Amd 1:2015:** Software lifecycle risk management integration
- **MDCG 2019-11:** Qualification and classification of software

### 1.3 Risk Management Team

| Role | Name / Department | Responsibility |
|---|---|---|
| Risk Management Lead | [Name] / Regulatory Affairs | Overall RMF ownership, risk acceptability decisions |
| Software Safety Engineer | [Name] / Engineering | Technical risk identification, risk control implementation |
| Clinical Safety Officer | [Name] / Clinical Affairs | Clinical risk assessment, benefit-risk balance |
| Quality Assurance | [Name] / QA | Verification of risk controls, audit support |
| Management Representative | [Name] / Executive | Final approval of residual risk acceptance |

### 1.4 Risk Acceptability Criteria

| Risk Level | Definition | Action Required |
|---|---|---|
| **Unacceptable** | Severity = Critical AND Probability ≥ Occasional | Risk control mandatory. Device cannot be released until reduced. |
| **ALARP (As Low As Reasonably Possible)** | Severity = High AND Probability ≥ Occasional OR Severity = Critical AND Probability = Remote | Risk controls required. Residual risk must be justified with benefit-risk analysis. |
| **Acceptable** | All other combinations | Document in Risk Management Report. Monitor in PMS. |

### 1.5 Probability Scale

| Level | Descriptor | Qualitative Definition | Quantitative (Annual, per user) |
|---|---|---|---|
| P1 | Negligible | Theoretically possible, never observed | < 1 in 1,000,000 |
| P2 | Remote | Rarely observed in field | 1 in 100,000 – 1 in 1,000,000 |
| P3 | Occasional | May occur in field | 1 in 10,000 – 1 in 100,000 |
| P4 | Probable | Expected to occur periodically | 1 in 1,000 – 1 in 10,000 |
| P5 | Frequent | Expected to occur regularly | > 1 in 1,000 |

### 1.6 Severity Scale

| Level | Descriptor | Clinical Definition | Example for This Device |
|---|---|---|---|
| S1 | Negligible | No injury or inconvenience | Minor UI glitch, non-critical display error |
| S2 | Minor | Temporary inconvenience, no medical intervention | User confusion, need to restart app |
| S3 | Serious | Temporary injury or condition requiring medical intervention | Missed glucose trend leading to mild hyperglycaemia |
| S4 | Critical | Permanent impairment or life-threatening condition | Severe hypoglycaemia requiring emergency treatment |
| S5 | Catastrophic | Death | Death due to diabetic ketoacidosis or hypoglycaemic coma |

### 1.7 Risk Evaluation Matrix

|  | **P1 Negligible** | **P2 Remote** | **P3 Occasional** | **P4 Probable** | **P5 Frequent** |
|---|---|---|---|---|---|
| **S5 Catastrophic** | ALARP | **Unacceptable** | **Unacceptable** | **Unacceptable** | **Unacceptable** |
| **S4 Critical** | Acceptable | ALARP | **Unacceptable** | **Unacceptable** | **Unacceptable** |
| **S3 Serious** | Acceptable | Acceptable | ALARP | ALARP | **Unacceptable** |
| **S2 Minor** | Acceptable | Acceptable | Acceptable | ALARP | ALARP |
| **S1 Negligible** | Acceptable | Acceptable | Acceptable | Acceptable | Acceptable |

---

## 2. Risk Analysis

### 2.1 Hazard Identification (HAZID)

Hazards are identified by reviewing:
- Intended use and reasonably foreseeable misuse
- Software architecture and data flows
- User interaction patterns
- Integration points (CGM APIs, cloud services)
- Environmental conditions of use
- Cybersecurity threat model

### 2.2 Risk Analysis Table

| ID | Hazard | Hazardous Situation | Potential Harm | Initial Prob. | Initial Sev. | Initial Risk |
|---|---|---|---|---|---|---|
| R01 | **Algorithm inaccuracy** — Glucose trend prediction model produces incorrect trend direction or magnitude | User follows dietary advice based on incorrect prediction during actual hyperglycaemic event | Missed medical intervention; progression to diabetic complications | P3 | S3 | **ALARP** |
| R02 | **Data breach** — Unauthorised access to protected health information (PHI) | Attacker exploits API vulnerability or misconfigured cloud storage | Privacy violation; discrimination; GDPR fines; reputational damage | P2 | S3 | **ALARP** |
| R03 | **Software crash / freeze** — Application terminates unexpectedly or becomes unresponsive | App crashes during active glucose spike; user unaware of trend | Loss of monitoring; missed critical trend; delayed user action | P3 | S3 | **ALARP** |
| R04 | **Algorithmic bias** — ML model trained on non-representative population | Non-Caucasian or elderly user receives inaccurate personalised advice | Ineffective or dangerous advice; health disparity; regulatory non-compliance | P3 | S3 | **ALARP** |
| R05 | **CGM integration failure** — API downtime, stale data, or corrupted transmission | App displays 2-hour-old glucose value as current; user acts on stale data | Decisions based on outdated values; inappropriate dietary/exercise actions | P3 | S3 | **ALARP** |
| R06 | **User misinterpretation** — Lay user misunderstands "stable" or "normal" reading | User interprets app output as "no diabetes risk" and stops medication | Dangerous self-treatment; delayed professional care | P4 | S3 | **ALARP** |
| R07 | **Inappropriate advice for T1DM** — Type 1 diabetic uses app without clinician oversight | T1DM user follows weight-loss advice without adjusting insulin | Ketoacidosis; severe hypoglycaemia; hospitalisation | P2 | S4 | **ALARP** |
| R08 | **Over-reliance on app** — User reduces or stops healthcare provider consultations | User treats app as replacement for endocrinologist visits | Delayed professional care; unmanaged comorbidities; complications | P4 | S3 | **ALARP** |
| R09 | **Incorrect unit display** — mg/dL vs mmol/L confusion or error | User reads 180 mg/dL as 180 mmol/L (≈ 10 mmol/L actual) | Wrong interpretation; incorrect self-management decisions | P2 | S4 | **ALARP** |
| R10 | **OTA update failure** — Over-the-air update bricks app or corrupts data | Update fails mid-install; app unusable; historical data lost | Loss of monitoring continuity; loss of trend history | P2 | S3 | **ALARP** |
| R11 | **Off-label use by paediatric population** — Child or adolescent uses app designed for adults | Paediatric user follows adult-oriented advice | Growth disruption; inappropriate glycaemic targets | P3 | S3 | **ALARP** |
| R12 | **Concurrent device incompatibility** — App conflicts with insulin pump or other diabetes app | Data collision or conflicting recommendations between apps | Confusion; wrong therapeutic decisions | P3 | S3 | **ALARP** |
| R13 | **Cloud service unavailability** — Backend outage prevents data sync or insight generation | User cannot access personalised insights during critical period | Loss of decision support; reliance on memory/estimation | P3 | S2 | Acceptable |
| R14 | **Notification fatigue** — Excessive alerts lead user to disable all notifications | Critical glucose alerts disabled along with routine reminders | Missed critical events due to alert desensitisation | P4 | S3 | **ALARP** |
| R15 | **Data integrity corruption** — Database corruption or sync conflict causes incorrect historical trend | App generates advice based on fabricated or corrupted historical data | Inappropriate long-term recommendations | P2 | S3 | **ALARP** |

### 2.3 FMEA-Style Analysis (Top 5 Risks)

| ID | Failure Mode | Effect | Cause | Current Controls | Detection Method |
|---|---|---|---|---|---|
| R01 | Algorithm predicts stable glucose when rising | Missed hyperglycaemia | Model undertrained on postprandial spikes | None | User symptom awareness |
| R05 | CGM API returns stale timestamp | User acts on old data | API caching, network delay | None | Visual timestamp check |
| R07 | T1DM user bypasses onboarding screening | Dangerous advice given | User dishonesty, weak validation | Basic age gate | None |
| R09 | Unit setting toggled accidentally | 10x dosage misinterpretation | UI ambiguity, no confirmation | None | User verification |
| R06 | "Stable" interpreted as "cured" | Medication discontinuation | Lack of health literacy | Basic IFU | None |

---

## 3. Risk Evaluation

All identified risks with Initial Risk = ALARP or Unacceptable require risk controls. Acceptable risks are monitored through PMS.

### 3.1 Risks Requiring Control (ALARP or higher)
R01, R02, R03, R04, R05, R06, R07, R08, R09, R10, R11, R12, R14, R15

### 3.2 Risks Currently Acceptable
R13 (Cloud unavailability) — Monitored in PMS.

---

## 4. Risk Control Measures

### 4.1 Risk Control Hierarchy (per ISO 14971)
1. **Inherent safety by design** (most preferred)
2. **Protective measures** in the device or production process
3. **Information for safety** (least preferred, always required as supplement)

### 4.2 Risk Control Table

| ID | Risk Control Measure | Control Type | Implementation Evidence | Verified By |
|---|---|---|---|---|
| **R01** | **Inherent:** Exclude high-risk glucose ranges from automated advice (e.g., >300 mg/dL or <70 mg/dL trigger "consult HCP" instead of lifestyle advice) | Design | SRS §4.2.1 | System Test TC-042 |
| **R01** | **Protective:** Multi-model ensemble with confidence threshold; low-confidence predictions trigger "insufficient data" message | Design | Architecture Doc §3.4 | Algorithm Validation AV-003 |
| **R01** | **Info:** IFU states: "This app provides lifestyle insights only. Always verify unusual readings with your healthcare provider." | Labeling | IFU §3.2 | Usability Test UT-007 |
| **R02** | **Inherent:** End-to-end encryption (AES-256) for all PHI at rest and in transit; TLS 1.3 minimum | Design | Security Arch §2.1 | Penetration Test PT-001 |
| **R02** | **Protective:** Role-based access control (RBAC); MFA for admin accounts; audit logging | Design | Security Arch §2.2 | Penetration Test PT-002 |
| **R02** | **Info:** Privacy policy and GDPR Art. 13/14 notice embedded in onboarding | Labeling | Privacy Policy v2.1 | Legal Review |
| **R03** | **Inherent:** Graceful degradation — app maintains last-known state; offline cache of last 24h data | Design | SRS §5.1.3 | System Test TC-089 |
| **R03** | **Protective:** Automated crash reporting (Firebase Crashlytics) with real-time alerting to ops team | Production | DevOps Runbook §4 | QA Audit Q1-2026 |
| **R03** | **Info:** IFU instructs user to restart app and manually check glucose if app freezes during critical period | Labeling | IFU §4.1 | Usability Test UT-012 |
| **R04** | **Inherent:** Training data diversity audit — minimum representation across age, ethnicity, BMI, diabetes duration | Design | ML Model Card §2.3 | Bias Audit BA-001 |
| **R04** | **Protective:** Stratified validation — performance metrics reported per demographic subgroup; subgroup underperformance blocks release | Process | Validation Protocol VP-102 | Algorithm Validation AV-015 |
| **R04** | **Info:** IFU states: "Insights are based on population-level data. Individual responses may vary." | Labeling | IFU §3.4 | Usability Test UT-009 |
| **R05** | **Inherent:** Data freshness validation — reject glucose readings >15 minutes old without explicit user confirmation | Design | SRS §4.1.2 | Integration Test IT-034 |
| **R05** | **Protective:** API health check every 60 seconds; degraded connection triggers visual warning banner | Design | SRS §5.2.1 | System Test TC-056 |
| **R05** | **Info:** Timestamp displayed prominently with "Last updated: X min ago" indicator | Labeling | UI Spec §2.3 | Usability Test UT-003 |
| **R06** | **Inherent:** Plain-language output grading — never use "normal" alone; always contextualise ("stable for the last 2 hours, based on your personal range") | Design | UI Spec §3.1 | Usability Test UT-001 |
| **R06** | **Protective:** Mandatory onboarding tutorial explaining "what this app does and does NOT do" | Design | Onboarding Flow v3.2 | Usability Test UT-004 |
| **R06** | **Info:** Persistent footer/disclaimer: "This app is not a diagnostic tool. Consult your doctor for medical decisions." | Labeling | UI Spec §4.1 | Usability Test UT-002 |
| **R07** | **Inherent:** Onboarding questionnaire screens for T1DM diagnosis; T1DM users blocked or routed to "clinician-only" mode | Design | SRS §3.1.1 | System Test TC-012 |
| **R07** | **Protective:** Annual re-confirmation of diabetes type; escalation to HCP if user indicates insulin pump use | Design | SRS §3.1.4 | System Test TC-015 |
| **R07** | **Info:** IFU contraindication: "Not intended for Type 1 diabetes management without direct clinician oversight." | Labeling | IFU §2.3 | Usability Test UT-011 |
| **R08** | **Inherent:** App nudges HCP consultation every 90 days of active use; tracks "last provider visit" date | Design | SRS §6.2.1 | System Test TC-067 |
| **R08** | **Protective:** Usage analytics flag users with >30 days of exclusive app reliance; trigger in-app HCP reminder | Design | Analytics Spec §3.4 | QA Review |
| **R08** | **Info:** IFU emphasises: "This app complements, not replaces, your healthcare team." | Labeling | IFU §1.2 | Usability Test UT-005 |
| **R09** | **Inherent:** Unit locked at onboarding with explicit confirmation; unit change requires 2-step verification | Design | SRS §4.3.1 | System Test TC-023 |
| **R09** | **Protective:** Unit displayed in EVERY glucose reading; never implied; color-coded range bands (green/yellow/red) independent of absolute values | Design | UI Spec §2.1 | Usability Test UT-006 |
| **R09** | **Info:** Onboarding visual comparison: "180 mg/dL = 10.0 mmol/L" with user's selected unit highlighted | Labeling | Onboarding Flow v3.2 | Usability Test UT-008 |
| **R10** | **Inherent:** Staged rollout (canary release); automatic rollback on error rate >1% | Production | DevOps Runbook §5 | Release Audit RA-001 |
| **R10** | **Protective:** Pre-update full data backup to encrypted cloud storage; post-update data integrity checksum | Production | DevOps Runbook §6 | System Test TC-091 |
| **R10** | **Info:** IFU states: "Ensure app is connected to Wi-Fi before updating. Do not force-close during update." | Labeling | IFU §5.2 | Usability Test UT-013 |
| **R11** | **Inherent:** Age gate at onboarding — app not available to users <18 years | Design | SRS §3.1.2 | System Test TC-013 |
| **R11** | **Protective:** Date-of-birth verification (not just self-reported age checkbox) | Design | SRS §3.1.3 | System Test TC-014 |
| **R11** | **Info:** App store listing and IFU state: "For adults 18+. Not intended for paediatric use." | Labeling | App Store Copy v1.2 | Legal Review |
| **R12** | **Inherent:** Device compatibility matrix maintained; app detects concurrent diabetes apps and displays conflict warning | Design | SRS §7.1.1 | Integration Test IT-045 |
| **R12** | **Protective:** Integration test suite covers top 5 insulin pump apps and CGM apps | Process | Test Plan TP-201 | QA Test Report |
| **R12** | **Info:** IFU lists known compatible and incompatible devices/apps | Labeling | IFU §6.1 | Usability Test UT-014 |
| **R14** | **Inherent:** Tiered notification system — critical alerts (glucose extremes) bypass Do Not Disturb; routine reminders respect user settings | Design | SRS §5.3.2 | System Test TC-078 |
| **R14** | **Protective:** Smart notification throttling — if user dismisses >3 routine alerts in 24h, app offers notification preference tuning | Design | SRS §5.3.4 | System Test TC-079 |
| **R14** | **Info:** Onboarding explains notification tiers and how to customise | Labeling | Onboarding Flow v3.2 | Usability Test UT-015 |
| **R15** | **Inherent:** Checksum validation on all database writes; automatic corruption detection and quarantine | Design | Architecture Doc §4.2 | System Test TC-095 |
| **R15** | **Protective:** Daily automated backup with 30-day retention; point-in-time recovery capability | Production | DevOps Runbook §7 | Disaster Recovery Drill |
| **R15** | **Info:** IFU advises users to periodically export data via standard format (CSV/JSON) | Labeling | IFU §5.3 | Usability Test UT-016 |

---

## 5. Residual Risk Evaluation

### 5.1 Residual Risk Table

| ID | Hazard | Risk Controls Applied | Residual Prob. | Residual Sev. | Residual Risk | Acceptable? |
|---|---|---|---|---|---|---|
| R01 | Algorithm inaccuracy | Confidence thresholds, HCP escalation for extremes, IFU disclaimer | P2 | S3 | Acceptable | ✅ Yes |
| R02 | Data breach | E2E encryption, RBAC, MFA, GDPR notices | P1 | S3 | Acceptable | ✅ Yes |
| R03 | Software crash | Offline cache, crash monitoring, IFU restart guidance | P2 | S2 | Acceptable | ✅ Yes |
| R04 | Algorithmic bias | Diversity audit, stratified validation, IFU variance statement | P2 | S3 | Acceptable | ✅ Yes |
| R05 | CGM integration failure | Freshness validation, health checks, timestamp display | P2 | S3 | Acceptable | ✅ Yes |
| R06 | User misinterpretation | Graded outputs, onboarding tutorial, persistent disclaimer | P3 | S2 | Acceptable | ✅ Yes |
| R07 | Inappropriate advice for T1DM | T1DM screening, annual re-confirmation, contraindication | P1 | S4 | ALARP | ⚠️ Benefit-risk justified |
| R08 | Over-reliance on app | HCP nudges, usage flagging, IFU emphasis | P3 | S2 | Acceptable | ✅ Yes |
| R09 | Incorrect unit display | Locked unit, 2-step change, prominent display, onboarding visual | P1 | S4 | ALARP | ⚠️ Benefit-risk justified |
| R10 | OTA update failure | Canary rollout, auto-rollback, backup, checksum | P1 | S3 | Acceptable | ✅ Yes |
| R11 | Off-label paediatric use | Age gate, DOB verification, app store/IFU statement | P2 | S3 | Acceptable | ✅ Yes |
| R12 | Concurrent device incompatibility | Compatibility matrix, conflict detection, IFU list | P2 | S3 | Acceptable | ✅ Yes |
| R14 | Notification fatigue | Tiered system, smart throttling, onboarding explanation | P3 | S2 | Acceptable | ✅ Yes |
| R15 | Data integrity corruption | Checksum validation, automated backup, user export | P1 | S3 | Acceptable | ✅ Yes |

### 5.2 ALARP Risks Requiring Benefit-Risk Justification

**R07 — Inappropriate Advice for T1DM (Residual: ALARP)**
Justification: Despite onboarding screening, a small probability remains that a T1DM user will access the app. However:
- The app never provides insulin-dosing advice (inherent safety limitation)
- Lifestyle advice (diet/exercise) is generally safe for T1DM under clinician oversight
- The contraindication is prominent in IFU and app store
- No Class IIa lifestyle-management SaMD can fully eliminate off-label use
- Benefit to target population (T2DM/prediabetes) significantly outweighs residual risk

**R09 — Incorrect Unit Display (Residual: ALARP)**
Justification: Despite locked units and visual confirmation, user error or device-sharing scenarios could theoretically cause confusion. However:
- Unit is displayed on every reading without abbreviation ambiguity
- Color-coded range bands provide glucose context independent of units
- No SaMD can fully eliminate all user error; controls reduce probability to Remote
- Benefit of user-managed glucose monitoring significantly outweighs residual risk

---

## 6. Benefit-Risk Analysis

### 6.1 Clinical Benefits
1. **Improved glycaemic awareness:** Users gain continuous visibility into glucose patterns linked to meals, exercise, and sleep
2. **Personalised lifestyle modification:** Evidence-based dietary and exercise recommendations tailored to individual glucose responses
3. **Weight management support:** Structured insights support clinically-recommended weight-loss goals for T2DM management
4. **Patient engagement:** Digital tool increases adherence to lifestyle interventions vs. paper-based or verbal advice alone
5. **Healthcare efficiency:** Reduces unnecessary clinic visits for stable patients; flags high-risk patterns for HCP attention

### 6.2 Residual Risks Summary
- 14 hazards identified, all reduced to Acceptable or ALARP
- No unacceptable residual risks remain
- Two ALARP risks (R07, R09) justified through information controls and benefit-risk balance
- No risk with Severity = Catastrophic (S5) remains above Negligible probability

### 6.3 Overall Benefit-Risk Conclusion
**The clinical benefits of the Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application substantially outweigh the residual risks when used as intended.**

The device provides meaningful therapeutic benefit to adults with prediabetes and Type 2 diabetes through enhanced self-management capabilities. All identified hazards have been controlled through a combination of inherent design safety, protective measures, and clear information for safe use. The residual risks are acceptable within the context of the device's intended purpose and patient population.

---

## 7. Risk Management Report

### 7.1 Summary
This Risk Management Report confirms that:
- All foreseeable hazards associated with the device have been identified
- Risk evaluation has been performed per the criteria defined in the Risk Management Plan
- Risk control measures have been implemented and verified
- No unacceptable residual risks remain
- All ALARP residual risks have been justified through benefit-risk analysis
- The device is safe for its intended purpose when used as directed

### 7.2 Verification of Risk Controls

| Verification Activity | Scope | Date | Result | Performed By |
|---|---|---|---|---|
| System Testing | All risk-control software features | [Date] | Pass | QA Engineering |
| Algorithm Validation | Trend prediction accuracy, confidence thresholds | [Date] | Pass | Data Science |
| Penetration Testing | Security controls, encryption, access control | [Date] | Pass | External Security Firm |
| Usability Testing (Formative) | IFU comprehension, onboarding flow, warning visibility | [Date] | Pass | UX Research |
| Usability Testing (Summative) | Critical task completion, error rates, comprehension | [Date] | Pass | UX Research |
| Integration Testing | CGM API reliability, data freshness, error handling | [Date] | Pass | QA Engineering |
| Bias Audit | Demographic subgroup performance parity | [Date] | Pass | Data Science |

### 7.3 Approvals

| Role | Name | Signature | Date |
|---|---|---|---|
| Risk Management Lead | [Name] | _______________ | [Date] |
| Software Safety Engineer | [Name] | _______________ | [Date] |
| Clinical Safety Officer | [Name] | _______________ | [Date] |
| Quality Assurance | [Name] | _______________ | [Date] |
| Management Representative | [Name] | _______________ | [Date] |

---

## 8. Production & Post-Production Monitoring

### 8.1 PMS Risk Monitoring
The following risks are actively monitored through Post-Market Surveillance:

| ID | Hazard | PMS Data Source | Review Frequency | Action Threshold |
|---|---|---|---|---|
| R01 | Algorithm inaccuracy | User-reported discrepancies, HCP complaints, PMCF outcomes | Quarterly | >5 reports/quarter of advice-harm correlation |
| R02 | Data breach | Security incident log, penetration test results, vulnerability scans | Monthly | Any confirmed breach |
| R03 | Software crash | Crashlytics reports, app store reviews, support tickets | Weekly | Crash-free rate <99.5% |
| R04 | Algorithmic bias | PMCF demographic outcome data, fairness metric drift | Annually | Subgroup AUC difference >0.05 |
| R05 | CGM integration failure | API uptime metrics, support tickets, user-reported sync issues | Weekly | Uptime <99.0% or >10 sync tickets/week |
| R06 | User misinterpretation | Usability feedback, app store reviews, HCP complaints | Quarterly | >3 complaints/quarter of misinterpretation |
| R07 | T1DM off-label use | Onboarding analytics, support tickets, adverse event reports | Monthly | Any confirmed T1DM adverse event |
| R09 | Unit confusion | Support tickets, user-reported errors | Quarterly | >2 tickets/quarter |
| R10 | Update failures | OTA success rate, support tickets, rollback frequency | Per-release | Success rate <98% |
| R15 | Data corruption | Automated integrity check failures, backup restore tests | Weekly | Any checksum failure |

### 8.2 Risk Review Triggers
A full risk management review is triggered by:
- New serious adverse event potentially related to device risk
- Change in intended use, patient population, or contraindications
- Software update affecting safety-critical functionality
- New hazard identified through PMS or vigilance
- Notified Body audit finding related to risk management
- Annual scheduled review (minimum)

### 8.3 Trend Analysis
PMS data is analysed quarterly for:
- Emerging hazard patterns not identified in initial risk analysis
- Effectiveness of risk controls in real-world use
- New cybersecurity threats or vulnerabilities
- Changes in user population or use environment

---

*Document Control*  
**Next Review Date:** [12 months from approval or upon trigger event]  
**Distribution:** Risk Management File (controlled copy), Technical Documentation Dossier, QMS Records  
**Retention:** Lifetime of device + 10 years per MDR Article 10(8)
