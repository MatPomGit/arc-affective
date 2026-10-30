"""P01 synthetic-only negative-control and feature-ablation invariants."""
from collections import Counter
from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arc_affective.p01_controls import (
    experiment, feature_sensitivity, negative_control, permute_training_trials,
)
from arc_affective.p01_evaluation import grouped_loso, synthetic_fixture


class SyntheticControlTests(unittest.TestCase):
    def setUp(self):
        self.rows = synthetic_fixture(subjects=4, trials=3, seed=21)

    def test_trial_shuffle_never_breaks_trial_consistency(self):
        shuffled = permute_training_trials(self.rows, seed=12)
        labels = {}
        for row in shuffled:
            key = (row.participant, row.trial)
            self.assertEqual(labels.setdefault(key, row.label), row.label)
        self.assertEqual(len(shuffled), len(self.rows))
        for before, after in zip(self.rows, shuffled):
            self.assertEqual((before.participant, before.trial, before.features),
                             (after.participant, after.trial, after.features))

    def test_train_shuffle_preserves_per_subject_prevalence(self):
        shuffled = permute_training_trials(self.rows, seed=35)
        original = {(r.participant, r.trial): r.label for r in self.rows}
        changed = {(r.participant, r.trial): r.label for r in shuffled}
        for participant in {r.participant for r in self.rows}:
            self.assertEqual(
                Counter(label for (subject, _), label in original.items()
                        if subject == participant),
                Counter(label for (subject, _), label in changed.items()
                        if subject == participant)
            )
        self.assertEqual(shuffled, permute_training_trials(self.rows, 35))

    def test_fold_holdout_excluded_from_permutation(self):
        train, test = next(grouped_loso(self.rows))
        selected = [self.rows[i] for i in train]
        untouched = [self.rows[i] for i in test]
        shuffled = permute_training_trials(selected, seed=7)
        self.assertTrue(set(row.participant for row in shuffled).isdisjoint(
            set(row.participant for row in untouched)))
        self.assertEqual(untouched, [self.rows[i] for i in test])
        changed_holdout = list(self.rows)
        for i in test:
            changed_holdout[i] = replace(changed_holdout[i], label=1-self.rows[i].label)
        new_train, _ = next(grouped_loso(changed_holdout))
        self.assertEqual(
            shuffled,
            permute_training_trials([changed_holdout[i] for i in new_train], 7)
        )

    def test_negative_control_is_deterministic_and_labeled(self):
        first = negative_control(self.rows, seed=11)
        self.assertEqual(first, negative_control(self.rows, 11))
        self.assertEqual(first["participants"], 4)
        self.assertTrue(first["train_only_shuffle"])
        self.assertTrue(first["outer_test_labels_untouched"])
        self.assertIsNone(first["p_value"])
        self.assertNotIn("synthetic-000", str(first))

    def test_feature_sensitivity_reports_all_not_only_best(self):
        report = feature_sensitivity(self.rows)
        cases = report["cases"]
        self.assertEqual(len(cases), 4)
        self.assertEqual([case["case"] for case in cases],
                         ["all", "omit_feature_0", "omit_feature_1",
                          "omit_feature_2"])
        self.assertEqual([case["n_features"] for case in cases], [3, 2, 2, 2])
        self.assertTrue(report["features_are_not_electrode_montages"])
        self.assertFalse(report["test_driven_model_selection_permitted"])

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            permute_training_trials(self.rows, seed=True)
        with self.assertRaises(ValueError):
            permute_training_trials([], seed=3)
        with self.assertRaises(ValueError):
            negative_control(self.rows, seed=False)
        with self.assertRaises(ValueError):
            feature_sensitivity([replace(r, features=(1.0,)) for r in self.rows])
        with self.assertRaises(ValueError):
            feature_sensitivity([
                replace(r, synthetic=False) for r in self.rows
            ])

    def test_experiment_does_not_claim_empirical_results(self):
        report = experiment(seed=21, subjects=4, trials=3)
        self.assertEqual(report["evidence"], "E0_synthetic_software_test_only")
        self.assertFalse(report["real_eeg_used"])
        self.assertFalse(report["rights_verified"])
        self.assertEqual(report["permutation"]["participants"], 4)
        self.assertEqual(len(report["feature_sensitivity"]["cases"]), 4)


if __name__ == "__main__":
    unittest.main()
