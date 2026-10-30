"""P01 synthetic-only negative controls and feature sensitivity.

This software tests whether grouped evaluation and trial-label permutation
work as specified. It does not implement clinical EEG decoding.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import replace
import json
import random
from typing import Sequence

from .p01_evaluation import (
    EVIDENCE, Observation, brier, evaluate, fit_linear, grouped_loso,
    synthetic_fixture, trial_predictions, tune_alpha,
)


def permute_training_trials(
    rows: Sequence[Observation], seed: int,
) -> list[Observation]:
    """Shuffle labels over complete trials *within* training participants.

    Preserves class prevalence per participant and the original window/trial
    correspondence. This function does not accept held-out observations from
    an outer fold: callers must supply only the training partition.
    """
    if type(seed) is not int or not rows:
        raise ValueError("Seed must be integer and training rows nonempty")
    by_subject: dict[str, dict[str, int]] = defaultdict(dict)
    for row in rows:
        if not isinstance(row, Observation):
            raise ValueError("Expected Observation")
        row.validate()
        trials = by_subject[row.participant]
        if row.trial in trials and trials[row.trial] != row.label:
            raise ValueError("Conflicting labels within a trial")
        trials[row.trial] = row.label
    rng = random.Random(seed)
    reassigned = {}
    for participant in sorted(by_subject):
        trial_labels = by_subject[participant]
        trial_keys = sorted(trial_labels)
        labels = [trial_labels[key] for key in trial_keys]
        rng.shuffle(labels)
        reassigned.update({
            (participant, key): label
            for key, label in zip(trial_keys, labels)
        })
    return [
        replace(row, label=reassigned[(row.participant, row.trial)])
        for row in rows
    ]


def negative_control(
    rows: Sequence[Observation], seed: int = 7,
) -> dict:
    """Outer test labels are untouched; only fold-local training is shuffled."""
    if type(seed) is not int:
        raise ValueError("Seed must be integer")
    rows = list(rows)
    folds = []
    for ordinal, (train_ids, test_ids) in enumerate(grouped_loso(rows), 1):
        train = [rows[i] for i in train_ids]
        test = [rows[i] for i in test_ids]
        shuffled = permute_training_trials(train, seed + ordinal)
        # Even hyperparameter selection sees only the permuted train fold.
        selected_alpha = tune_alpha(shuffled)
        fitted = fit_linear(shuffled, selected_alpha)
        labels, probabilities = trial_predictions(
            test, [fitted.predict(row.features) for row in test]
        )
        folds.append({
            "fold": ordinal,
            "test_trials": len(labels),
            "test_windows": len(test),
            "brier": brier(labels, probabilities),
            "alpha_from_permuted_train": selected_alpha,
        })
    return {
        "evidence": EVIDENCE,
        "control": "within_subject_training_trial_label_permutation",
        "train_only_shuffle": True,
        "outer_test_labels_untouched": True,
        "participants": len(folds),
        "mean_participant_brier": sum(f["brier"] for f in folds) / len(folds),
        "folds": folds,
        "p_value": None,
        "validity_of_neural_inference": "not_evaluated",
    }


def feature_sensitivity(rows: Sequence[Observation]) -> dict:
    """Report all leave-one-feature-out cases; never pick a test-set winner.

    Input is an abstract feature matrix, NOT physical EEG electrodes.
    """
    rows = list(rows)
    list(grouped_loso(rows))  # Validate complete and synthetic-only input.
    width = len(rows[0].features)
    if width < 2 or width > 16:
        raise ValueError("Feature sensitivity expects 2 to 16 features")
    variants = [("all", tuple(range(width)))]
    variants += [
        (f"omit_feature_{i}", tuple(j for j in range(width) if j != i))
        for i in range(width)
    ]
    cases = []
    for name, kept in variants:
        adjusted = [replace(row, features=tuple(row.features[j] for j in kept))
                    for row in rows]
        result = evaluate(adjusted)
        cases.append({
            "case": name,
            "n_features": len(kept),
            "participant_count": result["participants"],
            "mean_participant_brier": result["mean_participant_linear_brier"],
            "mean_participant_balanced_accuracy":
                result["mean_participant_linear_balanced_accuracy"],
        })
    return {
        "evidence": EVIDENCE,
        "analysis": "synthetic_leave_one_feature_out",
        "all_candidates_reported": True,
        "test_driven_model_selection_permitted": False,
        "features_are_not_electrode_montages": True,
        "cases": cases,
    }


def experiment(seed: int = 7, subjects: int = 5, trials: int = 4) -> dict:
    if type(seed) is not int:
        raise ValueError("Seed must be integer")
    rows = synthetic_fixture(subjects=subjects, trials=trials, seed=seed)
    return {
        "schema_version": 1,
        "evidence": EVIDENCE,
        "real_eeg_used": False,
        "external_validation": False,
        "rights_verified": False,
        "participant_level_claims": False,
        "seed": seed,
        "reference": evaluate(rows),
        "permutation": negative_control(rows, seed=seed),
        "feature_sensitivity": feature_sensitivity(rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--subjects", type=int, default=5)
    parser.add_argument("--trials", type=int, default=4)
    args = parser.parse_args()
    print(json.dumps(
        experiment(args.seed, args.subjects, args.trials),
        sort_keys=True, indent=2, allow_nan=False
    ))


if __name__ == "__main__":
    main()
