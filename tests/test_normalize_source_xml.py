"""Regression tests for conservative ATNS legacy rich-text normalization."""

from __future__ import annotations

import unittest

from scripts.normalize_source_xml import (
    entity_resource_iri,
    html_to_structured_text,
    remove_illegal_xml_characters,
)
from scripts.resource_identity import legacy_entity_iri


class RichTextNormalizationTests(unittest.TestCase):
    def test_generated_entity_iri_matches_sandbox_identity_rule(self) -> None:
        self.assertEqual(
            entity_resource_iri("3814", "1", {}),
            "https://data.idnau.org/pid/resource/b614bba5-8456-5bdd-a1c9-e161b5b1e35a",
        )

    def test_organization_uses_agent_specific_iri_with_stable_uuid(self) -> None:
        self.assertEqual(
            entity_resource_iri("8105", "3", {}),
            "https://data.idnau.org/pid/org/02f08bf6-163d-5ba6-98d3-6164df364316",
        )

    def test_established_agreement_iri_is_retained(self) -> None:
        self.assertEqual(
            entity_resource_iri("27", "1", {}),
            "https://data.idnau.org/pid/resource/dd9b004b-1c22-5b53-8381-bd93760ee922",
        )

    def test_reviewed_external_identity_overrides_generated_iri(self) -> None:
        self.assertEqual(
            entity_resource_iri("383", "3", {"383": "https://ror.org/00wqdbc63"}),
            "https://ror.org/00wqdbc63",
        )

    def test_previously_published_sample_iri_is_preserved_as_legacy_alias(self) -> None:
        self.assertEqual(
            legacy_entity_iri("618"),
            "https://data.idnau.org/pid/resource/050308f6-67e6-52f6-82c9-56c20413cac6",
        )

    def test_entity_3814_style_underlined_headings_are_retained(self) -> None:
        source = (
            "<u>Purpose</u> \\n\\nThe agreement text."
            "\\n\\n<u>Performance Indicators and Feedback Mechanisms</u>"
            "\\n\\nMonitoring text."
        )
        normalized, reasons, _ = html_to_structured_text(source)
        self.assertEqual(
            normalized,
            "Purpose\n\nThe agreement text.\n\n"
            "Performance Indicators and Feedback Mechanisms\n\nMonitoring text.",
        )
        self.assertEqual(reasons, [])

    def test_entity_7744_style_paragraphs_headings_and_lists_are_retained(self) -> None:
        source = (
            "<p><strong>Background to the Agreement:</strong></p>"
            "<p>Background text.<br></p>"
            "<p><em>Native Title Provisions:</em></p>"
            "<ul><li>first future act;</li><li>second future act.</li></ul>"
        )
        normalized, reasons, _ = html_to_structured_text(source)
        self.assertEqual(
            normalized,
            "Background to the Agreement:\n\nBackground text.\n\n"
            "Native Title Provisions:\n\n• first future act;\n\n• second future act.",
        )
        self.assertEqual(reasons, [])

    def test_source_wording_is_not_corrected(self) -> None:
        source = "<p>The Agreementmay contain a constructon error.</p>"
        normalized, _, _ = html_to_structured_text(source)
        self.assertEqual(normalized, "The Agreementmay contain a constructon error.")

    def test_link_text_and_external_target_are_retained(self) -> None:
        source = '<p>Read the <a href="https://example.com/agreement">agreement</a>.</p>'
        normalized, reasons, _ = html_to_structured_text(source)
        self.assertEqual(
            normalized, "Read the agreement (https://example.com/agreement)."
        )
        self.assertEqual(reasons, [])

    def test_xml_10_forbidden_controls_are_removed(self) -> None:
        normalized, count = remove_illegal_xml_characters("before\x03middle\x0bafter")
        self.assertEqual(normalized, "beforemiddleafter")
        self.assertEqual(count, 2)


if __name__ == "__main__":
    unittest.main()
