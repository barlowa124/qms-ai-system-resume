"""Generate a tailored QMS current-vs-proposed diagram pack with RACI overlay.

Outputs:
- qms_solution_diagram.mmd
- qms_solution_proposal.md
- qms_solution_proposal.html
"""

from __future__ import annotations

from pathlib import Path


def metric_rows() -> list[tuple[str, str, str, str, str, str, str]]:
  return [
    (
      "Patient Safety",
      "Safety review coverage for high-risk cases",
      "(# high-risk cases with documented AI plus human safety review / total high-risk cases) x 100",
      "eQMS case records + PV safety system",
      "Weekly",
      ">=99%",
      "Prevents unsupervised AI decisions for patient-impacting events",
    ),
    (
      "Patient Safety",
      "Critical escalation SLA attainment",
      "(# critical quality events escalated within SLA / total critical events) x 100",
      "Workflow timestamps",
      "Daily",
      ">=98%",
      "Shortens time to containment and clinical risk mitigation",
    ),
    (
      "Usage",
      "Weekly active quality users",
      "Count of unique users executing quality workflows per week",
      "Identity + workflow logs",
      "Weekly",
      "+15% in first 90 days",
      "Higher adoption improves consistency of safety controls",
    ),
    (
      "Usage",
      "Digital workflow completion rate",
      "(# cases completed in orchestrated workflow / total cases) x 100",
      "Workflow engine",
      "Weekly",
      ">=95%",
      "Reduces off-system workarounds that hide safety risk",
    ),
    (
      "Usage",
      "AI recommendation acceptance with rationale",
      "(# accepted AI recommendations with reviewer rationale / total AI recommendations) x 100",
      "AI decision logs",
      "Weekly",
      "Track trend, no forced target",
      "Ensures AI remains decision support, not autonomous control",
    ),
    (
      "ESG",
      "Paperless quality record rate",
      "(# records fully digital and e-signed / total quality records) x 100",
      "DMS + e-signature logs",
      "Monthly",
      ">=90% by wave 3",
      "Improves traceability while reducing paper-intensive processes",
    ),
    (
      "ESG",
      "Deviation rework reduction",
      "((baseline rework hours - current rework hours) / baseline rework hours) x 100",
      "Manufacturing + quality logs",
      "Monthly",
      ">=20% reduction",
      "Lower rework reduces process instability and quality drift",
    ),
    (
      "ESG",
      "Investigation cycle energy intensity",
      "kWh consumed per completed investigation",
      "Site utility + process telemetry",
      "Quarterly",
      "Downward trend",
      "Supports sustainable operations without compromising quality",
    ),
    (
      "Verifiability",
      "End-to-end traceability completeness",
      "(# cases with linked source data, model output, reviewer decision, and CAPA action / total cases) x 100",
      "Quality data platform",
      "Weekly",
      ">=98%",
      "Enables root-cause reconstruction for safety investigations",
    ),
    (
      "Verifiability",
      "Model output reproducibility",
      "(# sampled inferences reproducible within tolerance / total sampled inferences) x 100",
      "Model registry + replay harness",
      "Weekly",
      ">=99%",
      "Prevents non-deterministic safety decisions",
    ),
    (
      "Compliance",
      "Part 11 / Annex 11 control pass rate",
      "(# required controls passing automated checks / total required controls) x 100",
      "Compliance control monitor",
      "Weekly",
      "100%",
      "Maintains regulatory integrity of quality decisions",
    ),
    (
      "Compliance",
      "ALCOA+ data-integrity exception rate",
      "(# ALCOA+ exceptions / total quality records) x 100",
      "Audit trail analyzer",
      "Weekly",
      "<0.5%",
      "Protects evidentiary quality for patient-impacting decisions",
    ),
  ]


def compliance_assessment_rows() -> list[tuple[str, str, str, str, str]]:
  return [
    (
      "GxP impact classification",
      "Every AI-enabled workflow has documented GxP impact category",
      "Control owner attestation + QA review",
      "At release and at each major change",
      "Block release if missing",
    ),
    (
      "Computer software assurance (CSA)",
      "Risk-based validation protocol with objective evidence",
      "Validation package in controlled repository",
      "Before production and per change request",
      "Block release if failed",
    ),
    (
      "Human oversight enforcement",
      "No autonomous closure for patient-safety relevant records",
      "Workflow rule tests + periodic audit samples",
      "Continuous",
      "Auto-escalate any violation",
    ),
    (
      "Audit trail integrity",
      "Immutable logs for data access, model calls, approvals, overrides",
      "Automated integrity checks",
      "Daily",
      "Critical incident if tampering detected",
    ),
    (
      "Model change control",
      "Approved change ticket, validation evidence, rollback plan",
      "Change advisory board record",
      "Per model or prompt update",
      "Reject deployment if incomplete",
    ),
    (
      "Bias and performance drift",
      "Defined thresholds by case class and severity",
      "Monitoring dashboard + periodic challenge tests",
      "Weekly + monthly deep dive",
      "Freeze model if threshold breached",
    ),
  ]


def ai_hardening_rows() -> list[tuple[str, str, str, str, str]]:
  return [
    (
      "Full-stack inventory with risk tags",
      "Maintain a live inventory for every service, model endpoint, integration, queue, database, and vendor dependency. Record GxP impact, data class, risk tier, owner, and control owner.",
      "How do you know no hidden component bypasses controls?",
      "Versioned system inventory export with owner and control-owner attestations.",
      "Release gate fails if any high-risk component is missing owner, control owner, or risk label.",
    ),
    (
      "Control-to-implementation graph",
      "Map each policy control to workflow rules, code checks, telemetry, and evidence artifacts using deterministic control IDs.",
      "Can you prove controls are implemented and monitored, not only documented?",
      "Control matrix with policy links, implementation refs, telemetry refs, and evidence paths.",
      "Promotion is blocked if policy, implementation, telemetry, or evidence link is missing.",
    ),
    (
      "Signed release evidence bundle",
      "Generate a signed package per release containing commit SHAs, model and prompt versions, gate results, approvals, exceptions, SBOM, and provenance references.",
      "Show complete evidence for the exact production release.",
      "Signed release manifest, checksums, and immutable artifact references.",
      "Release promotion is blocked if signature or manifest completeness validation fails.",
    ),
    (
      "Decision reproducibility harness",
      "Replay sampled recommendations with version-pinned model and retrieval context to verify deterministic behavior within tolerance bounds.",
      "Can you reproduce this decision and explain differences?",
      "Replay report with case ID, input hash, output hash, tolerance, and pass or fail status.",
      "Weekly reproducibility pass rate must meet threshold by risk class.",
    ),
    (
      "Prompt and model change control",
      "Treat prompt and model updates as controlled quality changes requiring risk assessment, validation protocol, rollback plan, and accountable signoff.",
      "How are prompt and model changes governed under quality management?",
      "Change ticket package with validation evidence, approval chain, and rollback simulation.",
      "Merge fails when required change-control metadata or approvals are missing.",
    ),
    (
      "Adversarial and abuse-case testing",
      "Run scheduled test suites for prompt injection, unsafe output patterns, citation poisoning, and context-boundary failures.",
      "How do you prove resilience to misuse and hostile inputs?",
      "Adversarial test matrix, failure trends, and corrective-action records.",
      "Critical adversarial failures block release until corrective actions are verified.",
    ),
    (
      "Immutable lineage and rapid reconstruction",
      "Capture tamper-evident lineage linking inputs, retrieval traces, model outputs, reviewer decisions, and final workflow actions.",
      "Can you reconstruct a safety-critical decision quickly for investigators?",
      "Cryptographically chained event logs with reconstruction report and retrieval timings.",
      "Investigation packet generation must complete within defined service-level objective.",
    ),
  ]


def regulator_answer_rows() -> list[tuple[str, str, str]]:
  return [
    (
      "Show all AI-relevant systems and data paths across the enterprise stack.",
      "Provide the full-stack inventory with risk tags, ownership, and GxP impact classes.",
      "Inventory register plus ownership attestations and dependency export.",
    ),
    (
      "Prove each required control is enforced at runtime.",
      "Use the control-to-implementation graph linking policy to code, telemetry, and evidence artifacts.",
      "Control matrix with current status per control ID.",
    ),
    (
      "Produce complete evidence for this release.",
      "Deliver the signed release evidence bundle with manifest, checksums, and traceable references.",
      "Signed release dossier generated from CI promotion stage.",
    ),
    (
      "Replay one historical recommendation and confirm consistency.",
      "Run the reproducibility harness for the selected case and provide tolerance-based comparison output.",
      "Replay report including hashes, score deltas, and pass or fail verdict.",
    ),
    (
      "Explain how prompt and model updates are controlled.",
      "Show change-control records with risk assessment, validation evidence, rollback plan, and approvals.",
      "Model and prompt change package with full audit trail.",
    ),
    (
      "Demonstrate protection against misuse and adversarial manipulation.",
      "Provide scheduled adversarial testing results and corrective-action evidence.",
      "Adversarial suite run history and remediation tracking.",
    ),
    (
      "Reconstruct this case end-to-end for investigation.",
      "Use immutable lineage logs to generate a complete chronology from input to final action.",
      "Investigator packet with timestamps, actor IDs, model versions, and citation refs.",
    ),
  ]


def release_gate_rows() -> list[tuple[str, str, str, str, str]]:
  return [
    (
      "RG-01",
      "Inventory and ownership completeness",
      "Full-stack inventory export with risk labels, owner, and control owner",
      "CI pre-release gate",
      "Block release when any high-risk component has missing metadata",
    ),
    (
      "RG-02",
      "Control-to-implementation runtime coverage",
      "Control matrix linking policy IDs to code checks, telemetry, and evidence paths",
      "CI promotion gate",
      "Block release when any required control link is missing or stale",
    ),
    (
      "RG-03",
      "Signed release evidence bundle",
      "Signed manifest with commit SHAs, model and prompt versions, SBOM, provenance, approvals, and checksums",
      "Release packaging gate",
      "Block release when signature validation or manifest completeness fails",
    ),
    (
      "RG-04",
      "High-risk human review enforcement",
      "Reviewer sign-off records for all high-risk recommendations and overrides",
      "Runtime workflow gate",
      "Prevent case closure and raise escalation when sign-off is missing",
    ),
    (
      "RG-05",
      "Prompt and model change control",
      "Change ticket with risk assessment, validation evidence, rollback plan, and approvals",
      "Merge and deploy gate",
      "Reject merge and deployment for unapproved prompt or model changes",
    ),
    (
      "RG-06",
      "Decision reproducibility threshold",
      "Replay harness report with case IDs, input and output hashes, tolerance, and verdict",
      "Weekly reliability gate",
      "Freeze promotion when reproducibility drops below risk-class threshold",
    ),
    (
      "RG-07",
      "Adversarial misuse resilience",
      "Adversarial suite run log with failure severity and corrective action evidence",
      "Security quality gate",
      "Block release on unresolved critical adversarial failures",
    ),
    (
      "RG-08",
      "Immutable lineage and reconstruction readiness",
      "Tamper-evident lineage logs and successful investigator packet generation report",
      "Pre-production operational readiness gate",
      "Block release when end-to-end reconstruction service-level objective is unmet",
    ),
  ]


def p0_launch_gate_ids() -> set[str]:
  # Strict launch blockers for first production cut.
  return {"RG-02", "RG-03", "RG-04", "RG-05", "RG-08"}


def p1_post_launch_windows() -> dict[str, str]:
  return {
    "RG-01": "Enable within 30 days after launch",
    "RG-06": "Enable within 30 days after launch",
    "RG-07": "Enable within 45 days after launch",
  }


def p0_launch_gate_rows() -> list[tuple[str, str, str, str, str]]:
  p0 = p0_launch_gate_ids()
  return [row for row in release_gate_rows() if row[0] in p0]


def p1_post_launch_gate_rows() -> list[tuple[str, str, str, str, str]]:
  p0 = p0_launch_gate_ids()
  return [row for row in release_gate_rows() if row[0] not in p0]


def applied_release_gate_rows() -> list[tuple[str, str, str, str, str]]:
  return [
    (
      "Case intake and triage (launch baseline)",
      "RG-02",
      "Register each workflow, queue, and dependency in inventory and map policy controls to enforcement checks before enabling route",
      "P0 Launch Blocker",
      "No manual user input; generated from configuration and workflow metadata",
    ),
    (
      "Case intake and triage (post-launch hardening)",
      "RG-01",
      "Backfill and continuously reconcile full-stack inventory ownership metadata for all non-critical components",
      "P1 Post-Launch",
      "No manual user input; generated from configuration and workflow metadata",
    ),
    (
      "AI recommendation generation",
      "RG-04, RG-08",
      "Capture model version, prompt version, retrieval trace, output, and actor context in immutable lineage for every recommendation",
      "P0 Launch Blocker",
      "No extra steps for normal use; automatic capture",
    ),
    (
      "High-risk recommendation approval",
      "RG-04",
      "Require accountable reviewer sign-off and rationale before any patient-impacting action can proceed",
      "P0 Launch Blocker",
      "One mandatory rationale step for high-risk actions only",
    ),
    (
      "Prompt and model update workflow (launch baseline)",
      "RG-05",
      "Enforce approved change ticket with risk assessment, validation protocol, rollback plan, and accountable approvals before merge",
      "P0 Launch Blocker",
      "No operator burden; engineering workflow gate",
    ),
    (
      "Prompt and model update workflow (post-launch hardening)",
      "RG-06, RG-07",
      "Enable scheduled reproducibility replay and adversarial misuse suite with corrective-action tracking",
      "P1 Post-Launch",
      "No operator burden; engineering workflow gate",
    ),
    (
      "Release and deployment",
      "RG-03",
      "Generate signed release evidence bundle and validate checksum manifest before environment promotion",
      "P0 Launch Blocker",
      "No operator burden; CI packaging step",
    ),
    (
      "Investigation and regulator response",
      "RG-08",
      "Generate investigator packet from immutable lineage with timestamps, actor IDs, citations, and final disposition",
      "P0 Launch Blocker",
      "One-click export for reviewer and audit leads",
    ),
  ]


def build_metric_framework_markdown() -> str:
  lines = []
  lines.append("| Domain | Metric | Measurement Formula | Data Source | Cadence | Target | Patient Safety Link |")
  lines.append("|---|---|---|---|---|---|---|")
  for domain, metric, formula, source, cadence, target, safety_link in metric_rows():
    lines.append(
      f"| {domain} | {metric} | {formula} | {source} | {cadence} | {target} | {safety_link} |"
    )
  return "\n".join(lines)


def build_compliance_assessment_markdown() -> str:
  lines = []
  lines.append("| Assessment Area | Verification Method | Evidence | Cadence | Gate |")
  lines.append("|---|---|---|---|---|")
  for area, method, evidence, cadence, gate in compliance_assessment_rows():
    lines.append(f"| {area} | {method} | {evidence} | {cadence} | {gate} |")
  return "\n".join(lines)


def build_ai_hardening_markdown() -> str:
  lines = []
  lines.append("| Hardening Area | Implementation Pattern | Anticipated Regulator Question | Evidence Package | Enforcement Rule |")
  lines.append("|---|---|---|---|---|")
  for area, implementation, question, evidence, enforcement in ai_hardening_rows():
    lines.append(
      f"| {area} | {implementation} | {question} | {evidence} | {enforcement} |"
    )
  return "\n".join(lines)


def build_regulator_answers_markdown() -> str:
  lines = []
  lines.append("| Anticipated AI-Assisted Regulatory Challenge | Prepared Response | Demonstrable Artifact |")
  lines.append("|---|---|---|")
  for challenge, response, artifact in regulator_answer_rows():
    lines.append(f"| {challenge} | {response} | {artifact} |")
  return "\n".join(lines)


def build_evidence_bundle_markdown() -> str:
  return """Minimum signed release evidence bundle fields:

- release_id and release timestamp
- source commit SHAs and build run IDs
- model version and prompt version identifiers
- SBOM reference and provenance reference
- validation summary and gate verdicts
- approval records and exception records
- checksum manifest and signing certificate reference
"""


def build_release_gate_checklist_markdown() -> str:
  lines = []
  lines.append("| Gate ID | Launch Tier | Regulatory Gate | Required Evidence | Enforcement Point | Enforcement Outcome |")
  lines.append("|---|---|---|---|---|---|")
  p0 = p0_launch_gate_ids()
  p1_windows = p1_post_launch_windows()
  for gate_id, gate_name, evidence, enforcement, fail_action in release_gate_rows():
    if gate_id in p0:
      tier = "P0 Launch Blocker"
      outcome = fail_action
    else:
      tier = "P1 Post-Launch"
      window = p1_windows.get(gate_id, "Enable in first post-launch hardening wave")
      outcome = f"Do not block initial launch; {window}; block next release if unresolved"
    lines.append(
      f"| {gate_id} | {tier} | {gate_name} | {evidence} | {enforcement} | {outcome} |"
    )
  return "\n".join(lines)


def build_p0_launch_gate_markdown() -> str:
  lines = []
  lines.append("| Gate ID | P0 Launch Blocker | Required Evidence | Enforcement Point | Fail-Closed Action |")
  lines.append("|---|---|---|---|---|")
  for gate_id, gate_name, evidence, enforcement, fail_action in p0_launch_gate_rows():
    lines.append(
      f"| {gate_id} | {gate_name} | {evidence} | {enforcement} | {fail_action} |"
    )
  return "\n".join(lines)


def build_p1_post_launch_gate_markdown() -> str:
  lines = []
  lines.append("| Gate ID | P1 Post-Launch Enforcement | Required Evidence | Enforcement Point | Post-Launch Rule |")
  lines.append("|---|---|---|---|---|")
  windows = p1_post_launch_windows()
  for gate_id, gate_name, evidence, enforcement, _ in p1_post_launch_gate_rows():
    window = windows.get(gate_id, "Enable in first post-launch hardening wave")
    lines.append(
      f"| {gate_id} | {gate_name} | {evidence} | {enforcement} | {window}; block next release if unresolved |"
    )
  return "\n".join(lines)


def build_applied_release_gate_markdown() -> str:
  lines = []
  lines.append("| QMS Resume Reviewer Surface | Applied Gates | Applied Implementation Pattern | Launch Tier | User Burden Profile |")
  lines.append("|---|---|---|---|---|")
  for surface, gates, implementation, tier, user_burden in applied_release_gate_rows():
    lines.append(
      f"| {surface} | {gates} | {implementation} | {tier} | {user_burden} |"
    )
  return "\n".join(lines)


def build_usage_outcomes_markdown() -> str:
  return """- Weekly active quality users and digital workflow completion rate by site and function
- AI recommendation usage distribution by process type and severity class
- Override rates segmented by role with mandatory rationale capture
- Time-to-first-action after AI triage versus manual baseline
"""


def build_esg_outcomes_markdown() -> str:
  return """- Paperless quality record adoption and paper reduction trend
- Deviation rework hour reduction and right-first-time improvement
- Investigation cycle energy intensity and compute utilization trend
- Supplier quality interaction digitalization rate (fewer manual exchanges)
"""


def build_system_mermaid() -> str:
    lines: list[str] = []
    lines.append("flowchart LR")
    lines.append("  %% Current-state QMS")
    lines.append('  subgraph ASIS["Current QMS Structure (As-Is)"]')
    lines.append('    C_GOV["QMS Governance<br/>Policies + SOP ownership"]')
    lines.append('    C_DOC["Document Control<br/>SharePoint + templates"]')
    lines.append('    C_EVT["Quality Event Intake<br/>Email + manual forms"]')
    lines.append('    C_CASE["Deviation/CAPA/Change<br/>Spreadsheet routing"]')
    lines.append('    C_APV["Approvals<br/>Email + wet signatures"]')
    lines.append('    C_TRN["Training<br/>LMS + manual impact checks"]')
    lines.append('    C_AUD["Audits<br/>Shared evidence folders"]')
    lines.append('    C_DAT["KPI Reporting<br/>Manual extracts + lagging metrics"]')
    lines.append('    C_SRC["Source Systems<br/>ERP, MES, LIMS, PLM (siloed)"]')
    lines.append("  end")

    lines.append("  %% Target-state digital QMS")
    lines.append('  subgraph TOBE["Proposed Digital Process QMS (To-Be)"]')
    lines.append('    P_GOV["Compliance + Governance Layer<br/>Part 11, Annex 11, ALCOA+"]')
    lines.append('    P_ORC["Process Orchestration Layer<br/>BPMN workflows + SLA timers"]')
    lines.append('    P_DMS["Controlled Content Service<br/>Version control + e-signatures"]')
    lines.append('    P_EQM["Unified eQMS Case Hub<br/>Deviation, CAPA, Change, Complaint"]')
    lines.append('    P_INT["Integration Hub<br/>APIs + event streaming"]')
    lines.append('    P_DAT["Quality Data Platform<br/>Canonical model + traceability graph"]')
    lines.append('    P_AI["AI Quality Copilot<br/>NLP triage + risk scoring + draft actions"]')
    lines.append('    P_TRN["Training Impact Automation<br/>Role mapping + auto assignment"]')
    lines.append('    P_AUD["Continuous Audit Readiness<br/>Evidence graph + control checks"]')
    lines.append('    P_DSH["Quality Cockpit<br/>Real-time KPIs + predictive alerts"]')
    lines.append("  end")

    lines.append("  %% Existing functional flow")
    lines.append("  C_GOV --> C_DOC")
    lines.append("  C_DOC --> C_EVT")
    lines.append("  C_EVT --> C_CASE")
    lines.append("  C_APV --> C_CASE")
    lines.append("  C_CASE --> C_TRN")
    lines.append("  C_CASE --> C_AUD")
    lines.append("  C_CASE --> C_DAT")
    lines.append("  C_SRC --> C_DAT")

    lines.append("  %% Proposed functional flow")
    lines.append("  P_GOV --> P_ORC")
    lines.append("  P_ORC --> P_DMS")
    lines.append("  P_ORC --> P_EQM")
    lines.append("  P_INT --> P_DAT")
    lines.append("  P_DMS --> P_DAT")
    lines.append("  P_EQM --> P_DAT")
    lines.append("  P_EQM --> P_AI")
    lines.append("  P_AI -->|recommended controls| P_EQM")
    lines.append("  P_EQM --> P_TRN")
    lines.append("  P_EQM --> P_AUD")
    lines.append("  P_DAT --> P_DSH")
    lines.append("  P_AI -->|predictive signals| P_DSH")
    lines.append("  P_DSH -->|closed-loop actions| P_ORC")

    lines.append("  %% Migration mapping")
    lines.append("  C_GOV -. digitize governance controls .-> P_GOV")
    lines.append("  C_DOC -. move to controlled content lifecycle .-> P_DMS")
    lines.append("  C_EVT -. standardize event taxonomy .-> P_EQM")
    lines.append("  C_CASE -. convert workflow templates .-> P_ORC")
    lines.append("  C_APV -. replace email approvals with e-sign .-> P_ORC")
    lines.append("  C_TRN -. automate training impact .-> P_TRN")
    lines.append("  C_AUD -. always-on evidence trail .-> P_AUD")
    lines.append("  C_DAT -. unify quality model and KPI feed .-> P_DAT")
    lines.append("  C_SRC -. API/event integration .-> P_INT")

    lines.append("  classDef current fill:#FCE9CF,stroke:#A86A00,stroke-width:1px,color:#1F1F1F;")
    lines.append("  classDef target fill:#DDF4E5,stroke:#1E7A45,stroke-width:1px,color:#1F1F1F;")
    lines.append("  classDef platform fill:#DDEBFF,stroke:#245EA8,stroke-width:1px,color:#1F1F1F;")
    lines.append("  classDef ai fill:#FFE3C4,stroke:#B65E00,stroke-width:1px,color:#1F1F1F;")
    lines.append("  classDef governance fill:#F2DEFF,stroke:#7A2B9A,stroke-width:1px,color:#1F1F1F;")

    lines.append("  class C_GOV,C_DOC,C_EVT,C_CASE,C_APV,C_TRN,C_AUD,C_DAT,C_SRC current;")
    lines.append("  class P_ORC,P_DMS,P_EQM,P_TRN,P_AUD target;")
    lines.append("  class P_INT,P_DAT,P_DSH platform;")
    lines.append("  class P_AI ai;")
    lines.append("  class P_GOV governance;")

    return "\n".join(lines) + "\n"


def build_raci_markdown() -> str:
    rows = [
        ("Deviation intake and triage", "Quality Ops", "Head of Quality", "Manufacturing", "QA Systems"),
        ("CAPA planning and closure", "Process Owner", "Head of Quality", "Regulatory", "Data and AI"),
        ("Change control workflow", "Change Coordinator", "Quality Governance", "IT Validation", "Site Ops"),
        ("Training impact assignment", "Training Lead", "Quality Governance", "HR", "Process Owner"),
        ("Audit evidence readiness", "Audit Lead", "Head of Quality", "All Functions", "QA Systems"),
        ("AI recommendation approval", "Quality Ops", "Quality Governance", "Data Science", "Regulatory"),
        ("KPI and risk signal governance", "Quality Analytics", "Head of Quality", "Site Leadership", "Quality Ops"),
    ]

    lines = []
    lines.append("| Process | Responsible (R) | Accountable (A) | Consulted (C) | Informed (I) |")
    lines.append("|---|---|---|---|---|")
    for process, r_role, a_role, c_role, i_role in rows:
        lines.append(f"| {process} | {r_role} | {a_role} | {c_role} | {i_role} |")
    return "\n".join(lines)


def build_rollout_markdown() -> str:
    return """1. Wave 1 (8-12 weeks): unify taxonomy and digitize deviation/CAPA/change workflows.
2. Wave 2 (6-10 weeks): connect ERP/MES/LIMS and establish canonical quality data model.
3. Wave 3 (6-8 weeks): deploy AI triage, risk scoring, and recommendation governance.
4. Wave 4 (4-6 weeks): scale predictive cockpit, control monitoring, and continuous improvement automation.
"""


def build_kpi_markdown() -> str:
    return """- Deviation triage time: reduce by 40 percent
- CAPA cycle time: reduce by 25 percent
- On-time training completion after change: increase to 98 percent
- Audit evidence retrieval time: reduce by 60 percent
- Recurrence rate for high-risk deviations: reduce by 30 percent
"""
def build_markdown(mermaid: str) -> str:
  return f"""# QMS Digital Process Solution (Tailored Draft)\n\nThis draft maps the current QMS structure/functionality and a proposed digital process\nsolution with AI-enabled decision support and a clear operating model.\n\n## System Diagram\n\n```mermaid\n{mermaid}```\n\n## RACI Overlay\n\n{build_raci_markdown()}\n\n## Rollout Waves\n\n{build_rollout_markdown()}\n\n## Target KPI Outcomes\n\n{build_kpi_markdown()}\n\n## How Target Outcomes Are Measured\n\n{build_metric_framework_markdown()}\n\n## Usage Outcomes\n\n{build_usage_outcomes_markdown()}\n\n## ESG Outcomes\n\n{build_esg_outcomes_markdown()}\n\n## Verifiability and Compliance Assessments\n\n{build_compliance_assessment_markdown()}\n\n## AI Regulator Stress-Test Hardening\n\n{build_ai_hardening_markdown()}\n\n## Anticipated AI-Assisted Regulatory Challenges and Prepared Answers\n\n{build_regulator_answers_markdown()}\n\n## Release Evidence Bundle Minimum Fields\n\n{build_evidence_bundle_markdown()}\n\n## Strict P0 Launch Release Gates (QMS Resume Reviewer)\n\n{build_p0_launch_gate_markdown()}\n\n## P1 Post-Launch Enforcement Gates (Marked)\n\n{build_p1_post_launch_gate_markdown()}\n\n## Full Regulatory Gate Catalog (Tiered Reference)\n\n{build_release_gate_checklist_markdown()}\n\n## Applied Regulatory Gate Implementation for QMS Resume Reviewer\n\n{build_applied_release_gate_markdown()}\n\n## Patient Safety Guardrails\n\n- AI remains decision support, never autonomous closure for patient-impacting records
- High-risk cases require documented human review with accountable sign-off
- Any safety or compliance control failure triggers release hold and escalation
- Full decision lineage is retained for inspection and post-market investigation
\n## Notes\n\n- This is designed as a design-ready blueprint you can adapt to your exact tools.\n- If you share your current vendor stack, labels can be swapped directly in one pass.\n"""


def html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_html(mermaid: str) -> str:
    raci_rows = [
        ("Deviation intake and triage", "Quality Ops", "Head of Quality", "Manufacturing", "QA Systems"),
        ("CAPA planning and closure", "Process Owner", "Head of Quality", "Regulatory", "Data and AI"),
        ("Change control workflow", "Change Coordinator", "Quality Governance", "IT Validation", "Site Ops"),
        ("Training impact assignment", "Training Lead", "Quality Governance", "HR", "Process Owner"),
        ("Audit evidence readiness", "Audit Lead", "Head of Quality", "All Functions", "QA Systems"),
        ("AI recommendation approval", "Quality Ops", "Quality Governance", "Data Science", "Regulatory"),
        ("KPI and risk signal governance", "Quality Analytics", "Head of Quality", "Site Leadership", "Quality Ops"),
    ]

    raci_html_rows = "\n".join(
        "<tr>"
        + "".join(f"<td>{html_escape(cell)}</td>" for cell in row)
        + "</tr>"
        for row in raci_rows
    )

    kpis = [
        "Deviation triage time: reduce by 40 percent",
        "CAPA cycle time: reduce by 25 percent",
        "On-time training completion after change: increase to 98 percent",
        "Audit evidence retrieval time: reduce by 60 percent",
        "Recurrence rate for high-risk deviations: reduce by 30 percent",
    ]

    usage_outcomes = [
        "Weekly active quality users and digital workflow completion rate by site and function",
        "AI recommendation usage distribution by process type and severity class",
        "Override rates segmented by role with mandatory rationale capture",
        "Time-to-first-action after AI triage versus manual baseline",
    ]

    esg_outcomes = [
        "Paperless quality record adoption and paper reduction trend",
        "Deviation rework hour reduction and right-first-time improvement",
        "Investigation cycle energy intensity and compute utilization trend",
        "Supplier quality interaction digitalization rate (fewer manual exchanges)",
    ]

    kpi_items = "\n".join(f"<li>{html_escape(item)}</li>" for item in kpis)
    usage_items = "\n".join(f"<li>{html_escape(item)}</li>" for item in usage_outcomes)
    esg_items = "\n".join(f"<li>{html_escape(item)}</li>" for item in esg_outcomes)

    metric_html_rows = "\n".join(
        "<tr>"
        + "".join(f"<td>{html_escape(cell)}</td>" for cell in row)
        + "</tr>"
        for row in metric_rows()
    )

    compliance_html_rows = "\n".join(
        "<tr>"
        + "".join(f"<td>{html_escape(cell)}</td>" for cell in row)
        + "</tr>"
        for row in compliance_assessment_rows()
    )

    ai_hardening_html_rows = "\n".join(
      "<tr>"
      + "".join(f"<td>{html_escape(cell)}</td>" for cell in row)
      + "</tr>"
      for row in ai_hardening_rows()
    )

    regulator_answer_html_rows = "\n".join(
      "<tr>"
      + "".join(f"<td>{html_escape(cell)}</td>" for cell in row)
      + "</tr>"
      for row in regulator_answer_rows()
    )

    p0_launch_gate_html_rows = "\n".join(
      "<tr>"
      + "".join(f"<td>{html_escape(cell)}</td>" for cell in row)
      + "</tr>"
      for row in p0_launch_gate_rows()
    )

    p1_windows = p1_post_launch_windows()
    p1_post_launch_gate_html_rows = "\n".join(
      "<tr>"
      + f"<td>{html_escape(gate_id)}</td>"
      + f"<td>{html_escape(gate_name)}</td>"
      + f"<td>{html_escape(evidence)}</td>"
      + f"<td>{html_escape(enforcement)}</td>"
      + f"<td>{html_escape(p1_windows.get(gate_id, 'Enable in first post-launch hardening wave'))}; block next release if unresolved</td>"
      + "</tr>"
      for gate_id, gate_name, evidence, enforcement, _ in p1_post_launch_gate_rows()
    )

    p0 = p0_launch_gate_ids()
    release_gate_html_rows = "\n".join(
      "<tr>"
      + f"<td>{html_escape(gate_id)}</td>"
      + f"<td>{html_escape('P0 Launch Blocker' if gate_id in p0 else 'P1 Post-Launch')}</td>"
      + f"<td>{html_escape(gate_name)}</td>"
      + f"<td>{html_escape(evidence)}</td>"
      + f"<td>{html_escape(enforcement)}</td>"
      + (
        f"<td>{html_escape(fail_action)}</td>"
        if gate_id in p0
        else f"<td>{html_escape((p1_windows.get(gate_id, 'Enable in first post-launch hardening wave') + '; block next release if unresolved'))}</td>"
      )
      + "</tr>"
      for gate_id, gate_name, evidence, enforcement, fail_action in release_gate_rows()
    )

    applied_release_gate_html_rows = "\n".join(
      "<tr>"
      + "".join(f"<td>{html_escape(cell)}</td>" for cell in row)
      + "</tr>"
      for row in applied_release_gate_rows()
    )

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>QMS Digital Process Proposal</title>
  <style>
    :root {{
      --bg: #f7f7f2;
      --card: #ffffff;
      --ink: #1e1f24;
      --muted: #4d5562;
      --accent: #0c5ea8;
      --accent-soft: #d9ebff;
      --line: #d7dde5;
      --ok: #1f7a45;
      --warn: #a86a00;
    }}

    body {{
      margin: 0;
      font-family: Segoe UI, Tahoma, sans-serif;
      background:
        radial-gradient(circle at 10% 0%, #e9f4ff 0%, transparent 35%),
        radial-gradient(circle at 90% 100%, #fbeed8 0%, transparent 30%),
        var(--bg);
      color: var(--ink);
    }}

    .wrap {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
    }}

    .hero {{
      background: linear-gradient(125deg, #0c5ea8, #117844);
      color: white;
      border-radius: 14px;
      padding: 22px 24px;
      box-shadow: 0 10px 24px rgba(16, 54, 92, 0.25);
    }}

    .hero h1 {{
      margin: 0 0 8px;
      font-size: 1.7rem;
      letter-spacing: 0.01em;
    }}

    .hero p {{
      margin: 0;
      opacity: 0.94;
      line-height: 1.45;
    }}

    .grid {{
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 18px;
      margin-top: 18px;
    }}

    .card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 4px 10px rgba(16, 24, 40, 0.05);
    }}

    h2 {{
      margin: 4px 0 12px;
      font-size: 1.15rem;
    }}

    .muted {{
      color: var(--muted);
      margin: 0 0 8px;
      line-height: 1.4;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.93rem;
    }}

    th, td {{
      border: 1px solid var(--line);
      padding: 8px;
      text-align: left;
      vertical-align: top;
    }}

    th {{
      background: var(--accent-soft);
      color: #0d3356;
    }}

    ul {{
      margin-top: 8px;
      padding-left: 20px;
    }}

    .badge {{
      display: inline-block;
      margin-right: 8px;
      margin-bottom: 8px;
      padding: 6px 10px;
      border-radius: 999px;
      background: #ecf3fb;
      border: 1px solid #d2e2f6;
      color: #204a74;
      font-size: 0.85rem;
    }}

    .legend {{
      margin-top: 6px;
      font-size: 0.86rem;
      color: var(--muted);
    }}

    @media (max-width: 980px) {{
      .grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
  <script src=\"https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js\"></script>
</head>
<body>
  <div class=\"wrap\">
    <section class=\"hero\">
      <h1>QMS Digital Process Solution</h1>
      <p>
        Current-state to future-state map with migration links, operating model ownership,
        and measurable KPI targets for the proposed digital process architecture.
      </p>
    </section>

    <div class=\"grid\">
      <section class=\"card\">
        <h2>System Diagram</h2>
        <p class=\"muted\">
          Dashed links indicate migration mapping from existing functionality to the target model.
        </p>
        <div class=\"mermaid\">
{mermaid}
        </div>
        <p class=\"legend\">Legend: current-state nodes (amber), target process nodes (green), platform nodes (blue), governance (violet), AI (orange).</p>
      </section>

      <section class=\"card\">
        <h2>Rollout Waves</h2>
        <span class=\"badge\">Wave 1: Core workflows</span>
        <span class=\"badge\">Wave 2: Integrations + data model</span>
        <span class=\"badge\">Wave 3: AI controls</span>
        <span class=\"badge\">Wave 4: Predictive operations</span>
        <ul>
          <li>Wave 1 (8-12 weeks): digitize deviation, CAPA, and change workflows.</li>
          <li>Wave 2 (6-10 weeks): connect ERP/MES/LIMS and enforce canonical quality model.</li>
          <li>Wave 3 (6-8 weeks): deploy AI triage and risk scoring with approval controls.</li>
          <li>Wave 4 (4-6 weeks): scale real-time risk cockpit and closed-loop automation.</li>
        </ul>

        <h2>Target KPI Outcomes</h2>
        <ul>
{kpi_items}
        </ul>

        <h2>Usage Outcomes</h2>
        <ul>
      {usage_items}
        </ul>

        <h2>ESG Outcomes</h2>
        <ul>
      {esg_items}
        </ul>
      </section>
    </div>

    <section class=\"card\" style=\"margin-top: 18px;\">
      <h2>RACI Overlay</h2>
      <table>
        <thead>
          <tr>
            <th>Process</th>
            <th>Responsible (R)</th>
            <th>Accountable (A)</th>
            <th>Consulted (C)</th>
            <th>Informed (I)</th>
          </tr>
        </thead>
        <tbody>
          {raci_html_rows}
        </tbody>
      </table>
    </section>

    <section class=\"card\" style=\"margin-top: 18px;\">
      <h2>How Target Outcomes Are Measured</h2>
      <p class=\"muted\">
        Metrics include explicit formulas, evidence sources, and cadence for verifiability
        and regulatory readiness.
      </p>
      <table>
        <thead>
          <tr>
            <th>Domain</th>
            <th>Metric</th>
            <th>Measurement Formula</th>
            <th>Data Source</th>
            <th>Cadence</th>
            <th>Target</th>
            <th>Patient Safety Link</th>
          </tr>
        </thead>
        <tbody>
          {metric_html_rows}
        </tbody>
      </table>
    </section>

    <section class=\"card\" style=\"margin-top: 18px;\">
      <h2>Verifiability and Compliance Assessments</h2>
      <table>
        <thead>
          <tr>
            <th>Assessment Area</th>
            <th>Verification Method</th>
            <th>Evidence</th>
            <th>Cadence</th>
            <th>Gate</th>
          </tr>
        </thead>
        <tbody>
          {compliance_html_rows}
        </tbody>
      </table>

      <h2 style=\"margin-top: 14px;\">Patient Safety Guardrails</h2>
      <ul>
        <li>AI remains decision support only; no autonomous closure for patient-impacting records.</li>
        <li>High-risk records require documented human review and accountable sign-off.</li>
        <li>Control failures trigger release hold and mandatory escalation.</li>
        <li>Decision lineage is retained end-to-end for inspections and investigations.</li>
      </ul>
    </section>
    <section class="card" style="margin-top: 18px;">
      <h2>AI Regulator Stress-Test Hardening</h2>
      <p class="muted">
        Each hardening area maps implementation design to expected regulator AI queries,
        required evidence, and objective enforcement rules.
      </p>
      <table>
        <thead>
          <tr>
            <th>Hardening Area</th>
            <th>Implementation Pattern</th>
            <th>Anticipated Regulator Question</th>
            <th>Evidence Package</th>
            <th>Enforcement Rule</th>
          </tr>
        </thead>
        <tbody>
          {ai_hardening_html_rows}
        </tbody>
      </table>
    </section>

    <section class="card" style="margin-top: 18px;">
      <h2>Anticipated AI-Assisted Regulatory Challenges and Prepared Answers</h2>
      <table>
        <thead>
          <tr>
            <th>Anticipated Challenge</th>
            <th>Prepared Response</th>
            <th>Demonstrable Artifact</th>
          </tr>
        </thead>
        <tbody>
          {regulator_answer_html_rows}
        </tbody>
      </table>

      <h2 style="margin-top: 14px;">Release Evidence Bundle Minimum Fields</h2>
      <ul>
        <li>release_id and release timestamp</li>
        <li>source commit SHAs and build run IDs</li>
        <li>model version and prompt version identifiers</li>
        <li>SBOM reference and provenance reference</li>
        <li>validation summary and gate verdicts</li>
        <li>approval records and exception records</li>
        <li>checksum manifest and signing certificate reference</li>
      </ul>
    </section>

    <section class="card" style="margin-top: 18px;">
      <h2>Strict P0 Launch Release Gates (QMS Resume Reviewer)</h2>
      <p class="muted">
        P0 gates are strict launch blockers. Initial production release does not proceed
        if any P0 evidence requirement fails.
      </p>
      <table>
        <thead>
          <tr>
            <th>Gate ID</th>
            <th>P0 Launch Blocker</th>
            <th>Required Evidence</th>
            <th>Enforcement Point</th>
            <th>Fail-Closed Action</th>
          </tr>
        </thead>
        <tbody>
          {p0_launch_gate_html_rows}
        </tbody>
      </table>

      <h2 style="margin-top: 14px;">P1 Post-Launch Enforcement Gates (Marked)</h2>
      <p class="muted">
        P1 gates are explicitly marked for post-launch hardening and must be enabled within
        the listed window. If unresolved, the next release is blocked.
      </p>
      <table>
        <thead>
          <tr>
            <th>Gate ID</th>
            <th>P1 Post-Launch Enforcement</th>
            <th>Required Evidence</th>
            <th>Enforcement Point</th>
            <th>Post-Launch Rule</th>
          </tr>
        </thead>
        <tbody>
          {p1_post_launch_gate_html_rows}
        </tbody>
      </table>

      <h2 style="margin-top: 14px;">Full Regulatory Gate Catalog (Tiered Reference)</h2>
      <table>
        <thead>
          <tr>
            <th>Gate ID</th>
            <th>Launch Tier</th>
            <th>Regulatory Gate</th>
            <th>Required Evidence</th>
            <th>Enforcement Point</th>
            <th>Enforcement Outcome</th>
          </tr>
        </thead>
        <tbody>
          {release_gate_html_rows}
        </tbody>
      </table>

      <h2 style="margin-top: 14px;">Applied Regulatory Gate Implementation</h2>
      <table>
        <thead>
          <tr>
            <th>QMS Resume Reviewer Surface</th>
            <th>Applied Gates</th>
            <th>Applied Implementation Pattern</th>
            <th>Launch Tier</th>
            <th>User Burden Profile</th>
          </tr>
        </thead>
        <tbody>
          {applied_release_gate_html_rows}
        </tbody>
      </table>
    </section>
  </div>

  <script>
    mermaid.initialize({{
      startOnLoad: true,
      theme: "neutral",
      securityLevel: "loose",
      flowchart: {{ useMaxWidth: true, curve: "basis" }}
    }});
  </script>
</body>
</html>
"""


def write_outputs(out_dir: Path) -> tuple[Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    mermaid = build_system_mermaid()
    markdown = build_markdown(mermaid)
    html = build_html(mermaid)

    mmd_path = out_dir / "qms_solution_diagram.mmd"
    md_path = out_dir / "qms_solution_proposal.md"
    html_path = out_dir / "qms_solution_proposal.html"

    mmd_path.write_text(mermaid, encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    html_path.write_text(html, encoding="utf-8")

    return mmd_path, md_path, html_path


def main() -> None:
    out_dir = Path(r"c:\qms_digital_process_design")
    mmd_path, md_path, html_path = write_outputs(out_dir)

    print(f"Generated: {mmd_path}")
    print(f"Generated: {md_path}")
    print(f"Generated: {html_path}")


if __name__ == "__main__":
    main()
