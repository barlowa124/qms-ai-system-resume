import re
import tempfile
import unittest
from pathlib import Path

import generate_qms_solution_pack as solution_pack
import generate_qms_trust_hardened_diagram as trust_pack


def extract_gate_ids(text: str) -> set[str]:
    return set(re.findall(r"RG-\d+", text))


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


if __name__ == "__main__":
    unittest.main()
