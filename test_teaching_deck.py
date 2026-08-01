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
