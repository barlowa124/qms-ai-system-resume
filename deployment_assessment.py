"""Reviewer instrument and fail-closed scoring engine for assessing a REAL
clinical deployment of an AI-enabled QMS.

The design artifacts in this repository describe what a compliant system
*should* look like. This module is the counterpart used against a system that
is actually running: a structured evidence-gathering instrument plus a scoring
engine that refuses to hand out a clean result when evidence is absent.

Scope limitation (deliberate, load-bearing):
    This produces a FINDINGS REPORT, not a compliance determination, not a
    release authorization, and not a regulatory clearance. It is an aid for
    qualified QA / regulatory / clinical-safety personnel. Nothing here
    substitutes for validated quality processes, notified-body review, or
    applicable regulatory submissions.

CLI:
    python3 deployment_assessment.py instrument [--outdir DIR]
    python3 deployment_assessment.py template   [--out FILE]
    python3 deployment_assessment.py score RESPONSES.json [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Severity(str, Enum):
    """Consequence class if an item is found non-conformant."""

    PATIENT_SAFETY_CRITICAL = "patient_safety_critical"
    MAJOR = "major"
    MINOR = "minor"


class Response(str, Enum):
    """Permitted reviewer responses for an assessment item."""

    CONFORMANT = "conformant"
    PARTIAL = "partial"
    NON_CONFORMANT = "non_conformant"
    NOT_ASSESSED = "not_assessed"
    NOT_APPLICABLE = "not_applicable"


# Responses that do NOT clear an item. NOT_ASSESSED is deliberately included:
# absence of evidence is treated as absence of control (fail-closed).
NON_CLEARING_RESPONSES = frozenset(
    {Response.PARTIAL, Response.NON_CONFORMANT, Response.NOT_ASSESSED}
)

MIN_JUSTIFICATION_CHARS = 20

PLACEHOLDER_JUSTIFICATIONS = frozenset(
    {
        "-",
        "--",
        ".",
        "n/a",
        "n.a.",
        "na",
        "nil",
        "no",
        "none",
        "not applicable",
        "ok",
        "tbd",
        "todo",
        "x",
        "yes",
    }
)


def is_substantive_justification(note: str) -> bool:
    """A not_applicable claim must say why, not just assert itself.

    Rejects placeholder tokens and anything too short to carry a reason, so
    that scoping an item out costs more effort than assessing it.
    """
    cleaned = note.strip()
    if cleaned.casefold().rstrip(".") in PLACEHOLDER_JUSTIFICATIONS:
        return False
    return len(cleaned) >= MIN_JUSTIFICATION_CHARS


class Verdict(str, Enum):
    """Overall outcome. Intentionally worded to avoid implying approval."""

    BLOCKING_FINDINGS = "BLOCKING_FINDINGS"
    MAJOR_FINDINGS = "MAJOR_FINDINGS"
    MINOR_FINDINGS = "MINOR_FINDINGS"
    NO_BLOCKING_FINDINGS_IDENTIFIED = "NO_BLOCKING_FINDINGS_IDENTIFIED"
    INVALID_SUBMISSION = "INVALID_SUBMISSION"


@dataclass(frozen=True)
class AssessmentItem:
    item_id: str
    domain: str
    question: str
    inspect: str
    evidence_required: tuple[str, ...]
    pass_criteria: str
    disqualifying_finding: str
    severity: Severity
    linked_gates: tuple[str, ...] = field(default_factory=tuple)
    allows_not_applicable: bool = False


def assessment_items() -> list[AssessmentItem]:
    """The reviewer instrument.

    Ordered by what most commonly invalidates an AI-enabled clinical
    deployment in practice: unclear regulatory status, oversight that exists
    only on paper, and unverifiable data integrity.
    """
    return [
        AssessmentItem(
            item_id="DA-01",
            domain="Intended Use and Regulatory Status",
            question=(
                "Is the intended use documented, and has the regulatory status of the "
                "AI component been formally determined?"
            ),
            inspect=(
                "Intended-use statement, user population, clinical/patient impact analysis, "
                "and the written determination of whether the AI meets the definition of a "
                "medical device / SaMD, or an EU AI Act high-risk system"
            ),
            evidence_required=(
                "Signed intended-use statement",
                "Regulatory classification rationale with named accountable approver",
                "Legal/regulatory affairs concurrence record",
            ),
            pass_criteria=(
                "A documented, approved determination exists and is consistent with how the "
                "system is actually used in production"
            ),
            disqualifying_finding=(
                "The AI influences clinical or patient-impacting decisions with no documented "
                "regulatory classification, or actual use exceeds the stated intended use"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-01",),
        ),
        AssessmentItem(
            item_id="DA-02",
            domain="Human Oversight in Practice",
            question=(
                "Is human review actually enforced for patient-impacting decisions, as "
                "observed in production data rather than in policy?"
            ),
            inspect=(
                "A random sample of closed high-risk cases; attempt (in a validated non-production "
                "environment) to close a high-risk case without reviewer sign-off"
            ),
            evidence_required=(
                "Sample of >=20 closed high-risk cases with reviewer identity and timestamp",
                "System behavior record when sign-off is omitted",
                "Override log with captured rationale",
            ),
            pass_criteria=(
                "Every sampled patient-impacting closure carries an accountable reviewer "
                "sign-off, and the system technically prevents closure without one"
            ),
            disqualifying_finding=(
                "Any patient-impacting record closed without human sign-off, or oversight "
                "enforced only by procedure with no technical control"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-04",),
        ),
        AssessmentItem(
            item_id="DA-03",
            domain="Human Oversight in Practice",
            question=(
                "Is there evidence that reviewers exercise independent judgment rather than "
                "rubber-stamping AI output (automation bias)?"
            ),
            inspect=(
                "Acceptance and override rates segmented by reviewer, risk class, and time; "
                "median review dwell time relative to case complexity"
            ),
            evidence_required=(
                "Acceptance-rate distribution across reviewers",
                "Override events with substantive rationale text",
                "Dwell-time distribution for high-risk cases",
                "The same metrics segmented by queue depth, shift position, and campaign peak, "
                "to show whether oversight holds up under workload",
            ),
            pass_criteria=(
                "Override rate is non-zero for high-risk classes, rationale text is substantive, "
                "dwell time is plausible for the decision complexity, and none of these degrade "
                "materially as workload rises"
            ),
            disqualifying_finding=(
                "Near-100% acceptance with negligible dwell time, indicating oversight is "
                "nominal rather than genuine; or oversight metrics that hold in aggregate but "
                "collapse at high queue depth or end of shift"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-04",),
        ),
        AssessmentItem(
            item_id="DA-04",
            domain="Data Integrity (ALCOA+)",
            question=(
                "Are audit trails for AI inputs, outputs, approvals, and overrides complete "
                "and tamper-evident?"
            ),
            inspect=(
                "Audit trail configuration, retention settings, administrator privileges, and "
                "whether records can be altered or deleted without detection"
            ),
            evidence_required=(
                "Audit trail integrity check output",
                "Privileged-access review showing who can modify records",
                "Retention policy aligned to record class",
            ),
            pass_criteria=(
                "Audit trails are immutable or tamper-evident, cover model calls end to end, "
                "and no unlogged privileged path can alter quality records"
            ),
            disqualifying_finding=(
                "Any administrator can silently alter or delete quality records, or model "
                "invocations are not logged"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-08",),
        ),
        AssessmentItem(
            item_id="DA-05",
            domain="Traceability and Investigation Readiness",
            question=(
                "Can a specific closed case be reconstructed end to end, on demand, from "
                "source data through model version to final disposition?"
            ),
            inspect=(
                "Live reconstruction of a reviewer-selected closed case, timed"
            ),
            evidence_required=(
                "Investigator packet for a case chosen by the reviewer, not pre-prepared",
                "Model and prompt version bound to that specific decision",
                "Source data lineage for the inputs used",
            ),
            pass_criteria=(
                "Reconstruction succeeds within the documented service-level objective and "
                "identifies the exact model/prompt version that produced the output"
            ),
            disqualifying_finding=(
                "The deployed model version for a historical decision cannot be established"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-08", "RG-02"),
        ),
        AssessmentItem(
            item_id="DA-06",
            domain="Model Validation and Performance",
            question=(
                "Was the model validated on data independent of training, with performance "
                "characterized per clinically meaningful subgroup?"
            ),
            inspect=(
                "Validation protocol and report, dataset provenance, train/test separation "
                "controls, and subgroup performance breakdown"
            ),
            evidence_required=(
                "Validation protocol approved before execution",
                "Evidence of train/test independence",
                "Performance by risk class and relevant patient subgroups",
                "Documented acceptance criteria set in advance",
            ),
            pass_criteria=(
                "Independence is demonstrable, acceptance criteria were pre-specified and met, "
                "and subgroup performance is reported rather than only aggregate"
            ),
            disqualifying_finding=(
                "Aggregate-only performance claims, post-hoc acceptance criteria, or "
                "unresolvable train/test contamination"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-06",),
        ),
        AssessmentItem(
            item_id="DA-07",
            domain="Model Validation and Performance",
            question=(
                "Is performance drift monitored in production against defined thresholds with "
                "a defined response?"
            ),
            inspect=(
                "Drift monitoring dashboard, threshold definitions, alert history, and actions "
                "taken on past alerts"
            ),
            evidence_required=(
                "Threshold definitions per case class",
                "Alert history with dispositions",
                "Evidence of at least one closed-loop response to a drift signal",
            ),
            pass_criteria=(
                "Thresholds are defined, alerts route to an accountable owner, and past alerts "
                "show documented resolution"
            ),
            disqualifying_finding=(
                "Drift is unmonitored, or alerts have accumulated without disposition"
            ),
            severity=Severity.MAJOR,
            linked_gates=("RG-06",),
        ),
        AssessmentItem(
            item_id="DA-08",
            domain="Change Control",
            question=(
                "Does every model, prompt, and calibration-data change in the production "
                "history have an approved change record?"
            ),
            inspect=(
                "Model registry version history reconciled against change tickets for the "
                "trailing 12 months"
            ),
            evidence_required=(
                "Complete deployed-version history with dates",
                "Corresponding change tickets with risk assessment and rollback plan",
                "Reconciliation showing no unmatched deployments",
            ),
            pass_criteria=(
                "Every production version maps to an approved change record with no gaps"
            ),
            disqualifying_finding=(
                "Any undocumented production model or prompt change"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-05",),
        ),
        AssessmentItem(
            item_id="DA-09",
            domain="Human-AI Compatibility",
            question=(
                "For each model update, was backward compatibility assessed so that "
                "previously-correct decisions were not silently regressed?"
            ),
            inspect=(
                "Compatibility reports attached to change records, and reviewer acceptance-rate "
                "behavior immediately following each update"
            ),
            evidence_required=(
                "Backward compatibility score per update, segmented by risk class",
                "Newly-introduced-error analysis on a frozen evaluation set",
                "Reviewer notification records where compatibility was knowingly broken",
            ),
            pass_criteria=(
                "Compatibility is measured per update, and any breach affecting a "
                "patient-safety class carries documented justification plus reviewer notification"
            ),
            disqualifying_finding=(
                "Updates promoted on aggregate accuracy alone, with no compatibility analysis "
                "for patient-safety case classes"
            ),
            severity=Severity.MAJOR,
            linked_gates=("RG-09",),
        ),
        AssessmentItem(
            item_id="DA-10",
            domain="Reproducibility",
            question=(
                "Can a past AI decision be re-derived within a defined tolerance?"
            ),
            inspect=(
                "Replay of a reviewer-selected historical case against its recorded model version"
            ),
            evidence_required=(
                "Replay harness output with input/output hashes",
                "Documented tolerance and rationale for non-deterministic components",
                "Sampling frequency and recent pass rate",
            ),
            pass_criteria=(
                "Sampled replays meet the documented tolerance, and any non-determinism is "
                "characterized rather than unexplained"
            ),
            disqualifying_finding=(
                "Historical decisions cannot be reproduced and the variance is uncharacterized"
            ),
            severity=Severity.MAJOR,
            linked_gates=("RG-06",),
        ),
        AssessmentItem(
            item_id="DA-11",
            domain="Safety Signal and Incident Handling",
            question=(
                "Is there a defined path from an AI-related error to containment, CAPA, and "
                "where applicable regulatory reporting?"
            ),
            inspect=(
                "Incident history involving AI output, escalation timestamps, and CAPA "
                "effectiveness checks"
            ),
            evidence_required=(
                "AI-related incident log",
                "Time-to-containment for past incidents",
                "CAPA records with effectiveness verification",
                "Reportability decision records where patient impact occurred",
            ),
            pass_criteria=(
                "Incidents are captured, escalated within SLA, and CAPA effectiveness is "
                "verified rather than assumed closed"
            ),
            disqualifying_finding=(
                "A known AI-caused patient-impacting error with no CAPA or no reportability "
                "assessment"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-04",),
        ),
        AssessmentItem(
            item_id="DA-12",
            domain="Reviewer Competency",
            question=(
                "Are reviewers trained specifically on the AI system's known failure modes "
                "and limitations?"
            ),
            inspect=(
                "Training curriculum content, completion records, and whether training is "
                "reissued when model behavior changes"
            ),
            evidence_required=(
                "Curriculum covering documented failure modes",
                "Completion records for all active reviewers",
                "Retraining triggered by compatibility-breaking updates",
            ),
            pass_criteria=(
                "All active reviewers are current on training that names concrete failure "
                "modes, not just general system operation"
            ),
            disqualifying_finding=(
                "Reviewers accountable for patient-impacting sign-off have no training on AI "
                "limitations"
            ),
            severity=Severity.MAJOR,
            linked_gates=("RG-04",),
        ),
        AssessmentItem(
            item_id="DA-13",
            domain="Third-Party and Supply Chain",
            question=(
                "If an external or vendor model is used, are version pinning, change "
                "notification, and data handling contractually and technically controlled?"
            ),
            inspect=(
                "Vendor agreements, model version pinning configuration, and data processing "
                "terms covering any PHI or patient-identifiable input"
            ),
            evidence_required=(
                "Contractual change-notification terms",
                "Evidence of version pinning in production configuration",
                "Data processing agreement covering the data classes actually sent",
            ),
            pass_criteria=(
                "Vendor model versions cannot change silently, and data handling matches what "
                "is contractually permitted"
            ),
            disqualifying_finding=(
                "Production depends on a floating vendor model endpoint that can change "
                "without notice, or patient data is sent outside agreed terms"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-03", "RG-05"),
            allows_not_applicable=True,
        ),
        AssessmentItem(
            item_id="DA-14",
            domain="Security and Misuse Resilience",
            question=(
                "Has the system been tested against adversarial input and misuse relevant to "
                "its clinical context?"
            ),
            inspect=(
                "Adversarial test suite scope, findings, and remediation status; access "
                "controls on model configuration"
            ),
            evidence_required=(
                "Adversarial/misuse test results with severity ratings",
                "Remediation evidence for critical findings",
                "Access control review for prompt and model configuration",
            ),
            pass_criteria=(
                "Misuse testing covers the deployed clinical context, and open findings have "
                "an owner and a remediation plan"
            ),
            disqualifying_finding=(
                "No misuse testing has been performed for the deployed clinical context, or "
                "open findings have no owner or remediation plan. A confirmed exploitable "
                "defect in a patient-impacting pathway should be escalated as a safety signal "
                "under DA-11 rather than recorded only here"
            ),
            severity=Severity.MAJOR,
            linked_gates=("RG-07",),
        ),
        AssessmentItem(
            item_id="DA-15",
            domain="In-Silico / Virtualization Evidence",
            question=(
                "If in-silico or virtual organ model output supports a regulatory or "
                "safety-relevant conclusion, is it cross-validated against ground truth?"
            ),
            inspect=(
                "Correlation studies against wet-lab or clinical data, and the qualification "
                "tier assigned to each model's use"
            ),
            evidence_required=(
                "Correlation study protocol and results",
                "Qualification tier with submission-use flag",
                "Drift monitoring against ground-truth refresh",
            ),
            pass_criteria=(
                "Ground-truth correlation is documented and current for the claimed use tier"
            ),
            disqualifying_finding=(
                "In-silico output supports a submission or safety conclusion with no "
                "ground-truth correlation evidence"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-06",),
            allows_not_applicable=True,
        ),
        AssessmentItem(
            item_id="DA-16",
            domain="Use Outside the Validated Envelope",
            question=(
                "Is actual production usage monitored against the population the system was "
                "validated on, and are out-of-envelope inputs detected at the point of use?"
            ),
            inspect=(
                "Usage telemetry broken down by case type, product, site, and language, "
                "compared against the validation population; the runtime behaviour when an "
                "input falls outside that population"
            ),
            evidence_required=(
                "Validation population definition with the case types and products covered",
                "Production usage distribution over a recent period, on the same axes",
                "Runtime evidence that an out-of-envelope input is flagged or refused",
            ),
            pass_criteria=(
                "Production usage is shown to fall inside the validated population, and inputs "
                "outside it are flagged to the user rather than answered silently"
            ),
            disqualifying_finding=(
                "The system returns normal-looking output for case types, products, or sites "
                "absent from the validation set, with no indication to the user that the input "
                "is outside the validated envelope"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-01", "RG-06"),
        ),
        AssessmentItem(
            item_id="DA-17",
            domain="Silent Truncation and Incomplete Input",
            question=(
                "When input exceeds size limits or a source document fails to parse, does the "
                "system fail visibly rather than reason over partial data?"
            ),
            inspect=(
                "Context and token limit handling, document parse and OCR failure paths, and "
                "what the reviewer sees when input is incomplete"
            ),
            evidence_required=(
                "Truncation and parse-failure logs for a recent production period",
                "Screenshot or specification of the user-visible indication when input is "
                "incomplete",
                "A worked example of a long or partly unreadable record and its handling",
            ),
            pass_criteria=(
                "Truncation and parse failure are logged and surfaced to the reviewer before "
                "sign-off, and the affected output is marked as based on incomplete input"
            ),
            disqualifying_finding=(
                "Input is silently truncated or a source document silently fails to parse, and "
                "the reviewer sees output that is indistinguishable from a complete assessment"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-04", "RG-08"),
        ),
        AssessmentItem(
            item_id="DA-18",
            domain="Configuration Drift",
            question=(
                "Are prompt templates, inference parameters, and thresholds under the same "
                "change control as the model itself?"
            ),
            inspect=(
                "Change history for prompt templates, temperature and sampling settings, "
                "retrieval configuration, and routing or escalation thresholds"
            ),
            evidence_required=(
                "Diff-level change log for prompts and inference parameters",
                "QA review record for each production-affecting change",
                "Evidence that production configuration matches the validated configuration",
            ),
            pass_criteria=(
                "No production-affecting configuration change reaches users without a review "
                "record, and current production configuration matches what was validated"
            ),
            disqualifying_finding=(
                "A prompt, parameter, or threshold differs from the validated configuration, or "
                "was changed in production without a review record"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-05",),
        ),
        AssessmentItem(
            item_id="DA-19",
            domain="Repeat Submission and Anchoring",
            question=(
                "When the same event is submitted more than once, is the full sequence of "
                "outputs retained rather than only the one the reviewer accepted?"
            ),
            inspect=(
                "Audit trail for a single event identifier that received multiple submissions, "
                "and whether superseded outputs remain retrievable"
            ),
            evidence_required=(
                "Audit trail showing every submission and output for one event identifier",
                "Rate of repeat submission per event over a recent period",
                "Evidence that superseded outputs are retained and linked to the final record",
            ),
            pass_criteria=(
                "All submissions for an event are retained and linked, so a reviewer or "
                "inspector can see whether the accepted output was the first one"
            ),
            disqualifying_finding=(
                "Only the accepted output is retained, so re-running an event until a milder "
                "result appears would leave no trace"
            ),
            severity=Severity.MAJOR,
            linked_gates=("RG-08", "RG-04"),
        ),
        AssessmentItem(
            item_id="DA-20",
            domain="Retrospective Impact Assessment",
            question=(
                "When a defect is found in a model version, can every record that version "
                "touched be enumerated and re-reviewed?"
            ),
            inspect=(
                "The query path from a model version and date range to the full set of affected "
                "records, and any past occasion on which it was exercised"
            ),
            evidence_required=(
                "A demonstrated cohort query returning all records produced by a given model "
                "and prompt version over a stated window",
                "The documented procedure for impact assessment and re-review of affected "
                "records once a defect is confirmed",
                "Evidence from a real defect, compatibility breach, or drift alert where the "
                "affected population was quantified",
            ),
            pass_criteria=(
                "The affected population for a given model version and window can be produced "
                "on demand, and a procedure exists for re-reviewing it"
            ),
            disqualifying_finding=(
                "A confirmed model defect cannot be converted into a list of affected records, "
                "so the blast radius of a known error is unknown"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-08", "RG-09"),
        ),
        AssessmentItem(
            item_id="DA-21",
            domain="Degraded Mode and Fallback",
            question=(
                "When the model is unavailable, slow, or rate-limited, does the system degrade "
                "to a defined manual path rather than to an unvalidated substitute?"
            ),
            inspect=(
                "Timeout, retry, and fallback configuration; whether any fallback model, "
                "cached result, or reduced tier can serve a patient-impacting request; and what "
                "users are instructed to do during an outage"
            ),
            evidence_required=(
                "Fallback and timeout configuration, naming every model or cache that can "
                "serve a request",
                "Validation status of each such fallback path",
                "The documented manual procedure for outages, and evidence it was followed "
                "during a real incident",
            ),
            pass_criteria=(
                "Every path that can answer a patient-impacting request is within validation "
                "scope, and outages route to a documented manual procedure"
            ),
            disqualifying_finding=(
                "An unvalidated fallback model, reduced tier, or cached result can silently "
                "serve a patient-impacting request, or outage behaviour is undefined and left "
                "to individual judgement under time pressure"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-04", "RG-05"),
        ),
        AssessmentItem(
            item_id="DA-22",
            domain="Upstream Pipeline Drift",
            question=(
                "Are the preprocessing components that shape model input under change control, "
                "not just the model and prompt?"
            ),
            inspect=(
                "Version history for OCR engines, document parsers, chunking logic, tokenizers, "
                "and embedding models, and whether routine infrastructure maintenance can "
                "change them without a quality review"
            ),
            evidence_required=(
                "Pinned versions for every preprocessing component in the production path",
                "Change records for any preprocessing change since validation",
                "Evidence that the quality organisation is notified of infrastructure upgrades "
                "affecting these components",
            ),
            pass_criteria=(
                "Preprocessing components are versioned, pinned, and covered by the same change "
                "control as the model itself"
            ),
            disqualifying_finding=(
                "An OCR engine, parser, tokenizer, or embedding model can be upgraded as "
                "routine maintenance, silently changing model input with no quality review"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-03", "RG-05"),
        ),
        AssessmentItem(
            item_id="DA-23",
            domain="Retrieval Corpus Currency",
            question=(
                "If the system retrieves from a document corpus, is that corpus bound to the "
                "current effective revision set held in document control?"
            ),
            inspect=(
                "Synchronisation between document control and the retrieval index, and whether "
                "superseded revisions remain retrievable alongside current ones"
            ),
            evidence_required=(
                "The reconciliation process and its most recent run between document control "
                "and the retrieval index",
                "A search demonstrating that a recently superseded revision is no longer "
                "returned as authoritative",
                "Evidence that the corpus revision used is recorded with each output",
            ),
            pass_criteria=(
                "The retrieval corpus matches the current effective revision set, and the "
                "revision actually used is recorded with the output"
            ),
            disqualifying_finding=(
                "Superseded document revisions are retrievable and indistinguishable from "
                "current ones, so output can cite an obsolete specification or procedure"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-05", "RG-08"),
            allows_not_applicable=True,
        ),
        AssessmentItem(
            item_id="DA-24",
            domain="Output-to-Record Transcription",
            question=(
                "Does what reaches the official quality record preserve the qualifiers, scope, "
                "and caveats of the output the reviewer actually approved?"
            ),
            inspect=(
                "The transfer path from model output to the GxP record of truth, whether it is "
                "automated or manual copy-paste, and what is dropped in transit"
            ),
            evidence_required=(
                "Side-by-side comparison of approved output and the resulting record entry for "
                "sampled cases",
                "Evidence that confidence, scope limits, and caveats survive the transfer",
                "Controls preventing entry against the wrong record identifier",
            ),
            pass_criteria=(
                "The record entry preserves the substance and qualifiers of the approved "
                "output, and is bound to the correct record identifier"
            ),
            disqualifying_finding=(
                "Qualifiers, scope limits, or uncertainty present in the approved output are "
                "absent from the official record, so the record overstates what was concluded"
            ),
            severity=Severity.PATIENT_SAFETY_CRITICAL,
            linked_gates=("RG-04", "RG-08"),
        ),
        AssessmentItem(
            item_id="DA-25",
            domain="Long-Horizon Reconstruction",
            question=(
                "Will a decision still be reconstructable for the full record retention period, "
                "after the model version that produced it is retired?"
            ),
            inspect=(
                "Retention obligations for the affected records against the availability "
                "guarantees for each model version, including vendor sunset terms"
            ),
            evidence_required=(
                "Record retention period for the affected quality records",
                "Retention plan for model versions, prompts, and configuration, or an archived "
                "surrogate sufficient to explain a past decision",
                "Vendor sunset and version-availability terms where applicable",
            ),
            pass_criteria=(
                "Reconstruction capability is guaranteed for at least the record retention "
                "period, not merely for the operational life of the model"
            ),
            disqualifying_finding=(
                "Records must be retained for longer than the model version that produced them "
                "will remain available, with no archived surrogate"
            ),
            severity=Severity.MAJOR,
            linked_gates=("RG-03", "RG-08"),
        ),
    ]


def items_by_id() -> dict[str, AssessmentItem]:
    return {item.item_id: item for item in assessment_items()}


def patient_safety_critical_ids() -> set[str]:
    return {
        item.item_id
        for item in assessment_items()
        if item.severity is Severity.PATIENT_SAFETY_CRITICAL
    }


@dataclass(frozen=True)
class Finding:
    item_id: str
    domain: str
    severity: Severity
    response: Response
    note: str


@dataclass(frozen=True)
class AssessmentResult:
    verdict: Verdict
    findings: tuple[Finding, ...]
    errors: tuple[str, ...]
    assessed_count: int
    total_count: int

    @property
    def blocking(self) -> tuple[Finding, ...]:
        return tuple(
            f for f in self.findings if f.severity is Severity.PATIENT_SAFETY_CRITICAL
        )

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "assessed_count": self.assessed_count,
            "total_count": self.total_count,
            "errors": list(self.errors),
            "findings": [
                {
                    "item_id": f.item_id,
                    "domain": f.domain,
                    "severity": f.severity.value,
                    "response": f.response.value,
                    "note": f.note,
                }
                for f in self.findings
            ],
            "disclaimer": DISCLAIMER,
        }


DISCLAIMER = (
    "This is a findings report produced by an assessment aid. It is not a compliance "
    "determination, release authorization, or regulatory clearance. Interpretation and "
    "sign-off require qualified QA, regulatory, and clinical-safety personnel."
)


def blank_response_template() -> dict:
    """A fully unanswered response file.

    Every item defaults to not_assessed so that an untouched template scores as
    BLOCKING_FINDINGS rather than silently passing.
    """
    return {
        "deployment_name": "",
        "assessed_by": "",
        "assessment_date": "",
        "responses": {
            item.item_id: {
                "response": Response.NOT_ASSESSED.value,
                "note": "",
                "evidence_reference": "",
            }
            for item in assessment_items()
        },
    }


def _parse_response(raw: object, item_id: str, errors: list[str]) -> Response | None:
    if not isinstance(raw, dict):
        errors.append(f"{item_id}: response entry must be an object")
        return None

    value = raw.get("response")
    if not isinstance(value, str):
        errors.append(f"{item_id}: missing 'response' field")
        return None

    try:
        return Response(value.strip().lower())
    except ValueError:
        permitted = ", ".join(r.value for r in Response)
        errors.append(f"{item_id}: invalid response {value!r}; permitted: {permitted}")
        return None


def score(submission: dict) -> AssessmentResult:
    """Evaluate a filled-in response file, fail-closed.

    Rules:
      - An item absent from the submission is treated as not_assessed.
      - not_assessed / partial / non_conformant all produce a finding.
      - not_applicable is only honored for items that permit it AND that carry
        a substantive justification; otherwise it is an error and treated as
        unresolved. Placeholder text such as "n/a" does not count.
      - Any unresolved patient-safety-critical item yields BLOCKING_FINDINGS.
      - Structural errors yield INVALID_SUBMISSION regardless of content.
    """
    errors: list[str] = []
    findings: list[Finding] = []
    assessed = 0

    if not isinstance(submission, dict):
        return AssessmentResult(
            verdict=Verdict.INVALID_SUBMISSION,
            findings=(),
            errors=("submission must be a JSON object",),
            assessed_count=0,
            total_count=len(assessment_items()),
        )

    raw_responses = submission.get("responses")
    if not isinstance(raw_responses, dict):
        raw_responses = {}
        errors.append("submission is missing a 'responses' object")

    unknown_ids = set(raw_responses) - set(items_by_id())
    for unknown in sorted(unknown_ids):
        errors.append(f"unknown item id in submission: {unknown}")

    for item in assessment_items():
        entry = raw_responses.get(item.item_id)

        if entry is None:
            findings.append(
                Finding(
                    item_id=item.item_id,
                    domain=item.domain,
                    severity=item.severity,
                    response=Response.NOT_ASSESSED,
                    note="Item missing from submission; treated as not assessed.",
                )
            )
            continue

        response = _parse_response(entry, item.item_id, errors)
        if response is None:
            findings.append(
                Finding(
                    item_id=item.item_id,
                    domain=item.domain,
                    severity=item.severity,
                    response=Response.NOT_ASSESSED,
                    note="Unparseable response; treated as not assessed.",
                )
            )
            continue

        note = str(entry.get("note", "")).strip()

        if response is Response.NOT_APPLICABLE:
            if not item.allows_not_applicable:
                errors.append(
                    f"{item.item_id}: not_applicable is not permitted for this item"
                )
                findings.append(
                    Finding(
                        item_id=item.item_id,
                        domain=item.domain,
                        severity=item.severity,
                        response=Response.NOT_ASSESSED,
                        note="Invalid not_applicable; treated as not assessed.",
                    )
                )
                continue
            if not is_substantive_justification(note):
                errors.append(
                    f"{item.item_id}: not_applicable requires a substantive justification "
                    f"of at least {MIN_JUSTIFICATION_CHARS} characters stating why the item "
                    f"is out of scope"
                )
                findings.append(
                    Finding(
                        item_id=item.item_id,
                        domain=item.domain,
                        severity=item.severity,
                        response=Response.NOT_ASSESSED,
                        note="Unjustified not_applicable; treated as not assessed.",
                    )
                )
                continue
            assessed += 1
            continue

        if response is Response.CONFORMANT:
            assessed += 1
            continue

        # partial / non_conformant are genuine assessments with an adverse
        # result. not_assessed is NOT an assessment and must not inflate the
        # completeness counter.
        if response is not Response.NOT_ASSESSED:
            assessed += 1

        findings.append(
            Finding(
                item_id=item.item_id,
                domain=item.domain,
                severity=item.severity,
                response=response,
                note=note or "No reviewer note supplied.",
            )
        )

    if errors:
        verdict = Verdict.INVALID_SUBMISSION
    elif any(f.severity is Severity.PATIENT_SAFETY_CRITICAL for f in findings):
        verdict = Verdict.BLOCKING_FINDINGS
    elif any(f.severity is Severity.MAJOR for f in findings):
        verdict = Verdict.MAJOR_FINDINGS
    elif findings:
        verdict = Verdict.MINOR_FINDINGS
    else:
        verdict = Verdict.NO_BLOCKING_FINDINGS_IDENTIFIED

    return AssessmentResult(
        verdict=verdict,
        findings=tuple(findings),
        errors=tuple(errors),
        assessed_count=assessed,
        total_count=len(assessment_items()),
    )


INSTRUMENT_INTRO = f"""This instrument is used against a deployment that is already
running, to gather objective evidence rather than to review design intent. It is the
operational counterpart to the design artifacts in this repository.

**{DISCLAIMER}**

## How to use it

1. Do not accept pre-prepared evidence packets. Select cases at random yourself.
2. Prefer observed system behavior over described system behavior. Where an item asks
   whether a control is enforced, attempt the prohibited action in a validated
   non-production environment.
3. Record `not_assessed` honestly. The scoring engine treats unassessed items as
   unresolved, which is the intended behavior - absence of evidence is not evidence of
   control.
4. `not_applicable` is accepted only for items that permit it, and only with a written
   justification stating why the item is out of scope. Placeholder text such as "n/a" is
   rejected, so scoping an item out is deliberately more effort than assessing it.

## Severity meaning

| Severity | Meaning |
|---|---|
| `patient_safety_critical` | An unresolved finding blocks the overall result. Patient impact is plausible. |
| `major` | Material control weakness requiring documented remediation. |
| `minor` | Improvement opportunity; does not block. |
"""


def build_instrument_markdown() -> str:
    lines: list[str] = []
    lines.append("# Clinical Deployment Assessment Instrument")
    lines.append("")
    lines.append(INSTRUMENT_INTRO)
    lines.append("## Assessment Item Summary")
    lines.append("")
    lines.append("| Item | Domain | Severity | Linked Gates |")
    lines.append("|---|---|---|---|")
    for item in assessment_items():
        gates = ", ".join(item.linked_gates) if item.linked_gates else "-"
        lines.append(
            f"| {item.item_id} | {item.domain} | `{item.severity.value}` | {gates} |"
        )
    lines.append("")

    current_domain = None
    for item in assessment_items():
        if item.domain != current_domain:
            current_domain = item.domain
            lines.append(f"## {current_domain}")
            lines.append("")

        na = " (may be marked not applicable with justification)" if item.allows_not_applicable else ""
        lines.append(f"### {item.item_id} - {item.question}")
        lines.append("")
        lines.append(f"- **Severity**: `{item.severity.value}`{na}")
        if item.linked_gates:
            lines.append(f"- **Linked gates**: {', '.join(item.linked_gates)}")
        lines.append(f"- **What to inspect**: {item.inspect}")
        lines.append("- **Evidence to request**:")
        for evidence in item.evidence_required:
            lines.append(f"    - {evidence}")
        lines.append(f"- **Pass criteria**: {item.pass_criteria}")
        lines.append(f"- **Disqualifying finding**: {item.disqualifying_finding}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_instrument_html() -> str:
    rows = "\n".join(
        "<tr>"
        f"<td><code>{_esc(item.item_id)}</code></td>"
        f"<td>{_esc(item.domain)}</td>"
        f"<td><span class=\"sev sev-{_esc(item.severity.value)}\">{_esc(item.severity.value)}</span></td>"
        f"<td>{_esc(', '.join(item.linked_gates) or '-')}</td>"
        "</tr>"
        for item in assessment_items()
    )

    detail_blocks = []
    for item in assessment_items():
        evidence = "".join(f"<li>{_esc(e)}</li>" for e in item.evidence_required)
        gates = (
            f"<p><strong>Linked gates:</strong> {_esc(', '.join(item.linked_gates))}</p>"
            if item.linked_gates
            else ""
        )
        na = (
            "<p class=\"na\">May be marked not applicable with a written justification "
            "stating why the item is out of scope.</p>"
            if item.allows_not_applicable
            else ""
        )
        detail_blocks.append(
            f"""      <article class="item">
        <h3><code>{_esc(item.item_id)}</code> {_esc(item.question)}</h3>
        <p class="meta">{_esc(item.domain)} &middot;
          <span class="sev sev-{_esc(item.severity.value)}">{_esc(item.severity.value)}</span></p>
        {gates}
        <p><strong>What to inspect:</strong> {_esc(item.inspect)}</p>
        <p><strong>Evidence to request:</strong></p>
        <ul>{evidence}</ul>
        <p><strong>Pass criteria:</strong> {_esc(item.pass_criteria)}</p>
        <p class="dq"><strong>Disqualifying finding:</strong> {_esc(item.disqualifying_finding)}</p>
        {na}
      </article>"""
        )

    details = "\n".join(detail_blocks)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Clinical Deployment Assessment Instrument</title>
  <style>
    :root {{
      --bg: #f7f7f2; --card: #ffffff; --ink: #1e1f24; --muted: #4d5562;
      --accent: #0c5ea8; --line: #d7dde5; --crit: #a31c1c; --major: #a86a00;
      --minor: #1f7a45;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; padding: 32px 20px; background: var(--bg); color: var(--ink);
      font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    .wrap {{ max-width: 1080px; margin: 0 auto; }}
    h1 {{ font-size: 26px; margin: 0 0 6px; }}
    h2 {{ font-size: 19px; margin: 28px 0 10px; padding-bottom: 6px;
      border-bottom: 2px solid var(--accent); }}
    h3 {{ font-size: 15px; margin: 0 0 4px; }}
    section, .disclaimer {{ background: var(--card); border: 1px solid var(--line);
      border-radius: 10px; padding: 18px 20px; margin-bottom: 16px; }}
    .disclaimer {{ border-left: 4px solid var(--crit); color: var(--muted); }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
    th, td {{ border: 1px solid var(--line); padding: 7px 9px; text-align: left;
      vertical-align: top; font-size: 13.5px; }}
    th {{ background: #eef4fb; }}
    code {{ background: #eef1f5; padding: 1px 5px; border-radius: 4px; font-size: 12.5px; }}
    .item {{ border-top: 1px solid var(--line); padding: 14px 0; }}
    .item:first-of-type {{ border-top: none; }}
    .meta {{ color: var(--muted); font-size: 12.5px; margin: 0 0 8px; }}
    .dq {{ color: var(--crit); }}
    .na {{ color: var(--muted); font-style: italic; font-size: 13px; }}
    .sev {{ font-size: 11.5px; font-weight: 600; padding: 2px 7px; border-radius: 20px;
      color: #fff; white-space: nowrap; }}
    .sev-patient_safety_critical {{ background: var(--crit); }}
    .sev-major {{ background: var(--major); }}
    .sev-minor {{ background: var(--minor); }}
    ul {{ margin: 4px 0 8px 18px; padding: 0; }}
    li {{ margin: 2px 0; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Clinical Deployment Assessment Instrument</h1>
    <p class="meta">Evidence-gathering tool for an AI-enabled QMS deployment already in production.</p>

    <div class="disclaimer">{_esc(DISCLAIMER)}</div>

    <section>
      <h2>Assessment Item Summary</h2>
      <table>
        <thead>
          <tr><th>Item</th><th>Domain</th><th>Severity</th><th>Linked Gates</th></tr>
        </thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </section>

    <section>
      <h2>Assessment Items</h2>
{details}
    </section>
  </div>
</body>
</html>
"""


def format_report(result: AssessmentResult) -> str:
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append(f"VERDICT: {result.verdict.value}")
    lines.append("=" * 72)
    lines.append(f"Items assessed: {result.assessed_count}/{result.total_count}")
    lines.append("")

    if result.errors:
        lines.append(f"SUBMISSION ERRORS ({len(result.errors)}):")
        for error in result.errors:
            lines.append(f"  ! {error}")
        lines.append("")

    if result.blocking:
        lines.append(f"BLOCKING - PATIENT SAFETY CRITICAL ({len(result.blocking)}):")
        for finding in result.blocking:
            lines.append(f"  [{finding.item_id}] {finding.domain} - {finding.response.value}")
            lines.append(f"      {finding.note}")
        lines.append("")

    other = [f for f in result.findings if f.severity is not Severity.PATIENT_SAFETY_CRITICAL]
    if other:
        lines.append(f"OTHER FINDINGS ({len(other)}):")
        for finding in other:
            lines.append(
                f"  [{finding.item_id}] {finding.severity.value} - "
                f"{finding.domain} - {finding.response.value}"
            )
        lines.append("")

    if not result.findings and not result.errors:
        lines.append("No findings recorded against the instrument.")
        lines.append("")

    lines.append(DISCLAIMER)
    return "\n".join(lines)


def write_instrument(out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / "clinical_deployment_assessment.md"
    html_path = out_dir / "clinical_deployment_assessment.html"
    md_path.write_text(build_instrument_markdown(), encoding="utf-8")
    html_path.write_text(build_instrument_html(), encoding="utf-8")
    return md_path, html_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Clinical deployment assessment instrument and scoring engine.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_inst = sub.add_parser("instrument", help="Generate the reviewer instrument.")
    p_inst.add_argument(
        "--outdir", type=Path, default=Path(__file__).resolve().parent,
        help="Output directory (default: directory containing this script).",
    )

    p_tmpl = sub.add_parser("template", help="Emit a blank response file.")
    p_tmpl.add_argument(
        "--out", type=Path, default=None,
        help="Destination file (default: stdout).",
    )

    p_score = sub.add_parser("score", help="Score a filled-in response file.")
    p_score.add_argument("responses", type=Path, help="Path to the response JSON file.")
    p_score.add_argument("--json", action="store_true", help="Emit JSON instead of text.")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "instrument":
        md_path, html_path = write_instrument(args.outdir)
        print(f"Generated: {md_path}")
        print(f"Generated: {html_path}")
        return 0

    if args.command == "template":
        payload = json.dumps(blank_response_template(), indent=2)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(payload + "\n", encoding="utf-8")
            print(f"Wrote blank response template: {args.out}")
        else:
            print(payload)
        return 0

    # score
    try:
        submission = json.loads(args.responses.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: no such file: {args.responses}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {args.responses}: {exc}", file=sys.stderr)
        return 2

    result = score(submission)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(format_report(result))

    # Non-zero exit for anything that is not clean, so this can gate a pipeline.
    return 0 if result.verdict is Verdict.NO_BLOCKING_FINDINGS_IDENTIFIED else 1


if __name__ == "__main__":
    raise SystemExit(main())
