# SaMD EU MDR Compliance Agent

## Scope
This agent operates from `agents/samd-compliance-eu/`. It is scoped to this directory but can access the full repository.

## Purpose
Transform wellness applications into compliant Software as a Medical Device (SaMD) under EU MDR 2017/745.

## Current Focus Device
- **App:** Glucose fluctuation monitoring + personalised weight-loss insights
- **Market:** EU (MDR)
- **Classification:** Class IIa (Rule 11)
- **Standards:** ISO 13485, IEC 62304, ISO 14971, IEC 62366-1

## Skills
- `samd-eu-mdr` — Primary skill for MDR compliance, classification, documentation templates, QMS gaps, clinical evaluation, and EUDAMED registration.

## Jobs
- `jobs/compliance-audit.md` — Run a full MDR readiness gap analysis and generate a compliance roadmap.

## Outputs
Generated documents are written to `agents/samd-compliance-eu/output/` by default. The agent can also write to root-level `reports/` if instructed.

## Interaction Model
This agent is triggered manually on-demand. It has no scheduled cron job by default, but `agent-job/CRONS.json` can be updated to add periodic compliance audits.
