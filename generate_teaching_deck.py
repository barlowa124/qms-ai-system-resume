"""Generate the teaching deck on AI failure modes in GMP-adjacent QMS.

Audience: faculty at a biomanufacturing training and education centre who prepare
the QA and manufacturing workforce that will operate AI-assisted quality systems.

Framing decisions, deliberate:
  - The deployment discussed is de-identified throughout. No employer, client,
    vendor, or product is named. Every failure mode is stated generically enough
    to apply to any AI-assisted deviation-management deployment.
  - The content is the failure modes and the assessment instrument. The speaker's
    resignation is a single late slide stated as a conclusion, not a thesis.
  - Limitations are presented explicitly. An academic audience discounts a deck
    that only argues one way.

Outputs a Marp-compatible markdown deck (with speaker notes) and a standalone
HTML deck that presents in a browser and prints to PDF.
"""

from __future__ import annotations

import argparse
import html
import sys
from dataclasses import dataclass, field
from pathlib import Path

DECK_TITLE = "When Efficiency Targets Meet Patient Safety"
DECK_SUBTITLE = (
    "A prospective risk analysis of AI-assisted deviation report review, and an "
    "instrument for assessing a live deployment"
)

DISCLAIMER = (
    "This presentation describes generalized failure modes in AI-assisted quality "
    "systems. It does not identify any employer, client, vendor, or product, and it "
    "is not a compliance determination about any specific system. The system that "
    "motivated this analysis did not reach deployment, so nothing here is an account "
    "of a production failure. The assessment instrument shown is a reviewer aid; "
    "interpretation and sign-off require qualified QA, regulatory, and "
    "clinical-safety personnel."
)


@dataclass(frozen=True)
class Slide:
    """One slide. `notes` is what the speaker says, not what the audience reads."""

    title: str
    kind: str = "content"
    subtitle: str = ""
    bullets: tuple[str, ...] = ()
    callout: str = ""
    code: str = ""
    notes: str = ""
    items: tuple[str, ...] = field(default=())


def slides() -> list[Slide]:
    return [
        Slide(
            title=DECK_TITLE,
            kind="title",
            subtitle=DECK_SUBTITLE,
            notes=(
                "Open by setting scope honestly: this is not an argument that AI has no "
                "place in quality systems. It is an argument that deviation management is "
                "an unusually bad place to start, and that the assessment tooling the "
                "industry has does not yet ask the right questions. Say up front that no "
                "employer or client is named and nothing here is a compliance "
                "determination about any specific system."
            ),
        ),
        Slide(
            title="Why bring this to a training centre",
            bullets=(
                "You prepare the QA analysts, manufacturing associates, and technicians "
                "who will operate these systems.",
                "In every deployment I have seen, the safety case rests on a human "
                "reviewer catching the model's mistakes.",
                "That human is your graduate.",
                "Training on how to operate the system is not the same as training on how "
                "it fails.",
            ),
            callout=(
                "The control that regulators, vendors, and quality leadership all rely on "
                "is the one nobody is specifically trained for."
            ),
            notes=(
                "This is the hook. Establish immediately that this is their problem and not "
                "just an industry problem. Every AI-assisted quality system is justified on "
                "the basis that a qualified human reviews the output. The entire safety "
                "argument therefore depends on the competence of the reviewer, and reviewer "
                "training is a curriculum question. Do not rush this slide."
            ),
        ),
        Slide(
            title="Where an AI review aid actually sits",
            kind="section",
            bullets=(
                "A deviation is any departure from an approved procedure, specification, or "
                "process parameter.",
                "The investigation report is the record: root cause, impact assessment, CAPA, "
                "and the risk rationale behind the classification.",
                "That report is what QA reviews, and what an inspector reads years later.",
                "A tool that reviews draft reports before QA reaches them does not make the "
                "disposition decision. It shapes the record the decision is made from.",
            ),
            callout=(
                "Influencing the quality of the record is not the same as deciding the "
                "outcome. It is also not harmless. Hold both of those at once."
            ),
            notes=(
                "Be precise here, because the whole talk depends on it and it is the easiest "
                "thing to overstate. A draft-review aid does not classify or disposition. It "
                "does determine which weaknesses get fixed before a qualified reviewer ever "
                "sees the report. If someone objects that this makes the tool low-risk, agree "
                "that it lowers the ceiling on the risk and then ask how you would know if it "
                "started being used as a readiness gate instead of a drafting aid."
            ),
        ),
        Slide(
            title="Why it is an attractive place to deploy AI",
            bullets=(
                "High volume, text-heavy, and repetitive - the exact profile language models "
                "handle well.",
                "Chronic backlog. Investigation cycle time is a standing audit observation "
                "at many sites.",
                "Typical business case: 40 percent reduction in triage time, 25 percent "
                "reduction in CAPA cycle time.",
                "Those numbers are real and achievable. That is what makes this hard.",
            ),
            callout=(
                "Present the business case fairly. The people who build these systems are "
                "not reckless; they are responding to genuine operational pressure."
            ),
            notes=(
                "Resist the temptation to strawman the business case. If the audience thinks "
                "you are hostile to the technology, credibility is gone. The efficiency gains "
                "are real, the backlog pressure is real, and the people driving these programs "
                "are usually competent and well-intentioned. The problem is not motive."
            ),
        ),
        Slide(
            title="The uncomfortable part: it works in the demo",
            bullets=(
                "Aggregate accuracy on a validation set looks strong.",
                "Reviewers report that it saves them time and they like using it.",
                "Cycle-time metrics improve, visibly, in the first quarter.",
                "Every stakeholder sees confirmation that the decision was correct.",
            ),
            callout=(
                "A system that failed obviously would be safe. The dangerous case is the one "
                "that succeeds on every metric anyone is currently measuring."
            ),
            notes=(
                "This is the pivot of the talk. The failure modes that follow are not "
                "detectable by the metrics these programs are governed by. That is the "
                "structural problem: success indicators and safety indicators are different "
                "quantities, and only one set is on the dashboard."
            ),
        ),
        Slide(
            title="The asymmetry inside one organisation",
            bullets=(
                "One digital organisation can run two engineering standards at once, and both "
                "are usually visible in its own systems.",
                "Data platform and commercial product: versioned releases in the hundreds, "
                "pull-request gating, end-to-end test infrastructure, automated deployment, "
                "separate sandbox, test and production environments.",
                "AI application layer, including a tool entering the deviation workflow: no "
                "written requirements artifact, no automated feedback collection, and manual "
                "spot-checking as output validation.",
                "No stated competency requirement governed who could build on that layer - no "
                "defined prerequisite of experience with the model class, with validated "
                "systems, or with the regulated process the output touches.",
                "This is not a story about an organisation lacking engineering discipline. The "
                "discipline demonstrably existed. It had not reached the AI layer.",
            ),
            callout=(
                "The question is not whether an organisation can do rigorous engineering. It is "
                "whether the rigour reaches the system that touches a GMP record."
            ),
            notes=(
                "This is the pivot, and unlike the earlier version of this slide it is "
                "supportable from an organisation's own records rather than from impression. "
                "Make the fairness explicit and early: the strong practice on the data platform "
                "and the commercial product is real, and saying so is what makes the rest "
                "credible. The gap is specific to the AI application layer. "
                "Do not name the organisation, the products, the individuals, or any ticket "
                "identifiers, and do not quote colleagues - the substance carries the argument "
                "without any of that, and the quotes would expose people who spoke candidly "
                "about their own work. Expect a question about whether AI simply matures later "
                "than data engineering. That is a fair challenge: the answer is that maturity "
                "sequencing is reasonable everywhere except where the immature layer is the one "
                "touching a regulated record."
            ),
        ),
        Slide(
            title="Failure mode 1 - Automation bias",
            kind="failure",
            bullets=(
                "The diagnostic signature: acceptance rates approaching 100 percent, combined "
                "with dwell times too short to have read the case.",
                "Human review is documented, enforced in the workflow, and present in every "
                "audit trail.",
                "A few seconds is not enough to read a deviation, let alone evaluate the "
                "recommendation behind it.",
                "The control exists, is inspectable, and is not functioning.",
            ),
            callout=(
                "Teaching point: measure override rate and dwell time, segmented by risk "
                "class, queue depth, and shift position. Aggregate figures hide this."
            ),
            notes=(
                "This is the most important failure mode because it defeats the control the "
                "whole safety case rests on, and it does so while producing perfect "
                "documentary evidence of compliance. Emphasise that the reviewers are not "
                "lazy - a system that is right 95 percent of the time trains you to trust it, "
                "and that training is rational. Automation bias is well established in "
                "aviation and radiology literature; this is not speculative. "
                "IMPORTANT: do not cite specific acceptance or dwell figures unless you can "
                "state their source and are permitted to disclose them. The diagnostic "
                "signature is the teachable content and it needs no numbers. If asked whether "
                "you measured this, distinguish clearly between what you observed and what you "
                "are describing as a general pattern."
            ),
        ),
        Slide(
            title="Failure mode 2 - Silent truncation",
            kind="failure",
            bullets=(
                "A long batch record or investigation file exceeds the model's input limit.",
                "It is truncated at ingest, or a scanned page silently fails to parse.",
                "The model reasons over partial data and returns a normal, confident "
                "assessment.",
                "The output is indistinguishable from one based on the complete record.",
            ),
            callout=(
                "No one is at fault and no one can tell. The reviewer cannot catch an "
                "omission they have no way to see."
            ),
            notes=(
                "This is the cleanest example of the unintentional failure class. There is no "
                "attacker, no negligence, and no procedural violation. A competent reviewer "
                "following the procedure correctly signs off on an assessment built from "
                "incomplete input. Ask the audience how their graduates would detect this. "
                "The answer is that they cannot, which is why it has to be a system control."
            ),
        ),
        Slide(
            title="Failure mode 3 - The validated system stops being the running system",
            kind="failure",
            bullets=(
                "A prompt template is edited to make the wording clearer.",
                "An inference parameter or routing threshold is retuned.",
                "The OCR engine or document parser is upgraded as routine infrastructure "
                "maintenance.",
                "None of these is a model change, so none reliably triggers change control.",
            ),
            callout=(
                "Change control as written governs the model. The behaviour of the system is "
                "determined by the model plus everything around it."
            ),
            notes=(
                "The OCR upgrade is the one that lands hardest with technical audiences, "
                "because it is performed by an infrastructure team that has no idea it is "
                "touching a GxP-relevant path, as part of routine patching. It changes what "
                "the model sees on every case. Nothing in a conventional change control "
                "procedure would flag it."
            ),
        ),
        Slide(
            title="Failure mode 4 - Unbounded blast radius",
            kind="failure",
            bullets=(
                "A defect in a model version is confirmed at month six.",
                "The necessary question is: which records did it touch?",
                "Reconstructing one case on demand is a different capability from "
                "enumerating every affected case.",
                "Without the second, a confirmed defect cannot be scoped, and therefore "
                "cannot be remediated or reported.",
            ),
            callout=(
                "Most systems can answer 'what happened in this case'. Far fewer can answer "
                "'what else did this affect'."
            ),
            notes=(
                "This is the failure mode with the most direct regulatory consequence. "
                "Impact assessment and, where warranted, field action both depend on being "
                "able to bound the affected population. A traceability capability built for "
                "single-case investigation readiness does not automatically give you cohort "
                "enumeration by model version and date range. Nobody discovers this until "
                "they need it."
            ),
        ),
        Slide(
            title="The common thread",
            kind="section",
            bullets=(
                "In all four cases: a competent person, following the correct procedure, "
                "receives a wrong result with no signal that anything went wrong.",
                "No malice. No negligence. No attacker. No procedural violation.",
                "The controls are documented, inspectable, and present in the audit trail.",
                "They are also, in the specific conditions described, not working.",
            ),
            callout=(
                "The threat model that matters here is internal and unintentional. Security "
                "testing aimed at adversaries will not find any of this."
            ),
            notes=(
                "Land this explicitly. Most AI risk discussion is about misuse, prompt "
                "injection, or data exfiltration. Those are real but they are not the "
                "dominant risk in a controlled internal GMP environment where every user is "
                "authenticated, trained, and trying to do their job correctly. The dominant "
                "risk is silent wrongness."
            ),
        ),
        Slide(
            title="Why this is a patient safety question",
            bullets=(
                "A draft-review aid does not classify, disposition, or release. Say that "
                "plainly so nobody in the room thinks otherwise.",
                "It does determine whether a weak impact assessment or an unsupported risk "
                "rationale gets strengthened before QA ever sees it.",
                "Score an inadequate section as adequate, and the gap it should have surfaced "
                "travels forward into the record instead.",
                "The exposure is second-order and real: not a wrong decision made by a model, "
                "but a missed chance to catch a wrong decision made by a person.",
            ),
            callout=(
                "Data integrity expectations - ALCOA+, Part 11, Annex 11 - exist because "
                "quality records drive release decisions. A record a model improved, or failed "
                "to improve, is still the record."
            ),
            notes=(
                "This slide converts the preceding material into the language the audience "
                "governs by, and it is where you must be most disciplined. Do not claim the "
                "tool made release decisions - it was explicitly scoped not to. The honest "
                "argument is that it sits upstream of the record a release decision is made "
                "from, and that a missed flag is a real if indirect exposure. That argument is "
                "weaker than the dramatic version and it is the one you can defend."
            ),
        ),
        Slide(
            title="Why existing frameworks do not catch it",
            bullets=(
                "Computer system validation establishes fitness at a point in time; these "
                "systems drift continuously.",
                "Risk-based categorisation assumes deterministic input-output behaviour.",
                "Annex 11 and Part 11 predate language models and say nothing about "
                "acceptance-rate monitoring or context-window limits.",
                "None of these frameworks is wrong. They are necessary and currently "
                "insufficient.",
            ),
            callout=(
                "The gap is not a failure of the existing framework. It is a category the "
                "framework was not written to cover."
            ),
            notes=(
                "Be careful and generous here. This audience teaches these frameworks. The "
                "argument is additive, not dismissive: the existing apparatus is sound for "
                "deterministic systems and needs a supplement for probabilistic ones. If you "
                "come across as saying validation is broken, you lose the room."
            ),
        ),
        Slide(
            title="What I built in response",
            kind="section",
            bullets=(
                "A 25-item assessment instrument for a deployment that is already running, "
                "not a design under review.",
                "Each item specifies what to inspect, what evidence to request, an objective "
                "pass criterion, and a disqualifying finding.",
                "Items are traced to named release gates, so a finding maps to a control "
                "someone owns.",
                "Reviewer-administered, with a scoring engine that produces a findings report.",
            ),
            callout=(
                "The instrument is the deliverable I would want to hand to a QA reviewer who "
                "has one day on site and no prior AI background."
            ),
            notes=(
                "Transition from problem to contribution. The important design choice is that "
                "every item asks for observed system behaviour or a retrievable artifact, "
                "never for an opinion or a self-rating. A reviewer with no machine learning "
                "background can execute it, which is the point."
            ),
        ),
        Slide(
            title="The design principle: fail closed",
            bullets=(
                "An item recorded as not assessed counts as unresolved, exactly like a "
                "failure.",
                "An untouched template therefore scores as blocking, not as passing.",
                "Any single unresolved patient-safety item forces a blocking result "
                "regardless of the other 24.",
                "The cleanest available verdict is 'no blocking findings identified' - never "
                "'approved'.",
            ),
            callout=(
                "Absence of evidence is not evidence of control. Most maturity assessments "
                "score the opposite way, and that is how a deployment passes review without "
                "anyone having looked."
            ),
            notes=(
                "This is the slide a technical audience will engage with most. The default "
                "behaviour of almost every scorecard is that unanswered questions are "
                "silently excluded from the denominator, which means an assessment nobody "
                "completed can look like a pass. Inverting that default is the single most "
                "important property of the tool."
            ),
        ),
        Slide(
            title="What it produces",
            kind="demo",
            subtitle="Synthetic sample data - not findings from any real deployment",
            code=(
                "$ deployment_assessment.py score sample_responses.json\n"
                "\n"
                "========================================================================\n"
                "VERDICT: BLOCKING_FINDINGS\n"
                "========================================================================\n"
                "Items assessed: 25/25\n"
                "\n"
                "BLOCKING - PATIENT SAFETY CRITICAL (1):\n"
                "  [DA-03] Human Oversight in Practice - non_conformant\n"
                "      Acceptance rate 99.4% with 11s median dwell on high-risk cases.\n"
                "\n"
                "OTHER FINDINGS (1):\n"
                "  [DA-09] major - Human-AI Compatibility - partial\n"
                "\n"
                "$ echo $?\n"
                "1"
            ),
            notes=(
                "Say explicitly that this is synthetic input before you walk through it. The "
                "figures are invented to exercise the tool and describe nothing real. "
                "Three things to point out: the verdict language avoids any implication of "
                "approval; the finding cites a specific metric rather than a judgement; and the "
                "non-zero exit code means this can gate an automated release pipeline rather "
                "than living in a document nobody reads. If there is time, run it live - it is "
                "more convincing than a screenshot."
            ),
        ),
        Slide(
            title="Limitations I want to state plainly",
            bullets=(
                "Entirely self-attested. There is no evidence hashing and no reviewer "
                "independence check - a vendor could complete it about its own product.",
                "18 of 25 items block. A well-run deployment will likely still fail on first "
                "pass, which risks the verdict carrying no discriminating information.",
                "Never validated against real inspection outcomes. I do not know whether it "
                "predicts anything.",
                "Point-in-time. It has no expiry, and nothing forces reassessment after a "
                "model or infrastructure change.",
            ),
            callout=(
                "High line coverage on the scoring engine proves the logic is consistent. It "
                "says nothing about whether the rubric is correctly calibrated."
            ),
            notes=(
                "Do not skip this slide, and do not apologise through it. Volunteering the "
                "weaknesses is what separates an analysis from an advocacy pitch, and this "
                "audience will find these problems anyway. The calibration issue is the one "
                "worth genuinely asking their opinion on - if nearly everything blocks, the "
                "instrument stops distinguishing a careless deployment from a careful one."
            ),
        ),
        Slide(
            title="The conclusion I drew",
            bullets=(
                "The system never went live. I resigned before the alpha pilot began, so none "
                "of this is an account of a system in production.",
                "I put the question in writing to my line manager and to theirs: what "
                "operational standard should the alpha ship under, given the gap between the "
                "AI layer's practices and the standard the same organisation applied "
                "elsewhere. I built the case from its own records, and credited the "
                "engineering discipline demonstrated elsewhere in it.",
                "I followed it up in person with two questions - whether the project had the "
                "capacity to sustain compliance, and whether the function had the capacity to "
                "support an AI operating that close to a GMP process over time.",
                "The answers did not resolve either question for me. I was the accountable "
                "product owner, I was not prepared to take the alpha live on that basis, and I "
                "resigned that week.",
            ),
            callout=(
                "I am not claiming harm occurred and I am not claiming an unsafe system "
                "shipped. Neither happened. I raised a prospective risk in writing, did not "
                "get the assurance I needed, and declined to own the launch."
            ),
            notes=(
                "One slide, stated once, then move on. Leading with 'never went live' removes "
                "any suggestion that you are describing a production failure or accusing "
                "anyone of shipping something unsafe. "
                "The sequence is what makes this credible, so deliver it in order: a written "
                "memo to line management, an in-person follow-up with two specific questions, "
                "an explicit statement that patient safety was the critical constraint when "
                "resourcing was discussed, and a resignation that week. That is an escalation "
                "record, and it is your answer to 'why did you not just raise it internally'. "
                "Two disciplines. First, the in-person meeting was not recorded, so describe "
                "your own questions and your own conclusion and do not characterise anyone's "
                "replies - you have no record of them and it was a private conversation. "
                "Second, do not say you lost confidence in management, however true it felt at "
                "the time. It invites a debate about the character of people the room has never "
                "met, which you cannot win and do not need; 'the answers did not resolve either "
                "question' is the same fact without the grievance. "
                "Expect to be asked whether resigning was proportionate. It is a judgement "
                "call, you made it as the accountable product owner on the information you had, "
                "and the instrument is your attempt to make that judgement reviewable by other "
                "people. If asked for specifics you cannot share, say plainly that you are "
                "bound by confidentiality."
            ),
        ),
        Slide(
            title="The curriculum gap",
            kind="section",
            bullets=(
                "Reviewer training today covers system operation: how to log in, where to "
                "click, how to record a decision.",
                "It does not cover the failure modes of the specific system, which is what "
                "the reviewer is there to catch.",
                "Concretely teachable: automation bias and why high accuracy causes it; what "
                "incomplete input looks like; how to ask whether the system in front of you "
                "is the validated one.",
                "One instrument item exists solely to check that reviewers are trained on "
                "named failure modes rather than general operation.",
                "The same gap exists on the build side: typically no competency standard "
                "defines who may develop an AI feature that touches a regulated record, even "
                "where equivalent standards exist for the process it feeds.",
            ),
            callout=(
                "Your graduates are the last control in the chain. Right now they are being "
                "trained as operators of the system rather than as auditors of it."
            ),
            notes=(
                "This is the ask, and it should feel like a contribution rather than a "
                "complaint. Offer something concrete: a guest module, a case-study exercise "
                "built from the four failure modes, or the instrument itself as a teaching "
                "artifact. Have a specific next step ready if anyone is interested. "
                "The build-side competency bullet is the one this audience is best placed to "
                "act on, since defining and assessing competency is their core business. Keep "
                "it structural - an absent standard, not an assessment of any individual. If "
                "asked whether you saw this go wrong in practice, say the standard was absent "
                "and stop there. Speculating about whether a particular person met a standard "
                "that was never written is neither fair nor arguable, and it will cost you the "
                "room instantly."
            ),
        ),
        Slide(
            title="Questions I would like your view on",
            kind="closing",
            bullets=(
                "Is 18 of 25 items blocking the right calibration, or does it make the "
                "instrument useless in practice?",
                "Should the blocking set vary with the system's risk class rather than being "
                "fixed?",
                "Where does this belong in a curriculum - validation, quality systems, or "
                "its own module?",
                "What would convince you that a reviewer is genuinely competent to oversee a "
                "model rather than nominally assigned to it?",
                "What competency standard would you want met by someone building an AI feature "
                "that touches a regulated record?",
            ),
            notes=(
                "Ending on genuine questions rather than a summary invites collaboration and "
                "signals that you are not there to lecture them. These are real open problems, "
                "not rhetorical. Have your own tentative answer ready for each in case they "
                "turn it back on you. The last one is the question you most want answered, so "
                "ask it last and let it sit."
            ),
        ),
    ]


def _md_notes(text: str) -> str:
    if not text:
        return ""
    return f"\n<!--\nSpeaker notes: {text}\n-->\n"


def build_markdown() -> str:
    deck = slides()
    out: list[str] = [
        "---",
        "marp: true",
        "theme: default",
        "paginate: true",
        f'title: "{DECK_TITLE}"',
        "---",
        "",
    ]

    for index, slide in enumerate(deck):
        if index:
            out.append("---")
            out.append("")

        if slide.kind == "title":
            out.append(f"# {slide.title}")
            out.append("")
            if slide.subtitle:
                out.append(f"### {slide.subtitle}")
                out.append("")
            out.append(f"_{DISCLAIMER}_")
            out.append("")
        else:
            out.append(f"## {slide.title}")
            out.append("")
            if slide.subtitle:
                out.append(f"**{slide.subtitle}**")
                out.append("")

        for bullet in slide.bullets:
            out.append(f"- {bullet}")
        if slide.bullets:
            out.append("")

        if slide.code:
            out.append("```text")
            out.extend(slide.code.split("\n"))
            out.append("```")
            out.append("")

        if slide.callout:
            out.append(f"> {slide.callout}")
            out.append("")

        notes = _md_notes(slide.notes)
        if notes:
            out.append(notes.strip())
            out.append("")

    return "\n".join(out).rstrip() + "\n"


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def build_html() -> str:
    deck = slides()
    total = len(deck)
    sections: list[str] = []

    for index, slide in enumerate(deck, start=1):
        parts: list[str] = []
        heading = "h1" if slide.kind == "title" else "h2"
        parts.append(f"      <{heading}>{_esc(slide.title)}</{heading}>")

        if slide.subtitle:
            css_class = "subtitle" if slide.kind == "title" else "lead"
            parts.append(
                f"      <p class=\"{css_class}\">{_esc(slide.subtitle)}</p>"
            )

        if slide.bullets:
            parts.append("      <ul>")
            for bullet in slide.bullets:
                parts.append(f"        <li>{_esc(bullet)}</li>")
            parts.append("      </ul>")

        if slide.code:
            parts.append(f"      <pre class=\"demo\">{_esc(slide.code)}</pre>")

        if slide.callout:
            parts.append(f"      <blockquote>{_esc(slide.callout)}</blockquote>")

        if slide.kind == "title":
            parts.append(f"      <p class=\"disclaimer\">{_esc(DISCLAIMER)}</p>")

        if slide.notes:
            parts.append(
                f"      <aside class=\"notes\"><strong>Speaker notes.</strong> "
                f"{_esc(slide.notes)}</aside>"
            )

        parts.append(
            f"      <footer><span>{_esc(DECK_TITLE)}</span>"
            f"<span>{index} / {total}</span></footer>"
        )

        sections.append(
            f"    <section class=\"slide slide-{_esc(slide.kind)}\" id=\"s{index}\">\n"
            + "\n".join(parts)
            + "\n    </section>"
        )

    body = "\n".join(sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{_esc(DECK_TITLE)}</title>
<style>
  :root {{
    --ink: #16202b;
    --muted: #5a6a7a;
    --accent: #1e5f8f;
    --warn: #9a4a00;
    --rule: #d8e0e8;
    --bg: #f4f6f9;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  }}
  .toolbar {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 10;
    display: flex; gap: 12px; align-items: center;
    padding: 8px 16px; background: #fff; border-bottom: 1px solid var(--rule);
    font-size: 13px; color: var(--muted);
  }}
  .toolbar strong {{ color: var(--ink); }}
  .toolbar button {{
    font: inherit; cursor: pointer; padding: 4px 10px;
    border: 1px solid var(--rule); border-radius: 5px; background: #fff; color: var(--ink);
  }}
  main {{ padding: 56px 0 0; }}
  .slide {{
    position: relative;
    max-width: 960px;
    margin: 0 auto 28px;
    padding: 44px 52px 60px;
    background: #fff;
    border: 1px solid var(--rule);
    border-radius: 10px;
    min-height: 62vh;
  }}
  .slide-title {{ background: linear-gradient(160deg, #fff 55%, #eef4fa 100%); }}
  h1 {{ font-size: 40px; line-height: 1.15; margin: 0 0 18px; letter-spacing: -0.4px; }}
  h2 {{
    font-size: 27px; line-height: 1.25; margin: 0 0 22px;
    padding-bottom: 12px; border-bottom: 2px solid var(--accent);
  }}
  .slide-failure h2 {{ border-bottom-color: var(--warn); }}
  .subtitle {{ font-size: 19px; color: var(--muted); margin: 0 0 26px; }}
  .lead {{ font-size: 17px; font-weight: 600; margin: 0 0 16px; }}
  ul {{ margin: 0 0 20px; padding-left: 22px; }}
  li {{ margin-bottom: 11px; font-size: 17px; }}
  blockquote {{
    margin: 22px 0 0; padding: 14px 18px;
    background: #f0f6fb; border-left: 4px solid var(--accent);
    border-radius: 0 6px 6px 0; font-size: 16px;
  }}
  .slide-failure blockquote {{ background: #fdf4ec; border-left-color: var(--warn); }}
  pre.demo {{
    background: #10171f; color: #e6edf3; padding: 18px 20px; border-radius: 8px;
    font: 13px/1.5 "SF Mono", Menlo, Consolas, monospace; overflow-x: auto; margin: 0 0 18px;
  }}
  .disclaimer {{ font-size: 13px; color: var(--muted); font-style: italic; margin: 30px 0 0; }}
  aside.notes {{
    margin: 24px 0 0; padding: 14px 16px; border: 1px dashed var(--rule);
    border-radius: 6px; background: #fbfcfd; color: var(--muted); font-size: 14.5px;
  }}
  aside.notes strong {{ color: var(--ink); }}
  body.hide-notes aside.notes {{ display: none; }}
  footer {{
    position: absolute; left: 52px; right: 52px; bottom: 20px;
    display: flex; justify-content: space-between;
    font-size: 12px; color: var(--muted);
    border-top: 1px solid var(--rule); padding-top: 10px;
  }}
  @media print {{
    body {{ background: #fff; }}
    .toolbar {{ display: none; }}
    main {{ padding: 0; }}
    aside.notes {{ display: none; }}
    .slide {{
      border: none; border-radius: 0; margin: 0; padding: 40px 46px 56px;
      min-height: 100vh; page-break-after: always; max-width: none;
    }}
  }}
</style>
</head>
<body class="hide-notes">
  <div class="toolbar">
    <strong>{_esc(DECK_TITLE)}</strong>
    <span>{total} slides</span>
    <button id="toggle-notes">Show speaker notes</button>
    <span>Print to PDF for handout (notes are omitted)</span>
  </div>
  <main>
{body}
  </main>
<script>
  var btn = document.getElementById('toggle-notes');
  function toggleNotes() {{
    var hidden = document.body.classList.toggle('hide-notes');
    btn.textContent = hidden ? 'Show speaker notes' : 'Hide speaker notes';
  }}
  btn.addEventListener('click', toggleNotes);
  document.addEventListener('keydown', function (event) {{
    if (event.key === 'n' || event.key === 'N') {{
      toggleNotes();
    }}
  }});
</script>
</body>
</html>
"""


def write_deck(directory: Path) -> list[Path]:
    directory.mkdir(parents=True, exist_ok=True)
    written = []
    for name, content in (
        ("teaching_deck.md", build_markdown()),
        ("teaching_deck.html", build_html()),
    ):
        path = directory / name
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate the teaching deck on AI failure modes in QMS."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Directory to write teaching_deck.md and .html into",
    )
    parser.add_argument(
        "--outline",
        action="store_true",
        help="Print the slide outline with timings instead of writing files",
    )
    return parser


def print_outline() -> None:
    deck = slides()
    print(f"{len(deck)} slides\n")
    for index, slide in enumerate(deck, start=1):
        marker = {"title": "T", "section": "S", "failure": "F", "demo": "D", "closing": "C"}.get(
            slide.kind, " "
        )
        print(f"  {index:>2}. [{marker}] {slide.title}")
    print(
        "\nLegend: T title, S section marker, F failure mode, D live demo, C closing"
        "\nAt roughly 90 seconds per slide this runs about "
        f"{round(len(deck) * 1.5)} minutes before questions."
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.outline:
        print_outline()
        return 0
    for path in write_deck(args.out):
        print(f"Generated: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
