# Clinical Evaluation Plan (CEP)

**Document ID:** CEP-001  
**Version:** 1.0  
**Date:** 2026-07-15  
**Standard:** MDR Article 61, MDCG 2020-1, MDCG 2020-5  
**Device:** Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application  
**Classification:** Class IIa (Rule 11)  
**Status:** Draft — For Clinical Review

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Device Description](#2-device-description)
3. [Clinical Development Context](#3-clinical-development-context)
4. [Clinical Evaluation Strategy](#4-clinical-evaluation-strategy)
5. [Literature Review Protocol](#5-literature-review-protocol)
6. [Equivalence Assessment](#6-equivalence-assessment)
7. [Clinical Investigation Design (if needed)](#7-clinical-investigation-design-if-needed)
8. [PMCF Strategy](#8-pmcf-strategy)
9. [Clinical Data Analysis Plan](#9-clinical-data-analysis-plan)
10. [Risk-Benefit in Clinical Context](#10-risk-benefit-in-clinical-context)
11. [Timeline & Milestones](#11-timeline--milestones)
12. [Roles & Responsibilities](#12-roles--responsibilities)

---

## 1. Introduction

### 1.1 Purpose
This Clinical Evaluation Plan (CEP) defines the strategy and methodology for demonstrating the clinical safety and performance of the Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application in accordance with MDR Article 61 and MDCG 2020-1.

### 1.2 Regulatory Basis
- **MDR 2017/745, Article 61:** Clinical evaluation requirements
- **MDR 2017/745, Annex XIV, Part A:** Clinical evaluation methodology
- **MDCG 2020-1:** Guidance on clinical evaluation — performance evaluation
- **MDCG 2020-5:** Clinical evaluation — equivalence
- **MDCG 2020-13:** Clinical evaluation — legacy devices
- **IMDRF SaMD Clinical Evaluation Guidance**

### 1.3 Clinical Evaluation Approach
**Route B: Literature Review + Bench/Algorithm Validation + PMCF**

Justification:
- The device is a lifestyle management tool (non-invasive, non-drug-delivery)
- Extensive published literature exists on CGM-based interventions for T2DM and weight loss
- A full clinical investigation (Route A) would be disproportionate to the device's risk class and intended use
- PMCF will gather real-world outcome data to strengthen the evidence base post-launch

---

## 2. Device Description

### 2.1 Intended Purpose
Software for monitoring glucose fluctuations and providing personalised lifestyle insights to support weight management in adults with prediabetes, type 2 diabetes, or metabolic syndrome.

### 2.2 Clinical Claims
The manufacturer claims that the device:
1. **Improves glycaemic awareness:** Users gain continuous visibility into glucose patterns linked to meals, exercise, and sleep
2. **Supports weight management:** Personalised dietary and exercise recommendations tailored to individual glucose responses support clinically-recommended weight-loss goals
3. **Enhances patient engagement:** Digital self-monitoring increases adherence to lifestyle interventions
4. **Complements clinical care:** Structured data supports healthcare provider consultations

### 2.3 Target Population
- **Primary:** Adults (18-75) with prediabetes or Type 2 diabetes
- **Secondary:** Adults with metabolic syndrome
- **Exclusions:** Type 1 diabetes (without clinician oversight); children <18

### 2.4 Clinical Performance Characteristics
| Characteristic | Description | Measurement |
|---|---|---|
| **Analytical Performance** | Accuracy of glucose data ingestion and processing | Data fidelity vs. reference CGM |
| **Clinical Validity** | Correlation between personalised insights and weight-loss/glycaemic outcomes | Literature synthesis + PMCF |
| **Usability** | Safe and effective use by intended population | IEC 62366-1 testing |
| **Algorithm Performance** | Accuracy of trend prediction and recommendation relevance | Retrospective validation |

---

## 3. Clinical Development Context

### 3.1 State of the Art
Current standard of care for T2DM and prediabetes lifestyle management includes:
- Self-monitoring of blood glucose (SMBG) with fingerstick meters
- Continuous glucose monitoring (CGM) for pattern recognition
- Dietary counselling by diabetes educators
- Structured exercise programmes
- Digital health apps for logging and motivation (wellness-grade, non-SaMD)

### 3.2 Unmet Need
- **Limited personalisation:** Standard dietary advice is generic; individual glycaemic responses to foods vary significantly (Zeevi et al., 2015)
- **Low engagement:** Paper-based or verbal advice has poor long-term adherence
- **Data fragmentation:** Glucose data, weight data, and meal data exist in separate silos
- **Delayed feedback:** HbA1c testing every 3-6 months provides delayed feedback on lifestyle changes

### 3.3 Clinical Benefit Hypothesis
Real-time, personalised glucose-informed lifestyle recommendations will:
- Increase Time-in-Range (TIR) by ≥5% over 12 weeks
- Support weight loss of ≥3% over 12 weeks
- Improve diabetes self-management confidence (measured by validated questionnaire)

---

## 4. Clinical Evaluation Strategy

### 4.1 Route Selection
| Route | Description | Applicability |
|---|---|---|
| **Route A** | Prospective clinical investigation | Not selected — disproportionate for Class IIa lifestyle tool |
| **Route B** | Literature review + bench testing + PMCF | **Selected** — sufficient for Class IIa with strong literature base |
| **Route C** | Equivalent device claim | May supplement Route B if predicate identified |

### 4.2 Evidence Generation Plan

| Evidence Type | Source | Timeline | Purpose |
|---|---|---|---|
| **Literature Review** | Published peer-reviewed studies | Months 4-6 | Demonstrate state of art; support clinical claims |
| **Analytical Validation** | Internal testing with CGM reference data | Months 5-6 | Verify data processing accuracy |
| **Algorithm Validation** | Retrospective cohort analysis | Months 6-7 | Validate recommendation relevance |
| **Usability Validation** | IEC 62366-1 summative testing | Months 7-8 | Verify safe use by intended population |
| **PMCF** | Real-world user outcome data (post-launch) | Months 9+ | Gather confirmatory clinical evidence |

### 4.3 Clinical Evidence Questions

| # | Clinical Question | Evidence Needed |
|---|---|---|
| CQ1 | Does CGM-based lifestyle monitoring improve glycaemic control in T2DM? | Literature on CGM + lifestyle interventions |
| CQ2 | Do personalised dietary recommendations based on glycaemic response improve weight loss? | Literature on personalised nutrition + CGM |
| CQ3 | Does digital self-monitoring improve adherence to diabetes lifestyle interventions? | Literature on digital health + diabetes |
| CQ4 | Is the app safe for intended use (no serious adverse events related to device)? | Vigilance data + PMCF safety monitoring |
| CQ5 | Can the intended user population safely operate the app? | Summative usability testing |

---

## 5. Literature Review Protocol

### 5.1 Search Strategy

**Databases:** PubMed/MEDLINE, Cochrane Library, Embase, IEEE Xplore (for algorithm papers)

**Search Terms (example):**
```
("continuous glucose monitoring" OR "CGM" OR "flash glucose monitoring")
AND
("type 2 diabetes" OR "prediabetes" OR "metabolic syndrome")
AND
("lifestyle intervention" OR "diet" OR "exercise" OR "weight loss"
  OR "digital health" OR "mobile health" OR "mHealth"
  OR "personalised nutrition" OR "precision nutrition")
AND
("glycaemic control" OR "HbA1c" OR "time in range" OR "weight management")
```

**Date Range:** 2015-2026 (focus on CGM technology generation: Dexcom G6/G7, FreeStyle Libre 2/3)

**Language:** English, plus German, French, Spanish, Italian, Dutch (EU market languages)

**Inclusion Criteria:**
- Peer-reviewed original research, systematic reviews, meta-analyses
- Studies on adults (≥18 years)
- Studies involving CGM or flash glucose monitoring
- Studies reporting glycaemic or weight outcomes

**Exclusion Criteria:**
- Paediatric-only studies (<18 years)
- Type 1 diabetes studies (unless mixed population with T2DM subgroup analysis)
- Animal studies
- Case reports with n<5
- Non-peer-reviewed sources (blogs, white papers without peer review)

### 5.2 Literature Appraisal
Each included study assessed for:
- **Methodological quality:** Newcastle-Ottawa Scale (observational), Cochrane RoB (RCTs)
- **Relevance to device:** Direct relevance (CGM + lifestyle), indirect relevance (CGM alone, lifestyle alone)
- **Applicability to intended population:** Age, diabetes type, comorbidities

### 5.3 Expected Key Literature

| Topic | Expected Key Papers |
|---|---|
| CGM + T2DM outcomes | Vigersky et al. (2012); Ehrhardt et al. (2021); Martens et al. (2021) |
| Personalised nutrition + glycaemic response | Zeevi et al. (2015, Cell); Berry et al. (2020) |
| Digital health + diabetes self-management | Greenwood et al. (2017); Hou et al. (2021) |
| CGM + weight loss | Rossi et al. (2021); Ueno et al. (2022) |
| Time-in-Range clinical significance | Battelino et al. (2019, consensus report) |

---

## 6. Equivalence Assessment

### 6.1 Equivalence Under MDR (MDCG 2020-5)
MDR equivalence requires demonstration in three dimensions:
1. **Technical:** Same specifications, design, materials, software algorithms
2. **Biological:** Same interaction with human body (for software: same physiological data processing)
3. **Clinical:** Same intended use, patient population, contraindications, outcomes

### 6.2 Predicate Device Search

| Device | Manufacturer | CE Mark? | Relevance | Equivalence Assessment |
|---|---|---|---|---|
| **Livongo for Diabetes** | Teladoc Health | Yes (US: FDA Class II) | High — CGM + coaching | Partial — technical different; coaching is human, not algorithmic |
| **mySugr** | Roche | Yes | Medium — T2DM logging | Partial — no personalised insight algorithm |
| **BlueStar** | Welldoc | Yes (US) | High — T2DM digital therapeutic | Partial — insulin dosing module makes it Class IIb; different algorithm |
| **Noom** | Noom Inc. | No (wellness) | Low — weight loss only | Not equivalent — not SaMD, no glucose integration |
| **January AI** | January Inc. | Unknown | High — CGM + AI predictions | Possible — requires detailed technical comparison |

### 6.3 Equivalence Conclusion
**No fully equivalent device identified for direct equivalence claim under MDCG 2020-5.**

Rationale:
- Most comparable devices either include insulin-dosing (different classification/technical)
- Or are wellness apps without SaMD classification (different clinical claims)
- Or use human coaching rather than algorithmic personalisation (different technical)

**Approach:** Route B (literature + own validation) with PMCF for confirmatory evidence. If January AI or similar device is identified with full technical disclosure, equivalence may be reassessed.

---

## 7. Clinical Investigation Design (If Needed)

### 7.1 Trigger for Clinical Investigation
A clinical investigation will be initiated if:
- Literature review fails to provide sufficient evidence for clinical claims
- Notified Body requires additional evidence during technical documentation review
- PMCF data reveals unexpected safety signals requiring controlled study

### 7.2 Proposed Study Design (Contingency)

| Parameter | Specification |
|---|---|
| **Design** | Prospective, single-arm, pre-post intervention study |
| **Population** | n=100 adults with T2DM or prediabetes, HbA1c 6.5-9.0% |
| **Duration** | 12 weeks intervention + 4 weeks follow-up |
| **Intervention** | Use of app for glucose monitoring + personalised lifestyle insights |
| **Primary Endpoint** | Change in Time-in-Range (TIR) from baseline to 12 weeks |
| **Secondary Endpoints** | Weight change, HbA1c change, DDS-2 (diabetes distress), app usability (SUS) |
| **Safety Monitoring** | Adverse events, severe hypoglycaemia episodes, app-related incidents |
| **Statistical Analysis** | Paired t-test for TIR change; intention-to-treat analysis |
| **Regulatory** | Ethics committee approval; clinical trial registration (EudraCT or national registry) |

**Note:** This is a contingency plan. The primary strategy remains Route B with PMCF.

---

## 8. PMCF Strategy

### 8.1 PMCF Objectives
1. Confirm safety and performance in real-world use
2. Identify rare or long-term adverse effects
3. Ensure continued acceptability of benefit-risk profile
4. Detect emerging risks not identified in pre-market evaluation
5. Gather outcome data to support clinical claims

### 8.2 PMCF Methods

| Method | Description | Frequency | Data Source |
|---|---|---|---|
| **User Outcome Survey** | Standardised questionnaire: weight, HbA1c (self-reported), TIR (from app data), satisfaction | Quarterly (in-app prompt) | App analytics + survey database |
| **App Analytics Review** | Usage patterns, feature engagement, glucose trend improvements | Monthly | Mixpanel / internal analytics |
| **Complaint & Vigilance Trending** | Analysis of complaint themes, serious incidents, near-misses | Monthly | Complaint log; vigilance database |
| **HCP Feedback Collection** | Structured feedback from healthcare providers using app data in consultations | Annually | Email survey; focus groups |
| **Literature Surveillance** | Ongoing monitoring of new publications on CGM + lifestyle | Quarterly | PubMed alerts; systematic review updates |
| **Algorithm Performance Monitoring** | Drift detection in recommendation accuracy across demographics | Monthly | ML monitoring dashboard |

### 8.3 PMCF Data Collection

**With Explicit User Consent (GDPR Article 9):**
- Anonymised glucose trend data
- Weight change trajectories
- Feature engagement metrics
- Self-reported clinical outcomes (HbA1c, medication changes)

**Without Additional Consent (legitimate interest / contractual):**
- App crash reports
- Usage analytics (anonymised)
- Support ticket themes

### 8.4 PMCF Evaluation Report
- **Frequency:** Annually (minimum)
- **Content:** Safety data, outcome data, risk control effectiveness, benefit-risk reassessment
- **Integration:** Findings incorporated into CER updates and PSURs

---

## 9. Clinical Data Analysis Plan

### 9.1 Analytical Validation

**Objective:** Verify that the app accurately processes glucose inputs.

| Test | Method | Acceptance Criteria |
|---|---|---|
| Data ingestion accuracy | Compare app-displayed glucose vs. reference CGM data (n=1,000 paired readings) | 100% match within ±1 mg/dL |
| Unit conversion | Verify mg/dL ↔ mmol/L conversion across range | 100% accuracy (formula: mmol/L = mg/dL / 18) |
| Timestamp integrity | Verify UTC conversion, timezone handling, daylight saving | 100% correct |
| Data freshness validation | Test rejection of stale data (>15 min) | 100% rejection with user prompt |
| Range validation | Test rejection of values <20 or >600 mg/dL | 100% rejection with error message |

### 9.2 Algorithm Validation

**Objective:** Validate that personalised insights correlate with expected clinical outcomes.

| Test | Method | Acceptance Criteria |
|---|---|---|
| Trend prediction accuracy | Retrospective analysis: predicted trend vs. actual next reading | Directional accuracy ≥80% |
| Recommendation relevance | Expert clinician review of 100 generated recommendations | ≥85% rated clinically appropriate |
| Confidence threshold calibration | Analyse false positive/negative rate at confidence thresholds | FPR <20%, FNR <15% |
| Demographic parity | Compare recommendation quality across age, ethnicity, BMI subgroups | AUC difference <0.05 between subgroups |

### 9.3 Clinical Outcome Analysis (PMCF)

| Outcome | Measurement | Target | Analysis Method |
|---|---|---|---|
| Time-in-Range (TIR) | % readings 70-180 mg/dL | ≥5% improvement at 12 weeks | Paired analysis, baseline vs. follow-up |
| Weight loss | % body weight change | ≥3% at 12 weeks | Descriptive statistics |
| HbA1c change | Laboratory HbA1c (self-reported) | ≥0.3% reduction at 12 weeks | Descriptive statistics |
| Diabetes distress | DDS-2 questionnaire score | ≥0.5 point reduction | Paired t-test |
| User satisfaction | CSAT in-app survey | ≥4.0/5.0 | Descriptive statistics |

---

## 10. Risk-Benefit in Clinical Context

### 10.1 Clinical Benefits
1. **Improved glycaemic awareness:** Real-time CGM data visibility supports pattern recognition
2. **Personalised lifestyle modification:** Individual glucose responses inform dietary choices
3. **Weight management support:** Structured insights support calorie and activity goals
4. **Enhanced engagement:** Digital tool increases self-monitoring adherence
5. **Healthcare efficiency:** Data sharing supports clinician consultations

### 10.2 Clinical Risks
1. **Algorithm inaccuracy:** Incorrect predictions could lead to suboptimal lifestyle choices
2. **User misinterpretation:** Over-reliance or misunderstanding of outputs
3. **Off-label use:** T1DM or paediatric use despite contraindications
4. **Data quality issues:** Stale or incorrect glucose data leading to inappropriate advice

### 10.3 Risk Minimisation in Clinical Use
- T1DM screening and exclusion
- Extreme glucose value escalation (no advice given)
- Persistent "consult HCP" disclaimers
- Data freshness validation
- Clear IFU with contraindications

### 10.4 Overall Clinical Benefit-Risk
**The clinical benefits of enhanced glycaemic awareness and personalised lifestyle support substantially outweigh the manageable risks when the device is used as intended by the target population.**

---

## 11. Timeline & Milestones

| Milestone | Target Date | Deliverable | Owner |
|---|---|---|---|
| CEP Approval | Month 4 | Signed CEP | Clinical Affairs |
| Literature Search Complete | Month 5 | Search results, PRISMA flow diagram | Clinical Affairs |
| Literature Appraisal Complete | Month 6 | Appraised evidence table | Clinical Affairs |
| Analytical Validation Complete | Month 6 | AV-001 Report | Data Science |
| Algorithm Validation Complete | Month 7 | AV-002 Report | Data Science |
| Usability Validation Complete | Month 8 | UT-SUMM-001 Report | UX Research |
| CER Draft Complete | Month 8 | CER-001 v1.0 | Clinical Affairs |
| PMCF Plan Finalised | Month 9 | PMCF-001 | Clinical Affairs |
| CER Finalised | Month 9 | CER-001 Final | Clinical Affairs |
| NB Submission | Month 10 | Full Technical Dossier | Regulatory |

---

## 12. Roles & Responsibilities

| Role | Name | Responsibilities |
|---|---|---|
| Clinical Evaluation Lead | [Name] | Overall CEP ownership, literature review, CER authorship |
| Clinical Safety Officer | [Name] | Safety assessment, vigilance oversight, risk review |
| Data Scientist | [Name] | Algorithm validation, analytical validation, bias audit |
| UX Researcher | [Name] | Usability testing, user outcome surveys |
| Regulatory Affairs | [Name] | MDR compliance, NB liaison, documentation control |
| Medical Advisor | [Name] | Clinical interpretation, recommendation review, HCP liaison |

---

*Document Control*  
**Next Review Date:** [Upon significant clinical data update or design change]  
**Distribution:** Clinical Affairs, Regulatory Affairs, Data Science, UX Research  
**Retention:** Device lifetime + 10 years
