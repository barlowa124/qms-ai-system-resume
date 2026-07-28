---
marp: true
theme: default
paginate: true
title: "When Efficiency Targets Meet Patient Safety"
---

# When Efficiency Targets Meet Patient Safety

### Failure modes in AI-assisted deviation management, and an instrument for assessing a live deployment

_This presentation describes generalized failure modes in AI-assisted quality systems. It does not identify any employer, client, vendor, or product, and it is not a compliance determination about any specific system. The assessment instrument shown is a reviewer aid; interpretation and sign-off require qualified QA, regulatory, and clinical-safety personnel._

<!--
Speaker notes: Open by setting scope honestly: this is not an argument that AI has no place in quality systems. It is an argument that deviation management is an unusually bad place to start, and that the assessment tooling the industry has does not yet ask the right questions. Say up front that no employer or client is named and nothing here is a compliance determination about any specific system.
-->

---

## Why bring this to a training centre

- You prepare the QA analysts, manufacturing associates, and technicians who will operate these systems.
- In every deployment I have seen, the safety case rests on a human reviewer catching the model's mistakes.
- That human is your graduate.
- Training on how to operate the system is not the same as training on how it fails.

> The control that regulators, vendors, and quality leadership all rely on is the one nobody is specifically trained for.

<!--
Speaker notes: This is the hook. Establish immediately that this is their problem and not just an industry problem. Every AI-assisted quality system is justified on the basis that a qualified human reviews the output. The entire safety argument therefore depends on the competence of the reviewer, and reviewer training is a curriculum question. Do not rush this slide.
-->

---

## What deviation management actually decides

- A deviation is any departure from an approved procedure, specification, or process parameter.
- Triage decides three things: is this patient-impacting, how deep does the investigation go, and does it affect batch disposition.
- Those decisions feed CAPA, product release, and regulatory reporting.

> Misclassifying a deviation is not an efficiency miss. It is the first step in a chain that ends at product release.

<!--
Speaker notes: Spend time here even though the audience knows it. The point being established is that deviation triage is a decision with downstream safety consequences, not a clerical sorting task. Everything later depends on the audience accepting this. If someone pushes back that triage is only advisory, ask what happens when a minor classification means no investigation is opened.
-->

---

## Why it is an attractive place to deploy AI

- High volume, text-heavy, and repetitive - the exact profile language models handle well.
- Chronic backlog. Investigation cycle time is a standing audit observation at many sites.
- Typical business case: 40 percent reduction in triage time, 25 percent reduction in CAPA cycle time.
- Those numbers are real and achievable. That is what makes this hard.

> Present the business case fairly. The people who build these systems are not reckless; they are responding to genuine operational pressure.

<!--
Speaker notes: Resist the temptation to strawman the business case. If the audience thinks you are hostile to the technology, credibility is gone. The efficiency gains are real, the backlog pressure is real, and the people driving these programs are usually competent and well-intentioned. The problem is not motive.
-->

---

## The uncomfortable part: it works in the demo

- Aggregate accuracy on a validation set looks strong.
- Reviewers report that it saves them time and they like using it.
- Cycle-time metrics improve, visibly, in the first quarter.
- Every stakeholder sees confirmation that the decision was correct.

> A system that failed obviously would be safe. The dangerous case is the one that succeeds on every metric anyone is currently measuring.

<!--
Speaker notes: This is the pivot of the talk. The failure modes that follow are not detectable by the metrics these programs are governed by. That is the structural problem: success indicators and safety indicators are different quantities, and only one set is on the dashboard.
-->

---

## The asymmetry nobody closes

- Design-time review asks: is this system well designed and validated?
- That question gets asked thoroughly, by qualified people, with documented outcomes.
- Field assessment asks: is the system running right now still the one we validated?
- In my experience that second question has no owner, no cadence, and no instrument.

> Validation is a point-in-time event. An AI-assisted system drifts continuously, and much of the drift is invisible to change control as currently written.

<!--
Speaker notes: Name the gap precisely, because the rest of the talk is four instances of it plus a proposed instrument. Expect a question about periodic review. The answer is that periodic review as typically practised re-reads the documentation rather than interrogating the running system.
-->

---

## Failure mode 1 - Automation bias

- Observed pattern: 99.4 percent acceptance rate, 11 second median dwell time on high-risk cases.
- Human review is documented, enforced in the workflow, and present in every audit trail.
- Eleven seconds is not enough to read the deviation, let alone evaluate the recommendation.
- The control exists, is inspectable, and is not functioning.

> Teaching point: measure override rate and dwell time, segmented by risk class, queue depth, and shift position. Aggregate figures hide this.

<!--
Speaker notes: This is the most important failure mode because it defeats the control the whole safety case rests on, and it does so while producing perfect documentary evidence of compliance. Emphasise that the reviewers are not lazy - a system that is right 95 percent of the time trains you to trust it, and that training is rational. Automation bias is well established in aviation and radiology literature; this is not speculative.
-->

---

## Failure mode 2 - Silent truncation

- A long batch record or investigation file exceeds the model's input limit.
- It is truncated at ingest, or a scanned page silently fails to parse.
- The model reasons over partial data and returns a normal, confident assessment.
- The output is indistinguishable from one based on the complete record.

> No one is at fault and no one can tell. The reviewer cannot catch an omission they have no way to see.

<!--
Speaker notes: This is the cleanest example of the unintentional failure class. There is no attacker, no negligence, and no procedural violation. A competent reviewer following the procedure correctly signs off on an assessment built from incomplete input. Ask the audience how their graduates would detect this. The answer is that they cannot, which is why it has to be a system control.
-->

---

## Failure mode 3 - The validated system stops being the running system

- A prompt template is edited to make the wording clearer.
- An inference parameter or routing threshold is retuned.
- The OCR engine or document parser is upgraded as routine infrastructure maintenance.
- None of these is a model change, so none reliably triggers change control.

> Change control as written governs the model. The behaviour of the system is determined by the model plus everything around it.

<!--
Speaker notes: The OCR upgrade is the one that lands hardest with technical audiences, because it is performed by an infrastructure team that has no idea it is touching a GxP-relevant path, as part of routine patching. It changes what the model sees on every case. Nothing in a conventional change control procedure would flag it.
-->

---

## Failure mode 4 - Unbounded blast radius

- A defect in a model version is confirmed at month six.
- The necessary question is: which records did it touch?
- Reconstructing one case on demand is a different capability from enumerating every affected case.
- Without the second, a confirmed defect cannot be scoped, and therefore cannot be remediated or reported.

> Most systems can answer 'what happened in this case'. Far fewer can answer 'what else did this affect'.

<!--
Speaker notes: This is the failure mode with the most direct regulatory consequence. Impact assessment and, where warranted, field action both depend on being able to bound the affected population. A traceability capability built for single-case investigation readiness does not automatically give you cohort enumeration by model version and date range. Nobody discovers this until they need it.
-->

---

## The common thread

- In all four cases: a competent person, following the correct procedure, receives a wrong result with no signal that anything went wrong.
- No malice. No negligence. No attacker. No procedural violation.
- The controls are documented, inspectable, and present in the audit trail.
- They are also, in the specific conditions described, not working.

> The threat model that matters here is internal and unintentional. Security testing aimed at adversaries will not find any of this.

<!--
Speaker notes: Land this explicitly. Most AI risk discussion is about misuse, prompt injection, or data exfiltration. Those are real but they are not the dominant risk in a controlled internal GMP environment where every user is authenticated, trained, and trying to do their job correctly. The dominant risk is silent wrongness.
-->

---

## Why this is a patient safety question

- Deviation classification determines investigation depth.
- Investigation depth determines what is known at disposition.
- Disposition determines whether product is released.
- The path from a misclassified deviation to a patient is short and well-trodden.

> Data integrity expectations - ALCOA+, Part 11, Annex 11 - exist because quality records drive release decisions. An AI-generated record is still a record.

<!--
Speaker notes: This slide converts the preceding technical material into the language the audience governs by. If anyone in the room still thinks of this as an IT validation topic, this is where that changes. Keep the chain short and concrete; do not overclaim that harm has occurred.
-->

---

## Why existing frameworks do not catch it

- Computer system validation establishes fitness at a point in time; these systems drift continuously.
- Risk-based categorisation assumes deterministic input-output behaviour.
- Annex 11 and Part 11 predate language models and say nothing about acceptance-rate monitoring or context-window limits.
- None of these frameworks is wrong. They are necessary and currently insufficient.

> The gap is not a failure of the existing framework. It is a category the framework was not written to cover.

<!--
Speaker notes: Be careful and generous here. This audience teaches these frameworks. The argument is additive, not dismissive: the existing apparatus is sound for deterministic systems and needs a supplement for probabilistic ones. If you come across as saying validation is broken, you lose the room.
-->

---

## What I built in response

- A 25-item assessment instrument for a deployment that is already running, not a design under review.
- Each item specifies what to inspect, what evidence to request, an objective pass criterion, and a disqualifying finding.
- Items are traced to named release gates, so a finding maps to a control someone owns.
- Reviewer-administered, with a scoring engine that produces a findings report.

> The instrument is the deliverable I would want to hand to a QA reviewer who has one day on site and no prior AI background.

<!--
Speaker notes: Transition from problem to contribution. The important design choice is that every item asks for observed system behaviour or a retrievable artifact, never for an opinion or a self-rating. A reviewer with no machine learning background can execute it, which is the point.
-->

---

## The design principle: fail closed

- An item recorded as not assessed counts as unresolved, exactly like a failure.
- An untouched template therefore scores as blocking, not as passing.
- Any single unresolved patient-safety item forces a blocking result regardless of the other 24.
- The cleanest available verdict is 'no blocking findings identified' - never 'approved'.

> Absence of evidence is not evidence of control. Most maturity assessments score the opposite way, and that is how a deployment passes review without anyone having looked.

<!--
Speaker notes: This is the slide a technical audience will engage with most. The default behaviour of almost every scorecard is that unanswered questions are silently excluded from the denominator, which means an assessment nobody completed can look like a pass. Inverting that default is the single most important property of the tool.
-->

---

## What it produces

```text
$ deployment_assessment.py score site_a_responses.json

========================================================================
VERDICT: BLOCKING_FINDINGS
========================================================================
Items assessed: 25/25

BLOCKING - PATIENT SAFETY CRITICAL (1):
  [DA-03] Human Oversight in Practice - non_conformant
      Acceptance rate 99.4% with 11s median dwell on high-risk cases.

OTHER FINDINGS (1):
  [DA-09] major - Human-AI Compatibility - partial

$ echo $?
1
```

<!--
Speaker notes: Walk through the output slowly. Three things to point out: the verdict language avoids any implication of approval; the finding cites the specific observed metric rather than a judgement; and the non-zero exit code means this can gate an automated release pipeline rather than living in a document nobody reads. If there is time and network access, run it live - it is more convincing than a screenshot.
-->

---

## Limitations I want to state plainly

- Entirely self-attested. There is no evidence hashing and no reviewer independence check - a vendor could complete it about its own product.
- 18 of 25 items block. A well-run deployment will likely still fail on first pass, which risks the verdict carrying no discriminating information.
- Never validated against real inspection outcomes. I do not know whether it predicts anything.
- Point-in-time. It has no expiry, and nothing forces reassessment after a model or infrastructure change.

> High line coverage on the scoring engine proves the logic is consistent. It says nothing about whether the rubric is correctly calibrated.

<!--
Speaker notes: Do not skip this slide, and do not apologise through it. Volunteering the weaknesses is what separates an analysis from an advocacy pitch, and this audience will find these problems anyway. The calibration issue is the one worth genuinely asking their opinion on - if nearly everything blocks, the instrument stops distinguishing a careless deployment from a careful one.
-->

---

## The conclusion I drew

- I could not get these failure modes closed on a timeline I was comfortable with, in a context where the failure path reaches product disposition.
- I concluded that I did not want to hold accountability for a control I could not demonstrate was working.
- So I resigned, and I built the instrument I wished had existed.
- I am not claiming harm occurred. I am claiming the assessment that would have told us either way was not being performed.

> The distinction matters: an unassessed risk is not the same claim as a realised harm, and it is the one I can actually support.

<!--
Speaker notes: One slide, stated once, then move on. Do not editorialise and do not name anyone. The final bullet is the most important sentence in the deck - it is precise, defensible, and it is what makes the whole talk credible rather than aggrieved. If asked for specifics you cannot share, say plainly that you are bound by confidentiality and that the generalized failure modes are the transferable content.
-->

---

## The curriculum gap

- Reviewer training today covers system operation: how to log in, where to click, how to record a decision.
- It does not cover the failure modes of the specific system, which is what the reviewer is there to catch.
- Concretely teachable: automation bias and why high accuracy causes it; what incomplete input looks like; how to ask whether the system in front of you is the validated one.
- One instrument item exists solely to check that reviewers are trained on named failure modes rather than general operation.

> Your graduates are the last control in the chain. Right now they are being trained as operators of the system rather than as auditors of it.

<!--
Speaker notes: This is the ask, and it should feel like a contribution rather than a complaint. Offer something concrete: a guest module, a case-study exercise built from the four failure modes, or the instrument itself as a teaching artifact. Have a specific next step ready if anyone is interested.
-->

---

## Questions I would like your view on

- Is 18 of 25 items blocking the right calibration, or does it make the instrument useless in practice?
- Should the blocking set vary with the system's risk class rather than being fixed?
- Where does this belong in a curriculum - validation, quality systems, or its own module?
- What would convince you that a reviewer is genuinely competent to oversee a model rather than nominally assigned to it?

<!--
Speaker notes: Ending on genuine questions rather than a summary invites collaboration and signals that you are not there to lecture them. These four are real open problems, not rhetorical. Have your own tentative answer ready for each in case they turn it back on you.
-->
