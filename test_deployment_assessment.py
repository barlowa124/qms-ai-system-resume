"""Tests for the clinical deployment assessment instrument and scoring engine.

The scoring engine gates a patient-safety judgment, so the emphasis here is on
proving it CANNOT be coaxed into a clean result: omitted items, unknown ids,
malformed entries, and unjustified not-applicable claims must all fail closed.
"""

import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import deployment_assessment as da

REPO_ROOT = Path(__file__).resolve().parent
MODULE_PATH = REPO_ROOT / "deployment_assessment.py"


def all_conformant() -> dict:
    """A submission where every item is cleanly conformant."""
    submission = da.blank_response_template()
    for entry in submission["responses"].values():
        entry["response"] = "conformant"
        entry["note"] = "Evidence reviewed."
    return submission


class InstrumentIntegrityTests(unittest.TestCase):
    def test_item_ids_are_unique_and_well_formed(self) -> None:
        items = da.assessment_items()
        ids = [item.item_id for item in items]
        self.assertEqual(len(ids), len(set(ids)), "duplicate item ids")
        for item_id in ids:
            self.assertRegex(item_id, r"^DA-\d{2}$")

    def test_every_item_is_fully_specified(self) -> None:
        for item in da.assessment_items():
            with self.subTest(item=item.item_id):
                self.assertTrue(item.question.strip())
                self.assertTrue(item.inspect.strip())
                self.assertTrue(item.pass_criteria.strip())
                self.assertTrue(item.disqualifying_finding.strip())
                self.assertGreaterEqual(
                    len(item.evidence_required), 1,
                    "each item must name at least one concrete evidence artifact",
                )
                for evidence in item.evidence_required:
                    self.assertTrue(evidence.strip())

    def test_patient_safety_critical_items_exist_and_cover_core_risks(self) -> None:
        critical = da.patient_safety_critical_ids()
        self.assertGreaterEqual(len(critical), 5)

        domains = {
            item.domain
            for item in da.assessment_items()
            if item.severity is da.Severity.PATIENT_SAFETY_CRITICAL
        }
        # Oversight, integrity, traceability and change control are the
        # failure modes that most directly reach a patient.
        self.assertIn("Human Oversight in Practice", domains)
        self.assertIn("Data Integrity (ALCOA+)", domains)
        self.assertIn("Traceability and Investigation Readiness", domains)
        self.assertIn("Change Control", domains)

    def test_linked_gates_reference_the_design_gate_catalog(self) -> None:
        """Assessment items must tie back to real RG-xx gates."""
        import generate_qms_solution_pack as solution_pack

        known = {row[0] for row in solution_pack.release_gate_rows()}
        for item in da.assessment_items():
            for gate in item.linked_gates:
                with self.subTest(item=item.item_id, gate=gate):
                    self.assertIn(gate, known, f"{item.item_id} cites unknown gate {gate}")

    def test_only_genuinely_optional_items_allow_not_applicable(self) -> None:
        optional = {i.item_id for i in da.assessment_items() if i.allows_not_applicable}
        # Third-party models and in-silico evidence may legitimately not apply.
        self.assertSetEqual({"DA-13", "DA-15"}, optional)

    def test_disclaimer_disclaims_approval_authority(self) -> None:
        lowered = da.DISCLAIMER.lower()
        self.assertIn("not a compliance determination", lowered)
        self.assertIn("qualified", lowered)
        for artifact in (da.build_instrument_markdown(), da.build_instrument_html()):
            self.assertIn("not a compliance determination", artifact.lower())


class UnintentionalFailureCoverageTests(unittest.TestCase):
    """The realistic internal threat is a competent user getting a wrong answer
    with no signal that anything went wrong. Those paths must be covered and
    must block, since no adversary is required to reach them."""

    SILENT_FAILURE_ITEMS = ("DA-16", "DA-17", "DA-18")

    def test_silent_failure_modes_are_present(self) -> None:
        domains = {i.item_id: i.domain for i in da.assessment_items()}
        self.assertEqual("Use Outside the Validated Envelope", domains["DA-16"])
        self.assertEqual("Silent Truncation and Incomplete Input", domains["DA-17"])
        self.assertEqual("Configuration Drift", domains["DA-18"])
        self.assertEqual("Repeat Submission and Anchoring", domains["DA-19"])

    def test_silent_failure_items_are_blocking(self) -> None:
        critical = da.patient_safety_critical_ids()
        for item_id in self.SILENT_FAILURE_ITEMS:
            with self.subTest(item=item_id):
                self.assertIn(item_id, critical)

    def test_silent_failure_items_cannot_be_scoped_out(self) -> None:
        by_id = da.items_by_id()
        for item_id in self.SILENT_FAILURE_ITEMS + ("DA-19",):
            with self.subTest(item=item_id):
                self.assertFalse(
                    by_id[item_id].allows_not_applicable,
                    f"{item_id} applies to every deployment and must not be N/A-able",
                )

    def test_config_drift_is_distinct_from_model_change_control(self) -> None:
        """DA-08 governs the model; DA-18 governs the prompt and parameters,
        which are what people actually edit between releases."""
        by_id = da.items_by_id()
        self.assertNotEqual(by_id["DA-08"].domain, by_id["DA-18"].domain)
        self.assertIn("RG-05", by_id["DA-18"].linked_gates)

    def test_misuse_item_escalates_patient_impact_to_a_blocking_item(self) -> None:
        """Regression: DA-14 is major, so its disqualifying finding must not
        claim a patient-impacting critical defect terminates there. It routes
        to DA-11, which does block."""
        by_id = da.items_by_id()
        misuse = by_id["DA-14"]
        self.assertIs(da.Severity.MAJOR, misuse.severity)
        self.assertIn("DA-11", misuse.disqualifying_finding)
        self.assertIn("DA-11", da.patient_safety_critical_ids())


class FailClosedScoringTests(unittest.TestCase):
    """The engine must never produce a clean verdict without positive evidence."""

    def test_blank_template_is_blocking_and_counts_zero_assessed(self) -> None:
        result = da.score(da.blank_response_template())
        self.assertIs(da.Verdict.BLOCKING_FINDINGS, result.verdict)
        self.assertEqual(0, result.assessed_count, "not_assessed must not count as assessed")
        self.assertEqual(len(da.assessment_items()), len(result.findings))

    def test_empty_submission_is_invalid_not_clean(self) -> None:
        result = da.score({})
        self.assertIs(da.Verdict.INVALID_SUBMISSION, result.verdict)
        self.assertTrue(result.errors)

    def test_non_dict_submission_is_invalid(self) -> None:
        for bad in ([], "text", 42, None):
            with self.subTest(bad=bad):
                self.assertIs(da.Verdict.INVALID_SUBMISSION, da.score(bad).verdict)

    def test_omitted_item_is_treated_as_unassessed(self) -> None:
        submission = all_conformant()
        del submission["responses"]["DA-02"]

        result = da.score(submission)
        self.assertIs(da.Verdict.BLOCKING_FINDINGS, result.verdict)
        self.assertIn("DA-02", [f.item_id for f in result.blocking])

    def test_every_patient_safety_item_individually_blocks(self) -> None:
        """Each critical item alone must be sufficient to block."""
        for item_id in sorted(da.patient_safety_critical_ids()):
            with self.subTest(item=item_id):
                submission = all_conformant()
                submission["responses"][item_id]["response"] = "non_conformant"
                result = da.score(submission)
                self.assertIs(da.Verdict.BLOCKING_FINDINGS, result.verdict)
                self.assertIn(item_id, [f.item_id for f in result.blocking])

    def test_partial_conformance_still_produces_a_finding(self) -> None:
        submission = all_conformant()
        submission["responses"]["DA-04"]["response"] = "partial"
        result = da.score(submission)
        self.assertIs(da.Verdict.BLOCKING_FINDINGS, result.verdict)

    def test_major_only_findings_do_not_report_as_blocking(self) -> None:
        submission = all_conformant()
        submission["responses"]["DA-07"]["response"] = "non_conformant"
        result = da.score(submission)
        self.assertIs(da.Verdict.MAJOR_FINDINGS, result.verdict)
        self.assertEqual((), result.blocking)

    def test_unknown_item_id_invalidates_submission(self) -> None:
        submission = all_conformant()
        submission["responses"]["DA-99"] = {"response": "conformant"}
        result = da.score(submission)
        self.assertIs(da.Verdict.INVALID_SUBMISSION, result.verdict)
        self.assertTrue(any("DA-99" in e for e in result.errors))

    def test_invalid_response_value_invalidates_and_does_not_clear(self) -> None:
        submission = all_conformant()
        submission["responses"]["DA-01"]["response"] = "looks_fine_to_me"
        result = da.score(submission)
        self.assertIs(da.Verdict.INVALID_SUBMISSION, result.verdict)
        self.assertIn("DA-01", [f.item_id for f in result.findings])

    def test_malformed_entry_shape_does_not_clear_item(self) -> None:
        submission = all_conformant()
        submission["responses"]["DA-05"] = "conformant"  # string, not object
        result = da.score(submission)
        self.assertIs(da.Verdict.INVALID_SUBMISSION, result.verdict)
        self.assertIn("DA-05", [f.item_id for f in result.findings])

    def test_missing_response_field_does_not_clear_item(self) -> None:
        submission = all_conformant()
        submission["responses"]["DA-06"] = {"note": "we looked at it"}
        result = da.score(submission)
        self.assertIs(da.Verdict.INVALID_SUBMISSION, result.verdict)
        self.assertIn("DA-06", [f.item_id for f in result.findings])

    def test_response_value_is_case_and_whitespace_tolerant(self) -> None:
        submission = all_conformant()
        submission["responses"]["DA-01"]["response"] = "  CONFORMANT  "
        self.assertIs(
            da.Verdict.NO_BLOCKING_FINDINGS_IDENTIFIED, da.score(submission).verdict
        )


class NotApplicableRulesTests(unittest.TestCase):
    def test_not_applicable_rejected_where_not_permitted(self) -> None:
        submission = all_conformant()
        submission["responses"]["DA-02"]["response"] = "not_applicable"
        submission["responses"]["DA-02"]["note"] = "we do not think this matters"

        result = da.score(submission)
        self.assertIs(da.Verdict.INVALID_SUBMISSION, result.verdict)
        self.assertIn("DA-02", [f.item_id for f in result.findings])

    def test_not_applicable_requires_justification_even_where_permitted(self) -> None:
        submission = all_conformant()
        submission["responses"]["DA-13"]["response"] = "not_applicable"
        submission["responses"]["DA-13"]["note"] = "   "

        result = da.score(submission)
        self.assertIs(da.Verdict.INVALID_SUBMISSION, result.verdict)
        self.assertTrue(any("justification" in e for e in result.errors))

    def test_justified_not_applicable_is_accepted(self) -> None:
        submission = all_conformant()
        submission["responses"]["DA-13"]["response"] = "not_applicable"
        submission["responses"]["DA-13"]["note"] = "No third-party model; all inference in-house."

        result = da.score(submission)
        self.assertIs(da.Verdict.NO_BLOCKING_FINDINGS_IDENTIFIED, result.verdict)

    def test_placeholder_justification_does_not_scope_an_item_out(self) -> None:
        """Scoping out a patient-safety item must cost more than typing 'n/a'."""
        for placeholder in ("n/a", "N/A", "na", "none", "-", "tbd", "x", "N.A."):
            with self.subTest(placeholder=placeholder):
                submission = all_conformant()
                submission["responses"]["DA-13"]["response"] = "not_applicable"
                submission["responses"]["DA-13"]["note"] = placeholder

                result = da.score(submission)
                self.assertIs(da.Verdict.INVALID_SUBMISSION, result.verdict)
                self.assertIn("DA-13", [f.item_id for f in result.findings])

    def test_substantive_justification_helper_rejects_thin_text(self) -> None:
        self.assertFalse(da.is_substantive_justification(""))
        self.assertFalse(da.is_substantive_justification("   "))
        self.assertFalse(da.is_substantive_justification("no vendor"))
        self.assertTrue(
            da.is_substantive_justification(
                "No third-party model is used; all inference runs on in-house weights."
            )
        )


class CleanPathTests(unittest.TestCase):
    def test_fully_conformant_submission_reports_no_blocking_findings(self) -> None:
        result = da.score(all_conformant())
        self.assertIs(da.Verdict.NO_BLOCKING_FINDINGS_IDENTIFIED, result.verdict)
        self.assertEqual((), result.findings)
        self.assertEqual(result.total_count, result.assessed_count)

    def test_clean_verdict_still_carries_the_disclaimer(self) -> None:
        result = da.score(all_conformant())
        self.assertIn("not a compliance determination", da.format_report(result).lower())
        self.assertIn("disclaimer", result.to_dict())

    def test_result_serializes_to_json(self) -> None:
        payload = da.score(da.blank_response_template()).to_dict()
        encoded = json.dumps(payload)
        self.assertIn("BLOCKING_FINDINGS", encoded)


class ReportRenderingTests(unittest.TestCase):
    def test_report_lists_blocking_items_explicitly(self) -> None:
        submission = all_conformant()
        submission["responses"]["DA-04"]["response"] = "non_conformant"
        submission["responses"]["DA-04"]["note"] = "Admins can delete audit records."

        report = da.format_report(da.score(submission))
        self.assertIn("BLOCKING_FINDINGS", report)
        self.assertIn("DA-04", report)
        self.assertIn("Admins can delete audit records.", report)

    def test_instrument_markdown_contains_every_item(self) -> None:
        md = da.build_instrument_markdown()
        for item in da.assessment_items():
            self.assertIn(item.item_id, md)
            self.assertIn(item.pass_criteria, md)

    def test_instrument_html_escapes_and_contains_every_item(self) -> None:
        html = da.build_instrument_html()
        for item in da.assessment_items():
            self.assertIn(item.item_id, html)
        self.assertNotIn("<script>", html.lower())

    def test_write_instrument_creates_both_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "nested"
            md_path, html_path = da.write_instrument(target)
            self.assertTrue(md_path.exists())
            self.assertTrue(html_path.exists())
            self.assertEqual(md_path.read_text(encoding="utf-8"), da.build_instrument_markdown())


class CommittedInstrumentInSyncTests(unittest.TestCase):
    def test_committed_instrument_matches_generator(self) -> None:
        for filename, expected in (
            ("clinical_deployment_assessment.md", da.build_instrument_markdown()),
            ("clinical_deployment_assessment.html", da.build_instrument_html()),
        ):
            path = REPO_ROOT / filename
            if not path.exists():
                self.skipTest(f"{filename} not generated yet")
            self.assertEqual(
                path.read_text(encoding="utf-8"), expected,
                msg=f"{filename} is stale - re-run: python3 deployment_assessment.py instrument",
            )


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(MODULE_PATH), *args],
            capture_output=True, text=True, timeout=60,
        )

    def test_template_subcommand_emits_valid_json(self) -> None:
        proc = self.run_cli("template")
        self.assertEqual(0, proc.returncode, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(len(da.assessment_items()), len(payload["responses"]))

    def test_score_exits_nonzero_on_blocking_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "responses.json"
            path.write_text(json.dumps(da.blank_response_template()), encoding="utf-8")

            proc = self.run_cli("score", str(path))
            self.assertEqual(1, proc.returncode, "blocking findings must exit non-zero")
            self.assertIn("BLOCKING_FINDINGS", proc.stdout)

    def test_score_exits_zero_only_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "responses.json"
            path.write_text(json.dumps(all_conformant()), encoding="utf-8")

            proc = self.run_cli("score", str(path))
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertIn("NO_BLOCKING_FINDINGS_IDENTIFIED", proc.stdout)

    def test_score_json_flag_emits_machine_readable_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "responses.json"
            path.write_text(json.dumps(da.blank_response_template()), encoding="utf-8")

            proc = self.run_cli("score", str(path), "--json")
            payload = json.loads(proc.stdout)
            self.assertEqual("BLOCKING_FINDINGS", payload["verdict"])
            self.assertIn("disclaimer", payload)

    def test_score_handles_missing_file_and_bad_json(self) -> None:
        missing = self.run_cli("score", "/nonexistent/nope.json")
        self.assertEqual(2, missing.returncode)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{not json", encoding="utf-8")
            bad = self.run_cli("score", str(path))
            self.assertEqual(2, bad.returncode)
            self.assertIn("invalid JSON", bad.stderr)

    def test_instrument_subcommand_writes_to_outdir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            proc = self.run_cli("instrument", "--outdir", tmp)
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertTrue((Path(tmp) / "clinical_deployment_assessment.md").exists())
            self.assertTrue((Path(tmp) / "clinical_deployment_assessment.html").exists())

    def test_cli_requires_a_subcommand(self) -> None:
        self.assertNotEqual(0, self.run_cli().returncode)


class InProcessMainTests(unittest.TestCase):
    """Exercises main() directly so CLI branches are measured, not just spawned."""

    def test_main_instrument_writes_files_and_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code = da.main(["instrument", "--outdir", tmp])
            self.assertEqual(0, code)
            self.assertTrue((Path(tmp) / "clinical_deployment_assessment.md").exists())

    def test_main_template_to_file_and_to_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "nested" / "template.json"
            self.assertEqual(0, da.main(["template", "--out", str(out)]))
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(len(da.assessment_items()), len(payload["responses"]))

        self.assertEqual(0, da.main(["template"]))

    def test_main_score_returns_one_on_blocking_and_zero_on_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            blocking = Path(tmp) / "blocking.json"
            blocking.write_text(json.dumps(da.blank_response_template()), encoding="utf-8")
            self.assertEqual(1, da.main(["score", str(blocking)]))

            clean = Path(tmp) / "clean.json"
            clean.write_text(json.dumps(all_conformant()), encoding="utf-8")
            self.assertEqual(0, da.main(["score", str(clean)]))
            self.assertEqual(0, da.main(["score", str(clean), "--json"]))

    def test_main_score_returns_two_on_unreadable_input(self) -> None:
        self.assertEqual(2, da.main(["score", "/nonexistent/nope.json"]))

        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            self.assertEqual(2, da.main(["score", str(bad)]))


class MinorSeverityExtensionTests(unittest.TestCase):
    """The instrument documents a `minor` tier but ships no minor items.

    Sites are expected to append their own. These tests prove the tier behaves
    correctly when they do, so the documented extension point is not a lie.
    """

    def minor_item(self) -> da.AssessmentItem:
        return da.AssessmentItem(
            item_id="DA-90",
            domain="Site Extension",
            question="Is the dashboard branding current?",
            inspect="Dashboard header",
            evidence_required=("Screenshot",),
            pass_criteria="Branding matches current standard",
            disqualifying_finding="None; cosmetic only",
            severity=da.Severity.MINOR,
        )

    def test_minor_only_finding_yields_minor_verdict(self) -> None:
        extended = da.assessment_items() + [self.minor_item()]

        with unittest.mock.patch.object(da, "assessment_items", return_value=extended):
            submission = da.blank_response_template()
            for entry in submission["responses"].values():
                entry["response"] = "conformant"
            submission["responses"]["DA-90"]["response"] = "non_conformant"

            result = da.score(submission)
            self.assertIs(da.Verdict.MINOR_FINDINGS, result.verdict)
            self.assertEqual((), result.blocking)

    def test_severity_table_documents_every_defined_severity(self) -> None:
        md = da.build_instrument_markdown()
        for severity in da.Severity:
            self.assertIn(severity.value, md)


class ReportBranchTests(unittest.TestCase):
    """Covers each reporting branch of format_report."""

    def test_clean_report_states_no_findings(self) -> None:
        report = da.format_report(da.score(all_conformant()))
        self.assertIn("No findings recorded", report)

    def test_report_includes_error_section_for_invalid_submission(self) -> None:
        submission = all_conformant()
        submission["responses"]["DA-77"] = {"response": "conformant"}
        report = da.format_report(da.score(submission))
        self.assertIn("SUBMISSION ERRORS", report)
        self.assertIn("DA-77", report)

    def test_report_separates_major_from_blocking(self) -> None:
        submission = all_conformant()
        submission["responses"]["DA-07"]["response"] = "non_conformant"
        report = da.format_report(da.score(submission))
        self.assertIn("OTHER FINDINGS", report)
        self.assertNotIn("BLOCKING - PATIENT SAFETY CRITICAL", report)


if __name__ == "__main__":
    unittest.main()
