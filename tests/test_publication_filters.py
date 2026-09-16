"""Regression tests for ATNS source-level publication filters."""

from __future__ import annotations

import unittest

from scripts.publication_filters import confidential_entity_ids, is_public


class PublicationFilterTests(unittest.TestCase):
    def test_public_rows_must_be_explicitly_public_and_not_deleted(self) -> None:
        self.assertTrue(is_public({"Public": "1", "Deleted": "0"}))
        self.assertTrue(is_public({"Public": "true", "Deleted": "false"}))
        self.assertFalse(is_public({"Public": "0", "Deleted": "0"}))
        self.assertFalse(is_public({"Public": "1", "Deleted": "1"}))
        self.assertFalse(is_public({"Public": "", "Deleted": "0"}))

    def test_confidential_additional_rows_withhold_parent_entities(self) -> None:
        rows = [
            {"EntityID": "10", "Confidential": "0"},
            {"EntityID": "20", "Confidential": "1"},
            {"EntityID": "30", "Confidential": "true"},
            {"EntityID": "", "Confidential": "1"},
        ]
        self.assertEqual(confidential_entity_ids(rows), {"20", "30"})


if __name__ == "__main__":
    unittest.main()
