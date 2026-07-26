# Clinical Deployment Assessment Instrument

This instrument is used against a deployment that is already
running, to gather objective evidence rather than to review design intent. It is the
operational counterpart to the design artifacts in this repository.

**This is a findings report produced by an assessment aid. It is not a compliance determination, release authorization, or regulatory clearance. Interpretation and sign-off require qualified QA, regulatory, and clinical-safety personnel.**

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

## Assessment Item Summary

| Item | Domain | Severity | Linked Gates |
|---|---|---|---|
| DA-01 | Intended Use and Regulatory Status | `patient_safety_critical` | RG-01 |
| DA-02 | Human Oversight in Practice | `patient_safety_critical` | RG-04 |
| DA-03 | Human Oversight in Practice | `patient_safety_critical` | RG-04 |
| DA-04 | Data Integrity (ALCOA+) | `patient_safety_critical` | RG-08 |
| DA-05 | Traceability and Investigation Readiness | `patient_safety_critical` | RG-08, RG-02 |
| DA-06 | Model Validation and Performance | `patient_safety_critical` | RG-06 |
| DA-07 | Model Validation and Performance | `major` | RG-06 |
| DA-08 | Change Control | `patient_safety_critical` | RG-05 |
| DA-09 | Human-AI Compatibility | `major` | RG-09 |
| DA-10 | Reproducibility | `major` | RG-06 |
| DA-11 | Safety Signal and Incident Handling | `patient_safety_critical` | RG-04 |
| DA-12 | Reviewer Competency | `major` | RG-04 |
| DA-13 | Third-Party and Supply Chain | `patient_safety_critical` | RG-03, RG-05 |
| DA-14 | Security and Misuse Resilience | `major` | RG-07 |
| DA-15 | In-Silico / Virtualization Evidence | `patient_safety_critical` | RG-06 |
| DA-16 | Use Outside the Validated Envelope | `patient_safety_critical` | RG-01, RG-06 |
| DA-17 | Silent Truncation and Incomplete Input | `patient_safety_critical` | RG-04, RG-08 |
| DA-18 | Configuration Drift | `patient_safety_critical` | RG-05 |
| DA-19 | Repeat Submission and Anchoring | `major` | RG-08, RG-04 |

## Intended Use and Regulatory Status

### DA-01 - Is the intended use documented, and has the regulatory status of the AI component been formally determined?

- **Severity**: `patient_safety_critical`
- **Linked gates**: RG-01
- **What to inspect**: Intended-use statement, user population, clinical/patient impact analysis, and the written determination of whether the AI meets the definition of a medical device / SaMD, or an EU AI Act high-risk system
- **Evidence to request**:
    - Signed intended-use statement
    - Regulatory classification rationale with named accountable approver
    - Legal/regulatory affairs concurrence record
- **Pass criteria**: A documented, approved determination exists and is consistent with how the system is actually used in production
- **Disqualifying finding**: The AI influences clinical or patient-impacting decisions with no documented regulatory classification, or actual use exceeds the stated intended use

## Human Oversight in Practice

### DA-02 - Is human review actually enforced for patient-impacting decisions, as observed in production data rather than in policy?

- **Severity**: `patient_safety_critical`
- **Linked gates**: RG-04
- **What to inspect**: A random sample of closed high-risk cases; attempt (in a validated non-production environment) to close a high-risk case without reviewer sign-off
- **Evidence to request**:
    - Sample of >=20 closed high-risk cases with reviewer identity and timestamp
    - System behavior record when sign-off is omitted
    - Override log with captured rationale
- **Pass criteria**: Every sampled patient-impacting closure carries an accountable reviewer sign-off, and the system technically prevents closure without one
- **Disqualifying finding**: Any patient-impacting record closed without human sign-off, or oversight enforced only by procedure with no technical control

### DA-03 - Is there evidence that reviewers exercise independent judgment rather than rubber-stamping AI output (automation bias)?

- **Severity**: `patient_safety_critical`
- **Linked gates**: RG-04
- **What to inspect**: Acceptance and override rates segmented by reviewer, risk class, and time; median review dwell time relative to case complexity
- **Evidence to request**:
    - Acceptance-rate distribution across reviewers
    - Override events with substantive rationale text
    - Dwell-time distribution for high-risk cases
- **Pass criteria**: Override rate is non-zero for high-risk classes, rationale text is substantive, and dwell time is plausible for the decision complexity
- **Disqualifying finding**: Near-100% acceptance with negligible dwell time, indicating oversight is nominal rather than genuine

## Data Integrity (ALCOA+)

### DA-04 - Are audit trails for AI inputs, outputs, approvals, and overrides complete and tamper-evident?

- **Severity**: `patient_safety_critical`
- **Linked gates**: RG-08
- **What to inspect**: Audit trail configuration, retention settings, administrator privileges, and whether records can be altered or deleted without detection
- **Evidence to request**:
    - Audit trail integrity check output
    - Privileged-access review showing who can modify records
    - Retention policy aligned to record class
- **Pass criteria**: Audit trails are immutable or tamper-evident, cover model calls end to end, and no unlogged privileged path can alter quality records
- **Disqualifying finding**: Any administrator can silently alter or delete quality records, or model invocations are not logged

## Traceability and Investigation Readiness

### DA-05 - Can a specific closed case be reconstructed end to end, on demand, from source data through model version to final disposition?

- **Severity**: `patient_safety_critical`
- **Linked gates**: RG-08, RG-02
- **What to inspect**: Live reconstruction of a reviewer-selected closed case, timed
- **Evidence to request**:
    - Investigator packet for a case chosen by the reviewer, not pre-prepared
    - Model and prompt version bound to that specific decision
    - Source data lineage for the inputs used
- **Pass criteria**: Reconstruction succeeds within the documented service-level objective and identifies the exact model/prompt version that produced the output
- **Disqualifying finding**: The deployed model version for a historical decision cannot be established

## Model Validation and Performance

### DA-06 - Was the model validated on data independent of training, with performance characterized per clinically meaningful subgroup?

- **Severity**: `patient_safety_critical`
- **Linked gates**: RG-06
- **What to inspect**: Validation protocol and report, dataset provenance, train/test separation controls, and subgroup performance breakdown
- **Evidence to request**:
    - Validation protocol approved before execution
    - Evidence of train/test independence
    - Performance by risk class and relevant patient subgroups
    - Documented acceptance criteria set in advance
- **Pass criteria**: Independence is demonstrable, acceptance criteria were pre-specified and met, and subgroup performance is reported rather than only aggregate
- **Disqualifying finding**: Aggregate-only performance claims, post-hoc acceptance criteria, or unresolvable train/test contamination

### DA-07 - Is performance drift monitored in production against defined thresholds with a defined response?

- **Severity**: `major`
- **Linked gates**: RG-06
- **What to inspect**: Drift monitoring dashboard, threshold definitions, alert history, and actions taken on past alerts
- **Evidence to request**:
    - Threshold definitions per case class
    - Alert history with dispositions
    - Evidence of at least one closed-loop response to a drift signal
- **Pass criteria**: Thresholds are defined, alerts route to an accountable owner, and past alerts show documented resolution
- **Disqualifying finding**: Drift is unmonitored, or alerts have accumulated without disposition

## Change Control

### DA-08 - Does every model, prompt, and calibration-data change in the production history have an approved change record?

- **Severity**: `patient_safety_critical`
- **Linked gates**: RG-05
- **What to inspect**: Model registry version history reconciled against change tickets for the trailing 12 months
- **Evidence to request**:
    - Complete deployed-version history with dates
    - Corresponding change tickets with risk assessment and rollback plan
    - Reconciliation showing no unmatched deployments
- **Pass criteria**: Every production version maps to an approved change record with no gaps
- **Disqualifying finding**: Any undocumented production model or prompt change

## Human-AI Compatibility

### DA-09 - For each model update, was backward compatibility assessed so that previously-correct decisions were not silently regressed?

- **Severity**: `major`
- **Linked gates**: RG-09
- **What to inspect**: Compatibility reports attached to change records, and reviewer acceptance-rate behavior immediately following each update
- **Evidence to request**:
    - Backward compatibility score per update, segmented by risk class
    - Newly-introduced-error analysis on a frozen evaluation set
    - Reviewer notification records where compatibility was knowingly broken
- **Pass criteria**: Compatibility is measured per update, and any breach affecting a patient-safety class carries documented justification plus reviewer notification
- **Disqualifying finding**: Updates promoted on aggregate accuracy alone, with no compatibility analysis for patient-safety case classes

## Reproducibility

### DA-10 - Can a past AI decision be re-derived within a defined tolerance?

- **Severity**: `major`
- **Linked gates**: RG-06
- **What to inspect**: Replay of a reviewer-selected historical case against its recorded model version
- **Evidence to request**:
    - Replay harness output with input/output hashes
    - Documented tolerance and rationale for non-deterministic components
    - Sampling frequency and recent pass rate
- **Pass criteria**: Sampled replays meet the documented tolerance, and any non-determinism is characterized rather than unexplained
- **Disqualifying finding**: Historical decisions cannot be reproduced and the variance is uncharacterized

## Safety Signal and Incident Handling

### DA-11 - Is there a defined path from an AI-related error to containment, CAPA, and where applicable regulatory reporting?

- **Severity**: `patient_safety_critical`
- **Linked gates**: RG-04
- **What to inspect**: Incident history involving AI output, escalation timestamps, and CAPA effectiveness checks
- **Evidence to request**:
    - AI-related incident log
    - Time-to-containment for past incidents
    - CAPA records with effectiveness verification
    - Reportability decision records where patient impact occurred
- **Pass criteria**: Incidents are captured, escalated within SLA, and CAPA effectiveness is verified rather than assumed closed
- **Disqualifying finding**: A known AI-caused patient-impacting error with no CAPA or no reportability assessment

## Reviewer Competency

### DA-12 - Are reviewers trained specifically on the AI system's known failure modes and limitations?

- **Severity**: `major`
- **Linked gates**: RG-04
- **What to inspect**: Training curriculum content, completion records, and whether training is reissued when model behavior changes
- **Evidence to request**:
    - Curriculum covering documented failure modes
    - Completion records for all active reviewers
    - Retraining triggered by compatibility-breaking updates
- **Pass criteria**: All active reviewers are current on training that names concrete failure modes, not just general system operation
- **Disqualifying finding**: Reviewers accountable for patient-impacting sign-off have no training on AI limitations

## Third-Party and Supply Chain

### DA-13 - If an external or vendor model is used, are version pinning, change notification, and data handling contractually and technically controlled?

- **Severity**: `patient_safety_critical` (may be marked not applicable with justification)
- **Linked gates**: RG-03, RG-05
- **What to inspect**: Vendor agreements, model version pinning configuration, and data processing terms covering any PHI or patient-identifiable input
- **Evidence to request**:
    - Contractual change-notification terms
    - Evidence of version pinning in production configuration
    - Data processing agreement covering the data classes actually sent
- **Pass criteria**: Vendor model versions cannot change silently, and data handling matches what is contractually permitted
- **Disqualifying finding**: Production depends on a floating vendor model endpoint that can change without notice, or patient data is sent outside agreed terms

## Security and Misuse Resilience

### DA-14 - Has the system been tested against adversarial input and misuse relevant to its clinical context?

- **Severity**: `major`
- **Linked gates**: RG-07
- **What to inspect**: Adversarial test suite scope, findings, and remediation status; access controls on model configuration
- **Evidence to request**:
    - Adversarial/misuse test results with severity ratings
    - Remediation evidence for critical findings
    - Access control review for prompt and model configuration
- **Pass criteria**: Misuse testing covers the deployed clinical context, and open findings have an owner and a remediation plan
- **Disqualifying finding**: No misuse testing has been performed for the deployed clinical context, or open findings have no owner or remediation plan. A confirmed exploitable defect in a patient-impacting pathway should be escalated as a safety signal under DA-11 rather than recorded only here

## In-Silico / Virtualization Evidence

### DA-15 - If in-silico or virtual organ model output supports a regulatory or safety-relevant conclusion, is it cross-validated against ground truth?

- **Severity**: `patient_safety_critical` (may be marked not applicable with justification)
- **Linked gates**: RG-06
- **What to inspect**: Correlation studies against wet-lab or clinical data, and the qualification tier assigned to each model's use
- **Evidence to request**:
    - Correlation study protocol and results
    - Qualification tier with submission-use flag
    - Drift monitoring against ground-truth refresh
- **Pass criteria**: Ground-truth correlation is documented and current for the claimed use tier
- **Disqualifying finding**: In-silico output supports a submission or safety conclusion with no ground-truth correlation evidence

## Use Outside the Validated Envelope

### DA-16 - Is actual production usage monitored against the population the system was validated on, and are out-of-envelope inputs detected at the point of use?

- **Severity**: `patient_safety_critical`
- **Linked gates**: RG-01, RG-06
- **What to inspect**: Usage telemetry broken down by case type, product, site, and language, compared against the validation population; the runtime behaviour when an input falls outside that population
- **Evidence to request**:
    - Validation population definition with the case types and products covered
    - Production usage distribution over a recent period, on the same axes
    - Runtime evidence that an out-of-envelope input is flagged or refused
- **Pass criteria**: Production usage is shown to fall inside the validated population, and inputs outside it are flagged to the user rather than answered silently
- **Disqualifying finding**: The system returns normal-looking output for case types, products, or sites absent from the validation set, with no indication to the user that the input is outside the validated envelope

## Silent Truncation and Incomplete Input

### DA-17 - When input exceeds size limits or a source document fails to parse, does the system fail visibly rather than reason over partial data?

- **Severity**: `patient_safety_critical`
- **Linked gates**: RG-04, RG-08
- **What to inspect**: Context and token limit handling, document parse and OCR failure paths, and what the reviewer sees when input is incomplete
- **Evidence to request**:
    - Truncation and parse-failure logs for a recent production period
    - Screenshot or specification of the user-visible indication when input is incomplete
    - A worked example of a long or partly unreadable record and its handling
- **Pass criteria**: Truncation and parse failure are logged and surfaced to the reviewer before sign-off, and the affected output is marked as based on incomplete input
- **Disqualifying finding**: Input is silently truncated or a source document silently fails to parse, and the reviewer sees output that is indistinguishable from a complete assessment

## Configuration Drift

### DA-18 - Are prompt templates, inference parameters, and thresholds under the same change control as the model itself?

- **Severity**: `patient_safety_critical`
- **Linked gates**: RG-05
- **What to inspect**: Change history for prompt templates, temperature and sampling settings, retrieval configuration, and routing or escalation thresholds
- **Evidence to request**:
    - Diff-level change log for prompts and inference parameters
    - QA review record for each production-affecting change
    - Evidence that production configuration matches the validated configuration
- **Pass criteria**: No production-affecting configuration change reaches users without a review record, and current production configuration matches what was validated
- **Disqualifying finding**: A prompt, parameter, or threshold differs from the validated configuration, or was changed in production without a review record

## Repeat Submission and Anchoring

### DA-19 - When the same event is submitted more than once, is the full sequence of outputs retained rather than only the one the reviewer accepted?

- **Severity**: `major`
- **Linked gates**: RG-08, RG-04
- **What to inspect**: Audit trail for a single event identifier that received multiple submissions, and whether superseded outputs remain retrievable
- **Evidence to request**:
    - Audit trail showing every submission and output for one event identifier
    - Rate of repeat submission per event over a recent period
    - Evidence that superseded outputs are retained and linked to the final record
- **Pass criteria**: All submissions for an event are retained and linked, so a reviewer or inspector can see whether the accepted output was the first one
- **Disqualifying finding**: Only the accepted output is retained, so re-running an event until a milder result appears would leave no trace
