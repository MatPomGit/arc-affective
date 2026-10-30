"""Synthetic continuous-valence pilot tests, never human EEG measurements."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arc_affective.p01_continuous import (
    ALPHAS, ContinuousRow, choose_alpha, concordance, evaluate, fit_ridge,
    grouped_loso, mse, synthetic_fixture, training_weights, trial_predictions,
)


class ContinuousEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.rows = synthetic_fixture(subjects=4, trials=4, seed=19)

    def test_ccc_exact_perfect_inverse_and_constant_baseline(self):
        self.assertAlmostEqual(concordance([0, 1, 2], [0, 1, 2]), 1)
        self.assertAlmostEqual(concordance([0, 1, 2], [2, 1, 0]), -1)
        self.assertAlmostEqual(concordance([0, 1, 2], [1, 1, 1]), 0)
        self.assertIsNone(concordance([2, 2], [1, 3]))
        self.assertIsNone(concordance([2], [2]))
        self.assertAlmostEqual(mse([0, 2], [1, 1]), 1)

    def test_ccc_detects_bias_even_with_perfect_correlation(self):
        self.assertLess(concordance([1, 2, 3], [2, 3, 4]), 1)
        self.assertGreater(concordance([1, 2, 3], [2, 3, 4]), 0)
        with self.assertRaises(ValueError):
            concordance([1, 2], [1, float("nan")])

    def test_non_binary_trial_labels_and_determinism(self):
        report = evaluate(self.rows)
        self.assertEqual(report, evaluate(self.rows))
        self.assertEqual(report["participants"], 4)
        self.assertEqual(report["ccc_folds_evaluable"], 4)
        self.assertEqual(report["target"], "synthetic_continuous_valence_0_7")
        self.assertFalse(report["real_eeg_used"])
        self.assertFalse(report["protocol_frozen"])
        self.assertIsNone(report["confidence_intervals"])
        self.assertNotIn("synthetic-000", str(report))
        self.assertEqual(report["mean_participant_train_mean_ccc"], 0)

    def test_subject_loso_disjoint_and_complete(self):
        held_out = set()
        for tr, te in grouped_loso(self.rows):
            train = {self.rows[i].participant for i in tr}
            test = {self.rows[i].participant for i in te}
            self.assertFalse(train & test)
            self.assertEqual(len(test), 1)
            held_out.update(te)
        self.assertEqual(held_out, set(range(len(self.rows))))

    def test_outer_holdout_cannot_affect_training_or_nested_alpha(self):
        train_i, test_i = next(grouped_loso(self.rows))
        train = [self.rows[i] for i in train_i]
        alpha = choose_alpha(train)
        model = fit_ridge(train, alpha)
        changed = list(self.rows)
        for i in test_i:
            changed[i] = replace(changed[i],
                                 features=(10000.0, -10000.0),
                                 valence=0)
        again_i, _ = next(grouped_loso(changed))
        again = [changed[i] for i in again_i]
        self.assertEqual(choose_alpha(again), alpha)
        self.assertEqual(fit_ridge(again, alpha), model)
        self.assertIn(alpha, ALPHAS)

    def test_aggregation_avoids_window_pseudoreplication(self):
        rows = [ContinuousRow("p", "a", (1.0,), 1.5),
                ContinuousRow("p", "a", (2.0,), 1.5),
                ContinuousRow("p", "b", (3.0,), 4.0)]
        y, p = trial_predictions(rows, [1, 2, 5])
        self.assertEqual(y, [1.5, 4])
        self.assertEqual(p, [1.5, 5])
        with self.assertRaises(ValueError):
            trial_predictions(rows, [1, 2])

    def test_weight_equalizes_subject_trial_and_window_counts(self):
        rows = self.rows + [self.rows[0]] * 4
        w = training_weights(rows)
        subject_w = {}
        trial_w = {}
        for r, wt in zip(rows, w):
            subject_w[r.participant] = subject_w.get(r.participant, 0) + wt
            key = (r.participant, r.trial)
            trial_w[key] = trial_w.get(key, 0) + wt
        for value in subject_w.values():
            self.assertAlmostEqual(value, 0.25)
        for value in trial_w.values():
            self.assertAlmostEqual(value, 0.0625)

    def test_replication_of_entire_trial_cannot_change_fit(self):
        training = [r for r in self.rows if r.participant != "synthetic-000"]
        one_trial = [r for r in training if
                     (r.participant, r.trial) == ("synthetic-001", "trial-000")]
        first = fit_ridge(training, 0.1)
        second = fit_ridge(training + one_trial, 0.1)
        for a, b in zip(first.coefficients, second.coefficients):
            self.assertAlmostEqual(a, b, places=10)
        self.assertAlmostEqual(first.intercept, second.intercept, places=10)

    def test_constant_target_participant_is_excluded_from_ccc_mean(self):
        changed = [
            replace(r, valence=4.0) if r.participant == "synthetic-000"
            else r for r in self.rows
        ]
        report = evaluate(changed)
        self.assertEqual(report["ccc_folds_evaluable"], 3)
        self.assertIsNone(report["folds"][0]["ridge_ccc"])
        self.assertEqual(report["folds"][0]["train_mean_ccc"], None)

    def test_rejects_non_synthetic_nonfinite_and_conflicting_trial(self):
        with self.assertRaises(ValueError):
            evaluate([replace(r, synthetic=False) for r in self.rows])
        with self.assertRaises(ValueError):
            evaluate([replace(r, valence=float("nan")) for r in self.rows])
        with self.assertRaises(ValueError):
            evaluate([replace(r, valence=7.1) for r in self.rows])
        with self.assertRaises(ValueError):
            evaluate([replace(r, valence=True) for r in self.rows])
        changed = list(self.rows)
        changed[1] = replace(changed[1], valence=changed[1].valence + .1)
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            evaluate(changed)
        with self.assertRaises(ValueError):
            fit_ridge([], .1)

    def test_rejects_incomplete_data_and_wrong_feature_dimensions(self):
        with self.assertRaises(ValueError):
            evaluate(self.rows[:2])
        with self.assertRaises(ValueError):
            evaluate([replace(self.rows[0], features=(1.0,))] + self.rows[1:])
        with self.assertRaises(ValueError):
            fit_ridge(self.rows, True)
        with self.assertRaises(ValueError):
            fit_ridge(self.rows, 0)
        with self.assertRaises(ValueError):
            synthetic_fixture(subjects=3)
        model = fit_ridge(self.rows, .1)
        with self.assertRaises(ValueError):
            model.predict((1.0,))

    def test_no_trial_label_shortcut(self):
        # Continuous model has no binary_label / stimulus category field.
        self.assertFalse(hasattr(self.rows[0], "binary_label"))
        self.assertFalse(hasattr(self.rows[0], "targeted_valence"))
        self.assertTrue(all(0 <= r.valence <= 7 for r in self.rows))


if __name__ == "__main__":
    unittest.main()
