import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import generate_qms_solution_pack as solution_pack
import generate_qms_system_diagram as system_diagram
import generate_qms_trust_hardened_diagram as trust_pack

REPO_ROOT = Path(__file__).resolve().parent


def extract_gate_ids(text: str) -> set[str]:
    return set(re.findall(r"RG-\d+", text))


# Wording that must never appear as an *allowance* in the governance artifacts.
FORBIDDEN_AUTONOMY_PATTERNS = (
    r"autonomous(?:ly)?\s+clos",
    # Deliberately broad: any automatic-closure claim in these artifacts must
    # be negated. Requiring an adjacent risk qualifier missed real phrasings
    # such as "automatically closed for patient complaints".
    r"auto(?:matically)?\s+clos",
    r"without\s+human\s+review",
    r"no\s+reviewer\s+required",
    r"bypass\w*\s+(?:human|reviewer|safety)",
)

# Such wording is acceptable only when explicitly negated or prohibited.
NEGATION_PATTERN = r"\bno\b|\bnever\b|\bnot\b|prohibit|prevent|block"


def find_permissive_autonomy_violations(text: str) -> list[str]:
    """Return context windows where autonomy wording appears WITHOUT negation.

    An empty list means the text never authorizes autonomous handling of
    patient-impacting records. Exposed at module level so the guard itself
    can be unit-tested against known-bad input (see AutonomyGuardSelfTests).

    The negation search deliberately EXCLUDES the matched span. Otherwise a
    phrase like "no reviewer required" would suppress its own detection,
    because the "no" that forms part of the violation would be read as a
    negation of it.

    Heuristic limitation: a negation word appearing nearby but semantically
    unrelated can still mask a violation. This is a lint, not a parser.
    """
    violations: list[str] = []
    lowered = text.lower()
    for pattern in FORBIDDEN_AUTONOMY_PATTERNS:
        for match in re.finditer(pattern, lowered):
            before = lowered[max(0, match.start() - 90):match.start()]
            after = lowered[match.end():match.end() + 40]
            if not re.search(NEGATION_PATTERN, f"{before} {after}"):
                violations.append(f"{before}[[{match.group(0)}]]{after}".strip())
    return violations


class QmsGeneratorComprehensiveTests(unittest.TestCase):
    def section(self, text: str, start_marker: str, end_marker: str) -> str:
        start = text.index(start_marker)
        end = text.index(end_marker, start)
        return text[start:end]

    def split_gate_field(self, gate_field: str) -> set[str]:
        return {piece.strip() for piece in gate_field.split(",") if piece.strip()}

    def assert_gate_partition_integrity(self, module) -> None:
        release_rows = module.release_gate_rows()
        release_ids = {row[0] for row in release_rows}
        p0_ids = set(module.p0_launch_gate_ids())
        p1_ids = {row[0] for row in module.p1_post_launch_gate_rows()}

        self.assertEqual(len(release_rows), 9)
        self.assertEqual(len(release_ids), 9)
        self.assertSetEqual(release_ids, p0_ids | p1_ids)
        self.assertSetEqual(set(), p0_ids & p1_ids)

        windows = module.p1_post_launch_windows()
        self.assertSetEqual(set(windows.keys()), p1_ids)
        for window_text in windows.values():
            self.assertIn("Enable within", window_text)

    def test_release_gate_partitions_are_complete_and_disjoint(self) -> None:
        self.assert_gate_partition_integrity(solution_pack)
        self.assert_gate_partition_integrity(trust_pack)

    def test_solution_gate_table_text_matches_partition_rules(self) -> None:
        p0_ids = set(solution_pack.p0_launch_gate_ids())
        p1_ids = {row[0] for row in solution_pack.p1_post_launch_gate_rows()}

        catalog = solution_pack.build_release_gate_checklist_markdown()
        p0_table = solution_pack.build_p0_launch_gate_markdown()
        p1_table = solution_pack.build_p1_post_launch_gate_markdown()

        for gate_id in p0_ids:
            self.assertIn(f"| {gate_id} |", p0_table)
            self.assertIn(f"| {gate_id} | P0 Launch Blocker |", catalog)

        for gate_id in p1_ids:
            self.assertIn(f"| {gate_id} |", p1_table)
            self.assertIn(f"| {gate_id} | P1 Post-Launch |", catalog)

        self.assertIn("Do not block initial launch;", catalog)
        self.assertIn("block next release if unresolved", catalog)

    def test_solution_applied_mapping_covers_all_release_gates(self) -> None:
        release_ids = {row[0] for row in solution_pack.release_gate_rows()}
        covered_ids: set[str] = set()

        for _, gates, _, tier, _ in solution_pack.applied_release_gate_rows():
            parsed = self.split_gate_field(gates)
            covered_ids.update(parsed)

            if tier == "P0 Launch Blocker":
                self.assertTrue(parsed.issubset(solution_pack.p0_launch_gate_ids()))
            elif tier == "P1 Post-Launch":
                p1_ids = {row[0] for row in solution_pack.p1_post_launch_gate_rows()}
                self.assertTrue(parsed.issubset(p1_ids))
            else:
                self.fail(f"Unexpected launch tier: {tier}")

        self.assertSetEqual(release_ids, covered_ids)

    def test_trust_applied_mapping_covers_all_release_gates(self) -> None:
        release_ids = {row[0] for row in trust_pack.release_gate_rows()}
        applied_text = trust_pack.build_applied_release_gate_markdown()
        covered_ids = extract_gate_ids(applied_text)

        self.assertSetEqual(release_ids, covered_ids)
        self.assertIn("| Launch Tier |", applied_text)
        self.assertIn("| P0 Launch Blocker |", applied_text)
        self.assertIn("| P1 Post-Launch |", applied_text)

    def test_solution_metric_and_compliance_models_have_expected_coverage(self) -> None:
        metric_rows = solution_pack.metric_rows()
        compliance_rows = solution_pack.compliance_assessment_rows()
        hardening_rows = solution_pack.ai_hardening_rows()
        regulator_rows = solution_pack.regulator_answer_rows()

        self.assertGreaterEqual(len(metric_rows), 12)
        self.assertEqual(len(compliance_rows), 6)
        self.assertEqual(len(hardening_rows), 7)
        self.assertEqual(len(regulator_rows), 7)

        domains = {row[0] for row in metric_rows}
        self.assertSetEqual(
            domains,
            {"Patient Safety", "Usage", "ESG", "Verifiability", "Compliance"},
        )

    def test_solution_mermaid_contains_expected_control_flows(self) -> None:
        mermaid = solution_pack.build_system_mermaid()
        for snippet in (
            "flowchart LR",
            "P_EQM --> P_AI",
            "P_AI -->|recommended controls| P_EQM",
            "P_DSH -->|closed-loop actions| P_ORC",
            "C_SRC -. API/event integration .-> P_INT",
        ):
            self.assertIn(snippet, mermaid)

    def test_trust_mermaid_contains_security_and_digital_twin_paths(self) -> None:
        mermaid = trust_pack.build_mermaid()
        for snippet in (
            "flowchart LR",
            'T_DTWIN["Digital twin and drug virtualization validation"]',
            "T_AIGOV --> T_LOGS",
            "T_GATES --> E_PIPE",
            "T_DTWIN --> E_TWIN",
            "T_PROOF --> E_MATH",
        ):
            self.assertIn(snippet, mermaid)

    def test_solution_output_files_and_sections_are_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mmd_path, md_path, html_path = solution_pack.write_outputs(Path(tmp_dir))
            self.assertTrue(mmd_path.exists())
            self.assertTrue(md_path.exists())
            self.assertTrue(html_path.exists())

            mmd_text = mmd_path.read_text(encoding="utf-8")
            md_text = md_path.read_text(encoding="utf-8")
            html_text = html_path.read_text(encoding="utf-8")

            self.assertEqual(mmd_text, solution_pack.build_system_mermaid())

            for heading in (
                "## Verifiability and Compliance Assessments",
                "## AI Regulator Stress-Test Hardening",
                "## Anticipated AI-Assisted Regulatory Challenges and Prepared Answers",
                "## Strict P0 Launch Release Gates (QMS Resume Reviewer)",
                "## P1 Post-Launch Enforcement Gates (Marked)",
                "## Full Regulatory Gate Catalog (Tiered Reference)",
                "## Applied Regulatory Gate Implementation for QMS Resume Reviewer",
            ):
                self.assertIn(heading, md_text)

            for html_marker in (
                "QMS Digital Process Proposal",
                "Strict P0 Launch Release Gates (QMS Resume Reviewer)",
                "P1 Post-Launch Enforcement Gates (Marked)",
                "Full Regulatory Gate Catalog (Tiered Reference)",
                "Applied Regulatory Gate Implementation",
                "mermaid.initialize",
            ):
                self.assertIn(html_marker, html_text)

    def test_trust_output_files_and_sections_are_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mmd_path, md_path, html_path = trust_pack.write_outputs(Path(tmp_dir))
            self.assertTrue(mmd_path.exists())
            self.assertTrue(md_path.exists())
            self.assertTrue(html_path.exists())

            mmd_text = mmd_path.read_text(encoding="utf-8")
            md_text = md_path.read_text(encoding="utf-8")
            html_text = html_path.read_text(encoding="utf-8")
            md_text_lower = md_text.lower()

            self.assertEqual(mmd_text, trust_pack.build_mermaid())
            self.assertIn("## Digital Twin and Drug Virtualization Focus", md_text)
            self.assertIn("verification evidence that simulation behavior is stable", md_text_lower)
            self.assertIn("adversarial or misuse scenarios", md_text_lower)
            self.assertIn("Strict P0 Launch Release Gates (QMS Resume Reviewer)", md_text)
            self.assertIn("P1 Post-Launch Enforcement Gates (Marked)", md_text)

            self.assertIn("QMS AI System Interview Walkthrough", html_text)
            self.assertIn("Digital twin and drug virtualization validation", html_text)
            self.assertIn("<pre class=\"mermaid\">", html_text)

    def test_cross_generator_gate_models_are_consistent(self) -> None:
        solution_gate_rows = solution_pack.release_gate_rows()
        trust_gate_rows = trust_pack.release_gate_rows()
        self.assertEqual(solution_gate_rows, trust_gate_rows)
        self.assertSetEqual(solution_pack.p0_launch_gate_ids(), trust_pack.p0_launch_gate_ids())
        self.assertDictEqual(solution_pack.p1_post_launch_windows(), trust_pack.p1_post_launch_windows())

    def test_solution_and_trust_markdown_gate_sections_match_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            _, solution_md_path, _ = solution_pack.write_outputs(Path(tmp_dir))
            _, trust_md_path, _ = trust_pack.write_outputs(Path(tmp_dir))

            solution_markdown = solution_md_path.read_text(encoding="utf-8")
            trust_markdown = trust_md_path.read_text(encoding="utf-8")

            for markdown in (solution_markdown, trust_markdown):
                p0_section = self.section(
                    markdown,
                    "## Strict P0 Launch Release Gates (QMS Resume Reviewer)",
                    "## P1 Post-Launch Enforcement Gates (Marked)",
                )
                p1_section = self.section(
                    markdown,
                    "## P1 Post-Launch Enforcement Gates (Marked)",
                    "## Full Regulatory Gate Catalog (Tiered Reference)",
                )

                for gate_id in ("RG-02", "RG-03", "RG-04", "RG-05", "RG-08"):
                    self.assertIn(f"| {gate_id} |", p0_section)
                    self.assertNotIn(f"| {gate_id} |", p1_section)

                for gate_id in ("RG-01", "RG-06", "RG-07", "RG-09"):
                    self.assertIn(f"| {gate_id} |", p1_section)
                    self.assertNotIn(f"| {gate_id} |", p0_section)


class NarrativeToHtmlTests(unittest.TestCase):
    def test_paragraphs_and_inline_markup(self) -> None:
        html = solution_pack.narrative_to_html(
            "First **bold** para.\n\nSecond *italic* para."
        )
        self.assertIn("<p>First <strong>bold</strong> para.</p>", html)
        self.assertIn("<p>Second <em>italic</em> para.</p>", html)

    def test_unordered_and_ordered_lists(self) -> None:
        ul = solution_pack.narrative_to_html("- alpha\n- beta")
        self.assertIn("<ul><li>alpha</li><li>beta</li></ul>", ul)

        ol = solution_pack.narrative_to_html("1. first\n2. second")
        self.assertIn("<ol><li>first</li><li>second</li></ol>", ol)

    def test_wrapped_list_continuation_joins_same_item(self) -> None:
        html = solution_pack.narrative_to_html("- item start\n  continued text")
        self.assertIn("<li>item start continued text</li>", html)
        self.assertEqual(html.count("<li>"), 1)

    def test_heading_and_html_escaping(self) -> None:
        html = solution_pack.narrative_to_html("### My <Heading>")
        self.assertIn("<h3>My &lt;Heading&gt;</h3>", html)


class CompatibilityAndVirtualizationSectionTests(unittest.TestCase):
    def test_compatibility_and_virtualization_row_models(self) -> None:
        self.assertEqual(len(solution_pack.compatibility_metric_rows()), 4)
        self.assertEqual(len(solution_pack.organ_virtualization_rows()), 5)

        for row in solution_pack.compatibility_metric_rows():
            self.assertEqual(len(row), 3)
        for row in solution_pack.organ_virtualization_rows():
            self.assertEqual(len(row), 3)

    def test_rg09_present_in_gate_model_as_p1(self) -> None:
        release_ids = {row[0] for row in solution_pack.release_gate_rows()}
        self.assertIn("RG-09", release_ids)
        self.assertNotIn("RG-09", solution_pack.p0_launch_gate_ids())
        self.assertIn("RG-09", solution_pack.p1_post_launch_windows())

    def test_new_sections_render_in_markdown_and_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            _, md_path, html_path = solution_pack.write_outputs(Path(tmp_dir))
            md_text = md_path.read_text(encoding="utf-8")
            html_text = html_path.read_text(encoding="utf-8")

            for heading in (
                "## Human-AI Compatibility as a Release Criterion (RG-09)",
                "### RG-09 Measurement Definition",
                "### RG-09 Enforcement Pattern",
                "## Extension: Quality Governance for Organ Virtualization / In-Silico Model Programs",
                "### ESG Amplification from Virtualization",
            ):
                self.assertIn(heading, md_text)

            # citation must survive generation
            self.assertIn("arXiv:1906.01148", md_text)
            self.assertIn("Bansal", md_text)
            self.assertIn("arXiv:1906.01148", html_text)

            for html_marker in (
                "Human-AI Compatibility as a Release Criterion (RG-09)",
                "RG-09 Measurement Definition",
                "Extension: Quality Governance for Organ Virtualization",
                "ESG Amplification from Virtualization",
            ):
                self.assertIn(html_marker, html_text)

    def test_compatibility_metric_appears_in_kpi_table(self) -> None:
        table = solution_pack.build_metric_framework_markdown()
        self.assertIn("Backward compatibility of model updates", table)


class SystemDiagramRenderingTests(unittest.TestCase):
    """Covers generate_qms_system_diagram, which had no test coverage."""

    def test_normalize_label_escapes_mermaid_breaking_characters(self) -> None:
        self.assertEqual(system_diagram.normalize_label("a\nb"), "a<br/>b")
        self.assertEqual(system_diagram.normalize_label('say "hi"'), "say 'hi'")
        self.assertEqual(system_diagram.normalize_label("a|b"), "a/b")
        self.assertEqual(
            system_diagram.normalize_label('Line\nwith "quote" and |pipe|'),
            "Line<br/>with 'quote' and /pipe/",
        )

    def test_render_node_quotes_and_normalizes_label(self) -> None:
        node = system_diagram.Node("N1", 'Title\nSub "x"', "current")
        self.assertEqual(system_diagram.render_node(node), '    N1["Title<br/>Sub \'x\'"]')

    def test_render_edge_covers_all_four_branches(self) -> None:
        solid_labeled = system_diagram.Edge("A", "B", "does thing")
        solid_plain = system_diagram.Edge("A", "B")
        dashed_labeled = system_diagram.Edge("A", "B", "migrates", "dashed")
        dashed_plain = system_diagram.Edge("A", "B", "", "dashed")

        self.assertEqual(system_diagram.render_edge(solid_labeled), "A -->|does thing| B")
        self.assertEqual(system_diagram.render_edge(solid_plain), "A --> B")
        self.assertEqual(system_diagram.render_edge(dashed_labeled), "A -. migrates .-> B")
        self.assertEqual(system_diagram.render_edge(dashed_plain), "A -.-> B")

    def test_render_edge_normalizes_label_characters(self) -> None:
        edge = system_diagram.Edge("A", "B", "a|b")
        self.assertEqual(system_diagram.render_edge(edge), "A -->|a/b| B")

    def test_build_mermaid_structure_and_class_assignments(self) -> None:
        mermaid = system_diagram.build_mermaid()

        self.assertTrue(mermaid.startswith("flowchart LR"))
        self.assertTrue(mermaid.endswith("\n"))
        self.assertIn('subgraph CURRENT["Current QMS Structure (As-Is)"]', mermaid)
        self.assertIn('subgraph TARGET["Proposed Digital QMS (To-Be)"]', mermaid)
        self.assertIn("%% Migration mapping from current to proposed", mermaid)

        for css_class in ("current", "proposed", "platform", "governance", "ai"):
            self.assertIn(f"classDef {css_class} ", mermaid)

        # every declared node must receive a class assignment
        declared = set(re.findall(r"^\s{4}([A-Z_0-9]+)\[", mermaid, re.MULTILINE))
        assigned = set(re.findall(r"^\s+class ([A-Z_0-9]+) ", mermaid, re.MULTILINE))
        self.assertTrue(declared)
        self.assertSetEqual(declared, assigned)

    def test_build_mermaid_has_no_unrendered_newlines_in_labels(self) -> None:
        mermaid = system_diagram.build_mermaid()
        for line in mermaid.splitlines():
            if "[" in line and '"' in line:
                # raw newlines inside labels would have broken the line apart
                self.assertNotIn('\\n', line)

    def test_build_markdown_embeds_mermaid_in_fenced_block(self) -> None:
        mermaid = system_diagram.build_mermaid()
        md = system_diagram.build_markdown(mermaid)

        self.assertIn("# QMS System Diagram: Current vs Proposed Digital Process", md)
        self.assertIn("```mermaid\n", md)
        self.assertIn(mermaid, md)
        self.assertIn("## Suggested Rollout Sequence", md)
        self.assertIn("## QMS Value Outcomes", md)

    def test_write_outputs_creates_both_files_matching_builders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            mmd_path, md_path = system_diagram.write_outputs(Path(tmp_dir))

            self.assertTrue(mmd_path.exists())
            self.assertTrue(md_path.exists())
            self.assertEqual(mmd_path.name, "qms_system_diagram.mmd")
            self.assertEqual(md_path.name, "qms_system_diagram.md")

            expected_mermaid = system_diagram.build_mermaid()
            self.assertEqual(mmd_path.read_text(encoding="utf-8"), expected_mermaid)
            self.assertEqual(
                md_path.read_text(encoding="utf-8"),
                system_diagram.build_markdown(expected_mermaid),
            )

    def test_parse_args_defaults_to_script_dir_and_accepts_outdir(self) -> None:
        with mock.patch.object(sys, "argv", ["prog"]):
            self.assertEqual(system_diagram.parse_args().outdir, REPO_ROOT)

        with mock.patch.object(sys, "argv", ["prog", "--outdir", "/tmp/example"]):
            self.assertEqual(system_diagram.parse_args().outdir, Path("/tmp/example"))

    def test_write_outputs_creates_missing_nested_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            nested = Path(tmp_dir) / "a" / "b" / "c"
            self.assertFalse(nested.exists())
            mmd_path, md_path = system_diagram.write_outputs(nested)
            self.assertTrue(mmd_path.exists())
            self.assertTrue(md_path.exists())


class CommittedArtifactsInSyncTests(unittest.TestCase):
    """Guards against committed artifacts drifting from generator output.

    This is the failure mode where someone hand-edits a generated file, or
    changes a generator without regenerating, leaving the repo inconsistent.
    """

    def assert_committed_matches(self, filename: str, expected: str) -> None:
        path = REPO_ROOT / filename
        if not path.exists():
            self.skipTest(f"{filename} not present in repo")
        self.assertEqual(
            path.read_text(encoding="utf-8"),
            expected,
            msg=f"{filename} is stale - re-run its generator to regenerate it",
        )

    def test_system_diagram_artifacts_in_sync(self) -> None:
        mermaid = system_diagram.build_mermaid()
        self.assert_committed_matches("qms_system_diagram.mmd", mermaid)
        self.assert_committed_matches(
            "qms_system_diagram.md", system_diagram.build_markdown(mermaid)
        )

    def test_solution_pack_artifacts_in_sync(self) -> None:
        mermaid = solution_pack.build_system_mermaid()
        self.assert_committed_matches("qms_solution_diagram.mmd", mermaid)
        self.assert_committed_matches(
            "qms_solution_proposal.md", solution_pack.build_markdown(mermaid)
        )
        self.assert_committed_matches(
            "qms_solution_proposal.html", solution_pack.build_html(mermaid)
        )

    def test_trust_hardened_artifacts_in_sync(self) -> None:
        mermaid = trust_pack.build_mermaid()
        self.assert_committed_matches("qms_trust_hardened_system_diagram.mmd", mermaid)
        self.assert_committed_matches(
            "qms_trust_hardened_system_diagram.md", trust_pack.build_markdown(mermaid)
        )


class PatientSafetyInvariantTests(unittest.TestCase):
    """Enforces patient-safety invariants of the governance model as policy-as-code.

    These do not test a running clinical system. They assert that the governance
    artifacts cannot silently lose the safety properties they claim - e.g. that
    human oversight is never dropped, that safety gates stay fail-closed, and
    that no wording ever authorizes autonomous AI closure of patient-impacting
    records.
    """

    def test_patient_safety_domain_exists_with_hard_targets(self) -> None:
        rows = [row for row in solution_pack.metric_rows() if row[0] == "Patient Safety"]
        self.assertGreaterEqual(len(rows), 2, "Patient Safety metrics must not be removed")

        for _, metric, formula, source, cadence, target, safety_link in rows:
            # patient-safety metrics require a concrete numeric threshold,
            # not a "track the trend" soft target
            self.assertRegex(
                target,
                r">=\s*\d+(\.\d+)?%|<\s*\d+(\.\d+)?%",
                msg=f"Patient Safety metric '{metric}' must carry a numeric threshold",
            )
            self.assertTrue(formula.strip(), f"{metric} missing formula")
            self.assertTrue(source.strip(), f"{metric} missing data source")
            self.assertTrue(cadence.strip(), f"{metric} missing cadence")
            self.assertTrue(safety_link.strip(), f"{metric} missing patient safety link")

    def test_every_metric_declares_a_patient_safety_linkage(self) -> None:
        """No metric may exist without stating how it connects to patient safety."""
        for row in solution_pack.metric_rows():
            metric, safety_link = row[1], row[6]
            self.assertTrue(
                safety_link and safety_link.strip(),
                msg=f"Metric '{metric}' has no patient safety linkage",
            )
            self.assertGreater(
                len(safety_link.split()), 3,
                msg=f"Metric '{metric}' has a non-substantive safety linkage: {safety_link!r}",
            )

    def test_human_oversight_control_is_present_and_escalates(self) -> None:
        rows = {row[0]: row for row in solution_pack.compliance_assessment_rows()}
        self.assertIn(
            "Human oversight enforcement", rows,
            msg="Human oversight enforcement control must not be removed",
        )

        _, method, evidence, cadence, gate = rows["Human oversight enforcement"]
        self.assertIn("no autonomous closure", method.lower())
        self.assertIn("patient-safety", method.lower())
        self.assertEqual("Continuous", cadence, "Human oversight must be continuously enforced")
        self.assertRegex(
            gate.lower(), r"escalat|block|reject|freeze",
            msg="Human oversight violations must trigger an enforcement action",
        )
        self.assertTrue(evidence.strip())

    def test_all_compliance_controls_have_enforcement_actions(self) -> None:
        """A control with no enforcement action is documentation, not a control."""
        for area, method, evidence, cadence, gate in solution_pack.compliance_assessment_rows():
            self.assertTrue(gate.strip(), f"Control '{area}' has no enforcement gate")
            self.assertRegex(
                gate.lower(),
                r"block|reject|freeze|escalat|incident",
                msg=f"Control '{area}' enforcement is not actionable: {gate!r}",
            )
            self.assertTrue(method.strip(), f"Control '{area}' has no verification method")
            self.assertTrue(evidence.strip(), f"Control '{area}' has no evidence requirement")

    def test_p0_gates_are_all_fail_closed(self) -> None:
        """Every launch-blocking gate must describe a blocking action."""
        p0_ids = solution_pack.p0_launch_gate_ids()
        rows = {row[0]: row for row in solution_pack.release_gate_rows()}

        for gate_id in sorted(p0_ids):
            _, name, evidence, enforcement, fail_action = rows[gate_id]
            self.assertRegex(
                fail_action.lower(),
                r"block|prevent|reject|freeze|escalat",
                msg=f"P0 gate {gate_id} ({name}) is not fail-closed: {fail_action!r}",
            )
            self.assertTrue(evidence.strip(), f"{gate_id} has no required evidence")
            self.assertTrue(enforcement.strip(), f"{gate_id} has no enforcement point")

    def test_human_review_gate_is_a_p0_launch_blocker(self) -> None:
        """RG-04 (human review) must never be deferred to post-launch."""
        self.assertIn("RG-04", solution_pack.p0_launch_gate_ids())
        self.assertNotIn("RG-04", solution_pack.p1_post_launch_windows())

        rg04 = next(r for r in solution_pack.release_gate_rows() if r[0] == "RG-04")
        self.assertIn("human review", rg04[1].lower())
        self.assertRegex(rg04[4].lower(), r"prevent|block")

    def test_lineage_gate_is_a_p0_launch_blocker(self) -> None:
        """RG-08 (immutable lineage) underpins safety investigations."""
        self.assertIn("RG-08", solution_pack.p0_launch_gate_ids())
        rg08 = next(r for r in solution_pack.release_gate_rows() if r[0] == "RG-08")
        self.assertRegex(rg08[2].lower(), r"tamper-evident|immutable")

    def test_no_artifact_authorizes_autonomous_patient_impacting_closure(self) -> None:
        """Negative test: forbidden autonomy wording must not appear as an allowance."""
        mermaid = solution_pack.build_system_mermaid()
        corpus = {
            "solution markdown": solution_pack.build_markdown(mermaid),
            "solution html": solution_pack.build_html(mermaid),
            "trust markdown": trust_pack.build_markdown(trust_pack.build_mermaid()),
        }

        for label, text in corpus.items():
            self.assertGreater(len(text), 1000, f"{label} corpus unexpectedly small")
            violations = find_permissive_autonomy_violations(text)
            self.assertEqual(
                [], violations,
                msg=f"{label} contains permissive autonomy wording: {violations}",
            )

    def test_patient_safety_guardrails_section_states_core_guarantees(self) -> None:
        md = solution_pack.build_markdown(solution_pack.build_system_mermaid())
        section_start = md.index("## Patient Safety Guardrails")
        section = md[section_start:md.index("## Notes", section_start)]
        lowered = section.lower()

        self.assertIn("decision support", lowered)
        self.assertIn("never autonomous closure", lowered)
        self.assertIn("human review", lowered)
        self.assertRegex(lowered, r"release hold|escalation")
        self.assertRegex(lowered, r"lineage|inspection")

    def test_high_risk_ai_surfaces_require_human_review_gate(self) -> None:
        """Any applied surface touching high-risk AI output must invoke RG-04."""
        matched = 0
        for surface, gates, pattern, tier, burden in solution_pack.applied_release_gate_rows():
            haystack = f"{surface} {pattern}".lower()
            if "high-risk" in haystack and "recommendation" in haystack:
                matched += 1
                self.assertIn(
                    "RG-04", gates,
                    msg=f"Surface '{surface}' handles high-risk AI output but omits RG-04",
                )

        # Anti-vacuity: if the predicate stops matching, this test would pass
        # while checking nothing. Fail loudly instead.
        self.assertGreater(
            matched, 0,
            msg="No high-risk AI recommendation surface matched - predicate is stale",
        )

    def test_ai_recommendation_generation_captures_full_lineage(self) -> None:
        rows = {row[0]: row for row in solution_pack.applied_release_gate_rows()}
        self.assertIn("AI recommendation generation", rows)
        _, gates, pattern, tier, _ = rows["AI recommendation generation"]

        self.assertIn("RG-08", gates, "AI recommendation generation must capture lineage")
        self.assertEqual("P0 Launch Blocker", tier)
        for required in ("model version", "prompt version", "retrieval trace", "actor context"):
            self.assertIn(required, pattern.lower(), f"lineage must capture {required}")

    def test_regulatory_compliance_metrics_have_strict_targets(self) -> None:
        rows = [row for row in solution_pack.metric_rows() if row[0] == "Compliance"]
        self.assertGreaterEqual(len(rows), 2)

        targets = {row[1]: row[5] for row in rows}
        part11 = next(v for k, v in targets.items() if "Part 11" in k)
        self.assertEqual("100%", part11, "Part 11 control pass rate must require 100%")

        alcoa = next(v for k, v in targets.items() if "ALCOA" in k)
        self.assertRegex(alcoa, r"<\s*\d", "ALCOA+ exception rate must have an upper bound")


class AutonomyGuardSelfTests(unittest.TestCase):
    """Proves the patient-safety autonomy guard actually works.

    A safety scanner that never fires is indistinguishable from no scanner.
    These tests feed it known-bad and known-good text so a passing result on
    the real artifacts is meaningful rather than vacuous.
    """

    KNOWN_BAD = (
        "The system may autonomously close deviation records once scored.",
        "Low-severity cases are automatically closed for patient complaints.",
        "Triage results are applied without human review to speed cycle time.",
        "For routine events no reviewer required before closure.",
        "Operators may bypass human sign-off when the queue is backed up.",
    )

    KNOWN_GOOD = (
        "AI remains decision support, never autonomous closure for patient-impacting records.",
        "The workflow does not permit closure without human review of high-risk cases.",
        "Controls prevent bypassing reviewer sign-off for patient-safety events.",
        "High-risk cases require documented human review with accountable sign-off.",
    )

    def test_guard_flags_each_known_bad_phrasing(self) -> None:
        for sentence in self.KNOWN_BAD:
            with self.subTest(sentence=sentence):
                self.assertNotEqual(
                    [], find_permissive_autonomy_violations(sentence),
                    msg=f"Guard failed to flag unsafe wording: {sentence!r}",
                )

    def test_guard_allows_properly_negated_phrasing(self) -> None:
        for sentence in self.KNOWN_GOOD:
            with self.subTest(sentence=sentence):
                self.assertEqual(
                    [], find_permissive_autonomy_violations(sentence),
                    msg=f"Guard false-positived on safe wording: {sentence!r}",
                )

    def test_guard_detects_violation_injected_into_real_artifact(self) -> None:
        """End-to-end: a regression in the real document must be caught."""
        mermaid = solution_pack.build_system_mermaid()
        clean = solution_pack.build_markdown(mermaid)
        self.assertEqual([], find_permissive_autonomy_violations(clean))

        tampered = clean.replace(
            "## Notes",
            "## Loophole\n\nRoutine deviations may be autonomously closed by the model.\n\n## Notes",
        )
        self.assertNotEqual(
            [], find_permissive_autonomy_violations(tampered),
            msg="Guard did not catch an injected autonomy loophole",
        )

    def test_every_forbidden_pattern_is_exercised_by_a_known_bad_case(self) -> None:
        """Each pattern must have at least one covering example."""
        for pattern in FORBIDDEN_AUTONOMY_PATTERNS:
            with self.subTest(pattern=pattern):
                self.assertTrue(
                    any(re.search(pattern, s.lower()) for s in self.KNOWN_BAD),
                    msg=f"Pattern {pattern!r} has no known-bad example covering it",
                )


class AiGovernanceIntegrityTests(unittest.TestCase):
    """Structural integrity of the AI governance model across all artifacts."""

    def test_no_dangling_gate_references_in_any_artifact(self) -> None:
        """Every RG-xx mentioned anywhere must exist in the gate catalog."""
        known = {row[0] for row in solution_pack.release_gate_rows()}
        mermaid = solution_pack.build_system_mermaid()

        sources = {
            "solution markdown": solution_pack.build_markdown(mermaid),
            "solution html": solution_pack.build_html(mermaid),
            "trust markdown": trust_pack.build_markdown(trust_pack.build_mermaid()),
            "trust applied table": trust_pack.build_applied_release_gate_markdown(),
        }

        for label, text in sources.items():
            referenced = extract_gate_ids(text)
            unknown = referenced - known
            self.assertSetEqual(
                set(), unknown,
                msg=f"{label} references undefined gate IDs: {sorted(unknown)}",
            )

    def test_every_gate_is_applied_somewhere(self) -> None:
        """A defined gate that is never applied is dead policy."""
        defined = {row[0] for row in solution_pack.release_gate_rows()}
        applied: set[str] = set()
        for _, gates, _, _, _ in solution_pack.applied_release_gate_rows():
            applied.update(piece.strip() for piece in gates.split(",") if piece.strip())
        self.assertSetEqual(defined, applied)

    def test_gate_tier_labels_are_internally_consistent(self) -> None:
        """Applied-table tier labels must agree with the gate partition."""
        p0 = solution_pack.p0_launch_gate_ids()
        p1 = {row[0] for row in solution_pack.p1_post_launch_gate_rows()}

        for surface, gates, _, tier, _ in solution_pack.applied_release_gate_rows():
            ids = {piece.strip() for piece in gates.split(",") if piece.strip()}
            expected = p0 if tier == "P0 Launch Blocker" else p1
            self.assertTrue(
                ids.issubset(expected),
                msg=f"Surface '{surface}' labeled {tier} but references {sorted(ids - expected)}",
            )

    def test_model_change_control_covers_prompt_and_calibration_data(self) -> None:
        """RG-05 must treat prompt and calibration-data updates as controlled changes."""
        rg05 = next(r for r in solution_pack.release_gate_rows() if r[0] == "RG-05")
        self.assertIn("prompt", rg05[1].lower())
        for required in ("risk assessment", "validation evidence", "rollback plan", "approvals"):
            self.assertIn(required, rg05[2].lower())

        calibration = next(
            row for row in solution_pack.organ_virtualization_rows()
            if "calibration data" in row[0].lower()
        )
        self.assertIn("RG-05", calibration[2])

    def test_compatibility_gate_requires_justification_for_safety_classes(self) -> None:
        """RG-09 must not allow silent compatibility regressions on safety cases."""
        rg09 = next(r for r in solution_pack.release_gate_rows() if r[0] == "RG-09")
        self.assertRegex(rg09[4].lower(), r"block|prevent")
        self.assertIn("justification", rg09[4].lower())

        error_rate = next(
            row for row in solution_pack.compatibility_metric_rows()
            if "newly introduced error" in row[0].lower()
        )
        guidance = error_rate[2].lower()
        self.assertIn("patient-safety", guidance)
        self.assertIn("documented justification", guidance)

    def test_organ_virtualization_escalates_for_regulatory_submissions(self) -> None:
        tiering = next(
            row for row in solution_pack.organ_virtualization_rows()
            if "qualification tiering" in row[0].lower()
        )
        self.assertRegex(tiering[1].lower(), r"ind|nda|submission")
        self.assertIn("escalat", tiering[2].lower())

    def test_in_silico_predictions_require_wet_lab_cross_validation(self) -> None:
        """In-silico models must not be trusted without ground-truth correlation."""
        cross_val = next(
            row for row in solution_pack.organ_virtualization_rows()
            if "cross-validation" in row[0].lower()
        )
        self.assertRegex(cross_val[1].lower(), r"correlation study")
        self.assertRegex(cross_val[2].lower(), r"correlation coefficient|drift threshold")

    def test_adversarial_and_reproducibility_gates_exist(self) -> None:
        ids = {row[0] for row in solution_pack.release_gate_rows()}
        self.assertIn("RG-06", ids, "reproducibility gate must exist")
        self.assertIn("RG-07", ids, "adversarial resilience gate must exist")

        rg07 = next(r for r in solution_pack.release_gate_rows() if r[0] == "RG-07")
        self.assertRegex(rg07[2].lower(), r"adversarial")

    def test_hardening_rows_all_specify_enforcement_and_evidence(self) -> None:
        for area, pattern, question, evidence, rule in solution_pack.ai_hardening_rows():
            self.assertTrue(evidence.strip(), f"Hardening area '{area}' has no evidence package")
            self.assertTrue(rule.strip(), f"Hardening area '{area}' has no enforcement rule")
            self.assertRegex(
                rule.lower(),
                r"block|fail|reject|must|freeze|escalat",
                msg=f"Hardening area '{area}' rule is not enforceable: {rule!r}",
            )

    def test_regulator_answers_each_cite_a_demonstrable_artifact(self) -> None:
        for challenge, response, artifact in solution_pack.regulator_answer_rows():
            self.assertTrue(artifact.strip(), f"No artifact for challenge: {challenge!r}")
            self.assertTrue(response.strip(), f"No response for challenge: {challenge!r}")


class GeneratorEntrypointTests(unittest.TestCase):
    """Covers main() paths, which were previously the only uncovered lines."""

    def test_solution_pack_main_writes_to_explicit_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with mock.patch.object(sys, "argv", ["prog", tmp_dir]):
                solution_pack.main()
            for name in (
                "qms_solution_diagram.mmd",
                "qms_solution_proposal.md",
                "qms_solution_proposal.html",
            ):
                self.assertTrue((Path(tmp_dir) / name).exists(), f"{name} not generated")

    def test_trust_pack_main_writes_to_explicit_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with mock.patch.object(sys, "argv", ["prog", tmp_dir]):
                trust_pack.main()
            for name in (
                "qms_trust_hardened_system_diagram.mmd",
                "qms_trust_hardened_system_diagram.md",
                "qms_trust_hardened_system_diagram.html",
            ):
                self.assertTrue((Path(tmp_dir) / name).exists(), f"{name} not generated")

    def test_system_diagram_main_writes_to_explicit_outdir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "nested"
            with mock.patch.object(sys, "argv", ["prog", "--outdir", str(target)]):
                system_diagram.main()
            self.assertTrue((target / "qms_system_diagram.mmd").exists())
            self.assertTrue((target / "qms_system_diagram.md").exists())

    def test_mains_do_not_write_into_repo_when_given_a_target(self) -> None:
        """Guard: running main() with an explicit target must not touch the repo."""
        before = {
            p.name: p.stat().st_mtime
            for p in REPO_ROOT.glob("qms_*")
            if p.is_file()
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            with mock.patch.object(sys, "argv", ["prog", tmp_dir]):
                solution_pack.main()
                trust_pack.main()
        after = {
            p.name: p.stat().st_mtime
            for p in REPO_ROOT.glob("qms_*")
            if p.is_file()
        }
        self.assertDictEqual(before, after, "main() modified committed artifacts")


if __name__ == "__main__":
    unittest.main()
