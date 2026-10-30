"""P01 film-identity confounding and dual-disjoint split invariants, E0."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arc_affective.p01_stimulus_control import (
    StimulusTrial, audit_blocked_stimulus_control, audit_stimulus_confound,
    blocked_joint_disjoint_splits, joint_disjoint_splits,
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
                if not (r.participant == "synthetic-p00" and
                        r.stimulus in ("synthetic-film02", "synthetic-film03"))]
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



def film_blocks(n=8, size=4):
    return [
        tuple(f"synthetic-film{i:02d}" for i in range(start, start + size))
        for start in range(0, n, size)
    ]


class BlockedStimulusTests(unittest.TestCase):
    def setUp(self):
        self.rows = synthetic_fixture(participants=5, clips=8)
        self.blocks = film_blocks()

    def test_rectangular_complement_has_no_subject_or_film_leakage(self):
        partitions = list(blocked_joint_disjoint_splits(
            self.rows, self.blocks))
        self.assertEqual(len(partitions), 10)
        covered = []
        for train_i, test_i, excluded_i in partitions:
            self.assertEqual((len(train_i), len(test_i),
                              len(excluded_i)), (16, 4, 20))
            self.assertEqual(
                set(train_i) | set(test_i) | set(excluded_i),
                set(range(40)))
            self.assertFalse(set(train_i) & set(test_i))
            self.assertFalse(set(train_i) & set(excluded_i))
            self.assertFalse(set(test_i) & set(excluded_i))
            train, test = ([self.rows[i] for i in group]
                           for group in (train_i, test_i))
            self.assertTrue({r.participant for r in train}.isdisjoint(
                {r.participant for r in test}))
            self.assertTrue({r.stimulus for r in train}.isdisjoint(
                {r.stimulus for r in test}))
            covered.extend(test_i)
        self.assertEqual(sorted(covered), list(range(40)))

    def test_multi_film_folds_make_ccc_mathematically_evaluable(self):
        report = audit_blocked_stimulus_control(self.rows, self.blocks)
        self.assertEqual(report["fold_count"], 10)
        self.assertEqual(report["min_test_trials_per_fold"], 4)
        self.assertEqual(report["max_test_trials_per_fold"], 4)
        self.assertEqual(
            report["ccc_mathematically_defined_folds_for_constant_prior"], 10)
        self.assertEqual(report["ccc_undefined_folds_for_constant_prior"], 0)
        self.assertEqual(report["test_trials_total"], 40)
        self.assertTrue(report["each_trial_tested_exactly_once"])
        self.assertFalse(report["fold_scores_independent_for_inference"])
        self.assertIsNone(report["confidence_interval"])

    def test_constant_subject_ratings_report_undefined_ccc(self):
        rows = list(self.rows)
        for i, row in enumerate(rows):
            if (row.participant == "synthetic-p00" and
                    row.stimulus in self.blocks[0]):
                rows[i] = replace(row, valence=4.0)
        report = audit_blocked_stimulus_control(rows, self.blocks)
        self.assertEqual(report["ccc_undefined_folds_for_constant_prior"], 1)
        self.assertEqual(
            report["ccc_mathematically_defined_folds_for_constant_prior"], 9)

    def test_28_video_facedsized_example_is_not_a_frozen_partition(self):
        rows = synthetic_fixture(participants=4, clips=28)
        blocks = film_blocks(28, 4)
        report = audit_blocked_stimulus_control(rows, blocks)
        self.assertEqual(report["film_block_count"], 7)
        self.assertEqual(report["fold_count"], 28)
        self.assertEqual(report["test_trials_total"], 112)
        self.assertFalse(report["protocol_frozen"])
        self.assertFalse(report["real_eeg_used"])

    def test_noncontiguous_block_ids_accepted_without_label_selection(self):
        blocks = [
            ("synthetic-film00", "synthetic-film02", "synthetic-film04",
             "synthetic-film06"),
            ("synthetic-film01", "synthetic-film03", "synthetic-film05",
             "synthetic-film07"),
        ]
        report = audit_blocked_stimulus_control(self.rows, blocks)
        self.assertEqual(report["fold_count"], 10)
        self.assertTrue(report["block_assignment_outcome_free"])

    def test_partial_subject_film_block_allowed_only_with_two_trials(self):
        rows = [r for r in self.rows
                if not (r.participant == "synthetic-p00"
                        and r.stimulus == "synthetic-film01")]
        report = audit_blocked_stimulus_control(rows, self.blocks)
        self.assertEqual(report["test_trials_total"], 39)
        self.assertEqual(report["min_test_trials_per_fold"], 3)

        missing = [r for r in rows
                   if not (r.participant == "synthetic-p00" and
                           r.stimulus in ("synthetic-film02",
                                         "synthetic-film03"))]
        with self.assertRaisesRegex(ValueError, "two independent ratings"):
            list(blocked_joint_disjoint_splits(missing, self.blocks))

    def test_overlap_unknown_omission_singletons_and_duplicates_rejected(self):
        malformed = [
            [],
            [self.blocks[0]],
            [self.blocks[0], self.blocks[0]],
            [self.blocks[0], self.blocks[1][:-1]],
            [self.blocks[0], (*self.blocks[1], "unknown")],
            [self.blocks[0], (self.blocks[1][0],)],
            [("synthetic-film00", "synthetic-film00"), self.blocks[1]],
            ["synthetic-film00", self.blocks[1]],
            [[*self.blocks[0], None], self.blocks[1]],
        ]
        for bad in malformed:
            with self.subTest(bad=str(bad)), self.assertRaises(ValueError):
                list(blocked_joint_disjoint_splits(self.rows, bad))

    def test_block_assignment_remains_fixed_when_heldout_valence_changes(self):
        from arc_affective.p01_stimulus_control import _train_mean
        train_i, test_i, excluded_i = next(
            blocked_joint_disjoint_splits(self.rows, self.blocks))
        old_train_mean = _train_mean([self.rows[i] for i in train_i])
        adjusted = list(self.rows)
        for i in test_i:
            adjusted[i] = replace(adjusted[i], valence=7 - adjusted[i].valence)
        revised = next(blocked_joint_disjoint_splits(adjusted, self.blocks))
        self.assertEqual((train_i, test_i, excluded_i), revised)
        self.assertEqual(
            _train_mean([adjusted[i] for i in train_i]), old_train_mean)

    def test_aggregate_does_not_export_subject_or_film_identifiers(self):
        report = audit_blocked_stimulus_control(self.rows, self.blocks)
        self.assertNotIn("synthetic-p", str(report))
        self.assertNotIn("synthetic-film", str(report))
        self.assertFalse(report["participant_ids_exported"])
        self.assertFalse(report["stimulus_ids_exported"])
        self.assertFalse(report["confirmatory_inference_authorized"])
        self.assertFalse(report["model_input_eeg"])


if __name__ == "__main__":
    unittest.main()
