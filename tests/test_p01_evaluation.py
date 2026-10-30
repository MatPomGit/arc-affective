"""P01 deterministic synthetic grouped validation tests, no physiological data."""
import dataclasses
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arc_affective.p01_evaluation import (
    ALPHAS, EVIDENCE, Observation, brier, balanced_accuracy, evaluate,
    fit_linear, grouped_loso, synthetic_fixture, tune_alpha,
)


class GroupedEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.rows = synthetic_fixture(subjects=5, trials=4, seed=19)

    def test_deterministic_report_and_no_identity_export(self):
        report = evaluate(self.rows)
        self.assertEqual(report, evaluate(self.rows))
        self.assertEqual(report["evidence"], EVIDENCE)
        self.assertFalse(report["real_eeg_used"])
        self.assertFalse(report["external_validation"])
        self.assertEqual(report["participants"], 5)
        self.assertNotIn("synthetic-000", str(report))
        self.assertIsNone(report["confidence_intervals"])

    def test_outer_participants_and_trials_disjoint(self):
        seen = set()
        for train, test in grouped_loso(self.rows):
            t1 = {self.rows[i].participant for i in train}
            t2 = {self.rows[i].participant for i in test}
            self.assertFalse(t1 & t2)
            self.assertEqual(len(t2), 1)
            self.assertFalse(set(train) & set(test))
            seen.update(test)
            self.assertFalse({
                (self.rows[i].participant, self.rows[i].trial) for i in train
            } & {
                (self.rows[i].participant, self.rows[i].trial) for i in test
            })
        self.assertEqual(seen, set(range(len(self.rows))))

    def test_outer_holdout_never_affects_train_normalization_or_hyperparameter(self):
        train_indices, holdout = next(grouped_loso(self.rows))
        train = [self.rows[i] for i in train_indices]
        baseline_alpha = tune_alpha(train)
        baseline = fit_linear(train, baseline_alpha)
        self.assertIn(baseline_alpha, ALPHAS)
        shifted = list(self.rows)
        for i in holdout:
            shifted[i] = dataclasses.replace(
                shifted[i], features=(100000.0, -100000.0, 1e8),
                label=1 - shifted[i].label)
        train_again, _ = next(grouped_loso(shifted))
        revised = [shifted[i] for i in train_again]
        self.assertEqual(train, revised)
        self.assertEqual(tune_alpha(revised), baseline_alpha)
        self.assertEqual(fit_linear(revised, baseline_alpha), baseline)

    def test_baseline_is_train_only_prevalence(self):
        train, test = next(grouped_loso(self.rows))
        prior = sum(self.rows[i].label for i in train) / len(train)
        report = evaluate(self.rows)["folds"][0]
        self.assertAlmostEqual(
            report["majority_brier"],
            brier([self.rows[i].label for i in test], [prior] * len(test))
        )

    def test_brier_and_balanced_accuracy(self):
        self.assertAlmostEqual(brier([0, 1], [0.0, 1.0]), 0.0)
        self.assertAlmostEqual(balanced_accuracy([0, 1], [0.1, 0.9]), 1)
        self.assertIsNone(balanced_accuracy([1, 1], [0.8, 0.9]))
        report = evaluate(self.rows)
        self.assertTrue(all(0 <= fold["linear_brier"] <= 1
                            for fold in report["folds"]))
        self.assertTrue(all(fold["training_participants"] == 4
                            for fold in report["folds"]))

    def test_rejects_ineligible_and_malformed_data(self):
        with self.assertRaises(ValueError):
            evaluate(self.rows[:2])
        with self.assertRaises(ValueError):
            evaluate([dataclasses.replace(r, synthetic=False) for r in self.rows])
        with self.assertRaises(ValueError):
            evaluate([dataclasses.replace(r, features=(float("nan"),))
                      for r in self.rows])
        with self.assertRaises(ValueError):
            evaluate([dataclasses.replace(r, label=True) for r in self.rows])
        with self.assertRaises(ValueError):
            evaluate([dataclasses.replace(r, label=0) for r in self.rows])
        with self.assertRaises(ValueError):
            fit_linear([], 0.01)

    def test_trial_label_conflict_rejected(self):
        changed = list(self.rows)
        changed[1] = dataclasses.replace(changed[1], label=1-changed[1].label)
        with self.assertRaisesRegex(ValueError, "Conflicting labels"):
            evaluate(changed)


    def test_trial_aggregation_prevents_window_pseudoreplication(self):
        from arc_affective.p01_evaluation import trial_predictions, trial_weights
        rows = [
            Observation("p1", "a", (0.0,), 0),
            Observation("p1", "a", (0.0,), 0),
            Observation("p1", "b", (1.0,), 1),
        ]
        labels, probs = trial_predictions(rows, [0.1, 0.3, 0.9])
        self.assertEqual(labels, [0, 1])
        self.assertAlmostEqual(probs[0], 0.2)
        self.assertAlmostEqual(brier(labels, probs), (0.2**2 + 0.1**2) / 2)
        weights = trial_weights(rows)
        self.assertAlmostEqual(sum(weights[:2]), weights[2])

    def test_replication_of_whole_trial_does_not_change_training(self):
        from arc_affective.p01_evaluation import trial_predictions
        training = [r for r in self.rows if r.participant != "synthetic-000"]
        trial = [r for r in training
                 if r.participant == "synthetic-001" and r.trial == "trial-000"]
        original = fit_linear(training, 0.1)
        repeated = fit_linear(training + trial, 0.1)
        for first, second in zip(original.means, repeated.means):
            self.assertAlmostEqual(first, second, places=12)
        for first, second in zip(original.weights, repeated.weights):
            self.assertAlmostEqual(first, second, places=10)
        self.assertAlmostEqual(original.intercept, repeated.intercept, places=10)
        with self.assertRaises(ValueError):
            trial_predictions(trial, [float("nan")] * len(trial))

    def test_invalid_row_object_is_value_error(self):
        from arc_affective.p01_evaluation import validate_rows
        with self.assertRaises(ValueError):
            validate_rows([None, *self.rows])

    def test_single_class_heldout_not_inflated(self):
        rows = synthetic_fixture(subjects=4, trials=2, seed=1)
        rows = [dataclasses.replace(r, label=(int(r.participant[-3:]) % 2))
                for r in rows]
        report = evaluate(rows)
        self.assertEqual(report["balanced_accuracy_folds_evaluable"], 0)
        self.assertIsNone(report["mean_participant_linear_balanced_accuracy"])


if __name__ == "__main__":
    unittest.main()
