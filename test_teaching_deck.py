"""Tests for the teaching deck generator.

The important tests here are not about rendering. They enforce the framing
decisions that make the deck safe to present: no identifying details, the
resignation kept late and brief, and limitations stated rather than omitted.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import generate_teaching_deck as deck

REPO_ROOT = Path(__file__).resolve().parent

# Terms that would identify the employer, its clients, or its vendors. The deck
# argues from generalized failure modes; if any of these appear, the framing has
# drifted and the legal exposure changes.
IDENTIFYING_TERMS = (
    "kbi",
    "biopharma",
    "cdmo",
    "my employer",
    "my former employer",
    "the company i",
    "boulder",
    # Surfaced by the source memo. Colleague surnames, internal product and repo
    # names, and ticket identifiers - each of which would make the organisation
    # and named individuals identifiable.
    "sohoni",
    "rocher",
    "abrahamsen",
    "morimoto",
    "minghella",
    "votkevich",
    "kavanaugh",
    "lowery",
    "whitaker",
    "vazquez",
    "hoyt",
    "pereda",
    "fankhauser",
    "lofton",
    "bufford",
    "montalvo",
    "grissom",
    "guntz",
    "programview",
    "datahow",
    "das-pipelines",
    "platform-data-engineering",
    "field intelligence navigator",
    "ddas-",
    "ic2f",
    "posthog",
    "salesforce",
    "jira",
)


class DeIdentificationTests(unittest.TestCase):
    def test_rendered_deck_names_no_employer_client_or_vendor(self) -> None:
        for name, content in (
            ("markdown", deck.build_markdown()),
            ("html", deck.build_html()),
        ):
            lowered = content.lower()
            for term in IDENTIFYING_TERMS:
                with self.subTest(artifact=name, term=term):
                    self.assertNotIn(
                        term,
                        lowered,
                        f"{name} deck contains identifying term {term!r}; the deck must "
                        f"argue from generalized failure modes only",
                    )

    def test_disclaimer_states_it_is_not_a_determination_about_any_system(self) -> None:
        lowered = deck.DISCLAIMER.lower()
        self.assertIn("does not identify", lowered)
        self.assertIn("not a compliance determination", lowered)
        for content in (deck.build_markdown(), deck.build_html()):
            self.assertIn("does not identify", content.lower())

    def test_no_personal_competence_judgements(self) -> None:
        """A competency concern is defensible as an absent standard and indefensible
        as a verdict on an individual. The second form is a personnel claim about an
        identifiable person and has no place in a de-identified public talk."""
        forbidden = (
            "underqualified",
            "unqualified",
            "not qualified",
            "sparse resume",
            "thin resume",
            "incompetent",
            "lacked the experience",
            "no relevant experience",
        )
        haystack = deck.build_markdown().lower() + deck.build_html().lower()
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, haystack)

    def test_escalation_is_recorded_as_written_and_in_person(self) -> None:
        """The escalation record is the author's strongest fact - it answers 'why
        didn't you raise it internally'. It must survive future edits."""
        slide = next(s for s in deck.slides() if "conclusion i drew" in s.title.lower())
        joined = " ".join(slide.bullets).lower()
        self.assertIn("in writing", joined)
        self.assertIn("executive sponsor", joined)
        self.assertIn("compliance leadership", joined)

    def test_no_grievance_framing_about_management(self) -> None:
        """'The answers did not resolve the question' is the same fact as 'I lost
        confidence in management' without inviting a character debate.

        Checked against spoken content only. The speaker notes name these phrases in
        order to forbid them, which is guidance rather than a drift in framing.
        """
        haystack = " ".join(
            f"{s.title} {s.subtitle} {' '.join(s.bullets)} {s.callout}"
            for s in deck.slides()
        ).lower()
        for phrase in (
            "lost confidence in management",
            "lost faith in",
            "management refused",
            "they ignored",
            "nobody listened",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, haystack)

    def test_both_readiness_gaps_precede_the_failure_modes(self) -> None:
        """The two readiness gaps are the original argument; the failure modes exist
        to explain why they matter. If a failure mode leads, the deck reverts to a
        generic AI-risk talk and the author's own contribution is buried."""
        titles = [s.title.lower() for s in deck.slides()]
        engineering = next(i for i, t in enumerate(titles) if "asymmetry inside" in t)
        acceptance = next(i for i, t in enumerate(titles) if "other readiness gap" in t)
        first_failure = next(
            i for i, s in enumerate(deck.slides()) if s.kind == "failure"
        )
        self.assertLess(engineering, first_failure)
        self.assertLess(acceptance, first_failure)
        self.assertLess(engineering, acceptance, "engineering gap frames the human one")

    def test_readiness_gap_credits_genuine_appetite(self) -> None:
        """The survey response was the largest the organisation had recorded. Stating
        that keeps the slide a readiness finding rather than a swipe at colleagues."""
        slide = next(s for s in deck.slides() if "other readiness gap" in s.title.lower())
        joined = " ".join(slide.bullets).lower()
        self.assertIn("appetite was real", joined)
        self.assertIn("largest response", joined)

    def test_no_organisation_wide_ai_training_existed(self) -> None:
        """No AI training programme existed at all, and even the organisation's own
        first course was scoped to arrive during or after deployment - the timing
        failure behind the 'nobody trained for it' claim on the case-study slide."""
        slide = next(s for s in deck.slides() if "other readiness gap" in s.title.lower())
        joined = " ".join(slide.bullets).lower()
        self.assertIn("no organisation-wide training programme", joined)
        self.assertIn("during or after the alpha's deployment", joined)

    def test_intern_status_is_disclosed(self) -> None:
        """Describing oneself as the product owner while omitting that one was a
        temporary intern is a material omission. An audience that discovers it
        afterwards discounts everything else in the talk, so the disclosure must
        survive future edits."""
        slide = next(
            s for s in deck.slides() if "resourcing actually looked" in s.title.lower()
        )
        joined = " ".join(slide.bullets).lower()
        self.assertIn("temporary intern", joined)
        self.assertIn("that intern was me", joined)

    def test_experience_claim_does_not_overstate_exposure(self) -> None:
        """The presenter's first slide establishes this as a first exposure to the
        industry. A claim to have observed 'every deployment' or many deployments
        would contradict that and must not reappear."""
        haystack = " ".join(
            f"{s.title} {' '.join(s.bullets)} {s.callout}" for s in deck.slides()
        ).lower()
        for phrase in ("every deployment i", "deployments i have seen",
                       "deployments i've seen", "in every deployment"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, haystack)

    def test_product_owner_claim_is_qualified_by_seniority(self) -> None:
        """Wherever the deck claims the product owner role, it must also say who was
        holding it."""
        for slide in deck.slides():
            joined = " ".join(slide.bullets).lower()
            if "product owner" in joined:
                with self.subTest(slide=slide.title):
                    self.assertIn("intern", joined)

    def test_escalation_records_the_formal_quality_filing(self) -> None:
        """The author did not merely raise concerns informally; a formal observation was
        filed through the organisation's own procedure. That is the complete answer to
        'why did you not raise it internally' and must not be understated."""
        slide = next(s for s in deck.slides() if "conclusion i drew" in s.title.lower())
        joined = " ".join(slide.bullets).lower()
        self.assertIn("formal quality observation", joined)
        self.assertIn("deferral", joined)
        self.assertIn("before i filed it", joined)

    def test_recorded_sequencing_answer_is_stated_without_gloss(self) -> None:
        """The recorded answer - procedure after deployment - is the strongest single
        fact in the deck. It must appear, and must not be editorialised."""
        slide = next(s for s in deck.slides() if "control that did not exist" in s.title.lower())
        joined = " ".join(slide.bullets).lower()
        self.assertIn("after the alpha went live", joined)
        for gloss in ("astonishing", "backwards", "reckless", "absurd", "unbelievable"):
            with self.subTest(gloss=gloss):
                self.assertNotIn(gloss, joined)

    def test_self_modifying_system_is_covered_by_change_control_slide(self) -> None:
        """A system that adjusts its own behaviour from accumulated feedback changes a
        validated system with no edit for anyone to review. This is the current form of
        the drift problem and the deck must carry it."""
        slide = next(s for s in deck.slides() if "stops being the running system" in s.title.lower())
        joined = " ".join(slide.bullets).lower()
        self.assertIn("adjust its own", joined)
        self.assertIn("confirmed on record", joined)

    def test_change_control_finding_blames_the_instrument_not_a_person(self) -> None:
        """Activity tracking not recording machine-initiated change is a design property
        of the tracking system, not a failing of whoever described it."""
        slide = next(s for s in deck.slides() if "stops being the running system" in s.title.lower())
        spoken = f"{' '.join(slide.bullets)} {slide.callout}".lower()
        for phrase in ("failed to", "should have", "neglected", "did not bother",
                       "was wrong to"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, spoken)

    def test_built_slide_records_restraint_and_the_thesis(self) -> None:
        """Declining to build controls that encode Quality's decisions is a professional
        signal, and the procedure-defines-the-control line is the deck's thesis."""
        slide = next(s for s in deck.slides() if "what i built" in s.title.lower())
        joined = " ".join(slide.bullets).lower()
        self.assertIn("deliberately did not build", joined)
        self.assertIn("only meaningful inside the procedure that defines it", joined)

    def test_maintenance_capacity_finding_is_present(self) -> None:
        """Who sustains the validated state after launch is a first-order GMP question."""
        slide = next(s for s in deck.slides() if "resourcing actually" in s.title.lower())
        joined = " ".join(slide.bullets).lower()
        self.assertIn("no in-house developer assigned", joined)
        self.assertIn("no proactive maintenance model", joined)

    def test_hiring_finding_uses_the_author_as_its_own_evidence(self) -> None:
        """The competency finding is safe to make precisely because the unverified
        person was the author. If it ever generalises to how colleagues were hired it
        becomes an unevidenced claim about identifiable people."""
        slide = next(s for s in deck.slides() if "standard for who builds" in s.title.lower())
        joined = " ".join(slide.bullets).lower()
        self.assertIn("i was hired", joined)
        self.assertIn("i am the evidence", joined)
        for phrase in ("they were hired", "he was hired", "was hired without",
                       "nobody on the team was"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, joined)

    def test_hiring_finding_does_not_claim_the_decision_was_wrong(self) -> None:
        """The finding is an absent verification step, not a bad outcome. Claiming the
        hire was wrong would be both unfalsifiable and self-defeating."""
        slide = next(s for s in deck.slides() if "standard for who builds" in s.title.lower())
        joined = " ".join(slide.bullets).lower()
        self.assertIn("no step existed", joined)
        self.assertIn("not that the judgement was wrong", joined)

    def test_data_access_finding_is_framed_as_a_missing_prerequisite(self) -> None:
        """The defensible finding is that no prerequisite required build-side access to
        the records, and that review therefore rested on one person. Framing it as what
        a colleague did or did not know would be a personnel claim."""
        slide = next(s for s in deck.slides() if "who could actually see" in s.title.lower())
        joined = " ".join(slide.bullets).lower()
        self.assertIn("controlled document", joined)
        self.assertIn("no prerequisite", joined)
        self.assertIn("one person", joined)
        for phrase in ("did not know", "was unaware", "had no idea", "did not understand"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, joined)

    def test_missing_procedure_finding_is_present(self) -> None:
        """In a GMP quality system the absence of a controlled procedure is itself the
        finding. This is the deck's most quality-literate point and must not be lost."""
        slide = next(s for s in deck.slides() if "control that did not exist" in s.title.lower())
        joined = " ".join(slide.bullets).lower()
        self.assertIn("controlled procedure", joined)
        self.assertIn("no procedure governing", joined)
        self.assertIn("disclosure surface", joined)

    def test_shadow_ai_finding_names_no_users(self) -> None:
        """The finding is the absent procedure, not the people who improvised without
        one."""
        slide = next(s for s in deck.slides() if "control that did not exist" in s.title.lower())
        spoken = f"{' '.join(slide.bullets)} {slide.callout}".lower()
        for tool in ("gemini", "chatgpt", "chat gpt", "claude", "copilot", "perplexity"):
            with self.subTest(tool=tool):
                self.assertNotIn(tool, spoken)

    def test_resourcing_finding_precedes_the_failure_modes(self) -> None:
        titles = [s.title.lower() for s in deck.slides()]
        resourcing = next(i for i, t in enumerate(titles) if "resourcing actually" in t)
        first_failure = next(i for i, s in enumerate(deck.slides()) if s.kind == "failure")
        self.assertLess(resourcing, first_failure)

    def test_competency_gap_is_framed_as_an_absent_standard(self) -> None:
        md = deck.build_markdown().lower()
        self.assertIn("competency standard", md)
        self.assertIn("no stated competency requirement", md)

    def test_no_claim_that_harm_occurred(self) -> None:
        """The supportable claim is an unassessed risk, not a realised harm."""
        haystack = deck.build_markdown().lower()
        for overclaim in ("harmed patients", "caused harm", "patients were harmed"):
            with self.subTest(phrase=overclaim):
                self.assertNotIn(overclaim, haystack)


class SourcingTests(unittest.TestCase):
    """Regression: acceptance-rate and dwell-time figures originated as sample
    data invented to exercise the scoring CLI. They were briefly rendered on a
    slide labelled 'Observed pattern', which asserted field measurements that
    had no source. Slide bullets must not present numbers as observations."""

    def test_no_bullet_claims_an_observed_measurement(self) -> None:
        for slide in deck.slides():
            for bullet in slide.bullets:
                with self.subTest(slide=slide.title, bullet=bullet[:40]):
                    self.assertNotIn("observed pattern", bullet.lower())
                    self.assertNotIn("99.4", bullet)
                    self.assertNotIn("11 second", bullet.lower())

    def test_demo_output_is_labelled_synthetic(self) -> None:
        """The demo may use invented figures, but only if it says so on the slide."""
        demos = [s for s in deck.slides() if s.kind == "demo"]
        self.assertTrue(demos)
        for slide in demos:
            with self.subTest(slide=slide.title):
                self.assertIn("synthetic", slide.subtitle.lower())

    def test_automation_bias_notes_warn_against_citing_figures(self) -> None:
        slide = next(s for s in deck.slides() if "automation bias" in s.title.lower())
        self.assertIn("do not cite specific", slide.notes.lower())

    def test_deck_states_the_system_never_deployed(self) -> None:
        """The system never reached alpha. A deck implying a production failure
        would misrepresent the employer as having shipped something unsafe."""
        for name, content in (
            ("markdown", deck.build_markdown()),
            ("html", deck.build_html()),
        ):
            with self.subTest(artifact=name):
                self.assertIn("did not reach deployment", content.lower())
        self.assertIn("never went live", deck.build_markdown().lower())

    def test_no_slide_claims_the_tool_decided_disposition(self) -> None:
        """The design spec explicitly prohibited classification and disposition.
        The deck must not describe capabilities the system was scoped against."""
        forbidden = ("triage decides", "the ai classifies", "model classifies")
        for slide in deck.slides():
            joined = " ".join(slide.bullets).lower() + slide.callout.lower()
            for phrase in forbidden:
                with self.subTest(slide=slide.title, phrase=phrase):
                    self.assertNotIn(phrase, joined)


class FramingTests(unittest.TestCase):
    def test_failed_batch_cost_is_attributed_as_verbal_testimony(self) -> None:
        """The $9 million figure came from one supervisor in one meeting. It must
        stay attributed as testimony, not asserted as an audited company figure,
        and the commercial-upside point must stay framed as the author's own
        inference rather than a documented plan."""
        slide = next(
            s for s in deck.slides() if "attractive place to deploy ai" in s.title.lower()
        )
        joined = " ".join(slide.bullets).lower()
        self.assertIn("my supervisor told me directly", joined)
        self.assertIn("9 million", joined)
        notes = slide.notes.lower()
        self.assertIn("not an audited or", notes)
        self.assertIn("your own inference", notes)

    def test_regulatory_acceptance_argument_is_named(self) -> None:
        """The compliance case for a draft-review aid rests on the tool's input being
        optional and a human always approving. Naming this explicitly on the
        'where it sits' slide is what makes the later human-oversight finding read
        as a test of the premise rather than an unrelated complaint."""
        slide = next(
            s for s in deck.slides() if "actually sits" in s.title.lower()
        )
        joined = " ".join(slide.bullets).lower()
        self.assertIn("regulatory acceptance argument", joined)
        self.assertIn("optional", joined)
        self.assertIn("final approval", joined)

    def test_resignation_appears_late_and_only_once(self) -> None:
        titles = [s.title for s in deck.slides()]
        matches = [i for i, s in enumerate(deck.slides()) if "conclusion i drew" in s.title.lower()]
        self.assertEqual(1, len(matches), "the resignation must be exactly one slide")
        position = matches[0] / len(titles)
        self.assertGreater(
            position,
            0.75,
            "the resignation is the conclusion, not the thesis; it belongs in the last quarter",
        )

    def test_limitations_are_stated_not_omitted(self) -> None:
        titles = " ".join(s.title.lower() for s in deck.slides())
        self.assertIn("limitations", titles)

    def test_business_case_is_presented_before_the_criticism(self) -> None:
        """A deck that strawmans the motivation loses a technical audience."""
        kinds = [s.title.lower() for s in deck.slides()]
        business = next(i for i, t in enumerate(kinds) if "attractive place" in t)
        first_failure = next(
            i for i, s in enumerate(deck.slides()) if s.kind == "failure"
        )
        self.assertLess(business, first_failure)

    def test_every_slide_carries_speaker_notes(self) -> None:
        for slide in deck.slides():
            with self.subTest(slide=slide.title):
                self.assertTrue(
                    slide.notes.strip(),
                    "the speaker has to deliver this; every slide needs notes",
                )

    def test_four_failure_modes_are_present(self) -> None:
        failures = [s for s in deck.slides() if s.kind == "failure"]
        self.assertEqual(4, len(failures))
        for slide in failures:
            with self.subTest(slide=slide.title):
                self.assertTrue(slide.callout, "each failure mode needs its teaching point")

    def test_curriculum_ask_is_the_closing_movement(self) -> None:
        titles = [s.title.lower() for s in deck.slides()]
        curriculum = next(i for i, t in enumerate(titles) if "curriculum" in t)
        self.assertGreater(curriculum / len(titles), 0.8)


class RenderingTests(unittest.TestCase):
    def test_markdown_is_marp_frontmatter(self) -> None:
        md = deck.build_markdown()
        self.assertTrue(md.startswith("---\nmarp: true"))

    def test_markdown_emits_one_heading_per_slide(self) -> None:
        md = deck.build_markdown()
        all_slides = deck.slides()
        title_slides = sum(1 for s in all_slides if s.kind == "title")
        self.assertEqual(title_slides, md.count("\n# "), "one h1 per title slide")
        self.assertEqual(
            len(all_slides) - title_slides, md.count("\n## "), "one h2 per content slide"
        )

    def test_html_is_balanced_and_self_contained(self) -> None:
        page = deck.build_html()
        self.assertEqual(len(deck.slides()), page.count("<section"))
        self.assertEqual(len(deck.slides()), page.count("</section>"))
        self.assertNotIn("<script src=", page, "deck must not depend on network assets")
        self.assertNotIn("<link rel=\"stylesheet\"", page)

    def test_html_escapes_slide_text(self) -> None:
        page = deck.build_html()
        self.assertNotIn("<script>alert", page)
        self.assertIn("<!DOCTYPE html>", page)

    def test_notes_are_hidden_by_default_for_projection(self) -> None:
        page = deck.build_html()
        self.assertIn('body class="hide-notes"', page)

    def test_outline_runs(self) -> None:
        self.assertEqual(0, deck.main(["--outline"]))


class CommittedDeckInSyncTests(unittest.TestCase):
    def test_committed_deck_matches_generator(self) -> None:
        for filename, expected in (
            ("teaching_deck.md", deck.build_markdown()),
            ("teaching_deck.html", deck.build_html()),
        ):
            path = REPO_ROOT / filename
            if not path.exists():
                self.skipTest(f"{filename} not generated yet")
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                expected,
                msg=f"{filename} is stale - re-run: python3 generate_teaching_deck.py",
            )


if __name__ == "__main__":
    unittest.main()
