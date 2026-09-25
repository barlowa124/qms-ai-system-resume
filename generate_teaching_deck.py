"""Generate the teaching deck on AI failure modes in GMP-adjacent QMS.

Audience: faculty in a biomanufacturing master's program - the speaker's own
program - reviewing this placement as a case study of an AI implementation in life
sciences. This is a case-study review, not an advocacy pitch: the faculty are not
being told their curriculum has a gap they must fix, they are evaluating a case study
submitted to them. The speaker is a computer-science-background student in that
program; the placement described was their first exposure to the life sciences
industry, and the observations are offered as evidence for how they intend to
approach compliant, patient-safety-first AI implementation in life sciences going
forward.

Framing decisions, deliberate:
  - The deployment discussed is de-identified throughout. No employer, client,
    vendor, or product is named. Every failure mode is stated generically enough
    to apply to any AI-assisted deviation-management deployment.
  - The tone is descriptive, not prescriptive. Curriculum-relevant implications are
    stated as findings of the case study for the faculty to weigh, never as a
    request that they change anything.
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
    "instrument for assessing an already-built AI system"
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
                "Open with who you are before what you found: a computer-science-background "
                "student in this program, and this placement was your first exposure to the "
                "life sciences industry. That framing matters twice over. It explains why you "
                "noticed what an insider might not, and it frames this talk as a statement of "
                "how you intend to practice rather than a grievance against a former employer. "
                "Then set scope honestly: this is not an argument that AI has no place in quality "
                "systems, but an argument that deviation management is an unusually bad "
                "place to start, and that the assessment tooling the industry has does not yet "
                "ask the right questions. Say up front that no employer or client is named, and "
                "that nothing here is a compliance determination about any specific system."
            ),
        ),
        Slide(
            title="What this case study covers",
            bullets=(
                "A single AI-assisted deviation-review tool, built during my first "
                "placement in a regulated life sciences environment.",
                "The tool never reached deployment, so this is a prospective risk analysis: "
                "it does not describe a live failure.",
                "The one deployment I observed closely rested its entire safety case on a "
                "human reviewer catching the model's mistakes.",
                "Two governance questions surfaced during the placement: how reviewers are "
                "prepared to catch failure, and how builders are qualified to avoid causing "
                "it.",
            ),
            callout=(
                "The control every stakeholder relied on, the human reviewer, was, in "
                "this case, one nobody had been specifically trained for."
            ),
            notes=(
                "Orient the case study before any findings: one tool, one placement, never "
                "deployed. Present it as a case study submitted for review, and let any "
                "implication about their curriculum surface later from the findings themselves "
                "rather than asserting it now. Every AI-assisted quality system is "
                "justified on the basis that a qualified human reviews the output, so the "
                "entire safety argument depends on the reviewer's competence. Frame that as "
                "an observation from the case study rather than a claim about this program. Do "
                "not rush this slide."
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
                "A tool that reviews draft reports before QA reaches them shapes the record "
                "the decision is made from; it never makes the disposition decision itself.",
                "That distinction is also the crux of the regulatory acceptance argument for a "
                "system like this: the tool's input is optional, and a human always makes the "
                "final approval.",
            ),
            callout=(
                "Influencing the quality of the record falls short of deciding the outcome, "
                "yet it still carries real weight. Hold both of those at once."
            ),
            notes=(
                "Be precise here, because the whole talk depends on it and it is the easiest "
                "thing to overstate: a draft-review aid determines which weaknesses get fixed "
                "before a qualified reviewer ever sees the report, without classifying or "
                "dispositioning anything. If someone objects that this makes the tool low-risk, "
                "agree that it lowers the ceiling on the risk and then ask how you would know if "
                "it started being used as a readiness gate instead of a drafting aid. "
                "Name the regulatory argument explicitly on this slide, because it is the "
                "premise every later finding tests rather than contradicts. 'Optional, with a "
                "human always approving' is the whole compliance case in one sentence, and it "
                "is true as designed. Do not resolve the tension yet; just mark that it exists, "
                "and that the human-oversight finding later in the deck is a direct test of "
                "whether 'optional' survives contact with a 99 percent acceptance rate."
            ),
        ),
        Slide(
            title="Why it is an attractive place to deploy AI",
            bullets=(
                "High volume and text-heavy, with the same handful of investigation patterns "
                "recurring case after case: the exact profile language models handle well.",
                "Chronic backlog. Investigation cycle time is a standing audit observation "
                "at many sites.",
                "Typical business case: 40 percent reduction in triage time, 25 percent "
                "reduction in CAPA cycle time.",
                "Those targets are achievable. A tool that hits them can still be unsafe "
                "without anyone noticing.",
                "In a meeting, my supervisor told me directly that a single failed batch costs "
                "on the order of $9 million.",
                "At that price point, a tool that reliably caught what leads to a failed batch "
                "would have value well beyond one site's efficiency metrics: the kind of value "
                "that could plausibly be sold to the wider life sciences industry as its own "
                "product rather than used only internally.",
            ),
            callout=(
                "Present the business case fairly. The people who build these systems are "
                "not reckless; they are responding to genuine operational pressure."
            ),
            notes=(
                "Resist the temptation to strawman the business case. If the audience thinks "
                "you are hostile to the technology, credibility is gone. The efficiency gains "
                "are real, the backlog pressure is real, and the people driving these programs "
                "are usually competent and well-intentioned. The problem is not motive. "
                "Be precise about provenance on the last two bullets. The $9 million figure is "
                "a number one supervisor stated verbally in one meeting; it is not an audited "
                "or published company figure, so say so if asked. The commercial-product point is "
                "your own inference about incentive; nobody told you it was the plan. Both "
                "bullets exist only to explain the scale of the pressure driving speed, not to "
                "imply anyone had a hidden commercial motive; keep that distinction "
                "explicit if challenged."
            ),
        ),
        Slide(
            title="The asymmetry inside one organization",
            bullets=(
                "One digital organization can run two engineering standards at once, and both "
                "are usually visible in its own systems.",
                "Data platform and commercial product: versioned releases in the hundreds, "
                "pull-request gating, end-to-end test infrastructure, automated deployment, "
                "separate sandbox, test and production environments.",
                "AI application layer, including a tool entering the deviation workflow: no "
                "written requirements artifact, no automated feedback collection, and manual "
                "spot-checking as output validation.",
                "The engineering discipline in this organization demonstrably existed; it "
                "simply had not reached the AI layer.",
                "The gap reflected capacity, not indifference: IT was already stretched sustaining its existing "
                "stack, and the time of both the executive IT sponsor and the senior engineers "
                "who could have closed the gap was consistently occupied by other priorities.",
                "The people drawn into the build effort were often the same ones who govern the "
                "organization's data and respond to its data-integrity incidents elsewhere: "
                "real technical credibility, but not background industry knowledge of "
                "controlled documents like deviations.",
            ),
            callout=(
                "Rigorous engineering clearly exists in this organization. The open question is "
                "whether that rigor reaches the system that touches a GMP record."
            ),
            notes=(
                "This is the pivot, and unlike the earlier version of this slide it is "
                "supportable from an organization's own records rather than from impression. "
                "Make the fairness explicit and early: the strong practice on the data platform "
                "and the commercial product is real, and saying so is what makes the rest "
                "credible. The gap is specific to the AI application layer. "
                "The capacity bullet is what keeps this a resourcing finding rather than a "
                "verdict on anyone's priorities. IT was carrying its existing stack, and the "
                "specific people who could have closed the gap were occupied by other work; "
                "they were not declining to engage. Name no one and quote no one when you say it. "
                "The data-governance bullet makes the same distinction from a different angle: "
                "real technical credibility in an adjacent domain (data governance, "
                "data-integrity incident response) is not the same credibility as knowing what "
                "a controlled document is and how a deviation record is expected to behave. "
                "Keep it at the level of functions rather than people, and do not name anyone who was "
                "actually drawn into the build effort. "
                "Do not name the organization, the products, the individuals, or any ticket "
                "identifiers, and do not quote colleagues. The substance carries the argument "
                "without any of it, and attributed criticism of identifiable people turns a "
                "governance argument into a personnel dispute. Expect a question about whether "
                "AI simply matures later than data engineering. That is a fair challenge: the "
                "answer is that maturity "
                "sequencing is reasonable everywhere except where the immature layer is the one "
                "touching a regulated record."
            ),
        ),
        Slide(
            title="What the resourcing actually looked like",
            bullets=(
                "The portfolio containing this work carried a documented blocker recording "
                "missing resources and funding, roughly two thirds of its active items "
                "unassigned, and a backlog median over eight months.",
                "The product owner for the tool entering the deviation workflow was the "
                "project's only hire: a temporary intern. That intern was me.",
                "In a program governance forum, others independently questioned whether one "
                "temporary intern could realistically sustain an initiative of that scope.",
                "Senior engineering capacity existed (developers with a decade or more of "
                "experience) and was assigned to the commercial product and the data "
                "platform instead of the work entering the deviation workflow.",
                "The team that would maintain it long term confirmed on record: no allocated "
                "funding, no in-house developer assigned, no proactive maintenance model, and a "
                "reactive queue already holding dozens of unaddressed items at its highest "
                "priorities.",
                "No standard operating procedures existed for non-regulated engineering activity "
                "either. No direction was given on how to use the organization's version-control "
                "or ticketing systems; what I used drew entirely on knowledge I already had "
                "going in.",
                "That the resourcing was short was not only a documentation finding. A "
                "technically literate voice in the sponsor chain, consulted before staffing was "
                "finalized, reached the same conclusion.",
            ),
            callout=(
                "The staffing itself is the finding: the role existed, it was filled by "
                "the most junior and least permanent person available, and the organization's "
                "own records show it knew the resourcing was short."
            ),
            notes=(
                "Deliver the third bullet flatly and do not soften it. Disclosing that you were "
                "the intern is what makes the rest of the talk survivable: an audience that "
                "discovers it later concludes you inflated your standing, and an audience that "
                "hears it from you concludes you are being straight with them. It is also the "
                "strongest evidence you have, because it converts an abstract resourcing "
                "finding into a fact nobody can argue with. "
                "The fourth bullet matters just as much: the capacity question was raised "
                "independently by other people in a governance forum, which is what separates "
                "this from one junior person's idiosyncratic worry. Do not overstate it; they "
                "questioned the realism of the staffing and the pace it implied. They did not "
                "question patient safety. That framing was yours. "
                "Related and important: do not assert from the platform that you verbally "
                "warned any named individual or team that this was a patient safety matter. "
                "Whatever was said in unrecorded conversations, the surviving record of your "
                "escalation is the written quality observation, which carries a tracking "
                "identifier and a date and needs no corroboration from anyone's memory. A "
                "spoken warning you cannot evidence is both unprovable and an implicit "
                "accusation that someone heard it and proceeded regardless. The written filing "
                "makes the same point and cannot be disputed. "
                "Expect the obvious challenge: if you were an intern, why should anyone weight "
                "your judgment? Answer it directly. Seniority is not the claim: the records "
                "are the claim, and they were available to anyone who looked. Say that you were "
                "the person who happened to look. "
                "The maintenance-team bullet deserves a sentence of interpretation rather than "
                "being left as a list, because it is the one that connects to everything later. "
                "A reactive ticket queue is a perfectly sound way to maintain most software, "
                "since most defects announce themselves: something breaks, and a user reports "
                "it. Silent degradation produces no reporter. Nobody raises a ticket saying the "
                "model got quietly worse this quarter. A reactive queue is therefore "
                "structurally incapable of catching the failure mode that matters most in this "
                "class of system, and that is the bridge from this slide to the drift material "
                "later. "
                "The SOP bullet is deliberately narrow: it is about your own working practice. "
                "It is not a claim about anyone else's. Frame it as one more data point on what "
                "'resourced' meant in practice: even ordinary engineering tooling had no "
                "onboarding of its own, so what filled the gap was whatever you already knew "
                "coming in; the organization provided none of it. Say 'version-control and "
                "ticketing systems' rather than naming the specific products if asked directly "
                "which ones. The point is the absence of onboarding. Which tools were used is "
                "beside it. "
                "Two supporting points to hold in reserve. First, the scope exceeded the "
                "classification: the same intern was running technical assessments of external "
                "AI vendors and corresponding with them on the organization's behalf under the "
                "strategy office. If anyone suggests 'intern' understates your involvement, "
                "that is the answer. Second, be honest about the provenance of the portfolio "
                "figures. They are your own contemporaneous analysis of a ticket export you no "
                "longer hold, so present them as a finding you made at the time rather than as "
                "a document you can produce on request. If pressed for the underlying data, say "
                "plainly that it stayed with the employer. "
                "The last bullet exists only to show the shortfall was not invisible to someone "
                "technically qualified to judge it. Stop there. Do not name the person, do not "
                "describe their background or credentials, and do not say what they recommended. "
                "Any of those turns a corroboration point into a claim about an identifiable "
                "individual's judgment, which this slide does not need and cannot support."
            ),
        ),
        Slide(
            title="The standard for who builds it",
            bullets=(
                "No stated competency requirement governed who could build on the AI layer: no "
                "defined prerequisite of experience with the model class, with validated "
                "systems, or with the regulated process the output touches.",
                "The absence was visible at the point of entry. I was hired onto this work "
                "without being asked for a code sample, a repository, or any technical "
                "demonstration.",
                "My claim to be able to build it was accepted on assertion. For a technical "
                "role, that is an unusual step to skip.",
                "I am the evidence for this one: not that the judgment was wrong, but that "
                "no step existed that could have established it either way.",
            ),
            callout=(
                "Every other control in a GMP environment requires demonstrated competence "
                "before the work starts. This one required a conversation."
            ),
            notes=(
                "This is the competency finding, and it is the safest one in the deck to make "
                "because the person who went unverified was you. Nobody in the room can accuse "
                "you of settling a score with a colleague when you are the example. "
                "It should also land harder with this audience than any other slide, because "
                "verifying competence is what a training center exists to do. If industry "
                "assigns GMP-adjacent build work without checking whether the person can do it, "
                "that bears directly on what their qualifications are for and what they are "
                "worth. Ask them that question rather than answering it. "
                "Do not let the fourth bullet read as false modesty: it is a governance "
                "point, not self-deprecation. A hiring process that cannot distinguish a capable "
                "candidate from an incapable one has not made a good decision when it happens "
                "to get a capable one. It has made an unexamined decision with a fortunate "
                "outcome, and the next outcome is independent of this one. "
                "Say nothing about how anyone else on the project was hired. You do not know "
                "their process, and the argument does not need it. "
                "If you are asked how you established that no competency standard existed, "
                "answer from the documentation: no written prerequisite existed, and your own "
                "appointment demonstrates it. Do not answer by describing conversations in "
                "which you asked colleagues about their qualifications. That is not the "
                "evidence, the finding does not rest on it, and it would convert a point about "
                "a missing procedure into a claim about identifiable people, which is the one "
                "way this slide can go badly wrong."
            ),
        ),
        Slide(
            title="Who could actually see the data",
            bullets=(
                "A deviation record is a controlled document. Access to it is itself "
                "controlled, and granted deliberately.",
                "The team assigned to build the tool did not hold that access, and had not "
                "needed it in order to be assigned the work.",
                "No prerequisite required anyone on the build side to establish that they "
                "understood the regulatory status of the records the system would process.",
                "Sample review of the dataset therefore rested on one person: the temporary "
                "intern who happened to have access.",
                "The access itself outlasted the assignment. A month after departure, that "
                "access had not been revoked.",
            ),
            callout=(
                "A system cannot be validated against data its builders cannot see, and a "
                "review function with exactly one person in it is not a review function."
            ),
            notes=(
                "This is the concrete form of the competency point made earlier. The absent "
                "standard is not an abstraction: you can see it in who was able to look at the "
                "data at all. Keep it structural: the finding is the missing prerequisite and "
                "the single point of review, not any individual's knowledge. "
                "Press the second half of the callout. A dataset review that depends on one "
                "temporary person is a control that disappears when that person leaves, and "
                "that is exactly what happened. It also vindicates the concern others raised in "
                "the governance forum about the staffing being temporary. They were right, and "
                "the dataset review function is the thing that turned out to depend on it. "
                "Expect the obvious question: could access not simply have been granted? Yes, "
                "trivially, and that is the point. Nothing prevented it. No requirement "
                "prompted it, because no requirement existed. That is what an absent standard "
                "looks like in practice rather than on paper. "
                "State the last bullet strictly as the past-tense fact it is: access had not "
                "been revoked at the one-month mark. Do not speculate about the status today, "
                "and do not let the moment turn into a story about what happened after you left. "
                "The finding is the offboarding control, not your own subsequent conduct. If "
                "asked directly whether it has since been resolved, decline on scope rather than "
                "on knowledge: say plainly that your current personal situation is not something "
                "you are going to discuss here, because the finding is the organization's "
                "control gap rather than a status update on you. Do not claim you are unable to confirm "
                "something you can. That is its own small dishonesty, and this deck does not "
                "need it. A stated boundary is honest. A false claim of not knowing is not."
            ),
        ),
        Slide(
            title="The control that did not exist",
            bullets=(
                "In a GMP quality system, a process not described in a controlled procedure is "
                "not a controlled process.",
                "General-purpose AI was already in use across the organization (consumer "
                "chatbots and an enterprise assistant embedded in the office suite) for "
                "contract drafting, HR schema work, scripting and technical questions.",
                "There was no procedure governing any of it: no acceptable-use rule, and no "
                "data-classification rule for prompts. Nothing even required AI-assisted work "
                "to be recorded at all.",
                "When the gap was raised before deployment, the answer recorded at the time was "
                "that the governing procedure would be developed after the alpha went live.",
                "That promised procedure had no tracking identifier of its own; notable given "
                "that a global training program assuming the procedure would already exist "
                "was being discussed at the same time.",
                "Staff said so themselves. People asked whether their information stayed "
                "confidential, and described not knowing what they should or should not upload.",
                "The query is itself a disclosure surface. A domain-specific technical question "
                "can reveal what an organization is working on with no document attached.",
            ),
            callout=(
                "In a quality system, absence of a procedure is not neutral: it means the "
                "process runs without a control, and the organization cannot state what its "
                "own rule is."
            ),
            notes=(
                "This is the most quality-literate point in the deck and this audience will get "
                "it immediately: in a GMP system an uncontrolled process is outside its "
                "qualified state, and 'we have no procedure for that' is a finding rather than "
                "an excuse. "
                "Give credit where the record supports it. Informal awareness did exist in "
                "places (at least one function had been told not to expose proprietary client "
                "material to these tools), which shows the instinct was present but never "
                "systematized. That distinction is the whole point: a procedure gives you "
                "something reviewable, something you can train people on, and a shared "
                "instinct gives you none of that. "
                "The tracking-identifier bullet is a quality-system-literate way to show a "
                "promise was not yet a commitment: in a mature quality system, a future "
                "deliverable gets a tracking identifier and an owner the moment it is promised, "
                "precisely so someone can be held to it. This one had neither, which is worth "
                "flagging forward to the training-program finding on the next slide: the "
                "organization was already discussing the downstream training before the "
                "procedure it depends on was even tracked as a commitment. "
                "Dwell on the last bullet, because it is the one people miss. Staff assume "
                "disclosure requires attaching a document. It does not. The prompt is the "
                "disclosure, and a sufficiently specific technical question about a process, an "
                "organism or a molecule can identify the program it came from. "
                "If challenged that almost every organization is in this position, agree "
                "immediately and without defensiveness. That is exactly why it belongs in a "
                "curriculum rather than in a complaint about one employer. Name no tools' users "
                "and quote nobody."
            ),
        ),
        Slide(
            title="The other readiness gap: the people who would use it",
            bullets=(
                "Appetite was real. A company-wide AI survey drew the largest response the "
                "organization had on record.",
                "It also measured the gap. Around two thirds described themselves as "
                "beginners or non-users, and roughly one in ten as advanced.",
                "Nearly half named unclear rules as a barrier, and the single most requested "
                "form of support was clear guidance: ahead of training, ahead of use cases.",
                "Reported use of external AI services ran several times higher than use of the "
                "sanctioned internal tool.",
                "I then interviewed the respondents who had volunteered interest. Among that "
                "most enthusiastic group, working familiarity with model behavior was still "
                "rare: one could engage with what sampling temperature does to an output.",
                "That same volunteered-interest question is also where the build side shows "
                "up: interest from the IT function specifically was effectively negligible on "
                "it, on a question that cannot separate genuine disinterest from a team that "
                "already had no spare bandwidth to take on more. Consistent with that figure, "
                "not one person from that function reached out to me about the project directly "
                "at any point during my time there.",
                "Job impact and environmental cost dominated the free-text responses, "
                "alongside a broader worry about whether it would help daily work at all; how "
                "to supervise a model was not one of them.",
                "There was no organization-wide training program for AI use of any kind. "
                "The organization's own training function was still scoping its first AI "
                "course, and raised the possibility of my involvement in building or "
                "delivering it: during or after the alpha's deployment.",
                "In the entire time I was there, not one person asked me whether it was safe. "
                "Nobody asked whether its output could affect a decision or whether it belonged "
                "that close to a GMP process, and nobody raised the possibility of accidental "
                "prompt injection or accidental drift.",
            ),
            callout=(
                "Wanting a tool badly says nothing about being ready to supervise it. A "
                "population that cannot describe how it behaves cannot be the effective "
                "control on it."
            ),
            notes=(
                "This is the second readiness gap and it pairs with the engineering one: the "
                "layer was under-supported technically, and the population designated to "
                "supervise its output had little working familiarity with model behavior. "
                "The figures are the organization's own, from its own survey, which is what "
                "makes them usable. You are not characterizing colleagues from impression, you "
                "are reporting what the organization measured about itself. "
                "Keep the third bullet in reserve for the discussion, because it is the one "
                "that closes the argument. Nearly half the workforce named unclear rules as a "
                "barrier and asked for guidance above all else, which means the missing "
                "procedure was not only a governance defect visible to auditors: it was the "
                "single thing staff most wanted and did not have. The survey's own executive "
                "summary concluded that the constraint was trust and governance rather than "
                "lack of interest. If challenged on whether that is your interpretation, say "
                "that it was the organization's. "
                "The IT-interest bullet deliberately gives no count and no denominator. State "
                "it only as 'effectively negligible'. A specific number on a small function is "
                "exactly the kind of figure that narrows down who did or did not volunteer, "
                "which this deck avoids everywhere else and must avoid here too. "
                "If asked whether this contradicts the capacity framing on the asymmetry slide, "
                "do not deny the tension; name it honestly: a survey question about "
                "volunteering for more work cannot cleanly separate genuine disinterest from a "
                "team that already had no spare bandwidth, and this data cannot resolve that "
                "ambiguity by itself. What you can say is that IT was independently documented "
                "elsewhere in this case study as carrying the heaviest existing workload of any "
                "function measured, which is at least consistent with capacity, though it does "
                "not prove capacity was the only factor. "
                "The free-text responses included a minority of strongly hostile comments. Do "
                "not quote them and do not characterize their authors. The substantive concerns "
                "inside them, environmental cost and job displacement, are already on the slide "
                "and are the part that deserves an answer. "
                "Give the organization full credit for the survey response: it is evidence of "
                "genuine appetite, and saying so keeps this from sounding dismissive. The gap "
                "separates appetite from preparation; it says nothing about who is clever and "
                "who is foolish. "
                "These were experienced colleagues who engaged willingly and spoke candidly, "
                "and the enthusiast population is the fairest sample you could have drawn: if familiarity is "
                "thin there, it is thinner everywhere else. "
                "The temperature question is a fair probe rather than a trivia test, because "
                "sampling behavior is what determines whether the same input yields the same "
                "output twice, and that is the first thing a reviewer needs to know. "
                "If challenged that this is just normal early adoption, agree: appetite "
                "outrunning familiarity is ordinary and harmless everywhere except where the "
                "unfamiliar population is the designated control. Name nobody and quote "
                "nobody. "
                "Deliver the training-program bullet as a fact about organizational "
                "sequencing rather than a credential. What matters is not that you were asked, "
                "but that even the organization's own remedy was scoped to arrive during or after "
                "the thing it was meant to prepare people for. That is the timing failure in "
                "one sentence, and it needs no further comment from you. "
                "The final bullet is the concrete counterpart to everything the survey measured "
                "in the abstract. It is a first-hand observation about you rather than a claim "
                "about anyone else's competence, so it carries none of the naming risk the rest "
                "of this slide is careful about. Deliver it as absence of evidence you personally "
                "looked for throughout your time there, rather than a survey of what colleagues knew: "
                "you cannot know what every individual silently understood, only that in your "
                "own experience the question never once came up unprompted. Prompt injection and "
                "drift are named here because they are the two failure modes least likely to "
                "announce themselves, which is exactly why nobody asking about them is the "
                "finding rather than a reassuring silence."
            ),
        ),
        Slide(
            title="The uncomfortable part: it works in the demo",
            bullets=(
                "The tool never reached deployment, so what follows is the pattern this class "
                "of system follows elsewhere, not an account of what happened here.",
                "A documented example: a sepsis-prediction model deployed at hundreds of US "
                "hospitals reported a developer-side accuracy score in the high 0.70s to low "
                "0.80s. An independent external validation found it fell to 0.63, missing "
                "two-thirds of actual sepsis cases while flagging nearly one in five patients: "
                "a large enough volume of false alarms to cause severe alert fatigue among the "
                "clinicians relying on it (Wong et al., JAMA Internal Medicine, 2021).",
                "A second, independent example from a different clinical domain: an oncology "
                "decision-support tool was trained on a small number of hypothetical cases "
                "curated by a handful of specialists rather than broad real-world evidence, yet "
                "was marketed and adopted at over 200 hospitals worldwide: all while internal "
                "reviews had already found 'multiple examples of unsafe and incorrect treatment "
                "recommendations' (STAT News, based on internal company documents, 2018).",
                "The parallel to this case study is structural rather than coincidental: in "
                "both examples, the metric the organization could see (vendor-reported accuracy, "
                "adoption scale) was not the metric that mattered, and no independent "
                "validation requirement stood between the two.",
                "Aggregate accuracy on a validation set would look strong.",
                "Reviewers would report that it saves them time and that they like using it.",
                "Cycle-time metrics would visibly improve within the first quarter of use.",
                "Every stakeholder would see confirmation that the decision to deploy was "
                "correct.",
            ),
            callout=(
                "A system that failed obviously would be safe. The dangerous case is the one "
                "that succeeds on every metric anyone is currently measuring."
            ),
            notes=(
                "This slide is the bridge from the two readiness gaps to the failure modes. "
                "Lead with the first bullet and do not let it get skimmed: everything else about "
                "this tool is a forward-looking pattern rather than a report of what its "
                "reviewers or metrics actually did, because there were no reviewers and no metrics: it never "
                "reached deployment. Blurring that line is the one mistake that would undermine "
                "the deck's own credibility on the exact point it keeps insisting on elsewhere. "
                "The two citations are what make the pattern more than a plausible-sounding "
                "assertion. The sepsis model is a peer-reviewed, published account of vendor-"
                "reported metrics looking strong until an external party actually checked. The "
                "oncology tool is a different mechanism in the same family: internal reviewers "
                "had already identified unsafe recommendations while the product continued to "
                "be marketed and adopted at scale, which shows the gap can persist even when "
                "someone inside the organization does raise it. Two independent domains, two "
                "different ways the same pattern surfaces. Have both citations ready if asked, "
                "and do not overreach either: they illustrate the pattern, they do not stand in "
                "for evidence about this specific tool. "
                "Walk through the parallels explicitly rather than leaving the audience to infer "
                "them. The sepsis model's gap is the readiness-and-validation gap this case "
                "study describes in its own findings: a system trusted at scale on the strength "
                "of a developer-reported number, with no independent check required before that "
                "trust was extended, and a false-alarm volume large enough to train the exact "
                "override-and-tune-out behavior described in the next slide. The oncology tool's "
                "gap is closer to the escalation material at the end of this deck: someone "
                "inside the organization already had the concern on record, and it did not "
                "change what was marketed or deployed. That is not proof that raising a concern "
                "is pointless: it is exactly the risk that makes documenting the escalation "
                "yourself, in writing, through the formal channel, matter as much as it does. "
                "If asked why these two and not others, say plainly that they were chosen because "
                "they are independently published and well-documented, and because they span "
                "two different clinical domains and two different failure mechanisms. That is "
                "not because they are the most dramatic examples available. "
                "The obvious objection to everything you have just said is that a system this "
                "under-supported would fail visibly and get caught early. It would not. It "
                "would succeed on every metric anyone is currently measuring, which is exactly "
                "why the gaps matter: success indicators and safety indicators are different "
                "quantities, and only one set is on the dashboard."
            ),
        ),
        Slide(
            title="Failure mode 1: Automation bias",
            kind="failure",
            bullets=(
                "This is not an argument that human review is missing. This system has it. The "
                "argument is about what happens to that specific control under realistic "
                "conditions: which is the only way it can fail while still passing every audit.",
                "The diagnostic signature: acceptance rates approaching 100 percent, combined "
                "with dwell times too short to have read the case.",
                "Human review is documented and enforced in the workflow. It shows up in "
                "every audit trail.",
                "A few seconds is not enough to read a deviation, let alone evaluate the "
                "recommendation behind it.",
                "The control exists. It is inspectable. It is not functioning.",
                "On the ground, open caseload and case-age were not spread evenly across the "
                "reviewing team: a small subset of reviewers routinely carried "
                "disproportionate queue depth and the oldest unresolved records, exactly the "
                "variable the diagnostic signature depends on segmenting by; an aggregate "
                "acceptance rate would never surface it.",
                "In conversation, the QA and investigation team named that workload directly "
                "as a driver of turnover, citing more than one resignation during my own time "
                "on the placement.",
                "This is documented within life sciences rather than imported from another "
                "industry: reviews of computerized drug-safety alerts found override rates of "
                "49 to 96 percent across clinical settings (van der Sijs et al., JAMIA, 2006).",
                "A mammography study found the effect hit hardest where it is least expected: "
                "the most skilled radiologists became measurably less sensitive to difficult "
                "cancers specifically when a computer-aided detection tool prompted incorrectly "
                "(Povyakalo et al., Medical Decision Making, 2013).",
            ),
            callout=(
                "Teaching point: measure override rate and dwell time, then break the "
                "results down \u2014 risk class, queue depth, shift position \u2014 because "
                "aggregate figures hide exactly this kind of unevenness."
            ),
            notes=(
                "Open with the first bullet and mean it: the most common misreading of this "
                "slide is that it argues human review is absent, which invites the flat and "
                "correct rebuttal that this system has it. The actual argument is narrower and "
                "harder to dismiss: human review is the control the entire safety case rests on, "
                "and this is the documented failure mode of that specific control; it says "
                "nothing about oversight in general. "
                "This is the most important failure mode because it defeats the control the "
                "whole safety case rests on, and it does so while producing perfect "
                "documentary evidence of compliance. Emphasize that the reviewers are not "
                "lazy: a system that is right 95 percent of the time trains you to trust it, "
                "and that training is rational. "
                "Use the two life-sciences citations to close off the 'that is a different "
                "industry' objection before it is raised. The alert-override review spans "
                "clinical settings directly comparable to this one: a computerized system "
                "producing a recommendation a qualified professional is expected to check. The "
                "mammography finding is the sharper point and worth lingering on: the effect was "
                "largest in the most skilled readers rather than the least skilled, which pre-empts the "
                "objection that experienced reviewers would simply not be susceptible to this. "
                "IMPORTANT: do not cite specific acceptance or dwell figures for this tool "
                "unless you can state their source and are permitted to disclose them. The "
                "diagnostic signature is the teachable content and it needs no numbers of your "
                "own. If asked whether you measured this, distinguish clearly between what you "
                "observed and what you are describing as a documented general pattern. "
                "The caseload bullet is a genuine observation from reviewing on-the-ground "
                "records during the placement, kept deliberately at the level of shape rather "
                "than figures: do not give a case count, a day count, a headcount, or name any "
                "reviewer, even if asked directly. The point for this audience is that queue "
                "depth and case-age are worth segmenting by at all; no specific number from "
                "one site belongs in this room. "
                "The turnover bullet is verbal testimony from the team itself, gathered while "
                "you were still on the placement. It is not a documented exit-interview finding: "
                "attribute it that way if asked, the same way the earlier $9 million figure is "
                "attributed to one supervisor rather than presented as an audited number. Do not "
                "state a count of resignations beyond 'more than one', do not give a timeframe "
                "tighter than your own tenure, and do not name or describe anyone who left. The "
                "point is that the workload the team itself was naming as a retention problem is "
                "the same variable the diagnostic signature above depends on; whether workload "
                "was the sole or officially recorded reason anyone gave for leaving is a "
                "separate question this bullet does not answer."
            ),
        ),
        Slide(
            title="Failure mode 2: Silent truncation",
            kind="failure",
            bullets=(
                "A long batch record or investigation file exceeds the model's input limit.",
                "It is truncated at ingest, or a scanned page silently fails to parse.",
                "The model reasons over partial data and returns a normal, confident "
                "assessment.",
                "The output is indistinguishable from one based on the complete record.",
                "The event itself is not indistinguishable, though: token count against the "
                "context limit, and parser success or failure, are both deterministic, "
                "loggable signals. Nothing about a truncation event is inherently invisible.",
                "Cheap to build is not the same as resourced to build, though: the team that "
                "would have wired this signal into review is the same one already running an "
                "unfunded, reactive maintenance queue with no in-house developer assigned: the "
                "fix competes for capacity that, on this project, was not there.",
            ),
            callout=(
                "The reviewer cannot catch it from the output alone. But the event is a "
                "replicable, loggable metric: the failure is that nobody surfaces it to "
                "review, not that it cannot be surfaced."
            ),
            notes=(
                "This is the cleanest example of the unintentional failure class. There is no "
                "attacker. There is no negligence. There is no procedural violation. A competent reviewer "
                "following the procedure correctly signs off on an assessment built from "
                "incomplete input. Ask the audience how their graduates would detect this from "
                "the finished report. They cannot: the omission carries no signature in the "
                "output. "
                "Make the second half explicit, because it is what turns this from a shrug into "
                "a teachable fix: this is not an unknowable event. Token-limit and parse-success "
                "checks are cheap and already exist in most ingestion pipelines. The gap is that "
                "the signal was never wired to the review workflow; the signal itself is not "
                "missing. That is what makes this the most directly fixable of the four failure "
                "modes in the abstract, but do not let 'cheap' read as 'easy to have actually "
                "gotten built here'. The same resourcing gap named on the earlier slide (no "
                "allocated developer, a reactive queue already stacked with unaddressed items) "
                "is exactly what would have had to absorb this work. If asked who would have "
                "built it, say plainly that you do not know who at that function had the spare "
                "capacity, because the record shows none was allocated. This failure mode is not "
                "a counterexample to the resourcing finding; it is that finding recurring in a "
                "different room."
            ),
        ),
        Slide(
            title="Failure mode 3: The validated system stops being the running system",
            kind="failure",
            bullets=(
                "A prompt template is edited to make the wording clearer.",
                "An inference parameter or routing threshold is retuned.",
                "The OCR engine or document parser is upgraded as routine infrastructure "
                "maintenance.",
                "None of these is a model change, so none reliably triggers change control.",
                "Then the case that is not a change at all: a system designed to adjust its own "
                "scoring from accumulated reviewer corrections. Its behavior evolves by "
                "design, continuously, with no edit for anyone to review.",
                "On the project I worked on this was confirmed on record. Human-initiated "
                "changes were tracked. The system's own behavioral changes were not, because "
                "the tracking system exists to record what people do.",
            ),
            callout=(
                "Change control as written governs the model. The behavior of the system is "
                "determined by the model, plus everything around it, plus, increasingly, what "
                "the system has taught itself since validation."
            ),
            notes=(
                "The OCR upgrade is the one that lands hardest with technical audiences, "
                "because it is performed by an infrastructure team that has no idea it is "
                "touching a GxP-relevant path, as part of routine patching. It changes what "
                "the model sees on every case. Nothing in a conventional change control "
                "procedure would flag it. "
                "The last two bullets are the ones worth slowing down for, because they are the "
                "version of this problem that is arriving now rather than hypothetically. A "
                "feedback loop that improves a system is a feature, and it is the reason these "
                "tools get better in use. It is also a behavioral change to a validated system "
                "that no existing mechanism records, because activity tracking was designed "
                "around human work. State the confirmation neutrally and do not editorialise: "
                "the answer describes how the tracking system was designed; the person who gave "
                "it made no error. The gap is in the "
                "instrument rather than the individual. "
                "If asked what the fix looks like, say the honest thing: the accumulated "
                "adjustments need a version history, and need to be reviewed and approved "
                "through the same route as a human change, and almost nobody has built that yet."
            ),
        ),
        Slide(
            title="Failure mode 4: Unbounded blast radius",
            kind="failure",
            bullets=(
                "A defect in a model version is confirmed at month six.",
                "The necessary question is: which records did it touch?",
                "Reconstructing one case on demand is a different capability from "
                "enumerating every affected case.",
                "Without the second, a confirmed defect cannot be scoped, and therefore "
                "cannot be remediated or reported.",
                "The industry already has an answer to this exact structural question, just "
                "not yet for model versions: GMP batch genealogy (the 'where-used' query that "
                "identifies every finished-product batch containing a given raw-material lot) "
                "is a standard, regulator-expected recall-scoping capability. The gap is that "
                "the same discipline is not routinely extended to model versions.",
                "The scoping problem compounds if the system also adjusts its own future "
                "behavior from accumulated corrections, as in the previous failure mode: a "
                "defect that shaped what reviewers corrected during the affected window does "
                "not stay contained to the records it touched. It can also have shifted the "
                "model's behavior on every case that followed, and a cohort query by version "
                "and date range alone will not surface that.",
                "Detection latency raises the stakes further: a defect confirmed a year after "
                "introduction, on top of an under-resourced, reactive maintenance function, is "
                "not a bounded incident by the time anyone finds it: it is a moving target.",
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
                "they need it. "
                "The batch-genealogy bullet is the one to lean on hardest with this audience: it "
                "reframes the fix from 'a new AI capability nobody has built' to 'an existing "
                "GMP discipline not yet extended to model versions'. SAP Global Batch "
                "Traceability is a concrete, citable example of this capability already "
                "deployed at scale for materials. If pushed for evidence this is not "
                "AI-specific wishful thinking, commercial ML observability platforms (Arize AI "
                "is a verifiable example) already log a model-version field alongside every "
                "prediction's timestamp and support exporting exactly that cohort by version "
                "and date range. The pattern already exists in ML tooling too, it is simply not "
                "yet standard practice inside GMP-adjacent AI deployments specifically. "
                "If asked what would address the base version of this problem, say plainly: "
                "every record needs a model-version and timestamp tag at processing time, and "
                "the traceability system needs a cohort-query capability over that tag. Single-case "
                "lookup alone is not enough. That part is ordinary data engineering, though it "
                "leaves the compounding case unaddressed: a defect's output has already fed back "
                "into the model's own future behavior through the self-adjusting mechanism from "
                "the previous slide: a cohort-by-date query no longer bounds that, and nobody "
                "in the field has a clean answer for it yet. Keep the year-later scenario "
                "hypothetical and structural: the point is that weak detection capacity and a "
                "self-adjusting system multiply each other, not that this happened here."
            ),
        ),
        Slide(
            title="The common thread",
            kind="section",
            bullets=(
                "In all four cases: a competent person, following the correct procedure, "
                "receives a wrong result with no signal that anything went wrong.",
                "No malice. No negligence. No attacker. No procedural violation.",
                "The controls are documented and inspectable. They are present in the audit trail.",
                "In the specific conditions described, they are also not working.",
            ),
            callout=(
                "The threat model that matters here is internal and unintentional. Security "
                "testing aimed at adversaries will not find any of this."
            ),
            notes=(
                "Land this explicitly. Most AI risk discussion is about misuse, prompt "
                "injection, or data exfiltration. Those are real but they are not the "
                "dominant risk in a controlled internal GMP environment where every user is "
                "authenticated and trained, and is trying to do their job correctly. The dominant "
                "risk is silent wrongness."
            ),
        ),
        Slide(
            title="Why this is a patient safety question",
            bullets=(
                "A draft-review aid does not classify, disposition, or release.",
                "It does determine whether a weak impact assessment or an unsupported risk "
                "rationale gets strengthened before QA ever sees it.",
                "Score an inadequate section as adequate, and the gap it should have surfaced "
                "travels forward into the record instead.",
                "The exposure is second-order and real: a missed chance to catch a wrong "
                "decision made by a person, which is different from a wrong decision made by "
                "the model itself.",
            ),
            callout=(
                "Data integrity expectations (ALCOA+, Part 11, Annex 11) exist because "
                "quality records drive release decisions. A record a model improved, or failed "
                "to improve, is still the record."
            ),
            notes=(
                "Say the first bullet plainly so nobody in the room thinks otherwise: this "
                "tool does not classify, disposition, or release. "
                "This slide converts the preceding material into the language the audience "
                "governs by, and it is where you must be most disciplined. Do not claim the "
                "tool made release decisions: it was explicitly scoped not to. The honest "
                "argument is that it sits upstream of the record a release decision is made "
                "from, and that a missed flag is a real if indirect exposure. That argument is "
                "weaker than the dramatic version and it is the one you can defend."
            ),
        ),
        Slide(
            title="Why existing frameworks do not catch it",
            bullets=(
                "Computer system validation establishes fitness at a point in time; these "
                "systems drift continuously. IQ/OQ/PQ and periodic re-validation are "
                "retriggered by a change to code or configuration: a system that drifts from "
                "accumulated feedback with no code change, as in failure mode 3, simply never "
                "trips that trigger.",
                "Risk-based categorization assumes deterministic input-output behavior. A "
                "fixed test suite standing in for exhaustive testing only works if the same "
                "input reliably produces the same output; submit the same draft twice and a "
                "language model can legitimately return two different scores, and no risk "
                "category anticipates that as normal rather than as a defect.",
                "Annex 11 and Part 11 predate language models and say nothing about "
                "acceptance-rate monitoring or context-window limits: the specific blind "
                "spots behind failure modes 1 and 2 earlier in this talk.",
                "Change control and recall scoping assume a bounded, traceable propagation "
                "path for a defect, the same batch-genealogy logic behind failure mode 4. A "
                "shared model artifact affects every case processed after it, and no "
                "requirement mandates the cohort-query capability that would scope that.",
                "None of these frameworks is wrong. They are necessary and currently "
                "insufficient.",
            ),
            callout=(
                "This is not a framework failure so much as a category the framework was "
                "never written to cover."
            ),
            notes=(
                "Be careful and generous here. This audience teaches these frameworks. The "
                "argument is additive rather than dismissive: the existing apparatus is sound for "
                "deterministic systems and needs a supplement for probabilistic ones. If you "
                "come across as saying validation is broken, you lose the room. "
                "Each of the first four bullets is a deliberate callback to one of the four "
                "failure modes shown earlier: naming the number out loud is what turns this "
                "slide from an abstract framework critique into a demonstration that you can "
                "point to the exact concrete gap each framework misses."
            ),
        ),
        Slide(
            title="What I built in response",
            kind="section",
            bullets=(
                "First, in the product itself: a safety framework of 19 registered mechanisms "
                "covering prompt integrity verification, audit logging, scope detection, "
                "uncertainty annotation, disagreement escalation and deterministic replay.",
                "A 25-item assessment instrument built for a system that already exists, "
                "rather than a design still under review.",
                "Each item specifies what to inspect, what evidence to request, an objective "
                "pass criterion, and a disqualifying finding.",
                "Items are traced to named release gates, so a finding maps to a control "
                "someone owns.",
                "Reviewer-administered, with a scoring engine that produces a findings report.",
                "Some controls I deliberately did not build. Authentication, authorization and "
                "drift thresholds each depend on a decision that belongs to Quality rather than "
                "to a developer, so I documented each gap for the next maintainer instead of "
                "pre-empting them.",
                "A technical control is only meaningful inside the procedure that defines it. "
                "That is why the instrument inspects procedures rather than code.",
            ),
            callout=(
                "The instrument is the deliverable I would want to hand to a QA reviewer who "
                "has one day on site and no prior AI background."
            ),
            notes=(
                "Transition from problem to contribution. The important design choice is that "
                "every item asks for observed system behavior or a retrievable artifact, "
                "never for an opinion or a self-rating. A reviewer with no machine learning "
                "background can execute it, which is the point. "
                "Expect the sharpest challenge in the room here, and answer it directly rather "
                "than deflect: if no standard existed to identify a competent builder and no "
                "procedure existed either, why should anyone trust this instrument, and why did "
                "you not simply fix the underlying system yourself? Answer in three parts. "
                "First, the instrument's own design does not ask anyone to trust your "
                "competence: every item requires an observed system behavior or a retrievable "
                "artifact, never a self-rating or an opinion, which is deliberate: its output "
                "should not depend on who administers it. Second, it does not claim to be a "
                "validated procedure or an approved SOP, but a reviewer aid offered for the "
                "same scrutiny this whole talk invites, and the disclaimer says outright that "
                "interpretation and sign-off require qualified QA, regulatory, and "
                "clinical-safety personnel: it asks to be checked rather than trusted on your say-so. "
                "Third, on why the underlying system itself was not fixed: several of the "
                "specific gaps identified earlier are ordinary engineering, but ordinary "
                "engineering still needs a resourced, in-house developer, and the resourcing "
                "slide already established that this layer did not have one. Producing an "
                "assessment instrument was within the scope and authority available to a "
                "departing product owner. Rewriting another team's production system was not."
            ),
        ),
        Slide(
            title="The design principle: fail closed",
            bullets=(
                "An item recorded as not assessed counts as unresolved, exactly like a "
                "failure.",
                "An untouched template therefore scores as blocking, never as passing.",
                "Any single unresolved patient-safety item forces a blocking result "
                "regardless of the other 24.",
                "The cleanest available verdict is 'no blocking findings identified', never "
                "'approved'.",
            ),
            callout=(
                "Absence of evidence is not evidence of control. Most maturity assessments "
                "score the opposite way, and that is how a deployment passes review without "
                "anyone having looked."
            ),
            notes=(
                "This is the slide a technical audience will engage with most. The default "
                "behavior of almost every scorecard is that unanswered questions are "
                "silently excluded from the denominator, which means an assessment nobody "
                "completed can look like a pass. CMMI is the concrete example if someone "
                "asks for one: under the official SCAMPI appraisal method, a goal that lacks "
                "sufficient objective evidence is rated 'not rated,' and a process area with "
                "insufficient data coverage is excluded from the rating entirely rather than "
                "counted as a gap: the industry's own reference maturity model treats "
                "missing evidence as neutral rather than as a failure. Inverting that default "
                "is the single most important property of the tool."
            ),
        ),
        Slide(
            title="What it produces",
            kind="demo",
            subtitle="Synthetic sample data. No findings shown are from a real deployment.",
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
                "approval; the finding cites a specific metric rather than a judgment; and the "
                "non-zero exit code means this can gate an automated release pipeline rather "
                "than living in a document nobody reads. If there is time, run it live: it is "
                "more convincing than a screenshot."
            ),
        ),
        Slide(
            title="Limitations I want to state plainly",
            bullets=(
                "Entirely self-attested. There is no evidence hashing and no reviewer "
                "independence check: a vendor could complete it about its own product.",
                "18 of 25 items block. A well-run deployment will likely still fail on first "
                "pass, which risks the verdict carrying no discriminating information.",
                "Never validated against real inspection outcomes. I do not know whether it "
                "predicts anything.",
                "Point-in-time. It has no expiry, and nothing forces reassessment after a "
                "model or infrastructure change.",
            ),
            callout=(
                "High line coverage on the scoring engine proves the logic is consistent. It "
                "says nothing about whether the rubric's blocking threshold is set correctly."
            ),
            notes=(
                "Do not skip this slide, and do not apologize through it. Volunteering the "
                "weaknesses is what separates an analysis from an advocacy pitch, and this "
                "audience will find these problems anyway. The threshold issue is the one "
                "worth genuinely asking their opinion on: if nearly everything blocks, the "
                "instrument stops distinguishing a careless deployment from a careful one."
            ),
        ),
        Slide(
            title="The conclusion I drew",
            bullets=(
                "The system never went live. I resigned before the alpha pilot began, so none "
                "of this is an account of a system in production.",
                "I put the question in writing and then in person to the executive sponsor: "
                "what operational standard should the alpha ship under, given the gap between "
                "the AI layer's practices and the standard the same organization applied "
                "elsewhere. I built the case from its own records and credited the engineering "
                "discipline demonstrated elsewhere in it.",
                "The answer did not resolve the question, so I filed a formal quality "
                "observation through the organization's own observation procedure: requesting "
                "a tracking identifier, a named owner for the gap, a timeline for an AI use "
                "procedure, and deferral of GMP-adjacent deployment until one existed.",
                "I told my manager I was filing it before I filed it, and sent the analysis to "
                "compliance leadership so it would outlast my notice period rather than leave "
                "with me.",
                "Then I resigned and worked the notice, delivering the transition "
                "documentation I had promised.",
            ),
            callout=(
                "I am not claiming harm occurred and I am not claiming an unsafe system "
                "shipped. Neither happened. I raised a prospective risk through the "
                "organization's own quality channel, did not get the assurance I needed, and "
                "declined to own the launch."
            ),
            notes=(
                "One slide, stated once, then move on. Leading with 'never went live' removes "
                "any suggestion that you are describing a production failure or accusing "
                "anyone of shipping something unsafe. "
                "The sequence is what makes this credible, so deliver it in order: raised in "
                "writing and in person, answer received, formal quality observation filed "
                "through the organization's own procedure, manager told in advance, analysis "
                "routed to compliance so it would survive your departure, notice worked, "
                "transition documentation delivered. That is an escalation record rather than a "
                "complaint, and it is the complete answer to 'why did you not just raise it "
                "internally'. You did, through the channel the quality system provides. "
                "The advance notice to your manager is not a small detail and you should say it "
                "out loud. Filing a quality observation about your own project while telling "
                "your manager first is the difference between a professional act and a parting "
                "shot, and a room of quality professionals will register that difference "
                "immediately. "
                "You do hold a contemporaneous record of the response, which is why the "
                "recorded answer appears on the earlier procedure slide. State it as a "
                "documented answer about sequencing and infer nothing about motive. The "
                "inversion speaks for itself and any gloss you add will sound like an "
                "accusation. "
                "Do not say you lost confidence in management, however true it felt at the "
                "time. It invites a debate about the character of people the room has never "
                "met, which you cannot win and do not need; 'the answer did not resolve the "
                "question' is the same fact without the grievance. "
                "Expect to be asked whether resigning was proportionate. It is a judgment "
                "call, you made it on the information you had while holding the product owner "
                "role, and the instrument is your attempt to make that judgment reviewable by "
                "other people. If asked for specifics you cannot share, say plainly that you "
                "are bound by confidentiality. "
                "If asked why you are still pursuing AI in life sciences after this, answer it "
                "directly: this is the experience that told you what compliant, patient-safety-"
                "first implementation has to look like, and it is why you are staying in the "
                "field rather than avoiding it. The instrument on the earlier slides already "
                "puts that intent into practice; nothing about it is hypothetical."
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
                "A concrete example of what such a standard would catch: an interface that "
                "requires the user to phrase input in a narrow, undocumented way, and "
                "degrades into incoherent output rather than a clear error when they do not: "
                "shifting the cognitive burden back onto the person the tool exists to help.",
            ),
            callout=(
                "In this case study, the last control in the chain was a reviewer trained to "
                "operate the system, not to audit it."
            ),
            notes=(
                "Present this as a finding of the case study rather than a request, and let "
                "the faculty draw their own curriculum implications rather than proposing what "
                "they should change; if asked directly whether you have a suggestion, the "
                "four failure modes and the instrument itself are concrete material you can "
                "point to, but lead with the finding rather than the offer. "
                "The build-side competency bullet is the one this audience is best placed to "
                "evaluate, since defining and assessing competency is their core business. Keep "
                "it structural: the finding is an absent standard, and it says nothing about "
                "any individual. If asked whether you saw this go wrong in practice, say the "
                "standard was absent and stop there. Speculating about whether a particular person met a standard "
                "that was never written is neither fair nor arguable, and it will cost you the "
                "room instantly. "
                "The interface bullet is a generic illustration of what an absent build-side "
                "standard misses in practice, not an account of any specific tool or person's "
                "work. Do not let it become one if a question tries to make it so. If pressed "
                "for a real example, redirect to the general pattern: some interfaces make "
                "failure the user's fault by design, and that is exactly what a competency "
                "standard should catch before deployment rather than after."
            ),
        ),
        Slide(
            title="The reviewer question is starting to be tested. The builder question is not.",
            bullets=(
                "Preregistered experiments now directly test reviewer vigilance under AI "
                "oversight: a 12-week, double-blind trial had licensed pharmacy reviewers "
                "evaluate AI-drafted adverse event summaries under deliberately injected "
                "errors, and found the effect on true-error detection was nonmonotone rather "
                "than simply 'more errors shown, more caught' (Fang et al., SSRN working "
                "paper, 2025).",
                "A separate randomized experiment found reviewers corrected an overly harsh "
                "score less often when it was labeled AI-generated than when the identical "
                "score was labeled human-generated: a 22 percent larger fairness gap driven "
                "by the label alone (Goulas et al., PNAS Nexus, 2026).",
                "A parallel line of explainable-AI research is building frameworks for "
                "decomposing what a model's stated rationale is actually made of, aimed at "
                "giving a reviewer something legible to check against rather than a bare "
                "score.",
                "None of that answers who is competent to build the system a reviewer is "
                "checking. The empirical literature testing and qualifying builders for a "
                "regulated process is comparatively thin next to the literature testing "
                "reviewers.",
                "That asymmetry is the same one this case study found inside one "
                "organization: real, measurable attention to the reviewing side, and very "
                "little yet to the building side.",
            ),
            callout=(
                "The two questions this case study opened with are not equally studied. One "
                "now has a growing empirical literature. The other does not yet, and that is "
                "where I intend to keep working."
            ),
            notes=(
                "This slide updates the case study with where the field has moved since the "
                "placement ended, so date it clearly as recent, ongoing work rather than "
                "something available at the time. Say plainly that neither citation is from "
                "life sciences directly: the pharmacovigilance trial is adjacent, drug safety "
                "review performed by PharmD reviewers, and the grading study is from "
                "education, but the mechanism, a labeled recommendation changing how hard a "
                "person pushes back, generalizes to any domain where a human reviews a "
                "model's output before it becomes a record. "
                "Be exact about what the pharmacovigilance trial found: the relationship "
                "between error frequency and detection was not linear. Low-frequency error "
                "injection made true-error detection worse before higher frequency made it "
                "better. That nuance matters more than the headline, because it means 'show "
                "reviewers more errors' is not automatically a fix. "
                "The explainability bullet is deliberately generic. Do not claim any specific "
                "explanation method would have solved anything on this project; say only that "
                "a body of work exists on specifying what an explanation is made of, and that "
                "it targets the reviewer side of the problem rather than the builder side. "
                "The claim that builder-qualification research is thin is a comparative claim "
                "about where research attention has gone, not a claim that no such research "
                "exists anywhere. State it that way if pressed. "
                "Close by tying this back explicitly to the standard-for-who-builds-it and "
                "curriculum-gap slides: this is not a new finding about the case study, it is "
                "where you intend to keep working after it."
            ),
        ),
        Slide(
            title="Questions I would like your view on",
            kind="closing",
            bullets=(
                "With 18 of the 25 items able to block on their own, is that the right "
                "threshold, or does it make the instrument useless in practice?",
                "How much should the blocking set flex with the deployment's risk class, "
                "if at all?",
                "Which existing curriculum area is the more natural home for this, "
                "validation or quality systems, or does it deserve a module of its own?",
                "What would convince you that a reviewer assigned to oversee a model is "
                "actually competent to do it?",
                "Explainability research is starting to decompose what a model's rationale "
                "is actually made of. Turning that into something a reviewer is trained to "
                "use looks like a curriculum question more than a research one: do you agree?",
                "What competency standard would you want met by someone building an AI feature "
                "that touches a regulated record?",
                "If you defined that standard, what would make an employer verify it before "
                "assigning the work? Mine was never verified.",
            ),
            notes=(
                "Ending on genuine questions rather than a summary invites collaboration and "
                "signals that you are not there to lecture them. These are real open problems, "
                "not rhetorical exercises. Have your own tentative answer ready for each in case they "
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
    --ink: #101828;
    --muted: #475467;
    --accent: #0b4e8f;
    --accent-soft: #e8f1fb;
    --warn: #b54708;
    --rule: #e4e7ec;
    --bg: #f2f4f7;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: radial-gradient(circle at 50% -10%, #e6eef7 0%, transparent 40%), var(--bg);
    color: var(--ink);
    font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }}
  .toolbar {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 10;
    display: flex; gap: 14px; align-items: center;
    padding: 10px 20px;
    background: rgba(255,255,255,0.82);
    -webkit-backdrop-filter: blur(12px); backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--rule);
    font-size: 13px; color: var(--muted);
  }}
  .toolbar strong {{ color: var(--ink); font-weight: 650; }}
  .toolbar button {{
    font: inherit; font-weight: 600; cursor: pointer; padding: 5px 12px;
    border: 1px solid var(--rule); border-radius: 8px; background: #fff; color: var(--ink);
    box-shadow: 0 1px 2px rgba(16,24,40,0.06);
    transition: border-color .15s, box-shadow .15s;
  }}
  .toolbar button:hover {{ border-color: var(--accent); box-shadow: 0 1px 4px rgba(11,78,143,0.18); }}
  main {{ padding: 64px 0 0; }}
  .slide {{
    position: relative;
    max-width: 960px;
    margin: 0 auto 32px;
    padding: 48px 56px 64px;
    background: #fff;
    border: 1px solid var(--rule);
    border-radius: 16px;
    box-shadow: 0 1px 2px rgba(16,24,40,0.05), 0 12px 32px -16px rgba(16,24,40,0.14);
    min-height: 62vh;
  }}
  .slide-title {{
    background:
      radial-gradient(circle at 90% 0%, rgba(94,234,212,0.14), transparent 45%),
      linear-gradient(160deg, #fff 45%, #eaf2f9 100%);
  }}
  .slide-section {{
    background:
      radial-gradient(circle at 88% 8%, rgba(94,234,212,0.20), transparent 50%),
      linear-gradient(150deg, #0a2540 0%, #0b4e8f 70%, #0f766e 100%);
    border-color: transparent;
    color: #f4f8fc;
  }}
  .slide-section h2 {{ color: #fff; border-bottom-color: rgba(255,255,255,0.25); }}
  .slide-section .lead {{ color: rgba(255,255,255,0.95); }}
  .slide-section li, .slide-section p {{ color: #dbe7f3; }}
  .slide-section li::marker {{ color: #5eead4; }}
  .slide-section footer {{ color: rgba(255,255,255,0.55); border-top-color: rgba(255,255,255,0.18); }}
  .slide-section blockquote {{
    background: rgba(255,255,255,0.10); border-left-color: #5eead4;
    color: #f0f6fc;
  }}
  .slide-section .subtitle {{ color: #c3d5e8; }}
  .slide-section .disclaimer {{ color: rgba(255,255,255,0.6); }}
  .slide-section aside.notes {{
    background: rgba(255,255,255,0.07); border-color: rgba(255,255,255,0.25);
    color: #c3d5e8;
  }}
  .slide-section aside.notes strong {{ color: #fff; }}
  h1 {{ font-size: 42px; font-weight: 750; line-height: 1.12; margin: 0 0 18px; letter-spacing: -0.02em; color: #0a2540; }}
  h2 {{
    font-size: 26px; font-weight: 700; letter-spacing: -0.015em; line-height: 1.25;
    margin: 0 0 22px; padding-bottom: 12px; border-bottom: 2px solid var(--accent);
    color: #0a2540;
  }}
  .slide-failure h2 {{ border-bottom-color: var(--warn); }}
  .subtitle {{ font-size: 19px; color: var(--muted); margin: 0 0 26px; line-height: 1.5; }}
  .lead {{ font-size: 17px; font-weight: 650; margin: 0 0 16px; }}
  ul {{ margin: 0 0 20px; padding-left: 22px; }}
  li {{ margin-bottom: 11px; font-size: 17px; }}
  li::marker {{ color: var(--accent); }}
  blockquote {{
    margin: 22px 0 0; padding: 16px 20px;
    background: var(--accent-soft); border-left: 4px solid var(--accent);
    border-radius: 0 10px 10px 0; font-size: 16px; line-height: 1.55;
  }}
  .slide-failure blockquote {{ background: #fffaeb; border-left-color: var(--warn); }}
  pre.demo {{
    background: #0b1220; color: #e6edf3; padding: 20px 22px; border-radius: 10px;
    border: 1px solid #1e293b;
    font: 13px/1.55 "SF Mono", Menlo, Consolas, monospace; overflow-x: auto; margin: 0 0 18px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
  }}
  .disclaimer {{ font-size: 13px; color: var(--muted); font-style: italic; margin: 30px 0 0; line-height: 1.5; }}
  aside.notes {{
    margin: 26px 0 0; padding: 14px 18px; border: 1px dashed var(--rule);
    border-radius: 10px; background: #f8fafc; color: var(--muted); font-size: 14.5px; line-height: 1.5;
  }}
  aside.notes strong {{ color: var(--ink); }}
  body.hide-notes aside.notes {{ display: none; }}
  footer {{
    position: absolute; left: 56px; right: 56px; bottom: 20px;
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
      box-shadow: none;
    }}
    .slide-section {{
      background: #fff; color: var(--ink); border-bottom: 3px solid var(--accent);
    }}
    .slide-section h2 {{ color: var(--ink); }}
    .slide-section li, .slide-section p {{ color: var(--ink); }}
    .slide-section .subtitle, .slide-section .disclaimer {{ color: var(--muted); }}
    .slide-section blockquote {{
      background: var(--accent-soft); border-left-color: var(--accent);
      color: var(--ink);
    }}
    .slide-section footer {{ color: var(--muted); border-top-color: var(--rule); }}
    pre.demo {{ print-color-adjust: exact; -webkit-print-color-adjust: exact; }}
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
