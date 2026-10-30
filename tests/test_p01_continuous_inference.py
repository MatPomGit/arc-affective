"""P01 descriptive paired bootstrap software contract; all fixtures synthetic."""
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arc_affective.p01_continuous_inference import (
    paired_interval, synthetic_demo,
)


def rows(candidate=0.4, baseline=0.2):
    return [{
        "fold": i + 1,
        "ridge_ccc": candidate,
        "train_mean_ccc": baseline,
        "ridge_mse": 0.5 - candidate / 4,
        "train_mean_mse": 0.7 - baseline / 4,
    } for i in range(5)]


class DescriptiveIntervalsTests(unittest.TestCase):
    def test_constant_positive_ccc_difference(self):
        result = paired_interval(rows(), metric="ccc", resamples=250)
        self.assertEqual(result["status"], "descriptive_interval_only")
        self.assertAlmostEqual(result["mean_difference"], 0.2)
        self.assertAlmostEqual(result["interval_lower"], 0.2)
        self.assertAlmostEqual(result["interval_upper"], 0.2)
        self.assertFalse(result["confirmatory_inference_validated"])
        self.assertTrue(result["overlapping_loso_training_dependency_unresolved"])

    def test_zero_difference_ccc_interval(self):
        result = paired_interval(rows(.3, .3), metric="ccc", resamples=250)
        self.assertEqual(result["mean_difference"], 0)
        self.assertEqual(result["interval_lower"], 0)
        self.assertEqual(result["interval_upper"], 0)

    def test_reversed_direction(self):
        result = paired_interval(rows(.1, .4), metric="ccc", resamples=250)
        self.assertLess(result["mean_difference"], 0)
        self.assertEqual(result["direction"], "candidate_minus_reference")

    def test_mse_direction_is_reference_minus_candidate(self):
        result = paired_interval(rows(.4, .2), metric="mse", resamples=250)
        self.assertGreater(result["mean_difference"], 0)
        self.assertEqual(result["direction"], "reference_minus_candidate")

    def test_undefined_ccc_blocks_interval_instead_of_selection_bias(self):
        folds = rows()
        folds[0]["ridge_ccc"] = None
        result = paired_interval(folds, metric="ccc", resamples=250)
        self.assertEqual(result["status"], "blocked_undefined_participant_ccc")
        self.assertEqual(result["undefined_or_missing_participants"], 1)
        self.assertEqual(result["complete_cases"], 4)
        self.assertIsNone(result["interval_lower"])
        self.assertIsNone(result["mean_difference"])
        self.assertEqual(
            paired_interval(folds, metric="mse", resamples=250)
            ["status"], "descriptive_interval_only",
        )

    def test_duplicate_and_too_few_folds_rejected(self):
        folds = rows()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            paired_interval(folds + [folds[0]], metric="ccc")
        with self.assertRaises(ValueError):
            paired_interval(folds[:3], metric="ccc")
        with self.assertRaises(ValueError):
            paired_interval(rows(), metric="other")

    def test_invalid_score_and_parameter_rejected(self):
        for val in (True, float("nan"), float("inf"), 2.0):
            folds = rows()
            folds[0]["ridge_ccc"] = val
            with self.subTest(val=val), self.assertRaises(ValueError):
                paired_interval(folds, metric="ccc")
        for val in (-.1, float("nan"), True):
            folds = rows()
            folds[0]["ridge_mse"] = val
            with self.subTest(val=val), self.assertRaises(ValueError):
                paired_interval(folds, metric="mse")
        for options in ({"confidence": 1}, {"confidence": float("nan")},
                        {"resamples": True}, {"seed": True},
                        {"resamples": 10}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                paired_interval(rows(), metric="ccc", **options)

    def test_bootstrap_determinism_and_order_invariance_for_constant_folds(self):
        r = rows()
        self.assertEqual(paired_interval(r, metric="ccc", seed=30),
                         paired_interval(r, metric="ccc", seed=30))
        self.assertEqual(paired_interval(r, metric="ccc", seed=30),
                         paired_interval(list(reversed(r)), metric="ccc",
                                         seed=30))

    def test_demo_is_explicit_synthetic_and_no_id_export(self):
        report = synthetic_demo()
        self.assertEqual(report["evidence"], "E0_synthetic_software_test_only")
        self.assertFalse(report["real_eeg_used"])
        self.assertFalse(report["rights_verified"])
        self.assertFalse(report["protocol_frozen"])
        self.assertEqual(report["mse"]["participants"], 5)
        self.assertTrue(-2 <= report["ccc"]["mean_difference"] <= 2)
        self.assertNotIn("synthetic-000", str(report))
        self.assertIsNone(report["ccc"]["p_value"])


if __name__ == "__main__":
    unittest.main()
