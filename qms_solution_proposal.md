# QMS Digital Process Solution (Tailored Draft)

This draft maps the current QMS structure/functionality and a proposed digital process
solution with AI-enabled decision support and a clear operating model.

## System Diagram

```mermaid
flowchart LR
  %% Current-state QMS
  subgraph ASIS["Current QMS Structure (As-Is)"]
    C_GOV["QMS Governance<br/>Policies + SOP ownership"]
    C_DOC["Document Control<br/>SharePoint + templates"]
    C_EVT["Quality Event Intake<br/>Email + manual forms"]
    C_CASE["Deviation/CAPA/Change<br/>Spreadsheet routing"]
    C_APV["Approvals<br/>Email + wet signatures"]
    C_TRN["Training<br/>LMS + manual impact checks"]
    C_AUD["Audits<br/>Shared evidence folders"]
    C_DAT["KPI Reporting<br/>Manual extracts + lagging metrics"]
    C_SRC["Source Systems<br/>ERP, MES, LIMS, PLM (siloed)"]
  end
  %% Target-state digital QMS
  subgraph TOBE["Proposed Digital Process QMS (To-Be)"]
    P_GOV["Compliance + Governance Layer<br/>Part 11, Annex 11, ALCOA+"]
    P_ORC["Process Orchestration Layer<br/>BPMN workflows + SLA timers"]
    P_DMS["Controlled Content Service<br/>Version control + e-signatures"]
    P_EQM["Unified eQMS Case Hub<br/>Deviation, CAPA, Change, Complaint"]
    P_INT["Integration Hub<br/>APIs + event streaming"]
    P_DAT["Quality Data Platform<br/>Canonical model + traceability graph"]
    P_AI["AI Quality Copilot<br/>NLP triage + risk scoring + draft actions"]
    P_TRN["Training Impact Automation<br/>Role mapping + auto assignment"]
    P_AUD["Continuous Audit Readiness<br/>Evidence graph + control checks"]
    P_DSH["Quality Cockpit<br/>Real-time KPIs + predictive alerts"]
  end
  %% Existing functional flow
  C_GOV --> C_DOC
  C_DOC --> C_EVT
  C_EVT --> C_CASE
  C_APV --> C_CASE
  C_CASE --> C_TRN
  C_CASE --> C_AUD
  C_CASE --> C_DAT
  C_SRC --> C_DAT
  %% Proposed functional flow
  P_GOV --> P_ORC
  P_ORC --> P_DMS
  P_ORC --> P_EQM
  P_INT --> P_DAT
  P_DMS --> P_DAT
  P_EQM --> P_DAT
  P_EQM --> P_AI
  P_AI -->|recommended controls| P_EQM
  P_EQM --> P_TRN
  P_EQM --> P_AUD
  P_DAT --> P_DSH
  P_AI -->|predictive signals| P_DSH
  P_DSH -->|closed-loop actions| P_ORC
  %% Migration mapping
  C_GOV -. digitize governance controls .-> P_GOV
  C_DOC -. move to controlled content lifecycle .-> P_DMS
  C_EVT -. standardize event taxonomy .-> P_EQM
  C_CASE -. convert workflow templates .-> P_ORC
  C_APV -. replace email approvals with e-sign .-> P_ORC
  C_TRN -. automate training impact .-> P_TRN
  C_AUD -. always-on evidence trail .-> P_AUD
  C_DAT -. unify quality model and KPI feed .-> P_DAT
  C_SRC -. API/event integration .-> P_INT
  classDef current fill:#FCE9CF,stroke:#A86A00,stroke-width:1px,color:#1F1F1F;
  classDef target fill:#DDF4E5,stroke:#1E7A45,stroke-width:1px,color:#1F1F1F;
  classDef platform fill:#DDEBFF,stroke:#245EA8,stroke-width:1px,color:#1F1F1F;
  classDef ai fill:#FFE3C4,stroke:#B65E00,stroke-width:1px,color:#1F1F1F;
  classDef governance fill:#F2DEFF,stroke:#7A2B9A,stroke-width:1px,color:#1F1F1F;
  class C_GOV,C_DOC,C_EVT,C_CASE,C_APV,C_TRN,C_AUD,C_DAT,C_SRC current;
  class P_ORC,P_DMS,P_EQM,P_TRN,P_AUD target;
  class P_INT,P_DAT,P_DSH platform;
  class P_AI ai;
  class P_GOV governance;
```

## RACI Overlay

| Process | Responsible (R) | Accountable (A) | Consulted (C) | Informed (I) |
|---|---|---|---|---|
| Deviation intake and triage | Quality Ops | Head of Quality | Manufacturing | QA Systems |
| CAPA planning and closure | Process Owner | Head of Quality | Regulatory | Data and AI |
| Change control workflow | Change Coordinator | Quality Governance | IT Validation | Site Ops |
| Training impact assignment | Training Lead | Quality Governance | HR | Process Owner |
| Audit evidence readiness | Audit Lead | Head of Quality | All Functions | QA Systems |
| AI recommendation approval | Quality Ops | Quality Governance | Data Science | Regulatory |
| KPI and risk signal governance | Quality Analytics | Head of Quality | Site Leadership | Quality Ops |

## Rollout Waves

1. Wave 1 (8-12 weeks): unify taxonomy and digitize deviation/CAPA/change workflows.
2. Wave 2 (6-10 weeks): connect ERP/MES/LIMS and establish canonical quality data model.
3. Wave 3 (6-8 weeks): deploy AI triage, risk scoring, and recommendation governance.
4. Wave 4 (4-6 weeks): scale predictive cockpit, control monitoring, and continuous improvement automation.


## Target KPI Outcomes

- Deviation triage time: reduce by 40 percent
- CAPA cycle time: reduce by 25 percent
- On-time training completion after change: increase to 98 percent
- Audit evidence retrieval time: reduce by 60 percent
- Recurrence rate for high-risk deviations: reduce by 30 percent


## How Target Outcomes Are Measured

| Domain | Metric | Measurement Formula | Data Source | Cadence | Target | Patient Safety Link |
|---|---|---|---|---|---|---|
| Patient Safety | Safety review coverage for high-risk cases | (# high-risk cases with documented AI plus human safety review / total high-risk cases) x 100 | eQMS case records + PV safety system | Weekly | >=99% | Prevents unsupervised AI decisions for patient-impacting events |
| Patient Safety | Critical escalation SLA attainment | (# critical quality events escalated within SLA / total critical events) x 100 | Workflow timestamps | Daily | >=98% | Shortens time to containment and clinical risk mitigation |
| Usage | Weekly active quality users | Count of unique users executing quality workflows per week | Identity + workflow logs | Weekly | +15% in first 90 days | Higher adoption improves consistency of safety controls |
| Usage | Digital workflow completion rate | (# cases completed in orchestrated workflow / total cases) x 100 | Workflow engine | Weekly | >=95% | Reduces off-system workarounds that hide safety risk |
| Usage | AI recommendation acceptance with rationale | (# accepted AI recommendations with reviewer rationale / total AI recommendations) x 100 | AI decision logs | Weekly | Track trend, no forced target | Ensures AI remains decision support, not autonomous control |
| ESG | Paperless quality record rate | (# records fully digital and e-signed / total quality records) x 100 | DMS + e-signature logs | Monthly | >=90% by wave 3 | Improves traceability while reducing paper-intensive processes |
| ESG | Deviation rework reduction | ((baseline rework hours - current rework hours) / baseline rework hours) x 100 | Manufacturing + quality logs | Monthly | >=20% reduction | Lower rework reduces process instability and quality drift |
| ESG | Investigation cycle energy intensity | kWh consumed per completed investigation | Site utility + process telemetry | Quarterly | Downward trend | Supports sustainable operations without compromising quality |
| Verifiability | End-to-end traceability completeness | (# cases with linked source data, model output, reviewer decision, and CAPA action / total cases) x 100 | Quality data platform | Weekly | >=98% | Enables root-cause reconstruction for safety investigations |
| Verifiability | Model output reproducibility | (# sampled inferences reproducible within tolerance / total sampled inferences) x 100 | Model registry + replay harness | Weekly | >=99% | Prevents non-deterministic safety decisions |
| Verifiability | Backward compatibility of model updates | (# previously-correct cases still correct after update / # previously-correct cases) x 100, by risk class | Frozen evaluation set + model registry | Per model or prompt update | Threshold per risk class; stricter for patient-safety classes | Prevents accuracy-only updates from silently degrading human-AI team performance |
| Compliance | Part 11 / Annex 11 control pass rate | (# required controls passing automated checks / total required controls) x 100 | Compliance control monitor | Weekly | 100% | Maintains regulatory integrity of quality decisions |
| Compliance | ALCOA+ data-integrity exception rate | (# ALCOA+ exceptions / total quality records) x 100 | Audit trail analyzer | Weekly | <0.5% | Protects evidentiary quality for patient-impacting decisions |

## Usage Outcomes

- Weekly active quality users and digital workflow completion rate by site and function
- AI recommendation usage distribution by process type and severity class
- Override rates segmented by role with mandatory rationale capture
- Time-to-first-action after AI triage versus manual baseline


## ESG Outcomes

- Paperless quality record adoption and paper reduction trend
- Deviation rework hour reduction and right-first-time improvement
- Investigation cycle energy intensity and compute utilization trend
- Supplier quality interaction digitalization rate (fewer manual exchanges)


## Verifiability and Compliance Assessments

| Assessment Area | Verification Method | Evidence | Cadence | Gate |
|---|---|---|---|---|
| GxP impact classification | Every AI-enabled workflow has documented GxP impact category | Control owner attestation + QA review | At release and at each major change | Block release if missing |
| Computer software assurance (CSA) | Risk-based validation protocol with objective evidence | Validation package in controlled repository | Before production and per change request | Block release if failed |
| Human oversight enforcement | No autonomous closure for patient-safety relevant records | Workflow rule tests + periodic audit samples | Continuous | Auto-escalate any violation |
| Audit trail integrity | Immutable logs for data access, model calls, approvals, overrides | Automated integrity checks | Daily | Critical incident if tampering detected |
| Model change control | Approved change ticket, validation evidence, rollback plan | Change advisory board record | Per model or prompt update | Reject deployment if incomplete |
| Bias and performance drift | Defined thresholds by case class and severity | Monitoring dashboard + periodic challenge tests | Weekly + monthly deep dive | Freeze model if threshold breached |

## AI Regulator Stress-Test Hardening

| Hardening Area | Implementation Pattern | Anticipated Regulator Question | Evidence Package | Enforcement Rule |
|---|---|---|---|---|
| Full-stack inventory with risk tags | Maintain a live inventory for every service, model endpoint, integration, queue, database, and vendor dependency. Record GxP impact, data class, risk tier, owner, and control owner. | How do you know no hidden component bypasses controls? | Versioned system inventory export with owner and control-owner attestations. | Release gate fails if any high-risk component is missing owner, control owner, or risk label. |
| Control-to-implementation graph | Map each policy control to workflow rules, code checks, telemetry, and evidence artifacts using deterministic control IDs. | Can you prove controls are implemented and monitored, not only documented? | Control matrix with policy links, implementation refs, telemetry refs, and evidence paths. | Promotion is blocked if policy, implementation, telemetry, or evidence link is missing. |
| Signed release evidence bundle | Generate a signed package per release containing commit SHAs, model and prompt versions, gate results, approvals, exceptions, SBOM, and provenance references. | Show complete evidence for the exact production release. | Signed release manifest, checksums, and immutable artifact references. | Release promotion is blocked if signature or manifest completeness validation fails. |
| Decision reproducibility harness | Replay sampled recommendations with version-pinned model and retrieval context to verify deterministic behavior within tolerance bounds. | Can you reproduce this decision and explain differences? | Replay report with case ID, input hash, output hash, tolerance, and pass or fail status. | Weekly reproducibility pass rate must meet threshold by risk class. |
| Prompt and model change control | Treat prompt and model updates as controlled quality changes requiring risk assessment, validation protocol, rollback plan, and accountable signoff. | How are prompt and model changes governed under quality management? | Change ticket package with validation evidence, approval chain, and rollback simulation. | Merge fails when required change-control metadata or approvals are missing. |
| Adversarial and abuse-case testing | Run scheduled test suites for prompt injection, unsafe output patterns, citation poisoning, and context-boundary failures. | How do you prove resilience to misuse and hostile inputs? | Adversarial test matrix, failure trends, and corrective-action records. | Critical adversarial failures block release until corrective actions are verified. |
| Immutable lineage and rapid reconstruction | Capture tamper-evident lineage linking inputs, retrieval traces, model outputs, reviewer decisions, and final workflow actions. | Can you reconstruct a safety-critical decision quickly for investigators? | Cryptographically chained event logs with reconstruction report and retrieval timings. | Investigation packet generation must complete within defined service-level objective. |

## Anticipated AI-Assisted Regulatory Challenges and Prepared Answers

| Anticipated AI-Assisted Regulatory Challenge | Prepared Response | Demonstrable Artifact |
|---|---|---|
| Show all AI-relevant systems and data paths across the enterprise stack. | Provide the full-stack inventory with risk tags, ownership, and GxP impact classes. | Inventory register plus ownership attestations and dependency export. |
| Prove each required control is enforced at runtime. | Use the control-to-implementation graph linking policy to code, telemetry, and evidence artifacts. | Control matrix with current status per control ID. |
| Produce complete evidence for this release. | Deliver the signed release evidence bundle with manifest, checksums, and traceable references. | Signed release dossier generated from CI promotion stage. |
| Replay one historical recommendation and confirm consistency. | Run the reproducibility harness for the selected case and provide tolerance-based comparison output. | Replay report including hashes, score deltas, and pass or fail verdict. |
| Explain how prompt and model updates are controlled. | Show change-control records with risk assessment, validation evidence, rollback plan, and approvals. | Model and prompt change package with full audit trail. |
| Demonstrate protection against misuse and adversarial manipulation. | Provide scheduled adversarial testing results and corrective-action evidence. | Adversarial suite run history and remediation tracking. |
| Reconstruct this case end-to-end for investigation. | Use immutable lineage logs to generate a complete chronology from input to final action. | Investigator packet with timestamps, actor IDs, model versions, and citation refs. |

## Release Evidence Bundle Minimum Fields

Minimum signed release evidence bundle fields:

- release_id and release timestamp
- source commit SHAs and build run IDs
- model version and prompt version identifiers
- SBOM reference and provenance reference
- validation summary and gate verdicts
- approval records and exception records
- checksum manifest and signing certificate reference


## Strict P0 Launch Release Gates (QMS Resume Reviewer)

| Gate ID | P0 Launch Blocker | Required Evidence | Enforcement Point | Fail-Closed Action |
|---|---|---|---|---|
| RG-02 | Control-to-implementation runtime coverage | Control matrix linking policy IDs to code checks, telemetry, and evidence paths | CI promotion gate | Block release when any required control link is missing or stale |
| RG-03 | Signed release evidence bundle | Signed manifest with commit SHAs, model and prompt versions, SBOM, provenance, approvals, and checksums | Release packaging gate | Block release when signature validation or manifest completeness fails |
| RG-04 | High-risk human review enforcement | Reviewer sign-off records for all high-risk recommendations and overrides | Runtime workflow gate | Prevent case closure and raise escalation when sign-off is missing |
| RG-05 | Prompt and model change control | Change ticket with risk assessment, validation evidence, rollback plan, and approvals | Merge and deploy gate | Reject merge and deployment for unapproved prompt or model changes |
| RG-08 | Immutable lineage and reconstruction readiness | Tamper-evident lineage logs and successful investigator packet generation report | Pre-production operational readiness gate | Block release when end-to-end reconstruction service-level objective is unmet |

## P1 Post-Launch Enforcement Gates (Marked)

| Gate ID | P1 Post-Launch Enforcement | Required Evidence | Enforcement Point | Post-Launch Rule |
|---|---|---|---|---|
| RG-01 | Inventory and ownership completeness | Full-stack inventory export with risk labels, owner, and control owner | CI pre-release gate | Enable within 30 days after launch; block next release if unresolved |
| RG-06 | Decision reproducibility threshold | Replay harness report with case IDs, input and output hashes, tolerance, and verdict | Weekly reliability gate | Enable within 30 days after launch; block next release if unresolved |
| RG-07 | Adversarial misuse resilience | Adversarial suite run log with failure severity and corrective action evidence | Security quality gate | Enable within 45 days after launch; block next release if unresolved |
| RG-09 | Backward compatibility of model updates | Compatibility report showing newly introduced errors on previously-correct cases, segmented by risk class, plus reviewer acceptance-rate delta after rollout | Model update gate + post-rollout monitoring | Enable within 30 days after launch; block next model update if compatibility threshold is breached without documented justification |

## Full Regulatory Gate Catalog (Tiered Reference)

| Gate ID | Launch Tier | Regulatory Gate | Required Evidence | Enforcement Point | Enforcement Outcome |
|---|---|---|---|---|---|
| RG-01 | P1 Post-Launch | Inventory and ownership completeness | Full-stack inventory export with risk labels, owner, and control owner | CI pre-release gate | Do not block initial launch; Enable within 30 days after launch; block next release if unresolved |
| RG-02 | P0 Launch Blocker | Control-to-implementation runtime coverage | Control matrix linking policy IDs to code checks, telemetry, and evidence paths | CI promotion gate | Block release when any required control link is missing or stale |
| RG-03 | P0 Launch Blocker | Signed release evidence bundle | Signed manifest with commit SHAs, model and prompt versions, SBOM, provenance, approvals, and checksums | Release packaging gate | Block release when signature validation or manifest completeness fails |
| RG-04 | P0 Launch Blocker | High-risk human review enforcement | Reviewer sign-off records for all high-risk recommendations and overrides | Runtime workflow gate | Prevent case closure and raise escalation when sign-off is missing |
| RG-05 | P0 Launch Blocker | Prompt and model change control | Change ticket with risk assessment, validation evidence, rollback plan, and approvals | Merge and deploy gate | Reject merge and deployment for unapproved prompt or model changes |
| RG-06 | P1 Post-Launch | Decision reproducibility threshold | Replay harness report with case IDs, input and output hashes, tolerance, and verdict | Weekly reliability gate | Do not block initial launch; Enable within 30 days after launch; block next release if unresolved |
| RG-07 | P1 Post-Launch | Adversarial misuse resilience | Adversarial suite run log with failure severity and corrective action evidence | Security quality gate | Do not block initial launch; Enable within 45 days after launch; block next release if unresolved |
| RG-08 | P0 Launch Blocker | Immutable lineage and reconstruction readiness | Tamper-evident lineage logs and successful investigator packet generation report | Pre-production operational readiness gate | Block release when end-to-end reconstruction service-level objective is unmet |
| RG-09 | P1 Post-Launch | Backward compatibility of model updates | Compatibility report showing newly introduced errors on previously-correct cases, segmented by risk class, plus reviewer acceptance-rate delta after rollout | Model update gate + post-rollout monitoring | Do not block initial launch; Enable within 30 days after launch; block next model update if compatibility threshold is breached without documented justification |

## Applied Regulatory Gate Implementation for QMS Resume Reviewer

| QMS Resume Reviewer Surface | Applied Gates | Applied Implementation Pattern | Launch Tier | User Burden Profile |
|---|---|---|---|---|
| Case intake and triage (launch baseline) | RG-02 | Register each workflow, queue, and dependency in inventory and map policy controls to enforcement checks before enabling route | P0 Launch Blocker | No manual user input; generated from configuration and workflow metadata |
| Case intake and triage (post-launch hardening) | RG-01 | Backfill and continuously reconcile full-stack inventory ownership metadata for all non-critical components | P1 Post-Launch | No manual user input; generated from configuration and workflow metadata |
| AI recommendation generation | RG-04, RG-08 | Capture model version, prompt version, retrieval trace, output, and actor context in immutable lineage for every recommendation | P0 Launch Blocker | No extra steps for normal use; automatic capture |
| High-risk recommendation approval | RG-04 | Require accountable reviewer sign-off and rationale before any patient-impacting action can proceed | P0 Launch Blocker | One mandatory rationale step for high-risk actions only |
| Prompt and model update workflow (launch baseline) | RG-05 | Enforce approved change ticket with risk assessment, validation protocol, rollback plan, and accountable approvals before merge | P0 Launch Blocker | No operator burden; engineering workflow gate |
| Prompt and model update workflow (post-launch hardening) | RG-06, RG-07, RG-09 | Enable scheduled reproducibility replay, adversarial misuse suite with corrective-action tracking, and backward-compatibility scoring against the prior model version | P1 Post-Launch | No operator burden; engineering workflow gate |
| Post-update reviewer trust monitoring | RG-09 | Monitor reviewer acceptance and override rates per risk class after each model update to detect mental-model breakage that aggregate accuracy metrics would hide | P1 Post-Launch | No operator burden; derived from existing decision logs |
| Release and deployment | RG-03 | Generate signed release evidence bundle and validate checksum manifest before environment promotion | P0 Launch Blocker | No operator burden; CI packaging step |
| Investigation and regulator response | RG-08 | Generate investigator packet from immutable lineage with timestamps, actor IDs, citations, and final disposition | P0 Launch Blocker | One-click export for reviewer and audit leads |

## Human-AI Compatibility as a Release Criterion (RG-09)

Accuracy-only validation of model updates is insufficient in a human-in-the-loop
quality system. Empirical work on human-AI teams shows that **an update which
improves a model's aggregate accuracy can still degrade the performance of the
human-AI team**, because reviewers build a mental model of where the AI is
reliable and where it fails. When an update shifts the failure boundary, prior
reviewer intuition becomes miscalibrated — reviewers may over-trust newly-wrong
outputs or waste effort re-checking newly-correct ones.

Reference: Bansal, G., Nushi, B., Kamar, E., Weld, D. S., Lasecki, W. S., and
Horvitz, E. "Updates in Human-AI Teams: Understanding and Addressing the
Performance/Compatibility Tradeoff." *Proceedings of the AAAI Conference on
Artificial Intelligence*, 33(01), 2429-2437, 2019. See also "A Case for Backward
Compatibility for Human-AI Teams," arXiv:1906.01148. Their results across three
high-stakes classification domains (recidivism prediction, in-hospital mortality,
credit risk) show that standard ML training does not inherently produce
compatible updates, and that a retraining objective penalizing *newly introduced*
errors allows an explicit, tunable performance/compatibility tradeoff.

This matters directly here: `RG-05` verifies a model change was *authorized* and
`RG-06` verifies it is *reproducible*, but neither detects compatibility
regression. A model update could pass both gates and still reduce quality-review
accuracy in production.

### RG-09 Measurement Definition

| Metric | Formula | Threshold Guidance |
|---|---|---|
| Backward compatibility score | (# cases previously correct that remain correct under the new model version / # cases previously correct) x 100 | Define per risk class; high-risk case classes warrant a stricter floor than low-risk triage |
| Newly introduced error rate | (# cases previously correct that are now incorrect / total evaluated cases) x 100 | Any non-zero value affecting patient-safety-relevant case classes requires documented justification and reviewer notification |
| Reviewer acceptance-rate delta | (post-update acceptance rate - pre-update acceptance rate), segmented by risk class and role | Sharp movement in either direction is a signal of mental-model breakage, not just changed model quality |
| Compatibility-adjusted rollout stage | Percentage of traffic on new model version, gated by compatibility score holding above threshold | Staged rollout with automatic hold if compatibility degrades during ramp |

### RG-09 Enforcement Pattern

1. Maintain a **frozen evaluation set** of previously-adjudicated cases with recorded
   prior-model outputs and reviewer decisions, versioned alongside the model registry.
2. On every candidate model or prompt update, compute the compatibility score and
   newly-introduced-error rate against that frozen set, segmented by risk class.
3. Attach the compatibility report to the `RG-05` change ticket as required evidence —
   an update that improves aggregate accuracy while breaching the compatibility floor
   for a high-risk class requires explicit, documented sign-off rather than silent
   promotion.
4. After rollout, monitor reviewer acceptance and override rates (already captured in
   the KPI table as "AI recommendation acceptance with rationale") for shifts that
   indicate reviewers are recalibrating against changed failure modes.
5. Where compatibility and accuracy genuinely conflict, treat the tradeoff as a
   documented quality decision with accountable ownership — not an engineering
   default. Where feasible, apply a retraining objective that penalizes new errors,
   per Bansal et al., to reduce the severity of the tradeoff.

### Notification Requirement

When an approved update knowingly breaks compatibility for a case class, reviewers
working that class receive a targeted change notification describing what shifted,
so mental-model recalibration is deliberate rather than discovered through error.
This is a training-impact event and routes through the existing training impact
automation path.

## Extension: Quality Governance for Organ Virtualization / In-Silico Model Programs

Organ virtualization programs (organ-on-chip digital twins, physiologically-based
pharmacokinetic/pharmacodynamic simulation, in-silico toxicology and efficacy
prediction) introduce a class of AI/ML-driven artifacts that sit upstream of, and
increasingly substitute for, traditional wet-lab and animal studies. The same
control patterns defined above apply directly, with a few domain-specific
extensions:

| Extension Area | What Changes for Virtualized Organ Models | Applied Control Pattern |
|---|---|---|
| Model-to-biology traceability | Every virtual organ model instance must trace back to the specific tissue/cell source data, assay protocol version, and calibration dataset used to fit it | Immutable lineage graph (RG-08) extended to include biological source metadata, not just software/version metadata |
| Simulation reproducibility | A virtualized organ prediction (e.g., predicted hepatotoxicity response) must be reproducible within defined tolerance when replayed with the same model version and input parameters | Decision reproducibility harness (RG-06) applied to simulation outputs, with biological tolerance bands defined per endpoint |
| Cross-validation against wet-lab ground truth | Virtual model predictions require a documented, ongoing correlation study against real organ-on-chip or animal/clinical data until in-silico-only qualification is achieved for a given use case | New verification gate: minimum correlation coefficient and drift threshold per model class, reviewed on a fixed cadence |
| Model qualification tiering | Not all virtualized organ models carry the same regulatory weight; a model used for internal candidate triage carries lower risk than one submitted as supporting evidence in an IND/NDA package | GxP impact classification (existing control) extended with an explicit "regulatory submission use" flag that escalates required evidence |
| Change control for biological calibration data | Updating the training/calibration dataset for a virtual organ model (new donor tissue batch, new assay run) is treated as a model change requiring the same risk assessment and validation as a code or prompt change | Prompt and model change control (RG-05) extended to cover calibration-data updates, not only code/weights |

### ESG Amplification from Virtualization

Organ virtualization is one of the few AI initiatives where the quality-governance
story and the ESG story reinforce each other directly, rather than trading off:

- **Reduced animal use (3Rs: Replace, Reduce, Refine)** — every study substituted or
  reduced by a qualified virtual organ model is a concrete, auditable ESG metric,
  not just a compliance checkbox. This can be tracked alongside the existing ESG
  KPI table as: `(# studies replaced or reduced by qualified in-silico models /
  total comparable studies) x 100`, reported quarterly.
- **Compute-for-biology tradeoff visibility** — the existing "Investigation cycle
  energy intensity" KPI extends naturally to "Simulation compute intensity per
  qualified prediction," keeping the sustainability tradeoff of large-scale
  simulation visible rather than hidden behind a general AI-efficiency narrative.
- **Faster, lower-waste candidate triage** — early-stage virtual screening reduces
  reagent, animal, and manufacturing waste associated with candidates that would
  otherwise have failed later in the pipeline, tying directly into the existing
  "Deviation rework reduction" and right-first-time framing.

## Patient Safety Guardrails

- AI remains decision support, never autonomous closure for patient-impacting records
- High-risk cases require documented human review with accountable sign-off
- Any safety or compliance control failure triggers release hold and escalation
- Full decision lineage is retained for inspection and post-market investigation

## Notes

- This is designed as a design-ready blueprint you can adapt to your exact tools.
- If you share your current vendor stack, labels can be swapped directly in one pass.
