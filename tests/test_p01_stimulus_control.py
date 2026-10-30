"""P01 film-identity confounding and dual-disjoint split invariants, E0."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arc_affective.p01_stimulus_control import (
    StimulusTrial, audit_stimulus_confound, joint_disjoint_splits,
    participant_splits, synthetic_fixture, validate_trials,
)


class StimulusControlTests(unittest.TestCase):
    def setUp(self):
        self.rows = synthetic_fixture(participants=5, clips=4)

    def test_participant_loso_never_reuses_participants(self):
        for train_i, test_i in participant_splits(self.rows):
            train = [self.rows[i] for i in train_i]
            test = [self.rows[i] for i in test_i]
            self.assertTrue({r.participant for r in train}.isdisjoint(
                {r.participant for r in test}))
            self.assertEqual(len({r.stimulus for r in test}), 4)
            self.assertEqual({r.stimulus for r in train},
                             {r.stimulus for r in test})
        self.assertEqual(len(list(participant_splits(self.rows))), 5)

    def test_joint_splits_exclude_both_axes_and_cross_cells(self):
        partitions = list(joint_disjoint_splits(self.rows))
        self.assertEqual(len(partitions), len(self.rows))
        for train_i, test_i, removed_i in partitions:
            self.assertEqual(len(test_i), 1)
            self.assertEqual(len(train_i), 12)
            self.assertEqual(len(removed_i), 7)
            self.assertEqual(
                set(train_i) | set(test_i) | set(removed_i),
                set(range(len(self.rows))))
            self.assertFalse((set(train_i) & set(test_i)) or
                             (set(train_i) & set(removed_i)) or
                             (set(test_i) & set(removed_i)))
            held = self.rows[test_i[0]]
            self.assertTrue(all(
                self.rows[i].participant != held.participant
                and self.rows[i].stimulus != held.stimulus
                for i in train_i
            ))

    def test_film_only_prior_flags_identity_confounded_design(self):
        report = audit_stimulus_confound(self.rows)
        participant = report["participant_loso"]
        self.assertEqual(
            participant["test_trials_with_stimulus_seen_in_training"], 20)
        self.assertFalse(participant["stimulus_disjoint"])
        self.assertLess(
            participant["mean_participant_stimulus_prior_mse"],
            participant["mean_participant_train_mean_mse"])
        self.assertTrue(report["participant_and_stimulus_disjoint"]
                        ["stimulus_disjoint"])
        self.assertFalse(report["model_inputs_eeg"])
        self.assertFalse(report["validates_generalization_of_eeg"])

    def test_report_is_deterministic_and_never_exports_identifiers(self):
        one = audit_stimulus_confound(self.rows)
        self.assertEqual(one, audit_stimulus_confound(self.rows))
        self.assertNotIn("synthetic-p", str(one))
        self.assertNotIn("synthetic-film", str(one))
        self.assertFalse(one["statistical_inference_authorized"])
        self.assertIsNone(one["p_value"])
        self.assertIsNone(one["confidence_interval"])

    def test_held_out_rating_cannot_change_training_priors(self):
        from arc_affective.p01_stimulus_control import _clip_prior, _train_mean
        train_i, test_i = next(participant_splits(self.rows))
        train = [self.rows[i] for i in train_i]
        original_priors = _clip_prior(train)
        perturbed = list(self.rows)
        for i in test_i:
            perturbed[i] = replace(
                perturbed[i], valence=7 - perturbed[i].valence)
        changed_train = [perturbed[i] for i in train_i]
        self.assertEqual(original_priors, _clip_prior(changed_train))
        self.assertEqual(_train_mean(train), _train_mean(changed_train))

    def test_missing_clip_in_test_subject_uses_training_fallback(self):
        rows = list(self.rows)
        # Test subject sees one valid clip not shown in other subjects;
        # the others retain at least three clips.
        rows[0] = replace(rows[0], stimulus="synthetic-unseen-film")
        report = audit_stimulus_confound(rows)
        self.assertEqual(
            report["participant_loso"]
                  ["test_trials_with_stimulus_seen_in_training"], 19)

    def test_duplicate_trials_or_clips_for_subject_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate trial"):
            validate_trials(self.rows + [self.rows[0]])
        renamed = list(self.rows)
        renamed[1] = replace(renamed[1], stimulus=renamed[0].stimulus)
        with self.assertRaisesRegex(ValueError, "Duplicate stimulus"):
            validate_trials(renamed)

    def test_out_of_range_or_invalid_target_is_rejected(self):
        for val in (-0.1, 7.1, float("nan"), float("inf"), True, "3"):
            with self.subTest(val=str(val)):
                rows = list(self.rows)
                rows[0] = replace(rows[0], valence=val)
                with self.assertRaises(ValueError):
                    validate_trials(rows)

    def test_nonsynthetic_and_bad_identity_are_rejected(self):
        for changed in (
            {"synthetic": False},
            {"synthetic": 1},
            {"participant": " "},
            {"trial": " bad"},
            {"stimulus": ""},
        ):
            with self.subTest(changed=changed):
                rows = list(self.rows)
                rows[0] = replace(rows[0], **changed)
                with self.assertRaises(ValueError):
                    validate_trials(rows)

    def test_unbalanced_missing_cells_fail_if_joint_train_unsupported(self):
        # One clip occurs in only one subject; its intersection still has
        # enough train clips, but its own test is one held-out rating only.
        rows = [r for r in self.rows
                if r.stimulus != "synthetic-film03" or
                r.participant == "synthetic-p00"]
        with self.assertRaises(ValueError):
            validate_trials(rows)
        with self.assertRaises(ValueError):
            list(joint_disjoint_splits(rows))

    def test_too_few_subjects_and_clips_rejected(self):
        for kwargs in ({"participants": 3}, {"clips": 2},
                       {"participants": True}, {"clips": 3.0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                synthetic_fixture(**kwargs)
        with self.assertRaises(ValueError):
            validate_trials([])

    def test_trial_unit_is_one_independent_self_report(self):
        report = audit_stimulus_confound(self.rows)
        result = report["participant_and_stimulus_disjoint"]
        self.assertEqual(result["n_intersection_folds"], 20)
        self.assertEqual(result["mean_cross_cell_rows_excluded"], 7)
        self.assertTrue(result["single_trial_per_intersection"])
        self.assertFalse(result["ccc_defined_per_intersection"])


if __name__ == "__main__":
    unittest.main()
