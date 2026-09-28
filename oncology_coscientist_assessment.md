========================================================================
VERDICT: BLOCKING_FINDINGS
========================================================================
Items assessed: 25/25

BLOCKING - PATIENT SAFETY CRITICAL (10):
  [DA-01] Intended Use and Regulatory Status - non_conformant
      README limits the system to public retrospective TCGA data and states results reflect the dataset, not any clinical use. No regulatory classification exists or was sought. This is correct for a research tool, but any clinical framing is blocked.
  [DA-02] Human Oversight in Practice - partial
      The approval gate is a technical control: approve() refuses when the report bytes or the agent_run hash changed since render, and the API returns 409 on tamper. No production case sample exists to demonstrate observed enforcement.
  [DA-03] Human Oversight in Practice - partial
      Approvals record reviewer identity and an optional note, but nothing measures whether the reviewer engaged with the content versus rubber-stamping.
  [DA-06] Model Validation and Performance - partial
      Models are evaluated on held-out splits and checks abstain a model when integrity fails, but performance is characterized per cohort, not per clinically meaningful subgroup.
  [DA-08] Change Control - partial
      Every run binds code and config through git_sha and config_sha256, so the change history is auditable, but there are no approved change records or a documented change-control workflow.
  [DA-11] Safety Signal and Incident Handling - non_conformant
      No defined path from an AI-related error to containment, CAPA, or regulatory reporting exists. Defects are handled informally through git.
  [DA-13] Third-Party and Supply Chain - partial
      The agent runs a local Ollama model whose model_id is recorded per run; there is no vendor change-notification or data-handling contract because the model is local and open-weight. Version pinning remains informal.
  [DA-16] Use Outside the Validated Envelope - non_conformant
      No production usage monitoring against a validated population exists; out-of-envelope use is possible and unmonitored.
  [DA-20] Retrospective Impact Assessment - partial
      Runs carry model_id and config hashes so every record a model version touched is enumerable. No re-review workflow exists to act on that enumeration.
  [DA-21] Degraded Mode and Fallback - partial
      The recorded backend lets runs proceed without the live model. No documented manual fallback procedure defines degraded operation.

OTHER FINDINGS (6):
  [DA-07] major - Model Validation and Performance - non_conformant
  [DA-09] major - Human-AI Compatibility - partial
  [DA-12] major - Reviewer Competency - non_conformant
  [DA-14] major - Security and Misuse Resilience - partial
  [DA-19] major - Repeat Submission and Anchoring - partial
  [DA-25] major - Long-Horizon Reconstruction - partial

This is a findings report produced by an assessment aid. It is not a compliance determination, release authorization, or regulatory clearance. Interpretation and sign-off require qualified QA, regulatory, and clinical-safety personnel.
