# SOUP Inventory (Software of Unknown Provenance)

**Document ID:** SOUP-001  
**Version:** 1.0  
**Date:** 2026-07-15  
**Standard:** EN IEC 62304:2006 + Amd 1:2015, Clause 5.3.5 / 8.1.2  
**Device:** Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application  
**Classification:** EU MDR Class IIa (Rule 11)  
**Status:** Draft — For Engineering Review

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [SOUP Evaluation Criteria](#2-soup-evaluation-criteria)
3. [Mobile Application SOUP](#3-mobile-application-soup)
4. [Backend SOUP](#4-backend-soup)
5. [Machine Learning SOUP](#5-machine-learning-soup)
6. [Infrastructure & DevOps SOUP](#6-infrastructure--devops-soup)
7. [CGM Integration SOUP](#7-cgm-integration-soup)
8. [Known Anomalies & Risk Assessment](#8-known-anomalies--risk-assessment)
9. [SOUP Maintenance Plan](#9-soup-maintenance-plan)
10. [SOUP Change Log](#10-soup-change-log)

---

## 1. Introduction

### 1.1 Purpose
This SOUP Inventory identifies all Software of Unknown Provenance (third-party software, libraries, frameworks, operating systems, and cloud services) used in the Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application, per IEC 62304 requirements.

### 1.2 SOUP Definition (per IEC 62304)
> "SOFTWARE ITEM that is already developed and generally available and that has not been developed for the purpose of being incorporated into the MEDICAL DEVICE SOFTWARE"

### 1.3 SOUP Categories

| Category | Definition | Examples |
|---|---|---|
| **A1** — OS / Platform | Operating system, runtime environment | iOS, Android, Node.js runtime |
| **A2** — Development Framework | App development framework | React Native, Flutter, SwiftUI |
| **B1** — Core Libraries | Essential libraries for app functionality | Networking, JSON parsing, cryptography |
| **B2** — UI Components | User interface libraries and components | Charts, calendars, navigation |
| **B3** — Analytics & Monitoring | Usage tracking, crash reporting, logging | Firebase, Mixpanel, Sentry |
| **B4** — ML / AI Libraries | Machine learning frameworks and models | TensorFlow, scikit-learn, Core ML |
| **C1** — Cloud Infrastructure | Hosting, compute, storage services | AWS, GCP, Azure |
| **C2** — Managed Services | Third-party APIs and SaaS | Authentication, push notifications, email |
| **D1** — CGM SDKs / APIs | Continuous glucose monitor integrations | Dexcom SDK, FreeStyle Libre API |

---

## 2. SOUP Evaluation Criteria

### 2.1 Selection Criteria
Before adding new SOUP, the following must be evaluated:

| Criterion | Requirement | Verification Method |
|---|---|---|
| **Active Maintenance** | Last release or commit within 12 months | GitHub releases page, npm/pip registry |
| **Security Track Record** | No unpatched critical/high CVEs | Snyk, CVE database, NVD |
| **License Compatibility** | Permissive or compatible with commercial distribution | License review (OSI-approved) |
| **Documentation Quality** | Sufficient for integration and troubleshooting | Documentation review |
| **Community / Support** | Active community or commercial support | GitHub issues, Stack Overflow, vendor support |
| **Regulatory Awareness** | Manufacturer understands medical device context (if applicable) | Vendor inquiry, documentation |

### 2.2 Risk Classification

| Class | Criteria | Review Frequency |
|---|---|---|
| **Critical** | Directly involved in safety-critical functions (data processing, encryption, user authentication) | Monthly |
| **High** | Core functionality dependency; app cannot operate without | Quarterly |
| **Medium** | Important feature support; alternatives available | Quarterly |
| **Low** | Development tools, testing utilities, non-production | Annually |

---

## 3. Mobile Application SOUP

### 3.1 iOS Application

| # | Component | Version | Manufacturer | Purpose | Risk Class | License | Anomaly Monitoring |
|---|---|---|---|---|---|---|---|
| 1 | **iOS** | 16.0+ | Apple Inc. | Operating system | Critical | Proprietary | Apple security updates, release notes |
| 2 | **Swift** | 5.9+ | Apple Inc. | Programming language | Critical | Apache 2.0 | Swift evolution, security advisories |
| 3 | **SwiftUI** | iOS 16+ | Apple Inc. | UI framework | High | Proprietary | Apple developer documentation |
| 4 | **Foundation** | iOS 16+ | Apple Inc. | Core functionality | Critical | Proprietary | Apple security updates |
| 5 | **HealthKit** | iOS 16+ | Apple Inc. | Health data access | Critical | Proprietary | Apple release notes, API changes |
| 6 | **CryptoKit** | iOS 16+ | Apple Inc. | Cryptographic operations | Critical | Proprietary | Apple security updates |
| 7 | **Alamofire** | 5.8+ | Alamofire Software Foundation | HTTP networking | High | MIT | GitHub releases, CVE database |
| 8 | **SwiftLint** | 0.54+ | Realm Inc. | Code linting | Low | MIT | GitHub releases |
| 9 | **Charts** | 5.0+ | Daniel Cohen Gindi | Data visualisation | Medium | Apache 2.0 | GitHub releases, CVE database |
| 10 | **KeychainAccess** | 4.2+ | kishikawa katsumi | Secure keychain wrapper | High | MIT | GitHub releases |
| 11 | **Firebase iOS SDK** | 10.x | Google LLC | Analytics, crash reporting, push | High | Apache 2.0 | Google security bulletins |
| 12 | **TensorFlow Lite iOS** | 2.15+ | Google LLC | On-device ML inference | High | Apache 2.0 | TensorFlow security advisories |

### 3.2 Android Application

| # | Component | Version | Manufacturer | Purpose | Risk Class | License | Anomaly Monitoring |
|---|---|---|---|---|---|---|---|
| 1 | **Android OS** | 10+ (API 29+) | Google LLC | Operating system | Critical | Apache 2.0 | Google security bulletins |
| 2 | **Kotlin** | 1.9+ | JetBrains | Programming language | Critical | Apache 2.0 | Kotlin releases, security advisories |
| 3 | **Jetpack Compose** | 1.5+ | Google LLC | UI framework | High | Apache 2.0 | Android developer documentation |
| 4 | **AndroidX Core** | 1.12+ | Google LLC | Core Android libraries | Critical | Apache 2.0 | Google security bulletins |
| 5 | **Health Connect** | Android 14+ | Google LLC | Health data access | Critical | Apache 2.0 | Google release notes |
| 6 | **Retrofit** | 2.9+ | Square Inc. | HTTP networking | High | Apache 2.0 | GitHub releases, CVE database |
| 7 | **OkHttp** | 4.12+ | Square Inc. | HTTP client | High | Apache 2.0 | GitHub releases, CVE database |
| 8 | **Kotlin Coroutines** | 1.7+ | JetBrains | Async programming | High | Apache 2.0 | GitHub releases |
| 9 | **Room** | 2.6+ | Google LLC | Local database (SQLite) | High | Apache 2.0 | Google security bulletins |
| 10 | **DataStore** | 1.0+ | Google LLC | Preferences storage | Medium | Apache 2.0 | Google release notes |
| 11 | **MPAndroidChart** | 3.1+ | Philipp Jahoda | Data visualisation | Medium | Apache 2.0 | GitHub releases |
| 12 | **Firebase Android SDK** | 32.x | Google LLC | Analytics, crash reporting | High | Apache 2.0 | Google security bulletins |
| 13 | **TensorFlow Lite Android** | 2.15+ | Google LLC | On-device ML inference | High | Apache 2.0 | TensorFlow security advisories |
| 14 | **ktlint** | 1.0+ | Pinterest | Code linting | Low | MIT | GitHub releases |

---

## 4. Backend SOUP

| # | Component | Version | Manufacturer | Purpose | Risk Class | License | Anomaly Monitoring |
|---|---|---|---|---|---|---|---|
| 1 | **Python** | 3.11+ | Python Software Foundation | Programming language | Critical | PSF License | Python security advisories |
| 2 | **FastAPI** | 0.104+ | Sebastián Ramírez | Web framework | High | MIT | GitHub releases, CVE database |
| 3 | **Uvicorn** | 0.24+ | Encode | ASGI server | High | BSD 3-Clause | GitHub releases |
| 4 | **Pydantic** | 2.5+ | Samuel Colvin | Data validation | High | MIT | GitHub releases |
| 5 | **SQLAlchemy** | 2.0+ | SQLAlchemy Org | ORM / database abstraction | High | MIT | GitHub releases, CVE database |
| 6 | **Alembic** | 1.12+ | Mike Bayer | Database migrations | Medium | MIT | GitHub releases |
| 7 | **PostgreSQL** | 15.x | PostgreSQL Global Development Group | Primary database | Critical | PostgreSQL License | PostgreSQL security updates |
| 8 | **Redis** | 7.2+ | Redis Ltd. | Caching, session store | High | BSD 3-Clause | Redis security advisories |
| 9 | **Celery** | 5.3+ | Celery Project | Distributed task queue | Medium | BSD 3-Clause | GitHub releases |
| 10 | **PyJWT** | 2.8+ | José Padilla | JWT token handling | Critical | MIT | GitHub releases, CVE database |
| 11 | **cryptography** | 41.0+ | Python Cryptographic Authority | Encryption operations | Critical | Apache 2.0 / BSD | GitHub releases, CVE database |
| 12 | **bcrypt** | 4.1+ | Python Cryptographic Authority | Password hashing | Critical | Apache 2.0 | GitHub releases |
| 13 | **pytest** | 7.4+ | pytest-dev | Testing framework | Low | MIT | GitHub releases |
| 14 | **httpx** | 0.25+ | Encode | HTTP client | Medium | BSD 3-Clause | GitHub releases |
| 15 | **pydantic-settings** | 2.1+ | Samuel Colvin | Configuration management | Medium | MIT | GitHub releases |

---

## 5. Machine Learning SOUP

| # | Component | Version | Manufacturer | Purpose | Risk Class | License | Anomaly Monitoring |
|---|---|---|---|---|---|---|---|
| 1 | **TensorFlow** | 2.15+ | Google LLC | Model training | High | Apache 2.0 | TensorFlow security advisories |
| 2 | **TensorFlow Lite** | 2.15+ | Google LLC | On-device inference | High | Apache 2.0 | TensorFlow security advisories |
| 3 | **scikit-learn** | 1.3+ | scikit-learn developers | ML algorithms, validation | High | BSD 3-Clause | GitHub releases, CVE database |
| 4 | **pandas** | 2.1+ | pandas Development Team | Data manipulation | Medium | BSD 3-Clause | GitHub releases |
| 5 | **NumPy** | 1.26+ | NumPy Developers | Numerical computing | High | BSD 3-Clause | GitHub releases, CVE database |
| 6 | **SciPy** | 1.11+ | SciPy Developers | Scientific computing | Medium | BSD 3-Clause | GitHub releases |
| 7 | **Evidently AI** | 0.4+ | Evidently AI | ML model monitoring | Medium | Apache 2.0 | GitHub releases |
| 8 | ** fairlearn** | 0.9+ | Microsoft | Bias detection / fairness | Medium | MIT | GitHub releases |

---

## 6. Infrastructure & DevOps SOUP

| # | Component | Version | Manufacturer | Purpose | Risk Class | License | Anomaly Monitoring |
|---|---|---|---|---|---|---|---|
| 1 | **Docker** | 24.x | Docker Inc. | Containerisation | High | Apache 2.0 | Docker security advisories |
| 2 | **Kubernetes** | 1.28+ | CNCF / Google | Container orchestration | High | Apache 2.0 | Kubernetes security advisories |
| 3 | **Terraform** | 1.6+ | HashiCorp | Infrastructure as code | Medium | BSL 1.1 | HashiCorp security advisories |
| 4 | **GitHub Actions** | N/A | GitHub (Microsoft) | CI/CD automation | High | Proprietary | GitHub status page, security advisories |
| 5 | **AWS / GCP** | N/A | Amazon / Google | Cloud infrastructure | Critical | Proprietary | AWS/GCP security bulletins, status pages |
| 6 | **Kong** | 3.5+ | Kong Inc. | API gateway | High | Apache 2.0 | Kong security advisories |
| 7 | **Nginx** | 1.25+ | F5 / Nginx Inc. | Reverse proxy | High | BSD 2-Clause | Nginx security advisories |
| 8 | **Let's Encrypt** | N/A | ISRG | TLS certificate authority | Critical | N/A (public service) | Let's Encrypt status, cert expiry monitoring |
| 9 | **Snyk** | N/A | Snyk Ltd. | Vulnerability scanning | High | Proprietary (SaaS) | Snyk security advisories |
| 10 | **SonarQube** | 10.x | SonarSource | Code quality analysis | Medium | LGPL v3 / Commercial | SonarSource release notes |

---

## 7. CGM Integration SOUP

| # | Component | Version | Manufacturer | Purpose | Risk Class | License | Anomaly Monitoring |
|---|---|---|---|---|---|---|---|
| 1 | **Dexcom G7 API** | v3 | Dexcom Inc. | CGM data ingestion | Critical | Proprietary (API T&Cs) | Dexcom developer portal, API status |
| 2 | **FreeStyle Libre API** | v2 | Abbott Diabetes Care | CGM data ingestion | Critical | Proprietary (API T&Cs) | Abbott developer portal, API status |
| 3 | **Apple HealthKit** | iOS 16+ | Apple Inc. | iOS health data access | Critical | Proprietary | Apple release notes, API changes |
| 4 | **Google Health Connect** | Android 14+ | Google LLC | Android health data access | Critical | Proprietary | Google release notes, API changes |

### 7.1 CGM API Risk Notes

| API | Known Limitations | Risk Mitigation |
|---|---|---|
| **Dexcom G7** | Rate limits: 100 requests/hour; 3-month data history | Implement caching; request batching; fallback to manual entry |
| **FreeStyle Libre** | 2-hour warm-up period; 8-hour data gap after sensor replacement | Display sensor status; prompt manual entry during gaps |
| **HealthKit** | User can revoke permissions at any time; data may be manually entered by user | Permission monitoring; data source labeling; validation heuristics |
| **Health Connect** | Limited device support on older Android versions; permission model changes | Graceful degradation; manual entry fallback; version compatibility checks |

---

## 8. Known Anomalies & Risk Assessment

### 8.1 Current Known Anomalies

| SOUP | Anomaly ID | Description | Severity | Status | Planned Action |
|---|---|---|---|---|---|
| TensorFlow Lite | ANOM-001 | TFLite 2.15 has known memory leak in specific LSTM configurations | Medium | Open | Monitor; not applicable to current model architecture (no LSTM) |
| Firebase iOS SDK | ANOM-002 | Firebase 10.x crash reporter may miss Swift concurrency crashes | Low | Open | Monitor; fallback to native crash reporting |
| PostgreSQL | ANOM-003 | None currently known | — | — | Continue quarterly CVE monitoring |
| Python cryptography | ANOM-004 | None currently known | — | — | Continue monthly CVE monitoring |

### 8.2 SOUP Risk Assessment Summary

| Risk Category | Count | Highest Risk SOUP |
|---|---|---|
| Operating System / Platform | 2 | iOS, Android |
| Programming Language Runtime | 3 | Swift, Kotlin, Python |
| Database | 2 | PostgreSQL, Redis |
| Security / Cryptography | 4 | PyJWT, cryptography, bcrypt, CryptoKit |
| CGM Integration | 4 | Dexcom API, Libre API, HealthKit, Health Connect |
| ML Framework | 3 | TensorFlow, TensorFlow Lite, scikit-learn |
| Cloud Infrastructure | 2 | AWS/GCP, Kubernetes |

---

## 9. SOUP Maintenance Plan

### 9.1 Monitoring Schedule

| Frequency | Activity | Responsible | Evidence |
|---|---|---|---|
| **Daily** | Automated CI vulnerability scan (Snyk, Dependabot) | CI/CD system | Snyk dashboard |
| **Weekly** | Review security advisories for Critical/High SOUP | Engineering Lead | Security review meeting minutes |
| **Monthly** | Review CVE database for all SOUP; assess applicability | Security Champion | CVE review log |
| **Quarterly** | Full SOUP inventory review; update versions; assess new alternatives | Engineering + Regulatory | SOUP review meeting minutes |
| **Annually** | Comprehensive SOUP risk reassessment; vendor qualification review | Engineering + QA + Regulatory | SOUP risk assessment report |

### 9.2 Update Policy

| Update Type | Trigger | Timeline | Testing Required |
|---|---|---|---|
| **Security patch** | Critical/high CVE published | 7-30 days | Regression testing |
| **Bug fix release** | Bug affecting device functionality | Next sprint | Regression testing |
| **Feature release** | New capability needed | Next quarterly planning | Full V&V |
| **Major version** | Deprecation or architecture change | 90-day evaluation | Full V&V |
| **SOUP replacement** | Unacceptable risk or deprecation | 90-day migration | Full V&V |

### 9.3 Vendor Communication

| Vendor | Contact Method | Response SLA | Last Contact |
|---|---|---|---|
| Apple Developer Support | Developer portal + support tickets | 3-5 business days | [Date] |
| Google Cloud Support | Support console + partner engineer | 4 hours (Business) | [Date] |
| Dexcom Developer | Developer portal + email | 5-10 business days | [Date] |
| Abbott Developer | Developer portal + email | 5-10 business days | [Date] |
| PostgreSQL Community | Mailing list + security list | Variable | [Date] |

---

## 10. SOUP Change Log

| Date | SOUP | Action | From Version | To Version | Justification | Approved By |
|---|---|---|---|---|---|---|
| [Date] | [Initial setup] | Baseline inventory created | — | — | Project initiation | [Name] |
| | | | | | | |

---

*Document Control*  
**Next Review Date:** [Quarterly or upon SOUP change]  
**Distribution:** Engineering, QA, Regulatory, DevOps  
**Retention:** Device lifetime + 10 years
