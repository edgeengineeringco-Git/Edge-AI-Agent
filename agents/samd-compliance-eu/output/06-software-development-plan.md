# Software Development Plan (SDP)

**Document ID:** SDP-001  
**Version:** 1.0  
**Date:** 2026-07-15  
**Standard:** EN IEC 62304:2006 + Amd 1:2015 (Class B)  
**Device:** Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application  
**Classification:** EU MDR Class IIa (Rule 11)  
**Status:** Draft — For Design Review

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Development Process](#2-development-process)
3. [Software Lifecycle Activities](#3-software-lifecycle-activities)
4. [Software Planning](#4-software-planning)
5. [Software Requirements Analysis](#5-software-requirements-analysis)
6. [Software Architecture Design](#6-software-architecture-design)
7. [Software Detailed Design](#7-software-detailed-design)
8. [Software Unit Implementation & Verification](#8-software-unit-implementation--verification)
9. [Software Integration & Integration Testing](#9-software-integration--integration-testing)
10. [Software System Testing](#10-software-system-testing)
11. [Software Release](#11-software-release)
12. [Software Maintenance](#12-software-maintenance)
13. [Software Risk Management](#13-software-risk-management)
14. [Software Configuration Management](#14-software-configuration-management)
15. [SOUP Management](#15-soup-management)
16. [Software Verification Planning](#16-software-verification-planning)
17. [Timeline & Milestones](#17-timeline--milestones)

---

## 1. Introduction

### 1.1 Purpose
This Software Development Plan defines the processes, activities, and tasks for the development of the Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application in accordance with IEC 62304 Class B requirements.

### 1.2 Scope
Covers all software development lifecycle activities from requirements analysis through maintenance, including:
- Mobile applications (iOS, Android)
- Cloud backend services
- Machine learning inference pipeline
- Data storage and synchronization
- Third-party integrations (CGM APIs, health platforms)

### 1.3 Software Safety Classification
**Class B** (per IEC 62304)
- Software can contribute to hazardous situations
- Serious injury is not probable
- Rationale: Lifestyle recommendations only; no drug delivery or life-support control

### 1.4 Development Standards & Tools

| Category | Tool / Standard | Purpose |
|---|---|---|
| **Version Control** | Git + GitHub / GitLab | Source code management |
| **Issue Tracking** | Jira / Linear | Requirements, bugs, tasks |
| **CI/CD** | GitHub Actions / GitLab CI | Automated build, test, deploy |
| **Documentation** | Confluence / Notion | Design docs, wikis |
| **Code Quality** | SonarQube / CodeClimate | Static analysis, code coverage |
| **Security** | Snyk / Dependabot | Vulnerability scanning |
| **Testing** | Jest, XCTest, Espresso | Unit, integration, UI testing |
| **Monitoring** | Firebase Crashlytics, Sentry | Crash reporting, error tracking |
| **Analytics** | Mixpanel / Amplitude | Usage analytics |

---

## 2. Development Process

### 2.1 Process Model
**Agile with medical device design controls**
- Sprints: 2-week cycles
- Design reviews at major milestones (SRR, PDR, CDR, TRR, RRR)
- Traceability maintained continuously via Jira + Confluence
- Risk management integrated into every sprint

### 2.2 Process Map

```
┌──────────────────────────────────────────────────────────────┐
│  Planning → Requirements → Architecture → Detailed Design   │
│       ↓           ↓              ↓                ↓         │
│  Review ← Unit Implementation ← Integration ← System Test   │
│       ↓                                                        │
│  Release → Maintenance → Updates → Retirement              │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Software Lifecycle Activities

### 3.1 Activity Overview (IEC 62304)

| Activity | IEC 62304 Clause | Deliverable | Class B Requirement |
|---|---|---|---|
| Software Development Planning | 5.1 | SDP-001 | Required |
| Software Requirements Analysis | 5.2 | SRS-001 | Required |
| Software Architecture Design | 5.3 | SAD-001 | Required |
| Software Detailed Design | 5.4 | SDD-001 | Required |
| Software Unit Implementation | 5.5 | Source code | Required |
| Software Unit Verification | 5.5 | Unit test reports | Required |
| Software Integration & Testing | 5.6 | Integration test reports | Required |
| Software System Testing | 5.7 | System test reports | Required |
| Software Release | 5.8 | Release notes, DHF update | Required |
| Software Maintenance | 6 | Maintenance records | Required |
| Software Risk Management | 7 | Risk Management File | Required |
| Software Configuration Management | 8 | Configuration records | Required |
| Problem Resolution | 9 | Problem reports, CAPAs | Required |

---

## 4. Software Planning

### 4.1 Development Team

| Role | Responsibilities | FTE |
|---|---|---|
| Engineering Lead | Architecture, technical decisions, code review | 1.0 |
| iOS Developer | Swift/SwiftUI development, HealthKit integration | 1.0 |
| Android Developer | Kotlin/Jetpack Compose development, Health Connect | 1.0 |
| Backend Engineer | API development, database, infrastructure | 1.0 |
| ML Engineer | Algorithm development, model training, validation | 0.5 |
| QA Engineer | Test planning, automation, manual testing | 1.0 |
| DevOps Engineer | CI/CD, infrastructure, security | 0.5 |
| UX Designer | User research, wireframes, usability testing support | 0.5 |

### 4.2 Development Environment

| Component | Specification |
|---|---|
| **iOS Development** | macOS, Xcode 15+, Swift 5.9+, SwiftUI |
| **Android Development** | Android Studio Hedgehog, Kotlin 1.9+, Jetpack Compose |
| **Backend** | Python 3.11+, FastAPI, PostgreSQL 15, Redis |
| **ML Pipeline** | Python 3.11, TensorFlow Lite, scikit-learn |
| **Infrastructure** | AWS / GCP, Docker, Kubernetes, Terraform |
| **CI/CD** | GitHub Actions runners (Ubuntu + macOS) |

### 4.3 Coding Standards

| Language | Standard | Enforcement |
|---|---|---|
| Swift | Swift API Design Guidelines, SwiftLint | CI linting gate |
| Kotlin | Kotlin Coding Conventions, ktlint | CI linting gate |
| Python | PEP 8, Google Python Style, Black, Ruff | CI linting gate |
| TypeScript | Airbnb Style Guide, ESLint, Prettier | CI linting gate |

---

## 5. Software Requirements Analysis

### 5.1 Requirements Source
- MDR GSPR (Annex I) → mapped to functional requirements
- Risk Management File (RM-001) → safety requirements
- Usability Engineering File (IEC 62366-1) → usability requirements
- Stakeholder input (clinical advisor, target users)

### 5.2 Requirements Documentation
- **Master:** Software Requirements Specification (SRS-001)
- **Tracking:** Jira epics/stories with GSPR and risk traceability links
- **Review:** Formal SRS review at System Requirements Review (SRR)

### 5.3 Requirements Traceability
```
GSPR / Risk → Jira Epic → Jira Story → Design Doc → Code Commit → Test Case → Test Result
```

---

## 6. Software Architecture Design

### 6.1 Architecture Principles
1. **Separation of concerns:** Clear boundaries between UI, business logic, data access
2. **Offline-first:** Core functionality works without network; sync when available
3. **Security by design:** Encryption, authentication, authorization at every layer
4. **Testability:** Dependency injection, mockable interfaces, automated test coverage
5. **Scalability:** Cloud-native, containerised, auto-scaling

### 6.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │  iOS App     │  │ Android App  │  │  Web Portal  │        │
│   │  (SwiftUI)   │  │  (Compose)   │  │  (React)     │        │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
└──────────┼─────────────────┼─────────────────┼────────────────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │ HTTPS / TLS 1.3
┌────────────────────────────▼────────────────────────────────────┐
│                         API LAYER                                │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │  API Gateway │  │  Auth        │  │  Rate        │        │
│   │  (Kong/AWS)  │  │  (OAuth 2.0) │  │  Limiter     │        │
│   └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                       SERVICE LAYER                              │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │  Glucose     │  │  Insights    │  │  User        │        │
│   │  Service     │  │  Service     │  │  Service     │        │
│   └──────────────┘  └──────────────┘  └──────────────┘        │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │  Weight      │  │  Notification│  │  Analytics   │        │
│   │  Service     │  │  Service     │  │  Service     │        │
│   └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                         DATA LAYER                               │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│   │  PostgreSQL  │  │  Redis       │  │  Object      │        │
│   │  (Primary)   │  │  (Cache)     │  │  Storage     │        │
│   └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Key Architectural Decisions

| Decision | Rationale | Risk Impact |
|---|---|---|
| **Offline-first SQLite** | Core glucose data available without network | Mitigates R03 (software crash), R05 (CGM failure) |
| **Microservices backend** | Independent scaling and deployment of safety-critical services | Supports R10 (OTA updates), R13 (cloud unavailability) |
| **ML inference on-device** | Low latency, privacy-preserving trend prediction | Mitigates R02 (data breach), R05 (integration failure) |
| **Feature flags** | Gradual rollout, instant rollback of new features | Mitigates R10 (update failure), R14 (notification fatigue) |

---

## 7. Software Detailed Design

### 7.1 Module Breakdown

#### 7.1.1 iOS App Modules

| Module | Responsibility | Key Classes |
|---|---|---|
| **Onboarding** | Age verification, T1DM screening, unit selection, consent | `OnboardingFlow`, `AgeGateView`, `DiabetesTypeScreen` |
| **GlucoseData** | Data ingestion, validation, storage, sync | `GlucoseRepository`, `CGMSyncManager`, `DataValidator` |
| **TrendAnalysis** | Pattern recognition, trend computation, TIR | `TrendEngine`, `PatternDetector`, `TIRCalculator` |
| **Insights** | Recommendation generation, confidence scoring | `InsightsEngine`, `RecommendationGenerator`, `ConfidenceScorer` |
| **WeightManagement** | Weight logging, BMI, correlation analysis | `WeightTracker`, `BMICalculator`, `CorrelationAnalyzer` |
| **Notifications** | Alert management, throttling, scheduling | `NotificationManager`, `AlertScheduler`, `ThrottleEngine` |
| **Settings** | User profile, preferences, data export | `SettingsViewModel`, `ExportManager`, `UnitConverter` |
| **Security** | Encryption, authentication, session management | `AuthManager`, `KeychainWrapper`, `CryptoService` |

#### 7.1.2 Android App Modules
Mirror of iOS modules with Kotlin/Android-specific implementations.

#### 7.1.3 Backend Services

| Service | Responsibility | Tech Stack |
|---|---|---|
| **API Gateway** | Routing, rate limiting, auth validation | Kong / AWS API Gateway |
| **Auth Service** | User authentication, JWT management, MFA | Python / FastAPI, PostgreSQL |
| **Glucose Service** | Data ingestion, validation, storage | Python / FastAPI, PostgreSQL |
| **Insights Service** | ML model serving, recommendation generation | Python / FastAPI, TensorFlow Serving |
| **Notification Service** | Push notification delivery, scheduling | Python / FastAPI, Firebase FCM |
| **Analytics Service** | Event tracking, aggregated reporting | Python / FastAPI, ClickHouse |

#### 7.1.4 ML Pipeline

| Component | Responsibility | Tech Stack |
|---|---|---|
| **Feature Engineering** | Glucose feature extraction, meal correlation | Python, pandas, numpy |
| **Model Training** | Trend prediction model, recommendation model | Python, TensorFlow, scikit-learn |
| **Model Validation** | Cross-validation, bias audit, performance metrics | Python, TensorFlow, fairlearn |
| **Model Serving** | On-device inference (TensorFlow Lite) | TFLite, Core ML (iOS) |
| **Model Monitoring** | Drift detection, performance degradation alerts | Python, Evidently AI |

### 7.2 Interface Specifications

#### 7.2.1 Internal APIs (Mobile ↔ Backend)

```
POST /api/v1/glucose/ingest
  Body: { value: float, unit: "mg/dL"|"mmol/L", timestamp: ISO8601, source: "manual"|"dexcom"|"libre" }
  Response: { id: string, status: "accepted"|"rejected", reason?: string }

GET /api/v1/glucose/trends
  Query: { period: "1d"|"7d"|"14d"|"30d" }
  Response: { readings: [...], trends: { direction: "up"|"down"|"stable", confidence: float } }

POST /api/v1/insights/generate
  Body: { user_id: string, context: "post_meal"|"morning"|"exercise" }
  Response: { recommendations: [...], confidence: "high"|"medium"|"low" }

GET /api/v1/user/export
  Query: { format: "csv"|"json"|"pdf", start_date: ISO8601, end_date: ISO8601 }
  Response: { download_url: string, expires_at: ISO8601 }
```

#### 7.2.2 CGM Integration APIs

```
Dexcom G7 API:
  OAuth 2.0 + PKCE flow
  GET /v3/users/self/egvs  (Estimated Glucose Values)
  GET /v3/users/self/events

FreeStyle Libre API:
  OAuth 2.0 flow
  GET /glucose  (Glucose readings)
  GET /connections  (Linked devices)
```

---

## 8. Software Unit Implementation & Verification

### 8.1 Unit Implementation
- Code written per coding standards
- Peer review required for all changes (GitHub PR + 2 approvals)
- Static analysis gates in CI (SonarQube quality gate)
- Security scanning gates in CI (Snyk critical/high vulnerability block)

### 8.2 Unit Verification

| Component | Test Framework | Coverage Target | Safety-Critical? |
|---|---|---|---|
| iOS UI | XCTest | 70% | No |
| iOS Business Logic | XCTest | 85% | Yes |
| iOS Data Layer | XCTest | 90% | Yes |
| Android UI | Espresso | 70% | No |
| Android Business Logic | JUnit | 85% | Yes |
| Android Data Layer | JUnit | 90% | Yes |
| Backend APIs | pytest | 85% | Yes |
| ML Pipeline | pytest | 80% | Yes |
| Data Validation | pytest | 95% | Yes |

### 8.3 Unit Test Requirements for Safety-Critical Functions

| Function | Test Cases Required |
|---|---|
| `DataValidator.validateGlucoseValue()` | Bounds testing (19, 20, 21, 599, 600, 601); unit validation; null handling |
| `DataValidator.validateDataFreshness()` | 14min59s (pass), 15min00s (pass), 15min01s (fail); timezone handling |
| `GlucoseRepository.saveReading()` | Success, duplicate rejection, checksum validation, encryption verification |
| `InsightsEngine.generateRecommendation()` | Extreme glucose values (return HCP prompt); sufficient data (return insight); insufficient data (return "insufficient") |
| `UnitConverter.mgdlToMmoll()` | Known conversions (180→10.0, 70→3.9, 126→7.0); precision to 1 decimal |
| `AuthManager.authenticate()` | Valid credentials, invalid password, locked account, expired token, MFA required |
| `NotificationManager.sendCriticalAlert()` | Bypass DND, full-screen display, acknowledgement required, escalation timeout |

---

## 9. Software Integration & Integration Testing

### 9.1 Integration Points

| Integration | Components | Test Focus |
|---|---|---|
| **Mobile ↔ Backend** | iOS/Android → API Gateway | Authentication, data sync, error handling, offline queue |
| **Backend ↔ Database** | Services → PostgreSQL | Data integrity, transaction handling, rollback |
| **Backend ↔ CGM APIs** | Glucose Service → Dexcom/Libre | OAuth flow, data parsing, error handling, rate limits |
| **Backend ↔ ML Service** | Insights Service → TensorFlow Serving | Model loading, inference latency, error handling |
| **Mobile ↔ Health Platforms** | iOS → HealthKit; Android → Health Connect | Permission flow, data read/write, error handling |
| **Backend ↔ Notification Service** | Services → Firebase FCM | Delivery reliability, targeting, throttling |

### 9.2 Integration Test Strategy

| Test Type | Scope | Frequency | Environment |
|---|---|---|---|
| **Contract Tests** | API request/response validation | Every PR | CI (mocked dependencies) |
| **Integration Tests** | Service-to-service communication | Every PR | CI (test containers) |
| **End-to-End Tests** | Full user flows | Daily | Staging |
| **CGM API Integration Tests** | Real CGM sandbox APIs | Weekly | Staging |
| **Health Platform Tests** | HealthKit / Health Connect flows | Weekly | Physical devices |

### 9.3 Integration Test Scenarios (Safety-Critical)

| Scenario | Expected Behavior |
|---|---|
| CGM API returns 500 error | App displays cached data with "stale data" warning; retry in 5 minutes |
| CGM API returns glucose reading with future timestamp | Reject reading; log anomaly; alert ops team |
| Network unavailable during glucose sync | Queue sync request; retry when network restored; notify user if >1 hour stale |
| ML service timeout during insight generation | Return "insufficient data" message; do NOT generate low-confidence recommendation |
| Database write fails mid-transaction | Rollback transaction; display error to user; maintain data consistency |
| Concurrent glucose readings from manual + CGM | Prefer CGM timestamp; flag conflict for user confirmation |

---

## 10. Software System Testing

### 10.1 System Test Strategy

| Test Level | Scope | Entry Criteria | Exit Criteria |
|---|---|---|---|
| **Functional Testing** | All SRS requirements | Unit tests pass; integration tests pass | 100% SRS coverage; all critical/high tests pass |
| **Performance Testing** | Load, stress, endurance | Functional tests pass | Meet all PR requirements |
| **Security Testing** | Penetration, vulnerability scan | Functional tests pass | Zero critical/high vulnerabilities |
| **Usability Testing** | Formative + summative | Functional prototype available | Meet US requirements |
| **Compatibility Testing** | OS versions, devices, CGM models | Release candidate | Test matrix coverage |
| **Regression Testing** | Existing functionality after changes | Any code change | 100% regression suite pass |

### 10.2 System Test Protocols

| Protocol ID | Description | Coverage |
|---|---|---|
| TP-SYS-001 | Onboarding flow validation | FR-001 to FR-006 |
| TP-SYS-002 | Glucose data ingestion | FR-007 to FR-015 |
| TP-SYS-003 | Trend analysis and patterns | FR-016 to FR-022 |
| TP-SYS-004 | Personalised insights generation | FR-023 to FR-029 |
| TP-SYS-005 | Weight management features | FR-030 to FR-034 |
| TP-SYS-006 | Notifications and alerts | FR-035 to FR-040 |
| TP-SYS-007 | Data management and export | FR-041 to FR-045 |
| TP-SYS-008 | User profile and settings | FR-046 to FR-050 |
| TP-SYS-009 | Safety-critical features | SAF-001 to SAF-012 |
| TP-SYS-010 | Security and authentication | SEC-001 to SEC-016 |
| TP-SYS-011 | Performance and reliability | PR-001 to PR-010 |
| TP-SYS-012 | Accessibility | US-001 to US-012 |

### 10.3 System Test Environment

| Environment | Purpose | Configuration |
|---|---|---|
| **Development** | Developer testing | Local simulators/emulators |
| **CI Test** | Automated test execution | Docker containers, mocked APIs |
| **Staging** | Pre-release validation | Production-like, CGM sandbox APIs |
| **Beta** | Limited user testing | TestFlight (iOS), Internal Testing (Android) |
| **Production** | Live user environment | Full production stack |

---

## 11. Software Release

### 11.1 Release Criteria

| Criterion | Requirement | Verification |
|---|---|---|
| All SRS requirements implemented and tested | 100% coverage | Traceability matrix review |
| All safety-critical features verified | All SAF requirements tested | Safety test report |
| All known critical/high bugs resolved | Zero open critical/high bugs | Bug tracker review |
| Risk Management File reviewed and current | RM-001 approved | Management review |
| DHF complete and reviewed | All design records present | DHF checklist |
| Regulatory labeling verified | IFU, app store copy, in-app labels | Labeling review |
| Security scan clean | Zero critical/high vulnerabilities | Snyk/pen test report |
| Performance targets met | All PR targets achieved | Performance test report |

### 11.2 Release Types

| Type | Definition | Examples | Approval |
|---|---|---|---|
| **Major** | New features, algorithm changes, safety updates | v2.0.0 | Management Rep + Regulatory |
| **Minor** | Bug fixes, performance improvements, UI updates | v1.1.0 | Engineering Lead + QA |
| **Hotfix** | Critical security or safety issue | v1.1.1 | Engineering Lead (emergency) |

### 11.3 Release Procedure
1. **Build:** Generate release build from tagged commit
2. **Verify:** Run full test suite; security scan; performance test
3. **Stage:** Deploy to beta environment; monitor 48h
4. **Approve:** Release approval form with sign-offs
5. **Deploy:** Submit to app stores; backend deployment
6. **Monitor:** 72h critical monitoring period (crash rates, API health, user feedback)
7. **Document:** Update DHF, release notes, EUDAMED (if applicable)

### 11.4 Rollback Procedure
- Automatic canary rollback if error rate >1%
- Manual rollback capability within 30 minutes
- User notification if rollback affects active sessions

---

## 12. Software Maintenance

### 12.1 Maintenance Activities
- Problem resolution (bug fixes)
- SOUP updates (security patches, dependency updates)
- Performance optimisation
- Feature enhancements (via change control)
- Regulatory updates (MDR amendments, new guidance)

### 12.2 Problem Resolution Process
1. **Report:** Problem reported via support, monitoring, or PMS
2. **Log:** Problem logged in Jira with severity classification
3. **Investigate:** Root cause analysis; assess safety impact
4. **Plan:** Change plan with risk assessment (refer to SOP-009)
5. **Implement:** Code fix with unit/integration tests
6. **Verify:** Testing confirms fix; regression testing passed
7. **Release:** Hotfix or scheduled release
8. **Close:** Problem report closed; DHF updated

### 12.3 Problem Severity Classification

| Severity | Definition | Response Time | Example |
|---|---|---|---|
| **Critical** | Safety risk, data loss, complete service outage | 4 hours | App crashes on launch; data breach |
| **High** | Major functionality impaired, workaround difficult | 24 hours | CGM sync failing for all users |
| **Medium** | Functionality impaired, workaround available | 72 hours | Notification delay, minor UI glitch |
| **Low** | Cosmetic issue, no functional impact | Next sprint | Typo, minor alignment issue |

---

## 13. Software Risk Management

### 13.1 Integration with ISO 14971
Software risk management is integrated into the overall Risk Management File (RM-001):
- Software hazards identified during architecture and detailed design
- Risk controls implemented in code (validation, error handling, encryption)
- Risk control effectiveness verified through testing
- Residual risks monitored through PMS

### 13.2 Software-Specific Hazards
See RM-001 §2.2 for complete hazard list. Key software hazards:
- Algorithm inaccuracy (R01)
- Software crash (R03)
- Data breach (R02)
- CGM integration failure (R05)
- User misinterpretation (R06)

### 13.3 Risk Control Implementation in Software
| Risk | Software Control | Module |
|---|---|---|
| R01 | Confidence threshold; HCP escalation | InsightsEngine |
| R02 | Encryption; RBAC; MFA | CryptoService; AuthManager |
| R03 | Offline cache; crash monitoring | GlucoseRepository; Crashlytics |
| R05 | Data freshness validation; API health checks | DataValidator; CGMSyncManager |
| R06 | Graded outputs; persistent disclaimers | InsightsEngine; UI Components |

---

## 14. Software Configuration Management

### 14.1 Configuration Items
- Source code (all repositories)
- Build scripts and CI/CD pipelines
- Test cases and test data
- Documentation (SRS, architecture, design)
- SOUP components and versions
- Release packages

### 14.2 Version Control
- **Branching:** GitFlow (main, develop, feature/*, release/*, hotfix/*)
- **Commits:** All commits reference Jira ticket ID
- **Tags:** Release tags (`v1.0.0`, `v1.1.0`) on main branch
- **Protection:** main branch protected — requires PR + 2 approvals + CI pass

### 14.3 Change Control
- All changes via Pull Request
- PR template includes: description, testing, risk impact, GSPR impact
- Automated CI gates: build, lint, unit tests, integration tests, security scan
- Code review by at least 2 engineers (one senior)
- Merge only after all gates pass and approvals received

---

## 15. SOUP Management

### 15.1 SOUP Inventory
See separate SOUP Inventory document (SOUP-001) for complete list.

### 15.2 SOUP Management Process
1. **Evaluation:** Before adding new SOUP, evaluate: maintenance activity, security track record, license compatibility, documentation quality
2. **Approval:** Engineering Lead approves new SOUP; Regulatory notified if safety-relevant
3. **Monitoring:** Automated vulnerability scanning (Snyk, Dependabot) weekly
4. **Updates:** Security patches applied within 30 days of release; major updates evaluated quarterly
5. **Documentation:** SOUP inventory updated with version, known anomalies, maintenance plan

### 15.3 SOUP Anomaly Response
| Anomaly Type | Response | Timeline |
|---|---|---|
| Critical CVE | Emergency patch or SOUP replacement | 7 days |
| High CVE | Scheduled patch in next sprint | 30 days |
| Deprecation notice | Evaluate migration path | 90 days |
| Breaking change | Assess impact; plan update | Next quarterly review |

---

## 16. Software Verification Planning

### 16.1 Verification Summary

| Activity | Method | Responsible | Evidence |
|---|---|---|---|
| Code review | Peer review (PR) | Engineering | PR approvals |
| Static analysis | SonarQube, linting | CI/CD | Quality gate reports |
| Unit testing | Automated (XCTest, JUnit, pytest) | Engineering | Test reports |
| Integration testing | Automated (pytest, Postman) | QA + Engineering | Test reports |
| System testing | Manual + automated | QA | Test protocols + reports |
| Security testing | Snyk + pen test | Security firm | Pen test report |
| Usability testing | Formative + summative | UX Research | Usability reports |
| Algorithm validation | Retrospective analysis | Data Science | Validation report |

### 16.2 Verification Independence
- Unit tests: Developers (not independent)
- Integration tests: QA + Developers (partially independent)
- System tests: QA (independent)
- Usability tests: UX Research (independent)
- Security tests: External firm (independent)

---

## 17. Timeline & Milestones

| Milestone | Target | Deliverables |
|---|---|---|
| SRR Complete | Month 3 | Approved SRS, initial risk analysis |
| PDR Complete | Month 4 | Approved architecture, SOUP inventory |
| CDR Complete | Month 5 | Approved detailed design, test plans |
| Development Complete | Month 7 | Implemented code, unit tests passed |
| TRR Complete | Month 7 | Test environment ready, test protocols approved |
| System Testing Complete | Month 8 | All system tests passed, bug closure |
| RRR Complete | Month 9 | DHF complete, labeling approved, release authorised |
| CE Marking | Month 12 | NB certificate received, EUDAMED registered |

---

*Document Control*  
**Next Review Date:** [Upon major design change or architecture decision]  
**Distribution:** Engineering, QA, Regulatory, DevOps  
**Retention:** Device lifetime + 10 years
