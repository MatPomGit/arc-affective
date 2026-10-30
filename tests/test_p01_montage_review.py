"""Synthetic-only FACED montage stop-rule checks."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arc_affective.p01_montage_review import (
    COHORT1, COHORT2, SHARED, audit_family, audit_subset,
)


def proposed():
    return {
        "2": ["F3", "F4"],
        "4": ["F3", "F4", "C3", "C4"],
        "8": ["F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2"],
    }


class MontageReviewTests(unittest.TestCase):
    def test_shared_names_do_not_grant_analysis_authorization(self):
        r = audit_subset(["F3", "F4"])
        self.assertEqual(r["status"], "text_only_not_approved")
        self.assertEqual(r["shared_names"], ["F3", "F4"])
        self.assertFalse(r["eeg_analysis_allowed"])
        self.assertFalse(r["physical_positions_verified"])
        self.assertFalse(r["automated_alias_mapping_allowed"])

    def test_complete_nested_family_still_is_not_physical_match(self):
        r = audit_family(proposed())
        self.assertEqual(r["status"], "design_review_only")
        self.assertTrue(r["nested_by_exact_names"])
        self.assertFalse(r["physical_montage_approved"])
        self.assertFalse(r["signal_processing_allowed"])
        self.assertFalse(r["protocol_frozen"])

    def test_disputed_temporal_names_are_blocked(self):
        r = audit_subset(["T3", "T4"])
        self.assertEqual(r["status"], "blocked")
        self.assertEqual(r["cohort_specific_names"], ["T3", "T4"])
        self.assertIn("cohort_specific_names_or_roles", r["blockers"])

    def test_eog_mastoid_software_aliases_are_not_accepted(self):
        for names in (["A1", "A2"], ["HEOR", "HEOL"]):
            with self.subTest(names=names):
                r = audit_subset(names)
                self.assertEqual(r["status"], "blocked")
                self.assertFalse(r["automated_alias_mapping_allowed"])

    def test_unknown_labels_are_blocked_not_silently_normalized(self):
        r = audit_subset(["F3", "FakeElectrode"])
        self.assertEqual(r["status"], "blocked")
        self.assertEqual(r["unknown_names"], ["FakeElectrode"])

    def test_reject_malformed_and_duplicate_names(self):
        for value in (["F3"], ["F3", "F4", "C3"], ["F3", "F3"],
                      ["F3", "f3"], [" F3", "F4"], ["F3", None],
                      ["F3", ""], ["F3", 3], "F3,F4"):
            with self.subTest(value=str(value)), self.assertRaises(ValueError):
                audit_subset(value)

    def test_missing_or_wrong_size_family_is_rejected(self):
        p = proposed()
        del p["8"]
        with self.assertRaises(ValueError):
            audit_family(p)
        p = proposed()
        p["8"] = ["F3"] * 8
        with self.assertRaises(ValueError):
            audit_family(p)

    def test_non_nested_family_is_reported_without_autoreordering(self):
        p = proposed()
        p["2"] = ["O1", "O2"]
        r = audit_family(p)
        self.assertFalse(r["nested_by_exact_names"])
        self.assertEqual(r["subsets"]["2"]["shared_names"], ["O1", "O2"])

    def test_one_disputed_montage_blocks_family(self):
        p = proposed()
        p["8"][-1] = "A1"
        r = audit_family(p)
        self.assertEqual(r["status"], "blocked")
        self.assertEqual(r["blocked_sizes"], [8])

    def test_source_inventory_is_pinned_and_not_physical_evidence(self):
        self.assertEqual(len(COHORT1), 32)
        self.assertEqual(len(COHORT2), 32)
        self.assertEqual(len(SHARED), 26)
        self.assertNotIn("HEOR", SHARED)
        self.assertNotIn("A1", SHARED)


if __name__ == "__main__":
    unittest.main()
