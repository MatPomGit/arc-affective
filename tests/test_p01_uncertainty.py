"""Deterministic statistics tests: independent synthetic subject pairs only."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arc_affective.p01_uncertainty import (
    EVIDENCE, SubjectPair, paired_subject_interval, synthetic_demo,
)


def records(delta=0.1):
    return [SubjectPair(f"synthetic-p{i}", 0.5, 0.5 - delta)
            for i in range(6)]


class UncertaintyTests(unittest.TestCase):
    def test_zero_difference_has_zero_interval(self):
        report = paired_subject_interval(records(0.0), resamples=300)
        self.assertEqual(report["mean_delta"], 0.0)
        self.assertEqual(report["interval_lower"], 0.0)
        self.assertEqual(report["interval_upper"], 0.0)
        self.assertFalse(report["participant_identifiers_exported"])

    def test_identical_positive_difference_and_direction(self):
        report = paired_subject_interval(records(0.1), resamples=300)
        self.assertGreater(report["mean_delta"], 0)
        self.assertAlmostEqual(report["interval_lower"], report["mean_delta"])
        self.assertAlmostEqual(report["interval_upper"], report["mean_delta"])
        self.assertEqual(report["statistical_unit"], "independent_participant")

    def test_paired_direction_reverse(self):
        a = records(0.1)
        b = [SubjectPair(p.participant, p.candidate_brier, p.reference_brier)
             for p in a]
        first = paired_subject_interval(a, resamples=300)
        second = paired_subject_interval(b, resamples=300)
        self.assertAlmostEqual(first["mean_delta"], -second["mean_delta"])

    def test_mixed_heterogeneous_subjects_deterministic(self):
        a = [SubjectPair(f"p{i}", 0.3+i*0.03, 0.4-i*0.02)
             for i in range(7)]
        first = paired_subject_interval(a, resamples=500, seed=31)
        self.assertEqual(first, paired_subject_interval(a, resamples=500, seed=31))
        self.assertLessEqual(first["interval_lower"], first["interval_upper"])
        self.assertTrue(-1 <= first["mean_delta"] <= 1)
        self.assertNotIn("p0", str(first))

    def test_rejects_duplicate_and_insufficient_subjects(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            paired_subject_interval(records()[:4] + records()[:1])
        with self.assertRaises(ValueError):
            paired_subject_interval(records()[:3])

    def test_rejects_invalid_scores_and_parameters(self):
        invalid = [
            SubjectPair("p1", float("nan"), .5),
            SubjectPair("p1", -0.1, .5),
            SubjectPair("p1", .2, True),
        ]
        for item in invalid:
            with self.subTest(item=item), self.assertRaises(ValueError):
                paired_subject_interval([item, *records()[:4]])
        for options in ({"confidence": 1.0}, {"confidence": float("nan")},
                        {"resamples": 0}, {"resamples": True}, {"seed": True}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                paired_subject_interval(records(), **options)

    def test_demo_never_claims_actual_eeg(self):
        report = synthetic_demo()
        self.assertEqual(report["evidence"], EVIDENCE)
        self.assertFalse(report["real_eeg_used"])
        self.assertFalse(report["dataset_licence_verified"])
        self.assertEqual(report["result"]["participants"], 6)


if __name__ == "__main__":
    unittest.main()
