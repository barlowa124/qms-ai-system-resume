"""Robustness battery: fail-closed scoring boundaries — every loophole
for converting "no evidence" into "pass" must stay closed."""

import pytest

from deployment_assessment import (MIN_JUSTIFICATION_CHARS, Response,
                                   Severity, Verdict, assessment_items,
                                   blank_response_template,
                                   is_substantive_justification,
                                   items_by_id, patient_safety_critical_ids,
                                   score)


def _all(response="conformant", note="reviewed", **over):
    sub = blank_response_template()
    for v in sub["responses"].values():
        v["response"] = response
        v["note"] = note
    for item_id, patch in over.items():
        sub["responses"][item_id.replace("_", "-")].update(patch)
    return sub


class TestJustificationGate:
    @pytest.mark.parametrize("ph", ["-", "--", ".", "n/a", "n.a.", "na",
                                    "nil", "no", "none", "not applicable",
                                    "ok", "tbd", "todo", "x", "yes",
                                    "N/A", "TBD."])
    def test_placeholders_rejected(self, ph):
        assert not is_substantive_justification(ph)

    def test_length_boundary(self):
        assert not is_substantive_justification("x" * (MIN_JUSTIFICATION_CHARS - 1))
        assert is_substantive_justification("x" * MIN_JUSTIFICATION_CHARS)

    def test_whitespace_and_empty(self):
        assert not is_substantive_justification("")
        assert not is_substantive_justification("   " * 30)


class TestScoringBoundaries:
    def test_blank_template_is_blocking(self):
        # an untouched submission can never pass — fail-closed by default
        r = score(blank_response_template())
        assert r.verdict == Verdict.BLOCKING_FINDINGS
        assert r.assessed_count == 0
        assert len(r.blocking) == len(patient_safety_critical_ids())

    def test_all_conformant_no_findings(self):
        r = score(_all())
        assert r.verdict == Verdict.NO_BLOCKING_FINDINGS_IDENTIFIED
        assert r.assessed_count == r.total_count
        assert not r.findings

    def test_missing_item_treated_as_unassessed(self):
        sub = _all()
        del sub["responses"]["DA-01"]
        r = score(sub)
        assert r.verdict == Verdict.BLOCKING_FINDINGS
        assert any(f.item_id == "DA-01" for f in r.findings)

    def test_invalid_response_string_invalidates(self):
        sub = _all(DA_01={"response": "looks_fine"})
        r = score(sub)
        assert r.verdict == Verdict.INVALID_SUBMISSION
        assert r.errors

    def test_unknown_item_id_invalidates(self):
        sub = _all()
        sub["responses"]["DA-99"] = {"response": "conformant", "note": "x"}
        r = score(sub)
        assert r.verdict == Verdict.INVALID_SUBMISSION

    def test_non_dict_submission(self):
        for bad in [[], "text", 42, None]:
            assert score(bad).verdict == Verdict.INVALID_SUBMISSION

    def test_response_case_and_whitespace_tolerance(self):
        sub = _all(DA_01={"response": "  CONFORMANT  "})
        r = score(sub)
        assert r.verdict == Verdict.NO_BLOCKING_FINDINGS_IDENTIFIED


class TestNotApplicableGate:
    NA_ITEM = "DA-13"  # allows_not_applicable
    DISALLOWED = "DA-01"  # patient_safety_critical, no NA allowed

    def test_na_without_permission_is_error(self):
        sub = _all(**{self.DISALLOWED: {
            "response": "not_applicable",
            "note": "this is a long and substantive justification of scope"}})
        r = score(sub)
        assert r.verdict == Verdict.INVALID_SUBMISSION
        assert any("not permitted" in e for e in r.errors)

    def test_na_short_justification_rejected(self):
        sub = _all(**{self.NA_ITEM: {
            "response": "not_applicable", "note": "n/a"}})
        r = score(sub)
        assert r.verdict == Verdict.INVALID_SUBMISSION
        assert any("substantive" in e for e in r.errors)

    def test_na_substantive_clears(self):
        sub = _all(**{self.NA_ITEM: {
            "response": "not_applicable",
            "note": "no imaging component exists in this deployment"}})
        r = score(sub)
        assert r.verdict == Verdict.NO_BLOCKING_FINDINGS_IDENTIFIED


class TestVerdictOrdering:
    def test_major_only_findings(self):
        # every critical conformant, every major non-conformant
        critical = patient_safety_critical_ids()
        sub = _all()
        for iid in items_by_id():
            if iid not in critical:
                sub["responses"][iid]["response"] = "non_conformant"
        r = score(sub)
        assert r.verdict == Verdict.MAJOR_FINDINGS
        assert r.blocking == ()

    def test_single_critical_finding_blocks(self):
        critical = sorted(patient_safety_critical_ids())
        sub = _all(**{critical[0]: {"response": "non_conformant"}})
        r = score(sub)
        assert r.verdict == Verdict.BLOCKING_FINDINGS

    def test_partial_is_a_finding_not_a_pass(self):
        sub = _all(**{"DA-01": {"response": "partial"}})
        r = score(sub)
        assert r.verdict == Verdict.BLOCKING_FINDINGS
        assert any(f.response is Response.PARTIAL for f in r.findings)

    def test_not_assessed_does_not_inflate_count(self):
        sub = _all(**{"DA-01": {"response": "not_assessed"}})
        r = score(sub)
        assert r.assessed_count == r.total_count - 1

    def test_disclaimer_always_attached(self):
        for sub in (blank_response_template(), _all()):
            assert "not a compliance determination" in \
                score(sub).to_dict()["disclaimer"]
