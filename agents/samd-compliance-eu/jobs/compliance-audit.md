# Job: MDR Compliance Audit & Gap Analysis

## Objective
Conduct a comprehensive EU MDR readiness assessment for the glucose monitoring + weight-loss insights application. Produce a structured gap analysis report and a 12-month compliance roadmap.

## Context
The user has a wellness application that monitors glucose fluctuations and provides personalised insights for weight loss. They have:
- NO existing regulatory documentation
- NO QMS in place
- Target market: EU
- Goal: SaMD certification (CE marking)

## Tasks

### 1. Classification Confirmation
- Confirm Class IIa under MDR Annex VIII, Rule 11
- Document the classification justification with regulatory basis
- Flag any features that could trigger Class IIb or III reclassification

### 2. QMS Gap Analysis
- Assess current state against ISO 13485:2016 requirements
- Identify missing procedures, records, and controls
- Produce a priority-ranked gap remediation plan

### 3. Technical Documentation Roadmap
- List all Annex III documents required
- Estimate effort and assign priorities (Critical / High / Medium / Low)
- Identify which documents can be generated internally vs. requiring external support

### 4. Risk Management Foundation
- Identify top hazards for glucose monitoring lifestyle software
- Produce a preliminary Hazard Analysis table (ISO 14971)
- Define risk acceptance criteria

### 5. Clinical Evaluation Strategy
- Recommend clinical evidence route (Route A investigation vs. Route B literature + PMCF)
- Draft a Clinical Evaluation Plan outline
- Identify potential predicate devices or equivalent products

### 6. Standards & Guidance Mapping
- List all applicable harmonised standards and guidance documents
- Map each standard to the device lifecycle phases
- Identify gaps in current knowledge or implementation

### 7. Regulatory Timeline
- Produce a realistic 12-month roadmap from current state to CE marking
- Include Notified Body selection, audit windows, and EUDAMED milestones
- Highlight critical path items and parallelisable workstreams

## Output
Write a single comprehensive report to:
```
agents/samd-compliance-eu/output/YYYY-MM-DD-mdr-gap-analysis.md
```

Include:
- Executive Summary (1 page)
- Classification Justification
- Gap Analysis Matrix
- Risk Analysis (Top 10 Hazards)
- Clinical Evaluation Strategy
- 12-Month Roadmap (Gantt-style table)
- Next Actions (immediate 30-day priorities)

## Notes
- Be pragmatic. The user is a startup with no existing documentation.
- Prioritise the critical path to CE marking.
- Flag any areas where a qualified regulatory consultant or Notified Body pre-submission meeting is strongly recommended.
