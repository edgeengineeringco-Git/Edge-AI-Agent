# Quality Management System Procedures

**Document ID:** QMS-001  
**Version:** 1.0  
**Date:** 2026-07-15  
**Standard:** EN ISO 13485:2016  
**Device:** Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application  
**Status:** Draft — For Management Review

---

## Table of Contents
1. [Quality Manual Overview](#1-quality-manual-overview)
2. [SOP-001: Document Control](#2-sop-001-document-control)
3. [SOP-002: Management Review](#3-sop-002-management-review)
4. [SOP-003: Design & Development Planning](#4-sop-003-design--development-planning)
5. [SOP-004: Design Inputs](#5-sop-004-design-inputs)
6. [SOP-005: Design Outputs](#6-sop-005-design-outputs)
7. [SOP-006: Design Review](#7-sop-006-design-review)
8. [SOP-007: Design Verification](#8-sop-007-design-verification)
9. [SOP-008: Design Validation](#9-sop-008-design-validation)
10. [SOP-009: Design Changes](#10-sop-009-design-changes)
11. [SOP-010: Design Transfer](#11-sop-010-design-transfer)
12. [SOP-011: Design History File (DHF)](#12-sop-011-design-history-file-dhf)
13. [SOP-012: Software Configuration Management](#13-sop-012-software-configuration-management)
14. [SOP-013: SOUP Management](#14-sop-013-soup-management)
15. [SOP-014: Complaint Handling](#15-sop-014-complaint-handling)
16. [SOP-015: Vigilance & Adverse Event Reporting](#16-sop-015-vigilance--adverse-event-reporting)
17. [SOP-016: Corrective & Preventive Action (CAPA)](#17-sop-016-corrective--preventive-action-capa)
18. [SOP-017: Post-Market Surveillance (PMS)](#18-sop-017-post-market-surveillance-pms)
19. [SOP-018: Internal Audit](#19-sop-018-internal-audit)
20. [SOP-019: Supplier & Contractor Management](#20-sop-019-supplier--contractor-management)
21. [SOP-020: Training & Competency](#21-sop-020-training--competency)
22. [SOP-021: Controlled Release & Distribution](#22-sop-021-controlled-release--distribution)
23. [SOP-022: Traceability Matrix Maintenance](#23-sop-022-traceability-matrix-maintenance)
24. [SOP-023: Risk Management Integration](#24-sop-023-risk-management-integration)

---

## 1. Quality Manual Overview

### 1.1 Scope of QMS
This Quality Management System applies to the design, development, verification, validation, release, distribution, and post-market surveillance of the Glucose Fluctuation Monitoring & Personalised Weight-Loss Insights Application, a Class IIa Software as a Medical Device (SaMD) under EU MDR 2017/745.

**Exclusions:**
- ISO 13485:2016 Clause 7.5.1 (Production and service provision controls) — partially excluded for pure software. Controlled build and release procedures (SOP-021) replace physical production controls.
- ISO 13485:2016 Clause 7.5.2 (Cleanliness of product) — Not applicable to software-only device.
- ISO 13485:2016 Clause 7.5.5 (Particular requirements for sterile devices) — Not applicable.

All other clauses of ISO 13485:2016 are applicable and implemented.

### 1.2 Regulatory Framework
| Regulation / Standard | Application |
|---|---|
| EU MDR 2017/745 | Medical device regulation, CE marking, EUDAMED |
| EN ISO 13485:2016 | Quality management system |
| EN IEC 62304:2006 + Amd 1:2015 | Medical device software lifecycle |
| EN ISO 14971:2019 | Risk management |
| EN IEC 62366-1:2015 | Usability engineering |
| GDPR 2016/679 | Data protection |

### 1.3 Process Map

```
[Management] → [Quality Planning] → [Resource Management]
      ↓                ↓                    ↓
[Design & Development] → [Risk Management] → [Software Lifecycle]
      ↓                ↓                    ↓
[Verification & Validation] → [Release] → [Distribution]
      ↓                ↓                    ↓
[Post-Market Surveillance] → [CAPA] → [Management Review]
```

### 1.4 Quality Policy
> "We are committed to designing and maintaining safe, effective, and user-centred medical device software that meets all regulatory requirements and exceeds user expectations. We continuously improve our processes through data-driven decision making, risk-based thinking, and active stakeholder engagement."

### 1.5 Quality Objectives (2026)
| Objective | Target | Metric | Review Frequency |
|---|---|---|---|
| Software reliability | >99.5% crash-free rate | Crashlytics | Monthly |
| User safety | Zero serious incidents related to device malfunction | Vigilance log | Monthly |
| Regulatory compliance | 100% on-time PSUR submission | PSUR schedule | Annually |
| User satisfaction | App store rating >4.0 | App store analytics | Quarterly |
| Risk control effectiveness | 100% ALARP risks verified | Risk Management File | Quarterly |
| CAPA closure | 100% CAPAs closed within target date | CAPA log | Monthly |

---

## 2. SOP-001: Document Control

### 2.1 Purpose
Establish controls for the identification, storage, protection, retrieval, retention, and disposition of QMS documents and records.

### 2.2 Scope
All QMS documents, technical documentation, design records, and regulatory submissions.

### 2.3 Procedure

#### 2.3.1 Document Identification
- Every controlled document receives a unique Document ID: `[CATEGORY]-[NNN]` (e.g., QMS-001, RM-001, SRS-001)
- Document status: Draft → For Review → Approved → Superseded → Obsolete
- Version format: Major.Minor (e.g., 1.0, 1.1, 2.0)
  - Major: content change affecting safety, compliance, or intended use
  - Minor: editorial, formatting, or non-substantive corrections

#### 2.3.2 Document Approval
| Document Type | Drafted By | Reviewed By | Approved By |
|---|---|---|---|
| Quality Manual | QA Manager | Management Rep | CEO / MD |
| SOPs | Process Owner | QA Manager | Management Rep |
| Technical Documents | Engineering | Regulatory | Management Rep |
| Risk Management File | Regulatory | Clinical Safety Officer | Management Rep |
| Test Protocols | QA Engineer | Test Lead | QA Manager |

#### 2.3.3 Change Control
1. Change request submitted via Document Change Request (DCR) form
2. Impact assessment: safety, regulatory, compatibility, traceability
3. Approved changes implemented; document version incremented
4. Superseded versions archived; current version distributed
5. Training on changed documents assigned to affected personnel

#### 2.3.4 Record Retention
| Record Type | Retention Period | Storage Location |
|---|---|---|
| Design History File | Device lifetime + 10 years | Secure cloud + offline backup |
| Risk Management File | Device lifetime + 10 years | Secure cloud + offline backup |
| Complaint records | Device lifetime + 10 years | Secure cloud |
| Vigilance reports | Device lifetime + 10 years | Secure cloud |
| Internal audit reports | 5 years | Secure cloud |
| Training records | Employment + 5 years | HR system |
| Supplier records | Active + 5 years | Procurement system |

---

## 3. SOP-002: Management Review

### 3.1 Purpose
Ensure the QMS remains suitable, adequate, and effective through periodic review by top management.

### 3.2 Frequency
- **Scheduled:** Minimum annually, or per major milestone (design review, release, NB audit)
- **Unscheduled:** Triggered by serious adverse event, NB finding, or significant market change

### 3.3 Inputs
1. Status of actions from previous management reviews
2. Changes in regulatory requirements (MDR, standards, guidance)
3. Internal and external audit results
4. Customer feedback, complaints, and app store reviews
5. Process performance and product conformity (KPIs)
6. Status of CAPAs
7. Results of risk management reviews
8. Post-market surveillance data
9. Supplier performance
10. Resource adequacy

### 3.4 Outputs
1. Decisions and actions for QMS improvement
2. Resource allocation decisions
3. Changes to quality policy or objectives
4. Approved design changes or product updates
5. Management Review Report (signed minutes)

---

## 4. SOP-003: Design & Development Planning

### 4.1 Purpose
Define and document the design and development activities for each SaMD release.

### 4.2 Design Plan Contents
Every design plan shall include:
1. Design and development stages (requirements, architecture, implementation, V&V)
2. Review, verification, and validation activities for each stage
3. Responsibilities and authorities
4. Interfaces between different groups (engineering, QA, regulatory, clinical)
5. Resource requirements (personnel, tools, budget)
6. Timeline with milestones
7. Traceability strategy (GSPR → Design Input → Verification → Evidence)

### 4.3 Design Plan Approval
- Drafted by: Project Manager / Engineering Lead
- Reviewed by: QA Manager, Regulatory Lead, Clinical Safety Officer
- Approved by: Management Representative

---

## 5. SOP-004: Design Inputs

### 5.1 Purpose
Ensure all design inputs are identified, documented, reviewed, and approved before design proceeds.

### 5.2 Design Input Categories

#### 5.2.1 Functional Requirements
- Glucose data ingestion (manual entry + CGM API)
- Trend analysis and pattern recognition
- Personalised lifestyle recommendation generation
- User profile management (age, diabetes type, medications, goals)
- Notification and alerting system
- Data export and reporting

#### 5.2.2 Performance Requirements
- Glucose data processing latency: <2 seconds
- Recommendation generation latency: <5 seconds
- App launch time: <3 seconds
- Offline functionality: minimum 24 hours of cached data
- API uptime dependency: graceful degradation if backend unavailable

#### 5.2.3 Safety Requirements (from Risk Management)
- T1DM screening and exclusion
- Data freshness validation (>15 min = stale)
- Unit locking with 2-step change verification
- Confidence threshold for algorithm predictions
- Emergency escalation prompts for extreme glucose values

#### 5.2.4 Regulatory Requirements (GSPR Mapping)
- MDR Annex I, GSPR Chapters 1-23
- Each design input traced to applicable GSPR(s)
- Traceability maintained in central matrix

#### 5.2.5 Usability Requirements (from IEC 62366-1)
- Onboarding task completion rate >90% (summative testing)
- Critical warning comprehension rate >95%
- Error recovery rate >90%
- Accessibility compliance (WCAG 2.1 AA minimum)

### 5.3 Design Input Review
- All inputs reviewed for completeness, consistency, and testability
- Ambiguous or conflicting inputs resolved before approval
- Approved inputs become baseline; changes follow SOP-009

---

## 6. SOP-005: Design Outputs

### 6.1 Purpose
Ensure design outputs are documented, verified against inputs, and provide adequate information for subsequent processes.

### 6.2 Design Output Documents
1. Software Requirements Specification (SRS)
2. Software Architecture Design Document
3. Software Detailed Design Document (modules, interfaces, data models)
4. UI/UX Design Specifications (wireframes, prototypes, style guides)
5. API Specifications (internal and external)
6. Database Schema and Data Flow Diagrams
7. Test Protocols and Test Cases
8. Labelling and IFU drafts

### 6.3 Design Output Verification
- Each output verified against corresponding design input(s)
- Verification method: review, inspection, analysis, or testing
- Verification results documented and approved

---

## 7. SOP-006: Design Review

### 7.1 Purpose
Systematically review design results at defined stages to identify issues before proceeding.

### 7.2 Review Stages

| Stage | Trigger | Participants | Focus |
|---|---|---|---|
| **System Requirements Review (SRR)** | SRS complete | Engineering, QA, Regulatory, Clinical | Requirements completeness, GSPR coverage, safety requirements |
| **Preliminary Design Review (PDR)** | Architecture complete | Engineering, QA, Security, UX | Architecture soundness, SOUP selection, security design |
| **Critical Design Review (CDR)** | Detailed design complete | Engineering, QA, Regulatory, UX | Design completeness, testability, risk control implementation |
| **Test Readiness Review (TRR)** | Before system testing | QA, Engineering, Regulatory | Test coverage, traceability, test environment readiness |
| **Release Readiness Review (RRR)** | Before commercial release | All stakeholders | Documentation completeness, NB readiness, PMS readiness |

### 7.3 Review Outputs
- Design Review Report with findings, actions, and approvals
- Action items tracked to closure
- Go / No-Go decision documented

---

## 8. SOP-007: Design Verification

### 8.1 Purpose
Confirm that design outputs meet design input requirements.

### 8.2 Verification Methods
| Method | When Used | Example |
|---|---|---|
| **Test** | Functional requirements | Unit tests, integration tests, system tests |
| **Analysis** | Performance, safety | Algorithm accuracy analysis, load testing |
| **Inspection** | Documentation, code | Code review, document review |
| **Demonstration** | Usability requirements | Usability testing sessions |

### 8.3 Verification Levels
1. **Unit Verification:** Individual software modules (per IEC 62304 Class B)
2. **Integration Testing:** Module interfaces and data flows
3. **System Testing:** End-to-end functionality against SRS
4. **Regression Testing:** Existing functionality after changes

### 8.4 Traceability
Every test case linked to one or more design inputs via traceability matrix.

---

## 9. SOP-008: Design Validation

### 9.1 Purpose
Ensure the device meets user needs and intended use in the intended environment.

### 9.2 Validation Activities
1. **Clinical Validation:** Evidence that personalised insights improve weight-loss or glycaemic outcomes (via literature or PMCF)
2. **Usability Validation:** Summative usability testing per IEC 62366-1 with representative users
3. **Algorithm Validation:** Analytical validation of glucose trend predictions vs. clinical reference
4. **Cybersecurity Validation:** Penetration testing and vulnerability assessment

### 9.3 Validation Acceptance Criteria
- All critical and high-priority user tasks completed without serious use errors
- Clinical claims supported by evidence in Clinical Evaluation Report
- No critical security vulnerabilities (CVSS >7.0) unremediated

---

## 10. SOP-009: Design Changes

### 10.1 Purpose
Control changes to approved design inputs, outputs, and device specifications.

### 10.2 Change Categories

| Category | Definition | Approval Required |
|---|---|---|
| **Minor** | Editorial, UI cosmetic, non-safety bug fix | Engineering Lead |
| **Major** | Feature addition, algorithm change, interface change | Management Rep + Regulatory |
| **Critical** | Safety-critical fix, intended use change, patient population change | Management Rep + Regulatory + Clinical Safety Officer |

### 10.3 Change Control Procedure
1. Change Request (CR) submitted with rationale, impact assessment
2. Safety impact assessed (refer to Risk Management File)
3. Regulatory impact assessed (GSPR, classification, NB notification)
4. Traceability matrix updated
5. V&V activities planned for changed elements
6. Change implemented, verified, and validated
7. Change closed; Design History File updated

---

## 11. SOP-010: Design Transfer

### 11.1 Purpose
Ensure design outputs are correctly translated into production/release specifications.

### 11.2 Design Transfer Checklist
- [ ] All design outputs reviewed and approved
- [ ] Release build generated from controlled source code
- [ ] Build environment documented and validated
- [ ] Release notes prepared
- [ ] IFU and labeling finalised
- [ ] EUDAMED UDI-DI registered (if applicable)
- [ ] App store listing reviewed for regulatory compliance
- [ ] PMS system active and configured
- [ ] Support team trained on new release

---

## 12. SOP-011: Design History File (DHF)

### 12.1 Purpose
Maintain a comprehensive record of the design history for each device.

### 12.2 DHF Contents
```
DHF/
├── Design Plan
├── Design Input Documents (SRS, requirements)
├── Design Output Documents (architecture, detailed design, code)
├── Design Review Records
├── Verification Protocols and Reports
├── Validation Protocols and Reports
├── Design Change Records
├── Risk Management File (reference)
├── Clinical Evaluation Report (reference)
├── Labelling and IFU
└── Regulatory Correspondence
```

### 12.3 DHF Maintenance
- DHF initiated at project start
- Updated continuously throughout design and development
- Final DHF compiled and archived at device release
- Changes to released device: DHF supplement created

---

## 13. SOP-012: Software Configuration Management

### 13.1 Purpose
Establish and maintain the integrity of software products throughout the lifecycle.

### 13.2 Configuration Items
- Source code (all repositories)
- Build scripts and CI/CD pipelines
- Test cases and test data
- Documentation (SRS, architecture, IFU)
- Third-party libraries and dependencies (SOUP)
- Release packages (binaries, app bundles)

### 13.3 Version Control
- Git used for all source code and documentation
- Branching strategy: `main` (production), `develop` (integration), `feature/*`, `hotfix/*`
- All commits associated with Change Request or ticket ID
- Release tags: `v[Major].[Minor].[Patch]` (semantic versioning)

### 13.4 Build Control
- Automated CI/CD pipeline (GitHub Actions / GitLab CI / equivalent)
- Build environment documented and locked (Docker images, dependency versions)
- Each release build reproducible from source
- Build artifacts signed and checksum-verified

### 13.5 Release Checklist
- [ ] All CRs for release implemented and verified
- [ ] Regression test suite passed (100%)
- [ ] Security scan passed (no critical/high vulnerabilities)
- [ ] Code review completed for all changes
- [ ] Documentation updated and approved
- [ ] DHF updated
- [ ] Risk Management File reviewed for change impact
- [ ] App store regulatory labeling verified
- [ ] EUDAMED registration updated (if applicable)

---

## 14. SOP-013: SOUP Management

### 14.1 Purpose
Manage Software of Unknown Provenance (third-party libraries, APIs, OS) per IEC 62304.

### 14.2 SOUP Inventory
Maintain a living inventory of all SOUP items:

| Component | Version | Manufacturer | Purpose | Safety Class | Anomaly Monitoring | Maintenance Plan |
|---|---|---|---|---|---|---|
| React Native | [x.x.x] | Meta | Mobile framework | N/A | CVE database, npm audit | Quarterly review |
| Firebase / GCP | [x.x.x] | Google | Backend, auth, analytics | N/A | Google security bulletins | Monthly review |
| HealthKit API | [iOS xx] | Apple | iOS health data | N/A | Apple release notes | Per iOS release |
| Google Health Connect | [x.x.x] | Google | Android health data | N/A | Google release notes | Per Android release |
| [CGM SDK Name] | [x.x.x] | [Manufacturer] | Glucose data ingestion | N/A | Manufacturer advisories | Per manufacturer notice |
| TensorFlow Lite | [x.x.x] | Google | On-device ML inference | N/A | CVE database | Quarterly review |
| [Add all libraries] | | | | | | |

### 14.3 SOUP Evaluation Criteria
Before adding new SOUP:
- [ ] Active maintenance (commits/releases within 12 months)
- [ ] Security track record (no unpatched critical CVEs)
- [ ] License compatibility with commercial distribution
- [ ] Documentation adequacy for integration
- [ ] Manufacturer support availability

### 14.4 SOUP Anomaly Management
- Monitor SOUP for known anomalies (CVEs, deprecation, breaking changes)
- Document known anomalies in Risk Management File
- Maintain upgrade plan for SOUP with critical vulnerabilities
- Test integration after SOUP upgrades (regression testing)

---

## 15. SOP-014: Complaint Handling

### 15.1 Purpose
Establish a systematic process for receiving, evaluating, investigating, and responding to complaints.

### 15.2 Complaint Definition
Any written, electronic, or oral communication alleging deficiencies related to the identity, quality, durability, reliability, safety, effectiveness, or performance of the device.

### 15.3 Complaint Handling Procedure
1. **Receipt:** Log all complaints within 24 hours of receipt
2. **Triage:** Classify as:
   - **Service request** (how-to, feature request) → Support handles
   - **Quality complaint** (app malfunction, data error) → QA investigates
   - **Safety complaint** (potential adverse event) → Vigilance procedure (SOP-015)
3. **Investigation:** Root cause analysis; review against Risk Management File
4. **Action:** Corrective action, workaround, or explanation
5. **Response:** Communicate resolution to complainant within target SLA
6. **Closure:** Document outcome; trend for PMS

### 15.4 Complaint Log Fields
- Complaint ID, Date Received, Source, Device Version
- Complaint Description, Classification, Investigation Summary
- Root Cause, Corrective Action, Closure Date
- Trend Code (for PMS analysis)

---

## 16. SOP-015: Vigilance & Adverse Event Reporting

### 16.1 Purpose
Ensure timely reporting of serious incidents and field safety corrective actions to competent authorities.

### 16.2 Regulatory Basis
- MDR Article 87: Serious incident reporting
- MDR Article 92: Field Safety Corrective Actions (FSCA)
- MDCG 2021-1: Vigilance terminology and concepts

### 16.3 Serious Incident Definition
An incident that directly or indirectly led, might have led, or might lead to:
- Death of a patient, user, or other person
- Temporary or permanent serious deterioration of a person's state of health

### 16.4 Reporting Timeline
| Event Type | Timeline | Report To |
|---|---|---|
| Serious incident (death / unthreatened) | Immediately, but no later than 10 days | Competent Authority of Member State where incident occurred |
| Serious incident (other) | Immediately, but no later than 15 days | Competent Authority |
| Field Safety Corrective Action (FSCA) | Immediately | Competent Authority + affected users |
| Trend report (significant increase in non-serious incidents) | Quarterly if threshold met | Competent Authority |

### 16.5 Vigilance Procedure
1. **Detection:** Complaint, support ticket, HCP report, PMS data, or media
2. **Assessment:** Determine if serious incident per MDR definition
3. **Immediate action:** If ongoing risk, implement containment (app update, user notification, feature disable)
4. **Investigation:** Root cause analysis; refer to Risk Management File
5. **Reporting:** Submit to competent authority via EUDAMED or national system
6. **FSCA (if applicable):** Issue field safety notice; track implementation
7. **Closure:** Document in vigilance log; update Risk Management File and PMS data

---

## 17. SOP-016: Corrective & Preventive Action (CAPA)

### 17.1 Purpose
Systematically address nonconformities and implement actions to prevent recurrence.

### 17.2 CAPA Trigger Sources
- Internal audits
- Management reviews
- Complaints and vigilance
- Design reviews
- Testing failures
- PMS data trends
- Notified Body findings
- Supplier nonconformities

### 17.3 CAPA Procedure
1. **Identification:** Document the nonconformity or potential issue
2. **Evaluation:** Assess impact on product safety, compliance, and quality
3. **Investigation:** Root cause analysis (5 Whys, Fishbone, FMEA)
4. **Action Plan:** Define corrective action (fix the problem) and preventive action (prevent recurrence)
5. **Implementation:** Execute actions with assigned owner and deadline
6. **Verification:** Confirm effectiveness of actions (data, testing, monitoring)
7. **Closure:** Management approval; document in CAPA log

### 17.4 CAPA Log Fields
- CAPA ID, Date Opened, Source, Description
- Root Cause, Corrective Action, Preventive Action
- Owner, Target Date, Completion Date
- Verification Method, Verification Result, Closed By, Date Closed

---

## 18. SOP-017: Post-Market Surveillance (PMS)

### 18.1 Purpose
Systematically collect, analyse, and act on post-market data to confirm device safety and performance.

### 18.2 PMS Data Sources
1. **Complaints and vigilance reports**
2. **App store reviews and ratings**
3. **Social media and forum monitoring**
4. **Customer surveys and feedback forms**
5. **Published literature and competitor incidents**
6. **PMCF study data**
7. **Software analytics (usage, crash rates, feature engagement)**
8. **Cybersecurity threat intelligence**

### 18.3 PMS Plan Contents
- Data sources and collection methods
- Data analysis methodology (quantitative + qualitative)
- Frequency of analysis (quarterly for active PMS)
- Trend criteria and thresholds
- Action triggers (CAPA, risk management review, FSCA)
- PSUR schedule (every 2 years for Class IIa)

### 18.4 Periodic Safety Update Report (PSUR)
| Section | Content |
|---|---|
| 1. Executive Summary | Key findings, actions taken, conclusions |
| 2. Device Description | Intended use, patient population, sales volume |
| 3. Sales & Usage Data | Active users, geographic distribution, usage metrics |
| 4. Complaint Summary | Total complaints, categories, trends |
| 5. Vigilance Summary | Serious incidents, investigations, outcomes |
| 6. Risk Management Update | New hazards, risk control effectiveness |
| 7. PMCF Results | Clinical data collected, outcomes |
| 8. Benefit-Risk Conclusion | Updated benefit-risk assessment |
| 9. Actions & Plans | CAPAs, updates, planned changes |

---

## 19. SOP-018: Internal Audit

### 19.1 Purpose
Verify QMS conformity to ISO 13485 and MDR requirements.

### 19.2 Audit Program
- **Frequency:** Minimum annually; more frequent for high-risk processes
- **Scope:** All ISO 13485 clauses applicable to the organisation
- **Auditors:** Trained internal auditors independent of the area being audited

### 19.3 Audit Procedure
1. **Plan:** Define scope, criteria, schedule, and auditor assignments
2. **Prepare:** Review previous audit findings, process documentation, KPIs
3. **Conduct:** Opening meeting, evidence gathering, interviews, observation
4. **Report:** Document findings (conformity, nonconformity, observation)
5. **Close:** Management review of findings; CAPAs assigned
6. **Follow-up:** Verify CAPA effectiveness

### 19.4 Audit Findings Classification
| Class | Definition | Action Required |
|---|---|---|
| **Major Nonconformity** | Systematic failure or absence of a required process | Immediate corrective action; may affect certification |
| **Minor Nonconformity** | Isolated failure or partial implementation | Corrective action within defined timeframe |
| **Observation** | Potential issue, not yet a nonconformity | Monitor; preventive action recommended |

---

## 20. SOP-019: Supplier & Contractor Management

### 20.1 Purpose
Ensure suppliers and contractors meet quality and regulatory requirements.

### 20.2 Supplier Categories
| Category | Examples | Controls |
|---|---|---|
| **Critical** | CGM API provider, cloud infrastructure, security testing firm | Full qualification, annual audit, quality agreement |
| **Important** | Analytics provider, push notification service | Qualification questionnaire, performance monitoring |
| **General** | Office supplies, non-clinical software | Basic procurement controls |

### 20.3 Supplier Qualification
- Questionnaire (ISO 13485 certification, MDR awareness, security practices)
- Performance evaluation (uptime, support responsiveness, incident history)
- Quality Agreement defining responsibilities, change control, and audit rights

### 20.4 Contractor Controls
- Confidentiality and data processing agreements (GDPR Article 28)
- Competency verification (CV, certifications, references)
- Work product review and acceptance criteria
- Training on company QMS and device-specific requirements

---

## 21. SOP-020: Training & Competency

### 21.1 Purpose
Ensure all personnel are competent to perform their QMS roles.

### 21.2 Training Matrix

| Role | Required Training | Method | Frequency | Evidence |
|---|---|---|---|---|
| Software Engineer | IEC 62304, coding standards, security | Course + exam | At hire + annual | Certificate + test record |
| QA Engineer | ISO 13485, test methodology, audit | Course + practical | At hire + annual | Certificate + test record |
| Regulatory Affairs | MDR 2017/745, ISO 14971, clinical evaluation | External course | At hire + biennial | Certificate |
| Management Rep | ISO 13485, MDR, management systems | External course | At hire + biennial | Certificate |
| All Staff | GDPR, information security, company QMS | Internal training | At hire + annual | Attendance record + quiz |

### 21.3 Competency Records
- Training attendance and completion
- Assessment results (exams, practical evaluations)
- Certification copies
- Annual competency review

---

## 22. SOP-021: Controlled Release & Distribution

### 22.1 Purpose
Ensure only approved software versions are released to users.

### 22.2 Release Types
| Type | Definition | Approval |
|---|---|---|
| **Major Release** | New features, algorithm changes, safety-critical updates | Management Rep + Regulatory |
| **Minor Release** | Bug fixes, performance improvements, UI updates | Engineering Lead + QA Manager |
| **Hotfix** | Critical security or safety fix requiring immediate deployment | Engineering Lead (emergency) + retroactive Management Rep approval |

### 22.3 Release Procedure
1. **Build:** Generate release build from tagged commit
2. **Verify:** Run full regression test suite; security scan
3. **Stage:** Deploy to beta/test environment; monitor for 48h
4. **Approve:** Release approval form signed
5. **Deploy:** Push to app stores (Apple App Store, Google Play)
6. **Monitor:** Watch crash rates, API health, user feedback (72h critical period)
7. **Document:** Update DHF, release notes, EUDAMED (if UDI-DI changes)

### 22.4 Rollback Procedure
- Automated canary release with automatic rollback on error rate >1%
- Manual rollback capability within 30 minutes
- User notification if rollback affects active sessions

---

## 23. SOP-022: Traceability Matrix Maintenance

### 23.1 Purpose
Maintain bidirectional traceability between MDR requirements, design inputs, design outputs, verification, and validation.

### 23.2 Traceability Structure

```
MDR GSPR → Design Input → Design Output → Verification Method → Verification Evidence → Validation Evidence
```

### 23.3 Matrix Columns
| GSPR ID | GSPR Text | Design Input ID | SRS Section | Design Output ID | Arch/Detail Design | Test Protocol ID | Test Result | Validation Method | Val. Evidence |
|---|---|---|---|---|---|---|---|---|---|
| GSPR 1 | Risk management | DI-SAF-001 | §4.1 | DO-ARCH-003 | §3.2 | TP-SYS-042 | Pass | Risk Mgmt Report | RM-001 |

### 23.4 Maintenance
- Updated after every design change (SOP-009)
- Reviewed at each design review
- Verified for completeness before release
- Audit trail maintained for all changes

---

## 24. SOP-023: Risk Management Integration

### 24.1 Purpose
Ensure risk management is integrated throughout the QMS and device lifecycle.

### 24.2 Integration Points

| QMS Process | Risk Management Activity | Document Reference |
|---|---|---|
| Design Planning | Identify initial hazards; define safety requirements | Risk Management Plan |
| Design Inputs | Safety requirements from risk analysis become design inputs | Risk Analysis Table |
| Design Review | Verify risk controls are implemented in design | Design Review Checklist |
| Design Verification | Verify risk control effectiveness | Test Protocols |
| Design Validation | Validate risk controls in real-world use | Usability Test Report |
| Design Changes | Assess safety impact of all changes | Change Request Form |
| Complaint Handling | Evaluate complaints against known risks | Complaint Log |
| Vigilance | Report serious incidents; update risk file | Vigilance Log |
| PMS | Monitor risk control effectiveness in field | PMS Report |
| CAPA | Root cause analysis includes risk reassessment | CAPA Log |
| Internal Audit | Verify risk management process effectiveness | Audit Findings |

### 24.3 Risk Management Review Schedule
- **Continuous:** All design changes assessed for risk impact
- **Quarterly:** Review PMS data for emerging risks
- **Annually:** Full Risk Management File review (minimum)
- **Triggered:** Serious incident, NB finding, or significant design change

---

*Document Control*  
**Next Review Date:** [12 months from approval]  
**Distribution:** QMS Master (controlled), Technical Documentation Dossier, All Department Heads  
**Retention:** Device lifetime + 10 years
