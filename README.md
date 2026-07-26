# QMS AI System Portfolio (Private)

This repository packages my independently developed artifacts for an AI-enabled Quality Management System (QMS) strategy, architecture, and governance design — built as a design exercise for regulated (GxP) biotech/pharma environments, including patient-safety, compliance, and ESG considerations.

## Scope

This package includes:

1. QMS digital process system diagrams (as-is and to-be architecture).
2. A full solution proposal covering KPI, compliance, patient-safety, and ESG outcomes.
3. A regulatory-gate framework for AI-enabled quality workflows (P0 launch blockers, P1 post-launch hardening).
4. A hardened reference architecture addressing common AI-system trust gaps (provenance, reproducibility, human-in-the-loop enforcement).
5. A human-AI compatibility release criterion (RG-09) addressing the empirically documented performance/compatibility tradeoff in human-AI teams, so accuracy-only model updates cannot silently degrade reviewer decision quality.
6. An extension applying the same control patterns to organ virtualization / in-silico model programs (model-to-biology traceability, simulation reproducibility, wet-lab cross-validation, and ESG amplification via reduced animal use).
7. A **clinical deployment assessment instrument and fail-closed scoring engine** for evaluating an AI-enabled QMS that is already running in production, rather than reviewing design intent.

## Key Artifacts

1. [qms_solution_proposal.html](qms_solution_proposal.html)
2. [qms_solution_proposal.md](qms_solution_proposal.md)
3. [qms_system_diagram.md](qms_system_diagram.md)
4. [qms_solution_diagram.mmd](qms_solution_diagram.mmd)
5. [qms_trust_hardened_system_diagram.md](qms_trust_hardened_system_diagram.md)
6. [clinical_deployment_assessment.md](clinical_deployment_assessment.md) — reviewer instrument
7. [deployment_assessment.py](deployment_assessment.py) — instrument generator and scoring CLI

## Assessing a Live Deployment

The design artifacts above describe what a compliant system should look like. `deployment_assessment.py` is the counterpart used against a system that is actually running: a 19-item evidence-gathering instrument plus a scoring engine that refuses to return a clean result when evidence is absent.

```bash
# Generate the reviewer instrument (markdown + HTML)
python3 deployment_assessment.py instrument

# Emit a blank response file for the reviewer to complete
python3 deployment_assessment.py template --out responses.json

# Score a completed assessment (exit code 1 if anything is unresolved)
python3 deployment_assessment.py score responses.json
python3 deployment_assessment.py score responses.json --json
```

Design properties:

1. **Fail-closed.** `not_assessed` is treated as unresolved, so an untouched template scores `BLOCKING_FINDINGS`, not a pass. Absence of evidence is never treated as evidence of control.
2. **Patient-safety items block individually.** Any single unresolved `patient_safety_critical` item forces a blocking verdict regardless of how the rest scores.
3. **Structural abuse is rejected.** Unknown item ids, malformed entries, missing response fields, and unjustified `not_applicable` claims all yield `INVALID_SUBMISSION` rather than quietly clearing an item.
4. **No approval language.** The cleanest possible verdict is `NO_BLOCKING_FINDINGS_IDENTIFIED`. The tool produces findings, never a compliance determination.
5. **Traceable to the gate model.** Each assessment item links to the RG-xx gates defined in the solution proposal, and tests enforce that those references resolve.
6. **Scoping out costs more than assessing.** `not_applicable` is permitted on only two items, and placeholder justifications such as `n/a` are rejected as `INVALID_SUBMISSION`.

### Threat model

The items are weighted toward **internal and unintentional** failure rather than external attack, because that is the dominant risk in a regulated internal deployment. The scenario the instrument is built around is a competent user, following procedure correctly, receiving a wrong answer with no signal that anything went wrong:

- **`DA-16` Use outside the validated envelope.** Production usage drifts to case types, products, or sites absent from the validation population, and the system answers anyway.
- **`DA-17` Silent truncation and incomplete input.** A long record is truncated or a source document fails to parse, and the reviewer sees output indistinguishable from a complete assessment.
- **`DA-18` Configuration drift.** Prompts, parameters, and thresholds are the artifacts people actually edit between releases; `DA-08` governs the model, `DA-18` governs everything around it.
- **`DA-19` Repeat submission and anchoring.** Only the accepted output is retained, so re-running an event until a milder result appears leaves no trace.

The first three block on their own. Adversarial resilience (`DA-14`) is deliberately scoped as `major`: it checks that misuse testing was performed and that open findings have an owner, and routes any confirmed patient-impacting defect to `DA-11`, which does block.

**This is an assessment aid, not a regulatory determination.** Interpretation and sign-off require qualified QA, regulatory, and clinical-safety personnel. It does not substitute for validated quality processes or applicable regulatory submissions.

## Outcome Summary

1. Designed an evidence-based maturity framework spanning AI readiness, safety/compliance, and security posture for regulated engineering stacks.
2. Identified and documented common trust-erosion drivers in AI-enabled systems: non-fail-closed release gates, provenance gaps, inconsistent compliance controls.
3. Defined a staged (30-60-90 style) trust-recovery and rollout roadmap with concrete KPI instrumentation.
4. Authored hardening patterns for fail-closed security gates, provenance/SBOM requirements, and safe change-control practices for AI/model updates.

## Technical Highlights

1. Python-based generation pipelines for architecture and proposal artifacts (Mermaid diagrams, structured markdown/HTML reports).
2. A methodology for source-level code/config analysis and evidence extraction to support AI/compliance/security maturity scoring.
3. CI/CD policy hardening design for supply-chain and vulnerability posture (fail-closed scanning, build provenance, signed release evidence).
4. Compliance-by-design control mapping (21 CFR Part 11, Annex 11, ALCOA+) tied to concrete implementation and telemetry evidence.

## Testing

```bash
python3 -m pytest -q
```

The suite covers artifact generation, patient-safety invariants of the governance model (treated as policy-as-code), and the deployment scoring engine's fail-closed behavior. It also guards that committed artifacts stay in sync with their generators.

## Notes

1. This is a personal, independently authored portfolio package. It does not reference or include any employer-specific systems, repositories, or findings — all examples and scans described here are presented generically as a demonstration of methodology and skill, not as an audit of any named organization.
2. Designed to be adapted directly to a specific company's tools and stack.
