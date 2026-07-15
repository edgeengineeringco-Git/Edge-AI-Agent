# Software Requirements Specification (SRS)

**Document ID:** SRS-001  
**Version:** 1.0  
**Date:** 2026-07-15  
**Standard:** EN IEC 62304:2006 + Amd 1:2015 (Class B)  
**Device:** Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application  
**Classification:** EU MDR Class IIa (Rule 11)  
**Status:** Draft — For Design Review

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Functional Requirements](#3-functional-requirements)
4. [Performance Requirements](#4-performance-requirements)
5. [Safety Requirements](#5-safety-requirements)
6. [Security & Privacy Requirements](#6-security--privacy-requirements)
7. [Interface Requirements](#7-interface-requirements)
8. [Usability Requirements](#8-usability-requirements)
9. [Regulatory & Compliance Requirements](#9-regulatory--compliance-requirements)
10. [Environmental & Operational Requirements](#10-environmental--operational-requirements)
11. [Maintenance & Support Requirements](#11-maintenance--support-requirements)
12. [Traceability to GSPR](#12-traceability-to-gspr)

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification defines the functional, performance, safety, and regulatory requirements for the Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application, a Class IIa SaMD.

### 1.2 Intended Use
Software for monitoring glucose fluctuations and providing personalised lifestyle insights to support weight management in adults (18+) with prediabetes, type 2 diabetes, or metabolic syndrome.

### 1.3 Patient Population
- **Primary:** Adults (18-75) with prediabetes or Type 2 diabetes
- **Secondary:** Adults with metabolic syndrome seeking weight management
- **Excluded:** Children/adolescents (<18); Type 1 diabetes users without clinician oversight

### 1.4 Contraindications
- Not intended for Type 1 diabetes management without direct clinician oversight
- Not intended for insulin dosing decisions
- Not intended for acute hypoglycaemia emergency management
- Not intended for paediatric use

### 1.5 Definitions & Acronyms
| Term | Definition |
|---|---|
| **SaMD** | Software as a Medical Device |
| **CGM** | Continuous Glucose Monitor |
| **PHI** | Protected Health Information |
| **SOUP** | Software of Unknown Provenance |
| **GSPR** | General Safety & Performance Requirements (MDR Annex I) |
| **TREO** | Not applicable — included for completeness |
| **PMCF** | Post-Market Clinical Follow-up |
| **HCP** | Healthcare Provider |

---

## 2. System Overview

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER DEVICES                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  iOS App     │  │ Android App  │  │  Web Portal  │      │
│  │ (SwiftUI)    │  │ (Kotlin)     │  │ (React)      │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │ HTTPS / TLS 1.3
┌───────────────────────────▼─────────────────────────────────┐
│                   CLOUD BACKEND                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ API Gateway  │  │ Auth Service │  │ ML Inference │      │
│  │ (Kong/AWS)   │  │ (OAuth 2.0)  │  │ (Python/TF)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Data Store   │  │ Notification │  │ Analytics    │      │
│  │ (PostgreSQL) │  │ (Firebase)   │  │ (Mixpanel)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
          │
          │ OAuth / API Keys
┌─────────▼───────────────────────────────────────────────────┐
│              EXTERNAL INTEGRATIONS                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Dexcom G7    │  │  Apple       │  │  Google      │      │
│  │ API          │  │  HealthKit   │  │  Health      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │  FreeStyle   │  │  OAuth      │                         │
│  │  Libre API   │  │  Providers  │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Software Safety Classification
Per IEC 62304: **Class B**
- Software can contribute to hazardous situations
- Serious injury is not probable
- No acute life-support or drug-delivery control

**Rationale:** The app provides lifestyle recommendations, not insulin dosing or emergency interventions. Failure could lead to missed trends but serious injury requires multiple compounding factors.

### 2.3 Platform Requirements
| Platform | Minimum Version | Target Version |
|---|---|---|
| iOS | iOS 16.0 | iOS 17+ |
| Android | Android 10 (API 29) | Android 14+ |
| Backend | N/A | Cloud-native, containerised |

---

## 3. Functional Requirements

### 3.1 User Onboarding

| ID | Requirement | Priority | GSPR Ref |
|---|---|---|---|
| FR-001 | App shall verify user age ≥18 years via date-of-birth entry before account creation | Critical | GSPR 1, 23.4 |
| FR-002 | App shall present diabetes type questionnaire; users self-reporting T1DM shall be blocked or routed to "clinician-only" mode with explicit warning | Critical | GSPR 1, 23.4 |
| FR-003 | App shall present mandatory onboarding tutorial explaining intended use, limitations, and "consult your doctor" disclaimer | Critical | GSPR 23.4 |
| FR-004 | App shall require explicit acceptance of Terms of Use, Privacy Policy, and IFU before first use | High | GSPR 23.4, GDPR 7 |
| FR-005 | App shall collect baseline health profile: height, weight, target weight, diabetes diagnosis status, medications, activity level | High | — |
| FR-006 | App shall allow user to select glucose unit (mg/dL or mmol/L) with visual confirmation and 2-step change process | Critical | GSPR 1, 5 |

### 3.2 Glucose Data Ingestion

| ID | Requirement | Priority | GSPR Ref |
|---|---|---|---|
| FR-007 | App shall support manual glucose entry with timestamp, value, unit, and context (fasting, post-meal, etc.) | High | GSPR 1 |
| FR-008 | App shall integrate with Dexcom G7 API for automated glucose data sync | High | GSPR 1, 17.2 |
| FR-009 | App shall integrate with FreeStyle Libre API for automated glucose data sync | Medium | GSPR 1, 17.2 |
| FR-010 | App shall integrate with Apple HealthKit for iOS glucose data import | Medium | GSPR 1 |
| FR-011 | App shall integrate with Google Health Connect for Android glucose data import | Medium | GSPR 1 |
| FR-012 | App shall validate data freshness: reject glucose readings >15 minutes old without explicit user confirmation | Critical | GSPR 1, 5 |
| FR-013 | App shall display "Last updated: X min ago" prominently with every glucose reading | Critical | GSPR 5, 23.4 |
| FR-014 | App shall validate glucose value ranges: reject values <20 mg/dL or >600 mg/dL as likely entry errors | High | GSPR 1, 5 |
| FR-015 | App shall store all glucose data with UTC timestamp and timezone offset | High | GSPR 17.2 |

### 3.3 Trend Analysis & Pattern Recognition

| ID | Requirement | Priority | GSPR Ref |
|---|---|---|---|
| FR-016 | App shall compute glucose trend (rising, falling, stable) based on last 3 readings minimum | High | GSPR 1 |
| FR-017 | App shall display glucose trend arrow (↑ ↓ →) with confidence indicator (high/medium/low) | High | GSPR 5 |
| FR-018 | App shall identify postprandial glucose patterns (1-2h post-meal spikes) | Medium | GSPR 1 |
| FR-019 | App shall identify dawn phenomenon patterns (early morning elevation) | Medium | GSPR 1 |
| FR-020 | App shall identify nocturnal hypoglycaemia patterns (3-6 AM lows) | Medium | GSPR 1 |
| FR-021 | App shall compute Time-in-Range (TIR): percentage of readings within 70-180 mg/dL over 14-day rolling window | High | GSPR 1 |
| FR-022 | App shall compute Glucose Management Indicator (GMI) as estimated HbA1c proxy | Medium | GSPR 1 |

### 3.4 Personalised Insights & Recommendations

| ID | Requirement | Priority | GSPR Ref |
|---|---|---|---|
| FR-023 | App shall generate personalised dietary recommendations based on glucose response patterns to logged meals | High | GSPR 1 |
| FR-024 | App shall generate personalised exercise recommendations based on glucose trends and user activity data | High | GSPR 1 |
| FR-025 | App shall generate sleep hygiene recommendations if nocturnal glucose patterns correlate with sleep data | Medium | GSPR 1 |
| FR-026 | App shall display recommendation confidence level (high/medium/low) based on data sufficiency | Critical | GSPR 5 |
| FR-027 | App shall NOT generate lifestyle recommendations when glucose <70 mg/dL or >300 mg/dL; shall instead display "Consult your healthcare provider immediately" | Critical | GSPR 1, 5 |
| FR-028 | App shall weight recommendations by evidence strength: stronger evidence = higher prominence | Medium | GSPR 1 |
| FR-029 | App shall personalise recommendations based on user goals: weight loss priority, glucose stability priority, or balanced | High | — |

### 3.5 Weight Management Features

| ID | Requirement | Priority | GSPR Ref |
|---|---|---|---|
| FR-030 | App shall allow daily weight logging with trend visualisation | High | — |
| FR-031 | App shall correlate weight trends with glucose patterns and meal logging | Medium | GSPR 1 |
| FR-032 | App shall calculate and display BMI trend with personalised target range | Medium | — |
| FR-033 | App shall generate weekly weight-loss progress summary with glucose co-metrics | Medium | — |
| FR-034 | App shall recommend caloric targets based on basal metabolic rate (BMR) calculation and weight-loss goal | Medium | — |

### 3.6 Notifications & Alerts

| ID | Requirement | Priority | GSPR Ref |
|---|---|---|---|
| FR-035 | App shall implement tiered notification system: Critical (glucose extremes), Important (trends), Routine (reminders) | High | GSPR 5 |
| FR-036 | Critical notifications (glucose <70 or >300 mg/dL) shall bypass Do Not Disturb and display full-screen alert | Critical | GSPR 5 |
| FR-037 | Critical alerts shall include "Consult your healthcare provider" call-to-action, NOT lifestyle advice | Critical | GSPR 1, 5 |
| FR-038 | App shall implement smart notification throttling: if user dismisses >3 routine alerts in 24h, offer preference tuning | Medium | GSPR 5 |
| FR-039 | App shall send HCP consultation reminder every 90 days of active use | High | GSPR 5 |
| FR-040 | App shall send weekly summary notification with glucose and weight trends | Low | — |

### 3.7 Data Management & Export

| ID | Requirement | Priority | GSPR Ref |
|---|---|---|---|
| FR-041 | App shall store minimum 90 days of glucose data locally (offline cache) | High | GSPR 17.2 |
| FR-042 | App shall sync data to cloud backend when network available | High | GSPR 17.2 |
| FR-043 | App shall allow user to export all data in standard formats (CSV, JSON, PDF report) | High | GSPR 23.4, GDPR 20 |
| FR-044 | App shall allow user to delete account and all associated data (GDPR Right to Erasure) | High | GDPR 17 |
| FR-045 | App shall maintain data integrity through checksum validation on all database writes | High | GSPR 17.2 |

### 3.8 User Profile & Settings

| ID | Requirement | Priority | GSPR Ref |
|---|---|---|---|
| FR-046 | App shall allow user to update health profile (weight, medications, goals) | High | — |
| FR-047 | App shall require annual re-confirmation of diabetes type and medication status | High | GSPR 1 |
| FR-048 | App shall allow customisation of glucose target ranges (with default 70-180 mg/dL) | Medium | GSPR 5 |
| FR-049 | App shall allow notification preference customisation per tier | Medium | GSPR 5 |
| FR-050 | App shall support multiple language localisations (EN, DE, FR, ES, IT, NL initially) | Medium | GSPR 23.4 |

---

## 4. Performance Requirements

| ID | Requirement | Target | Measurement Method |
|---|---|---|---|
| PR-001 | App launch time (cold start) | <3 seconds | Automated timing test |
| PR-002 | Glucose data display latency after sync | <2 seconds | Automated timing test |
| PR-003 | Recommendation generation latency | <5 seconds | Automated timing test |
| PR-004 | API response time (p95) | <500 ms | Backend monitoring |
| PR-005 | Offline functionality duration | Minimum 24 hours | Manual test |
| PR-006 | App crash-free rate | >99.5% | Crashlytics analytics |
| PR-007 | Data sync success rate | >99.0% | Backend analytics |
| PR-008 | Concurrent user support | 10,000+ simultaneous | Load testing |
| PR-009 | Battery impact (background sync) | <5% per day | Device profiling |
| PR-010 | Storage footprint (app size) | <100 MB | Build artifact size |

---

## 5. Safety Requirements

### 5.1 Critical Safety Requirements

| ID | Requirement | Rationale | Risk Ref |
|---|---|---|---|
| SAF-001 | App shall NOT provide insulin dosing calculations, recommendations, or reminders | Prevents Class IIb/III reclassification; prevents insulin overdose | R07 |
| SAF-002 | App shall NOT claim to diagnose diabetes, prediabetes, or any medical condition | Prevents diagnostic device classification; prevents false reassurance | R06 |
| SAF-003 | App shall NOT provide emergency medical advice or emergency contact automation | Prevents life-support software classification | R07 |
| SAF-004 | App shall display persistent "This app is not a diagnostic tool" disclaimer | Mitigates user misinterpretation | R06 |
| SAF-005 | App shall escalate to HCP consultation prompt for glucose <70 mg/dL or >300 mg/dL | Prevents dangerous lifestyle advice during acute events | R01, R27 |
| SAF-006 | App shall block or restrict functionality for self-reported T1DM users | Prevents dangerous off-label use | R07 |
| SAF-007 | App shall validate data freshness and reject stale CGM data without confirmation | Prevents decisions on outdated glucose values | R05 |
| SAF-008 | App shall lock glucose units at onboarding with 2-step verification for changes | Prevents unit confusion leading to 10x misinterpretation | R09 |

### 5.2 Data Safety Requirements

| ID | Requirement | Rationale | Risk Ref |
|---|---|---|---|
| SAF-009 | All PHI shall be encrypted at rest (AES-256) and in transit (TLS 1.3) | GDPR + MDR data protection | R02 |
| SAF-010 | User authentication shall require strong password or biometric (Face ID / Fingerprint) | Prevents unauthorised access to health data | R02 |
| SAF-011 | Session timeout after 5 minutes of inactivity | Limits exposure if device lost/stolen | R02 |
| SAF-012 | Automated backup of user data to encrypted cloud storage with 30-day retention | Prevents data loss from device failure | R10 |

---

## 6. Security & Privacy Requirements

### 6.1 Authentication & Authorization

| ID | Requirement | Priority |
|---|---|---|
| SEC-001 | OAuth 2.0 + PKCE for all third-party integrations (CGM APIs, health platforms) | Critical |
| SEC-002 | JWT tokens with 24-hour expiration; refresh token rotation | Critical |
| SEC-003 | Rate limiting: 100 requests/minute per user, 1000 requests/minute per IP | High |
| SEC-004 | Account lockout after 5 failed login attempts; 15-minute cooldown | High |

### 6.2 Data Protection

| ID | Requirement | Priority |
|---|---|---|
| SEC-005 | GDPR Article 25 (Privacy by Design): data minimisation, purpose limitation, storage limitation | Critical |
| SEC-006 | GDPR Article 30: maintain Record of Processing Activities (RoPA) | Critical |
| SEC-007 | Data Protection Impact Assessment (DPIA) completed and reviewed annually | Critical |
| SEC-008 | Anonymisation/pseudonymisation of analytics data | High |
| SEC-009 | User consent management: granular consent for data processing, marketing, research | Critical |
| SEC-010 | Data breach notification procedure: detect within 72h, notify authorities within 72h, notify users without undue delay | Critical |

### 6.3 Application Security

| ID | Requirement | Priority |
|---|---|---|
| SEC-011 | OWASP Mobile Top 10 compliance | Critical |
| SEC-012 | Annual penetration testing by external security firm | High |
| SEC-013 | Dependency vulnerability scanning (Snyk, Dependabot) in CI/CD | High |
| SEC-014 | Certificate pinning for API communication | High |
| SEC-015 | Code obfuscation and anti-tampering measures for mobile builds | Medium |
| SEC-016 | Runtime application self-protection (RASP) for backend | Medium |

---

## 7. Interface Requirements

### 7.1 User Interfaces

| ID | Requirement | Platform |
|---|---|---|
| UI-001 | Primary interface: mobile app (iOS + Android) with native UI frameworks | iOS, Android |
| UI-002 | Secondary interface: web portal for data export and account management | Web |
| UI-003 | Accessibility: WCAG 2.1 AA compliance minimum; VoiceOver/TalkBack support | All |
| UI-004 | Responsive design: supports phone and tablet form factors | iOS, Android |
| UI-005 | Dark mode support | iOS, Android |

### 7.2 Hardware Interfaces

| ID | Requirement | Notes |
|---|---|---|
| HW-001 | Compatible with iPhone 8 and newer | iOS minimum hardware |
| HW-002 | Compatible with Android devices supporting API 29+ | Android minimum hardware |
| HW-003 | CGM device compatibility: Dexcom G7, FreeStyle Libre 2/3 | Via manufacturer APIs |
| HW-004 | Wearable integration: Apple Watch, Wear OS (future) | HealthKit / Health Connect |

### 7.3 Software Interfaces

| ID | Requirement | Protocol |
|---|---|---|
| SI-001 | Dexcom G7 API | REST / OAuth 2.0 |
| SI-002 | FreeStyle Libre API | REST / OAuth 2.0 |
| SI-003 | Apple HealthKit | Native iOS framework |
| SI-004 | Google Health Connect | Native Android framework |
| SI-005 | Firebase Cloud Messaging | Push notifications |
| SI-006 | Mixpanel / Amplitude | Analytics |
| SI-007 | SendGrid / AWS SES | Email notifications |

### 7.4 Communication Interfaces

| ID | Requirement | Specification |
|---|---|---|
| CI-001 | Mobile app to backend API | HTTPS / TLS 1.3 / JSON |
| CI-002 | Backend to database | TLS-encrypted connection |
| CI-003 | Backend to ML inference service | gRPC / TLS 1.3 |
| CI-004 | Real-time data sync (optional future) | WebSocket / TLS 1.3 |

---

## 8. Usability Requirements

### 8.1 Summative Usability Testing Criteria (per IEC 62366-1)

| ID | Requirement | Target | Test Method |
|---|---|---|---|
| US-001 | Onboarding task completion rate | >90% of participants | Summative usability test |
| US-002 | Critical warning comprehension rate | >95% of participants | Summative usability test |
| US-003 | Error recovery rate (after intentional error) | >90% of participants | Summative usability test |
| US-004 | Time to complete primary task (log glucose + view trend) | <60 seconds | Summative usability test |
| US-005 | System Usability Scale (SUS) score | >68 | Questionnaire |
| US-006 | User satisfaction score (CSAT) | >4.0 / 5.0 | In-app survey |

### 8.2 User Interface Safety Requirements

| ID | Requirement | Rationale |
|---|---|---|
| US-007 | Glucose value displayed in largest font on main screen | Prevents misreading |
| US-008 | Unit (mg/dL or mmol/L) displayed adjacent to every glucose value | Prevents unit confusion |
| US-009 | Color-coded range bands: green (in-range), yellow (borderline), red (out-of-range) | Provides context independent of absolute value |
| US-010 | Critical alerts require explicit user acknowledgement (not auto-dismiss) | Ensures user sees safety-critical information |
| US-011 | "Consult HCP" prompts use high-contrast, unambiguous visual design | Ensures visibility and comprehension |
| US-012 | All medical terminology accompanied by plain-language explanation | Supports health literacy |

---

## 9. Regulatory & Compliance Requirements

### 9.1 EU MDR Requirements

| ID | Requirement | MDR Reference |
|---|---|---|
| REG-001 | CE marking displayed in app splash screen and app store listing | MDR Article 20 |
| REG-002 | Basic UDI-DI assigned and registered in EUDAMED | MDR Article 27, Annex VI |
| REG-003 | Manufacturer name and address displayed in app | MDR Article 10(10) |
| REG-004 | Instructions for Use accessible within app and on website | MDR Annex III, 2 |
| REG-005 | Date of manufacture (release version date) displayed | MDR Annex I, GSPR 23.3 |
| REG-006 | Unique device identifier (version/build) traceable to release | MDR Article 27 |

### 9.2 GDPR Requirements

| ID | Requirement | GDPR Reference |
|---|---|---|
| REG-007 | Lawful basis: explicit consent (Article 6(1)(a) + Article 9(2)(a)) | GDPR Art. 6, 9 |
| REG-008 | Privacy notice provided at onboarding, accessible in-app | GDPR Art. 13, 14 |
| REG-009 | User rights: access, rectification, erasure, portability, restriction | GDPR Art. 15-22 |
| REG-010 | Data Processing Agreement (DPA) with all subprocessors | GDPR Art. 28 |
| REG-011 | EU representative appointed (if manufacturer outside EU) | GDPR Art. 27 |

---

## 10. Environmental & Operational Requirements

| ID | Requirement | Specification |
|---|---|---|
| ENV-001 | Operating temperature | 0°C to 40°C (device-dependent) |
| ENV-002 | Storage temperature | -20°C to 60°C (device-dependent) |
| ENV-003 | Humidity | 5% to 95% non-condensing |
| ENV-004 | Network connectivity | Wi-Fi or mobile data required for sync |
| ENV-005 | Offline operation | Core functionality available for 24h without network |
| ENV-006 | Battery requirement | Standard smartphone battery sufficient |

---

## 11. Maintenance & Support Requirements

| ID | Requirement | Specification |
|---|---|---|
| MNT-001 | OTA update capability | In-app update prompt + app store distribution |
| MNT-002 | Update frequency | Minor: monthly; Major: quarterly; Hotfix: as needed |
| MNT-003 | Support hours | Business hours (9:00-17:00 CET) + critical issue 24/7 escalation |
| MNT-004 | Support channels | In-app chat, email, website contact form |
| MNT-005 | Response SLA | Critical (safety): 4 hours; High: 24 hours; Medium: 72 hours |
| MNT-006 | End-of-life notice | Minimum 12 months notice before app discontinuation |
| MNT-007 | Data migration path | Provided if app discontinued or platform changes |

---

## 12. Traceability to GSPR

### 12.1 GSPR Mapping Summary

| GSPR Chapter | GSPR Description | SRS Requirements | Verification Evidence |
|---|---|---|---|
| **1** | Risk management | SAF-001 to SAF-012, FR-012 to FR-014 | Risk Management File RM-001 |
| **2** | Safety integrated in design | All SAF requirements, FR-027 | Design Review Records |
| **3** | Usability | US-001 to US-012 | Usability Test Reports |
| **4** | Performance & safety | PR-001 to PR-010, FR-016 to FR-022 | System Test Reports |
| **5** | Acceptable risk-benefit | FR-026, FR-027, SAF-005 | Risk Management Report |
| **6** | Risk reduction | SAF-001 to SAF-008 | Risk Analysis Table |
| **7** | Post-market surveillance | MNT-001 to MNT-007 | PMS Plan |
| **8** | Electrical safety | N/A (software-only) | N/A |
| **9** | Mechanical safety | N/A (software-only) | N/A |
| **10** | Radiation safety | N/A (software-only) | N/A |
| **11** | Software lifecycle | All SRS sections | IEC 62304 Records |
| **12** | Active devices | N/A (software-only) | N/A |
| **13** | Biological evaluation | N/A (no patient contact) | N/A |
| **14** | Sterility | N/A (software-only) | N/A |
| **15** | Measuring function | FR-007 to FR-015 | Algorithm Validation |
| **16** | Protection against radiation | N/A | N/A |
| **17** | Electronic data | SEC-001 to SEC-016, SAF-009 to SAF-012 | Penetration Test Report |
| **18** | Active implantable | N/A | N/A |
| **19** | Environment & public safety | ENV-001 to ENV-006 | Environmental Test Report |
| **20** | In vitro diagnostic | N/A (not IVD) | N/A |
| **21** | Diagnostic performance | N/A (not diagnostic) | N/A |
| **22** | Protection of patient/user | All SAF requirements, US-007 to US-012 | Usability + Safety Testing |
| **23** | Information supplied | FR-003, FR-004, REG-001 to REG-006 | IFU + Labeling Review |

---

*Document Control*  
**Next Review Date:** [Upon design change or major release]  
**Distribution:** Engineering, QA, Regulatory, Clinical Affairs  
**Retention:** Device lifetime + 10 years
