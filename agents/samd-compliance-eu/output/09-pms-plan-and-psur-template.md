# Post-Market Surveillance (PMS) Plan & PSUR Template

**Document ID:** PMS-001 / PSUR-001  
**Version:** 1.0  
**Date:** 2026-07-15  
**Standard:** EU MDR 2017/745, Articles 83-86, Annex III  
**Device:** Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application  
**Classification:** Class IIa (Rule 11)  
**PSUR Frequency:** Every 2 years (Article 86)  
**Status:** Draft — For Regulatory Review

---

## Table of Contents

### Part A: PMS Plan
1. [PMS Scope and Objectives](#1-pms-scope-and-objectives)
2. [PMS Organisation and Responsibilities](#2-pms-organisation-and-responsibilities)
3. [PMS Data Sources](#3-pms-data-sources)
4. [Data Collection Methods](#4-data-collection-methods)
5. [Data Analysis and Evaluation](#5-data-analysis-and-evaluation)
6. [Trend Detection and Thresholds](#6-trend-detection-and-thresholds)
7. [Corrective and Preventive Actions](#7-corrective-and-preventive-actions)
8. [PMS System Documentation](#8-pms-system-documentation)
9. [PMS Review Schedule](#9-pms-review-schedule)

### Part B: PSUR Template
10. [PSUR Executive Summary](#10-psur-executive-summary)
11. [PSUR Section 1: Device Description](#11-psur-section-1-device-description)
12. [PSUR Section 2: Sales and Usage Data](#12-psur-section-2-sales-and-usage-data)
13. [PSUR Section 3: Complaint Summary](#13-psur-section-3-complaint-summary)
14. [PSUR Section 4: Vigilance Summary](#14-psur-section-4-vigilance-summary)
15. [PSUR Section 5: Risk Management Update](#15-psur-section-5-risk-management-update)
16. [PSUR Section 6: PMCF Results](#16-psur-section-6-pmcf-results)
17. [PSUR Section 7: Benefit-Risk Conclusion](#17-psur-section-7-benefit-risk-conclusion)
18. [PSUR Section 8: Actions and Plans](#18-psur-section-8-actions-and-plans)

---

## Part A: PMS Plan

## 1. PMS Scope and Objectives

### 1.1 Scope
This Post-Market Surveillance Plan applies to the Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application, a Class IIa SaMD distributed in the European Union.

### 1.2 Objectives
1. **Confirm safety and performance** in real-world use conditions
2. **Identify emerging risks** not detected during pre-market evaluation
3. **Monitor effectiveness of risk controls** implemented in the device
4. **Detect trends** in complaints, adverse events, and device performance
5. **Ensure continued acceptability** of the benefit-risk profile
6. **Generate clinical evidence** through PMCF to support regulatory compliance
7. **Meet regulatory obligations** for PSUR submission (every 2 years for Class IIa)

### 1.3 Regulatory Basis
- **MDR Article 83:** Post-market surveillance system of the manufacturer
- **MDR Article 84:** Post-market surveillance plan
- **MDR Article 85:** Post-market surveillance report (for Class I)
- **MDR Article 86:** Periodic safety update report (for Class IIa, IIb, III)
- **MDR Annex III, 1.2:** PMS plan as part of technical documentation
- **MDCG 2021-1:** Vigilance terminology and concepts

---

## 2. PMS Organisation and Responsibilities

| Role | Name / Department | PMS Responsibilities |
|---|---|---|
| **PMS Lead** | [Name] / Regulatory Affairs | Overall PMS plan ownership; PSUR authorship; NB liaison |
| **Clinical Safety Officer** | [Name] / Clinical Affairs | Clinical data review; adverse event assessment; PMCF oversight |
| **QA Manager** | [Name] / Quality Assurance | Complaint handling; CAPA management; audit support |
| **Engineering Lead** | [Name] / Engineering | Technical investigation; software update planning; SOUP monitoring |
| **Data Analyst** | [Name] / Data Science | Analytics review; trend analysis; algorithm performance monitoring |
| **Customer Support Lead** | [Name] / Support | Complaint receipt and initial triage; user feedback collection |
| **Management Representative** | [Name] / Executive | PMS budget approval; major action decisions; PSUR sign-off |

### 2.1 PMS Committee
- **Composition:** PMS Lead, Clinical Safety Officer, QA Manager, Engineering Lead
- **Frequency:** Monthly (standard) / Ad-hoc (triggered by serious incident)
- **Purpose:** Review PMS data, assess trends, assign actions, prepare PSUR

---

## 3. PMS Data Sources

### 3.1 Proactive Data Sources

| Source | Data Type | Collection Method | Frequency |
|---|---|---|---|
| **App Analytics** | Usage patterns, feature engagement, session duration, crash rates | Mixpanel / internal analytics | Continuous |
| **User Outcome Surveys** | Weight change, HbA1c (self-reported), satisfaction, diabetes distress | In-app survey prompts | Quarterly |
| **Algorithm Performance Monitoring** | Prediction accuracy, confidence distribution, demographic parity | ML monitoring dashboard | Continuous |
| **Software Performance Metrics** | API latency, error rates, sync success rates, uptime | Backend monitoring (Datadog / Grafana) | Continuous |
| **Literature Surveillance** | New publications on CGM + lifestyle interventions | PubMed alerts; systematic review updates | Quarterly |
| **Competitor Monitoring** | Recalls, safety notices, regulatory actions for comparable devices | EUDAMED; FDA MAUDE; competitor websites | Quarterly |

### 3.2 Reactive Data Sources

| Source | Data Type | Collection Method | Response Time |
|---|---|---|---|
| **Customer Support Tickets** | User issues, questions, feature requests | Zendesk / Freshdesk / equivalent | Within 24h |
| **App Store Reviews** | User feedback, ratings, complaints | Apple App Store Connect; Google Play Console | Weekly review |
| **Social Media & Forums** | Unsolicited user feedback, safety concerns | Brand monitoring tools (Mention, Brandwatch) | Weekly review |
| **Complaint Reports** | Formal complaints per ISO 13485 | Complaint handling procedure (SOP-014) | Within 24h |
| **Vigilance Reports** | Serious incidents, near-misses | Vigilance procedure (SOP-015) | Immediate |
| **Healthcare Provider Feedback** | Clinical observations, safety concerns | Email survey; direct communication | Annual collection |

### 3.3 Data Source Coverage Matrix

| Data Source | Safety | Performance | Usability | Satisfaction | Clinical Outcomes |
|---|---|---|---|---|---|
| App Analytics | ✅ | ✅ | ✅ | ⚠️ | ⚠️ |
| User Surveys | ✅ | ✅ | ✅ | ✅ | ✅ |
| Algorithm Monitoring | ✅ | ✅ | ⚠️ | ⚠️ | ✅ |
| Support Tickets | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| App Store Reviews | ✅ | ⚠️ | ✅ | ✅ | ⚠️ |
| Vigilance Reports | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| Literature Surveillance | ✅ | ✅ | ⚠️ | ⚠️ | ✅ |
| HCP Feedback | ✅ | ✅ | ⚠️ | ⚠️ | ✅ |

---

## 4. Data Collection Methods

### 4.1 In-App User Surveys

**Quarterly Health Outcome Survey**
- **Trigger:** User has been active for ≥90 days
- **Frequency:** Once per quarter (max 4 per year)
- **Questions:**
  1. What is your current weight? (kg/lbs)
  2. What was your most recent HbA1c? (% or mmol/mol)
  3. How many times per week do you check the app?
  4. How helpful are the personalised insights? (1-5 scale)
  5. Have you discussed app data with your healthcare provider? (Yes/No)
  6. Have you experienced any adverse events you believe are related to the app? (Yes/No + free text)
  7. Net Promoter Score: How likely are you to recommend this app? (0-10)

**Quarterly Usability Survey**
- **Trigger:** Random sample of active users
- **Frequency:** Once per quarter
- **Questions:**
  1. How easy is it to log glucose data? (1-5)
  2. How easy is it to understand your insights? (1-5)
  3. Have you encountered any app errors or crashes? (Yes/No + details)
  4. Do you find the notifications helpful or annoying? (Helpful/Annoying/Neutral)

### 4.2 App Analytics Collection

**Automatically Collected (Anonymised):**
- Daily active users (DAU), monthly active users (MAU)
- Session frequency and duration
- Feature usage (glucose logging, insight viewing, weight logging, data export)
- Crash rates and error frequencies
- CGM sync success/failure rates
- Algorithm confidence distribution
- Notification engagement (open rate, dismiss rate)

**NOT Collected (Privacy Protection):**
- Individual glucose values (unless explicitly consented for PMCF)
- Individual weight values (unless explicitly consented for PMCF)
- Precise geolocation
- Personal identifiers in analytics

### 4.3 Support Ticket Categorisation

| Category | Description | PMS Relevance |
|---|---|---|
| **S-001** | App crash / freeze | Safety (R03) |
| **S-002** | CGM sync failure | Safety (R05), Performance |
| **S-003** | Incorrect glucose display | Safety (R09) |
| **S-004** | Wrong recommendation | Safety (R01) |
| **S-005** | Data loss / corruption | Safety (R10, R15) |
| **S-006** | Account / login issue | Security |
| **S-007** | Notification issue | Usability (R14) |
| **S-008** | Feature request | Product improvement |
| **S-009** | Billing / subscription | Commercial |
| **S-010** | General question | Support |

---

## 5. Data Analysis and Evaluation

### 5.1 Analysis Methods

| Analysis Type | Method | Tools | Frequency |
|---|---|---|---|
| **Quantitative Trending** | Time-series analysis, statistical process control | Python (pandas, matplotlib), Excel | Monthly |
| **Qualitative Thematic** | Thematic coding of free-text feedback | NVivo / manual coding | Quarterly |
| **Comparative Analysis** | Compare current period vs. previous period, vs. benchmarks | Internal dashboards | Quarterly |
| **Risk Signal Detection** | Review complaints/vigilance against Risk Management File | Risk Management Review | Monthly |
| **Algorithm Performance** | Drift detection, fairness metrics, accuracy trends | Evidently AI, custom dashboards | Monthly |

### 5.2 Key Performance Indicators (KPIs)

| KPI | Target | Measurement | Review Frequency |
|---|---|---|---|
| **Crash-free rate** | >99.5% | Crashlytics | Weekly |
| **CGM sync success rate** | >99.0% | Backend analytics | Weekly |
| **User-reported serious incidents** | Zero | Vigilance log | Monthly |
| **Complaint rate** | <0.5% of active users/quarter | Complaint log | Quarterly |
| **App store rating** | >4.0 / 5.0 | App store analytics | Monthly |
| **Support ticket resolution time** | <48h (median) | Zendesk | Monthly |
| **NPS score** | >30 | Quarterly survey | Quarterly |
| **Algorithm directional accuracy** | >80% | ML monitoring | Monthly |
| **TIR improvement (PMCF)** | ≥5% at 12 weeks | Quarterly survey | Quarterly |

### 5.3 Signal Detection Criteria

A "signal" requiring investigation is triggered when:

| Signal Type | Threshold | Investigation Trigger |
|---|---|---|
| **Complaint spike** | >200% increase vs. previous quarter | Immediate investigation |
| **Crash rate spike** | Crash-free rate drops below 99.0% | Immediate investigation |
| **Safety-related complaint** | Any complaint alleging harm | Immediate investigation |
| **CGM sync failure** | >2% failure rate for 7 consecutive days | Immediate investigation |
| **Algorithm bias** | Subgroup AUC difference >0.05 | Investigation within 7 days |
| **App store rating drop** | Rating drops below 3.5 for 14 days | Investigation within 7 days |
| **Vigilance report** | Any serious incident reported | Immediate investigation |
| **Literature signal** | New publication indicating safety concern | Investigation within 14 days |

---

## 6. Trend Detection and Thresholds

### 6.1 Trend Reporting (MDR Article 88)

**Trend Definition:** A statistically significant increase in the frequency or severity of incidents that are not serious incidents but could lead to serious incidents if they recur or go undetected.

**Trend Thresholds:**

| Metric | Baseline | Trend Threshold | Reporting Action |
|---|---|---|---|
| Non-serious complaints (S-001 to S-007) | <0.5%/quarter | >1.0%/quarter for 2 consecutive quarters | Trend report to competent authority |
| App crashes | <0.5%/session | >1.0%/session for 7 days | Investigation + potential FSCA |
| CGM sync failures | <1.0% | >3.0% for 7 days | Investigation + manufacturer notification |
| User-reported algorithm errors | <0.1%/quarter | >0.5%/quarter | Investigation + risk management review |
| Data export failures | <0.2%/request | >1.0%/request for 7 days | Investigation |

### 6.2 Statistical Methods

**Control Charts:**
- p-charts for complaint rates (proportion)
- c-charts for count data (number of crashes)
- X-bar charts for continuous metrics (sync success rate)

**Alert Rules (Western Electric Rules):**
1. Any single point outside 3-sigma control limits
2. Two out of three consecutive points outside 2-sigma limits
3. Eight consecutive points on one side of the centerline

---

## 7. Corrective and Preventive Actions

### 7.1 Action Triggers

| Trigger | Investigation Required | Typical Actions |
|---|---|---|
| Serious incident | Immediate root cause analysis | CAPA; potential FSCA; vigilance report |
| Complaint spike | Trend analysis; root cause | Software update; user communication; IFU update |
| Crash rate spike | Technical investigation | Hotfix release; rollback; enhanced monitoring |
| Algorithm bias detected | Bias audit; model retraining | Model update; revalidation; user communication |
| Competitor recall / safety notice | Comparative risk assessment | Risk management review; device assessment |
| New literature indicating risk | Clinical assessment | Risk management review; CER update |

### 7.2 Field Safety Corrective Action (FSCA) Criteria

An FSCA is initiated when:
- A serious incident pattern is identified
- A defect poses unacceptable risk to users
- A software bug affects safety-critical functionality
- Regulatory authority requests corrective action

**FSCA Actions may include:**
- Software update (OTA or app store)
- User safety notification (in-app, email, push)
- Temporary feature disablement
- Device recall (extremely unlikely for SaMD; typically addressed via update)

---

## 8. PMS System Documentation

### 8.1 PMS Records

| Record | Location | Retention |
|---|---|---|
| PMS Plan | QMS Document Control | Device lifetime + 10 years |
| PSURs | QMS Document Control | Device lifetime + 10 years |
| Complaint log | QMS Records | Device lifetime + 10 years |
| Vigilance log | QMS Records | Device lifetime + 10 years |
| App analytics | Analytics platform + archive | 5 years |
| Survey responses | Secure database | 5 years |
| PMS Committee minutes | QMS Records | Device lifetime + 10 years |
| CAPA records | QMS Records | Device lifetime + 10 years |

### 8.2 PMS System Validation
The PMS system (tools, databases, procedures) shall be validated to ensure:
- Data integrity
- Confidentiality and security
- Reliable data collection and analysis
- Traceability of actions

---

## 9. PMS Review Schedule

| Activity | Frequency | Responsible | Evidence |
|---|---|---|---|
| App analytics review | Weekly | Data Analyst | Analytics dashboard review |
| Crash / error review | Weekly | Engineering Lead | Crashlytics review |
| Support ticket review | Weekly | Customer Support Lead | Ticket triage meeting |
| PMS Committee meeting | Monthly | PMS Lead | Meeting minutes |
| Complaint trend analysis | Monthly | QA Manager | Complaint trend report |
| Algorithm performance review | Monthly | Data Scientist | ML monitoring report |
| App store review analysis | Monthly | Customer Support Lead | Review summary |
| Social media monitoring | Monthly | Marketing / Support | Monitoring report |
| Quarterly PMS data analysis | Quarterly | PMS Lead | Quarterly PMS report |
| User survey analysis | Quarterly | Clinical Safety Officer | Survey analysis report |
| Literature surveillance update | Quarterly | Clinical Affairs | Literature review update |
| PSUR preparation | Biennial | PMS Lead | PSUR document |
| Annual PMS system review | Annually | PMS Lead + Management Rep | Annual PMS review report |
| Risk management review (PMS-triggered) | As needed | Risk Management Lead | Risk management review minutes |

---

## Part B: PSUR Template

## 10. PSUR Executive Summary

**PSUR Period:** [Start Date] to [End Date]  
**Device:** Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application  
**Basic UDI-DI:** [To be assigned]  
**Manufacturer:** [Company Name]  
**Notified Body:** [Name and number]  
**Previous PSUR:** [Date of previous PSUR, or "First PSUR"]

### 10.1 Summary of Findings

| Area | Status | Key Findings |
|---|---|---|
| **Safety** | [Acceptable / Requires Action] | [Number of serious incidents, trends, actions taken] |
| **Performance** | [Acceptable / Requires Action] | [Crash rates, sync rates, algorithm accuracy trends] |
| **Usability** | [Acceptable / Requires Action] | [App store rating, survey results, support themes] |
| **Benefit-Risk** | [Favourable / Requires Reassessment] | [Overall benefit-risk conclusion] |

### 10.2 Actions Taken During Reporting Period

| Action | Date | Reason | Outcome |
|---|---|---|---|
| [Action description] | [Date] | [Trigger] | [Result] |

### 10.3 Actions Planned for Next Period

| Action | Target Date | Rationale |
|---|---|---|
| [Action description] | [Date] | [Rationale] |

---

## 11. PSUR Section 1: Device Description

### 11.1 Device Identity
| Attribute | Details |
|---|---|
| Device name | [App Name] |
| Basic UDI-DI | [To be assigned] |
| Version(s) covered | [e.g., 1.0.0 - 1.2.3] |
| Platform | iOS, Android |
| Classification | Class IIa (Rule 11) |

### 11.2 Intended Purpose
[Same as IFU Section 2]

### 11.3 Changes During Reporting Period

| Change | Version | Date | Regulatory Impact | NB Notified? |
|---|---|---|---|---|
| [Description] | [Version] | [Date] | [None / Minor / Major] | [Yes / No / N/A] |

---

## 12. PSUR Section 2: Sales and Usage Data

### 12.1 Distribution Data

| Region | Downloads | Active Users (end of period) | Device Versions in Use |
|---|---|---|---|
| Germany | [Number] | [Number] | [Versions] |
| France | [Number] | [Number] | [Versions] |
| Italy | [Number] | [Number] | [Versions] |
| Spain | [Number] | [Number] | [Versions] |
| Netherlands | [Number] | [Number] | [Versions] |
| Other EU | [Number] | [Number] | [Versions] |
| **Total EU** | **[Number]** | **[Number]** | |

### 12.2 Usage Metrics

| Metric | Value | Trend vs. Previous Period |
|---|---|---|
| Average sessions per user per week | [Number] | [↑ / ↓ / →] |
| Average session duration | [Minutes] | [↑ / ↓ / →] |
| Feature usage (top 3) | [Features] | [Trends] |
| CGM connection rate | [%] | [↑ / ↓ / →] |
| Data export frequency | [Exports/month] | [↑ / ↓ / →] |

---

## 13. PSUR Section 3: Complaint Summary

### 13.1 Complaint Overview

| Category | Number | % of Active Users | Trend |
|---|---|---|---|
| App crash / freeze | [Number] | [%] | [↑ / ↓ / →] |
| CGM sync failure | [Number] | [%] | [↑ / ↓ / →] |
| Incorrect display | [Number] | [%] | [↑ / ↓ / →] |
| Wrong recommendation | [Number] | [%] | [↑ / ↓ / →] |
| Data loss | [Number] | [%] | [↑ / ↓ / →] |
| Login / account | [Number] | [%] | [↑ / ↓ / →] |
| Notification issue | [Number] | [%] | [↑ / ↓ / →] |
| Feature request | [Number] | [%] | [↑ / ↓ / →] |
| Other | [Number] | [%] | [↑ / ↓ / →] |
| **Total** | **[Number]** | **[%]** | |

### 13.2 Top Complaint Themes (Free Text Analysis)

| Rank | Theme | Frequency | Action Taken |
|---|---|---|---|
| 1 | [Theme] | [Number] | [Action] |
| 2 | [Theme] | [Number] | [Action] |
| 3 | [Theme] | [Number] | [Action] |

### 13.3 App Store Review Summary

| Platform | Average Rating | Total Reviews | % Positive (4-5 stars) | Key Themes |
|---|---|---|---|---|
| iOS | [Rating] | [Number] | [%] | [Themes] |
| Android | [Rating] | [Number] | [%] | [Themes] |

---

## 14. PSUR Section 4: Vigilance Summary

### 14.1 Serious Incidents

| Incident ID | Date | Description | Root Cause | Action Taken | Reported to CA? |
|---|---|---|---|---|---|
| [ID] | [Date] | [Description] | [Cause] | [Action] | [Yes/No] |

**Total Serious Incidents:** [Number]

### 14.2 Near-Misses

| Near-Miss ID | Date | Description | Potential Harm | Preventive Action |
|---|---|---|---|---|
| [ID] | [Date] | [Description] | [Harm] | [Action] |

### 14.3 Field Safety Corrective Actions (FSCA)

| FSCA ID | Date | Description | Affected Users | Implementation Rate |
|---|---|---|---|---|
| [ID] | [Date] | [Description] | [Number] | [%] |

---

## 15. PSUR Section 5: Risk Management Update

### 15.1 Risk File Review

| Risk ID | Hazard | Control Effectiveness | New Information | Action Required |
|---|---|---|---|---|
| R01 | Algorithm inaccuracy | [Effective / Partial / Ineffective] | [Any new data] | [None / Monitor / Update] |
| R02 | Data breach | [Effective / Partial / Ineffective] | [Any new data] | [None / Monitor / Update] |
| R03 | Software crash | [Effective / Partial / Ineffective] | [Any new data] | [None / Monitor / Update] |
| R04 | Algorithmic bias | [Effective / Partial / Ineffective] | [Any new data] | [None / Monitor / Update] |
| R05 | CGM integration failure | [Effective / Partial / Ineffective] | [Any new data] | [None / Monitor / Update] |
| R06 | User misinterpretation | [Effective / Partial / Ineffective] | [Any new data] | [None / Monitor / Update] |
| R07 | T1DM off-label use | [Effective / Partial / Ineffective] | [Any new data] | [None / Monitor / Update] |
| R09 | Unit confusion | [Effective / Partial / Ineffective] | [Any new data] | [None / Monitor / Update] |
| [Add others] | | | | |

### 15.2 New Hazards Identified

| New Hazard ID | Description | Risk Assessment | Controls Implemented |
|---|---|---|---|
| [ID] | [Description] | [Risk level] | [Controls] |

### 15.3 Risk Control Updates

| Risk ID | Updated Control | Reason for Update | Verification |
|---|---|---|---|
| [ID] | [Description] | [Reason] | [Method] |

---

## 16. PSUR Section 6: PMCF Results

### 16.1 PMCF Activities Conducted

| Activity | Period | Sample Size | Key Findings |
|---|---|---|---|
| User outcome survey | [Dates] | [N] | [Findings] |
| Algorithm performance monitoring | [Dates] | [N users] | [Findings] |
| HCP feedback collection | [Dates] | [N providers] | [Findings] |
| Literature surveillance | [Dates] | [N papers reviewed] | [Findings] |

### 16.2 Clinical Outcome Data

| Outcome | Baseline | Current | Change | Target Met? |
|---|---|---|---|---|
| Time-in-Range (TIR) | [%] | [%] | [±%] | [Yes/No] |
| Weight change | [kg] | [kg] | [±kg] | [Yes/No] |
| HbA1c change | [%] | [%] | [±%] | [Yes/No] |
| Diabetes distress (DDS-2) | [Score] | [Score] | [±Score] | [Yes/No] |
| User satisfaction (CSAT) | [Score] | [Score] | [±Score] | [Yes/No] |

### 16.3 PMCF Conclusion
[Summary of whether PMCF data supports the continued safety and performance of the device, and whether any updates to the Clinical Evaluation Report are needed.]

---

## 17. PSUR Section 7: Benefit-Risk Conclusion

### 17.1 Benefit Summary
[Summary of clinical benefits demonstrated through PMS and PMCF data]

### 17.2 Risk Summary
[Summary of risks identified during the reporting period, including serious incidents, complaints, and emerging hazards]

### 17.3 Benefit-Risk Assessment
**Conclusion:** [Favourable / Conditionally Favourable / Unfavourable]

**Justification:**
[Detailed justification for the benefit-risk conclusion, referencing specific data from the PSUR sections above.]

### 17.4 Comparison to State of the Art
[Comparison of the device's benefit-risk profile to comparable devices and standard of care]

---

## 18. PSUR Section 8: Actions and Plans

### 18.1 Actions Completed During Reporting Period

| Action | Completion Date | Outcome |
|---|---|---|
| [Action] | [Date] | [Outcome] |

### 18.2 Actions Planned for Next Reporting Period

| Action | Target Date | Rationale | Owner |
|---|---|---|---|
| [Action] | [Date] | [Rationale] | [Name] |

### 18.3 CER Update Plan

| Update Type | Trigger | Planned Date |
|---|---|---|
| CER annual update | PSUR completion | [Date] |
| CER major revision | Significant new clinical data | [As needed] |

---

## PSUR Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| PMS Lead | [Name] | _______________ | [Date] |
| Clinical Safety Officer | [Name] | _______________ | [Date] |
| QA Manager | [Name] | _______________ | [Date] |
| Management Representative | [Name] | _______________ | [Date] |

---

*Document Control*  
**PMS Plan Next Review:** [Annually or upon significant change]  
**PSUR Submission Schedule:** Every 2 years (Class IIa)  
**Distribution:** Regulatory Affairs, Clinical Affairs, QA, Management  
**Retention:** Device lifetime + 10 years
