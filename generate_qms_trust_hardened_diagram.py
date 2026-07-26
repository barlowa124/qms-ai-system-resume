"""Generate a neutral-tone QMS AI interview walkthrough diagram pack.

Outputs:
- qms_trust_hardened_system_diagram.mmd
- qms_trust_hardened_system_diagram.md
- qms_trust_hardened_system_diagram.html
"""

from __future__ import annotations

import sys
from pathlib import Path


def build_mermaid() -> str:
    lines: list[str] = []
    lines.append("flowchart LR")
    lines.append("  %% QMS AI interview walkthrough architecture")

    lines.append('  subgraph OBS["Reference Observations (Industry-Neutral)"]')
    lines.append('    R_DEPLOY["Deployment configuration can exceed implementation transparency"]')
    lines.append('    R_SCAN["Security scans may exist without blocking behavior"]')
    lines.append('    R_SUPPLY["Provenance and SBOM controls may be inconsistent"]')
    lines.append('    R_COMP["Compliance evidence can be distributed across tools"]')
    lines.append('    R_MIG["Migration scripts can include direct connection patterns"]')
    lines.append('    R_AI["AI reasoning, citations, and logs may not be presented together"]')
    lines.append("  end")

    lines.append('  subgraph TARGET["Target QMS AI Architecture"]')
    lines.append('    T_POLICY["Policy checks and branch protections"]')
    lines.append('    T_GATES["Blocking security and quality gates"]')
    lines.append('    T_SUPPLY["Artifact integrity metadata: provenance and SBOM"]')
    lines.append('    T_RELEASE["Release validation by environment tier"]')
    lines.append('    T_DB["Secure migration connection handling"]')
    lines.append('    T_EQMS["Unified eQMS workflow orchestration"]')
    lines.append('    T_DATA["Canonical quality data model and traceability graph"]')
    lines.append('    T_AIGOV["AI governance service with human review and guardrails"]')
    lines.append('    T_LOGS["AI interaction logs and decision audit trail"]')
    lines.append('    T_REASON["Model reasoning records and reviewer rationale"]')
    lines.append('    T_PROOF["Formal consistency tests (including identity checks such as a=a where applicable)"]')
    lines.append('    T_CITE["Citation traceability and source quality checks"]')
    lines.append('    T_TRAIN["Training and retraining trend monitoring"]')
    lines.append('    T_DTWIN["Digital twin and drug virtualization validation"]')
    lines.append('    T_METRICS["Safety and performance trend metrics"]')
    lines.append('    T_REG["Regulatory and investigator evidence dossier"]')
    lines.append("  end")

    lines.append('  subgraph EVIDENCE["Audit and Technical Evidence"]')
    lines.append('    E_PIPE["CI and release workflow configurations"]')
    lines.append('    E_MIG["Migration workflow controls"]')
    lines.append('    E_LOG["Inference and decision logs"]')
    lines.append('    E_MODEL["Model cards, version history, and change records"]')
    lines.append('    E_MATH["Equation validation and invariant test reports"]')
    lines.append('    E_SRC["Citation ledger and source retention records"]')
    lines.append('    E_DRIFT["Dataset lineage and retraining trend reports"]')
    lines.append('    E_TWIN["Digital twin verification reports and comparator studies"]')
    lines.append('    E_AUDIT["Investigator-ready audit packet"]')
    lines.append("  end")

    lines.append("  %% Observation-to-design mapping")
    lines.append('  R_SCAN -. addressed with .-> T_GATES')
    lines.append('  R_SUPPLY -. addressed with .-> T_SUPPLY')
    lines.append('  R_MIG -. addressed with .-> T_DB')
    lines.append('  R_COMP -. addressed with .-> T_EQMS')
    lines.append('  R_COMP -. measured with .-> T_METRICS')
    lines.append('  R_AI -. addressed with .-> T_AIGOV')
    lines.append('  R_AI -. documented with .-> T_LOGS')
    lines.append('  R_DEPLOY -. governed by .-> T_POLICY')

    lines.append("  %% Core target flow")
    lines.append('  T_POLICY --> T_GATES')
    lines.append('  T_GATES --> T_SUPPLY')
    lines.append('  T_SUPPLY --> T_RELEASE')
    lines.append('  T_RELEASE --> T_REG')
    lines.append('  T_DB --> T_REG')

    lines.append('  T_EQMS --> T_DATA')
    lines.append('  T_DATA --> T_METRICS')
    lines.append('  T_AIGOV --> T_LOGS')
    lines.append('  T_AIGOV --> T_REASON')
    lines.append('  T_AIGOV --> T_CITE')
    lines.append('  T_AIGOV --> T_PROOF')
    lines.append('  T_DATA --> T_TRAIN')
    lines.append('  T_DATA --> T_DTWIN')

    lines.append('  T_LOGS --> T_REG')
    lines.append('  T_REASON --> T_REG')
    lines.append('  T_PROOF --> T_REG')
    lines.append('  T_CITE --> T_REG')
    lines.append('  T_TRAIN --> T_REG')
    lines.append('  T_DTWIN --> T_REG')
    lines.append('  T_METRICS --> T_REG')

    lines.append("  %% Evidence mapping")
    lines.append('  T_GATES --> E_PIPE')
    lines.append('  T_SUPPLY --> E_PIPE')
    lines.append('  T_RELEASE --> E_PIPE')
    lines.append('  T_DB --> E_MIG')
    lines.append('  T_LOGS --> E_LOG')
    lines.append('  T_REASON --> E_MODEL')
    lines.append('  T_PROOF --> E_MATH')
    lines.append('  T_CITE --> E_SRC')
    lines.append('  T_TRAIN --> E_DRIFT')
    lines.append('  T_DTWIN --> E_TWIN')
    lines.append('  T_REG --> E_AUDIT')

    lines.append("  classDef obs fill:#FCE9CF,stroke:#A86A00,stroke-width:1px,color:#1F1F1F;")
    lines.append("  classDef target fill:#DDF4E5,stroke:#1E7A45,stroke-width:1px,color:#1F1F1F;")
    lines.append("  classDef evidence fill:#DDEBFF,stroke:#245EA8,stroke-width:1px,color:#1F1F1F;")

    lines.append("  class R_DEPLOY,R_SCAN,R_SUPPLY,R_COMP,R_MIG,R_AI obs;")
    lines.append(
        "  class T_POLICY,T_GATES,T_SUPPLY,T_RELEASE,T_DB,T_EQMS,T_DATA,T_AIGOV,T_LOGS,T_REASON,T_PROOF,T_CITE,T_TRAIN,T_DTWIN,T_METRICS,T_REG target;"
    )
    lines.append("  class E_PIPE,E_MIG,E_LOG,E_MODEL,E_MATH,E_SRC,E_DRIFT,E_TWIN,E_AUDIT evidence;")

    return "\n".join(lines) + "\n"


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
    (
      "RG-09",
      "Backward compatibility of model updates",
      "Compatibility report showing newly introduced errors on previously-correct cases, segmented by risk class, plus reviewer acceptance-rate delta after rollout",
      "Model update gate + post-rollout monitoring",
      "Block next model update when compatibility threshold is breached without documented justification",
    ),
  ]


def p0_launch_gate_ids() -> set[str]:
  return {"RG-02", "RG-03", "RG-04", "RG-05", "RG-08"}


def p1_post_launch_windows() -> dict[str, str]:
  return {
    "RG-01": "Enable within 30 days after launch",
    "RG-06": "Enable within 30 days after launch",
    "RG-07": "Enable within 45 days after launch",
    "RG-09": "Enable within 30 days after launch",
  }


def p0_launch_gate_rows() -> list[tuple[str, str, str, str, str]]:
  p0 = p0_launch_gate_ids()
  return [row for row in release_gate_rows() if row[0] in p0]


def p1_post_launch_gate_rows() -> list[tuple[str, str, str, str, str]]:
  p0 = p0_launch_gate_ids()
  return [row for row in release_gate_rows() if row[0] not in p0]


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
    lines.append(f"| {gate_id} | {tier} | {gate_name} | {evidence} | {enforcement} | {outcome} |")
  return "\n".join(lines)


def build_p0_launch_gate_markdown() -> str:
  lines = []
  lines.append("| Gate ID | P0 Launch Blocker | Required Evidence | Enforcement Point | Fail-Closed Action |")
  lines.append("|---|---|---|---|---|")
  for gate_id, gate_name, evidence, enforcement, fail_action in p0_launch_gate_rows():
    lines.append(f"| {gate_id} | {gate_name} | {evidence} | {enforcement} | {fail_action} |")
  return "\n".join(lines)


def build_p1_post_launch_gate_markdown() -> str:
  lines = []
  lines.append("| Gate ID | P1 Post-Launch Enforcement | Required Evidence | Enforcement Point | Post-Launch Rule |")
  lines.append("|---|---|---|---|---|")
  windows = p1_post_launch_windows()
  for gate_id, gate_name, evidence, enforcement, _ in p1_post_launch_gate_rows():
    window = windows.get(gate_id, "Enable in first post-launch hardening wave")
    lines.append(f"| {gate_id} | {gate_name} | {evidence} | {enforcement} | {window}; block next release if unresolved |")
  return "\n".join(lines)


def build_applied_release_gate_markdown() -> str:
  return """| QMS Resume Reviewer Surface | Applied Gates | Applied Implementation Pattern | Launch Tier | User Burden Profile |
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
"""


def build_markdown(mermaid_text: str) -> str:
    return f"""# QMS AI System Interview Walkthrough

This walkthrough uses neutral language and focuses on evidence that interviewers, investigators, and regulators typically request.

## System Diagram

```mermaid
{mermaid_text}```

## Investigator Questions and Evidence Package

| Investigator Question | Evidence to Show | Why It Matters |
|---|---|---|
| What did the AI see and decide? | Full AI interaction logs with timestamps, model version, inputs, outputs, and human actions | Supports auditability and case reconstruction |
| Why did the model produce this recommendation? | Reasoning record, reviewer rationale, and model documentation | Supports explainability and accountability |
| Is the model mathematically consistent? | Formal consistency checks, invariant tests, and equation validation reports (including identity checks such as a=a where applicable) | Demonstrates internal logical and numerical consistency |
| Are citations and references trustworthy? | Citation ledger with source IDs, retrieval snapshots, and quality checks | Supports evidence integrity |
| How has retraining changed the model over time? | Versioned training data lineage, retraining trigger log, and performance trend reports | Shows controlled change management |
| How are digital twins and drug virtualization validated? | Comparator studies, verification reports, boundary-condition tests, and safety review signoff | Supports patient and animal safety objectives |

## Hardening Implementations for AI-Assisted Regulatory Assessments

| Hardening Area | Implementation Pattern | Primary Evidence Artifact |
|---|---|---|
| Full-stack inventory with risk tags | Catalog every service, model endpoint, integration, queue, database, and vendor dependency with GxP impact, data class, risk tier, owner, and control owner. | Versioned inventory register with ownership attestations |
| Control-to-implementation graph | Link each policy control to workflow enforcement, code checks, runtime telemetry, and evidence output with deterministic control IDs. | Control matrix with policy-code-telemetry-evidence references |
| Signed release evidence bundle | Generate signed manifest per release containing commit SHAs, model and prompt versions, SBOM, provenance, gate results, approvals, and exceptions. | Signed release dossier with checksum manifest |
| Decision reproducibility harness | Replay sampled recommendations under version-pinned model and retrieval context to validate deterministic behavior within tolerance. | Replay report with input hash, output hash, and pass or fail verdict |
| Prompt and model change control | Require risk assessment, validation protocol, rollback plan, and accountable approval for each model or prompt change. | Change-control package with validation evidence |
| Adversarial and abuse-case testing | Execute scheduled tests for prompt injection, unsafe outputs, citation poisoning, and context-boundary failures. | Adversarial test matrix with remediation records |
| Immutable lineage and rapid reconstruction | Store tamper-evident decision lineage that links inputs, citations, outputs, reviewer actions, and final case disposition. | Investigator packet generated from chained event logs |

## Anticipated Cross-Stack Investigation Challenges and Prepared Answers

| Anticipated Challenge | Prepared Response | Demonstrable Artifact |
|---|---|---|
| Show the entire AI-relevant stack and identify critical exposure points. | Provide inventory export filtered by risk tier and GxP impact class. | Stack inventory snapshot with owner and control-owner attestations |
| Prove required controls are enforced in runtime operations. | Present control graph linking policy to enforcement logic and telemetry status. | Control matrix health report with pass or fail status by control ID |
| Reproduce one historical recommendation and explain the outcome. | Run replay harness for selected case and compare output against tolerance policy. | Reproducibility report with case-level comparison metrics |
| Demonstrate resilience against adversarial or misuse scenarios. | Show scheduled abuse-case suite results and corrective actions for prior failures. | Adversarial trend report and corrective action log |
| Reconstruct a safety-critical case for investigator review. | Generate end-to-end timeline packet from immutable lineage records. | Investigator-ready audit packet with timestamps and actor lineage |

## Strict P0 Launch Release Gates (QMS Resume Reviewer)

{build_p0_launch_gate_markdown()}

## P1 Post-Launch Enforcement Gates (Marked)

{build_p1_post_launch_gate_markdown()}

## Full Regulatory Gate Catalog (Tiered Reference)

{build_release_gate_checklist_markdown()}

## Applied Regulatory Gate Implementation for QMS Resume Reviewer

{build_applied_release_gate_markdown()}

## Neutral Architecture Summary

1. Governance and Policy Controls
- Policy checks and branch protections prevent uncontrolled changes to quality-critical workflows.

2. Security and Artifact Integrity
- Security gates block on high-risk findings.
- Build artifacts include provenance and SBOM metadata.

3. Release Validation
- Environment-tier validation confirms release readiness before promotion.
- Migration connectivity and transport controls are verified in validation steps.

4. Data and Workflow Traceability
- Unified eQMS workflows feed a canonical quality data model.
- A traceability graph links case context, model use, decisions, and outcomes.

5. AI Oversight and Evidence
- AI remains decision support with human review.
- Logs, reasoning records, citation traces, and formal checks are captured for review.

## Training and Retraining Trend Review

Use time-based trend views for:

1. Training dataset volume and composition per model version.
2. Data quality indicators and drift metrics.
3. Retraining trigger reasons and approval records.
4. Performance before and after retraining, segmented by risk class.
5. Safety-related outcome trends after model updates.

## Digital Twin and Drug Virtualization Focus

For digital twin and drug virtualization programs, include:

1. Verification evidence that simulation behavior is stable under defined constraints.
2. Validation evidence against observed or reference outcomes.
3. Boundary and stress testing across clinically relevant scenarios.
4. Clear mapping from model assumptions to safety controls.
5. Regulator-facing dossier that links methods, evidence, and risk controls.

## Interview Walkthrough Sequence

1. Problem context and safety objective.
2. Architecture and control points.
3. Investigator evidence package.
4. Model reasoning, consistency checks, and citations.
5. Retraining trends and digital twin validation evidence.
6. Regulatory readiness and next-step roadmap.
"""


def build_html(mermaid_text: str, markdown_text: str) -> str:
    escaped_mermaid = mermaid_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    escaped_notes = markdown_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>QMS AI System Interview Walkthrough</title>
  <script type=\"module\">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    mermaid.initialize({{ startOnLoad: true, theme: 'default', securityLevel: 'loose' }});
  </script>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 24px; color: #1f2937; }}
    h1 {{ margin-bottom: 8px; }}
    .diagram {{ border: 1px solid #d1d5db; border-radius: 10px; padding: 12px; background: #ffffff; }}
    .notes {{ margin-top: 18px; border: 1px solid #d1d5db; border-radius: 10px; padding: 12px; background: #f9fafb; white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>QMS AI System Interview Walkthrough</h1>
  <div class=\"diagram\">
    <pre class=\"mermaid\">{escaped_mermaid}</pre>
  </div>
  <div class=\"notes\">{escaped_notes}</div>
</body>
</html>
"""


def write_outputs(out_dir: Path) -> tuple[Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    mermaid_text = build_mermaid()
    markdown_text = build_markdown(mermaid_text)

    mmd_path = out_dir / "qms_trust_hardened_system_diagram.mmd"
    md_path = out_dir / "qms_trust_hardened_system_diagram.md"
    html_path = out_dir / "qms_trust_hardened_system_diagram.html"

    mmd_path.write_text(mermaid_text, encoding="utf-8")
    md_path.write_text(markdown_text, encoding="utf-8")
    html_path.write_text(build_html(mermaid_text, markdown_text), encoding="utf-8")

    return mmd_path, md_path, html_path


def main() -> None:
    # Default to the directory containing this script; allow an explicit override.
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    mmd_path, md_path, html_path = write_outputs(out_dir)
    print(f"Generated Mermaid: {mmd_path}")
    print(f"Generated Markdown: {md_path}")
    print(f"Generated HTML: {html_path}")


if __name__ == "__main__":
    main()
