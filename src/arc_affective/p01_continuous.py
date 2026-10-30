"""P01 synthetic continuous-valence LOSO, not empirical EEG inference.

Prospective candidate A: continuous 0-7 trial self-report. No actual corpus
import is allowed through this software-only test module.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
import random
from typing import Sequence

ALPHAS = (0.01, 0.1, 1.0)
EVIDENCE = "E0_synthetic_software_test_only"


@dataclass(frozen=True)
class ContinuousRow:
    participant: str
    trial: str
    features: tuple[float, ...]
    valence: float
    synthetic: bool = True

    def validate(self) -> None:
        if not isinstance(self.participant, str) or not self.participant.strip():
            raise ValueError("Participant key required")
        if not isinstance(self.trial, str) or not self.trial.strip():
            raise ValueError("Trial key required")
        if type(self.synthetic) is not bool or not self.synthetic:
            raise ValueError("Only synthetic records permitted")
        if (type(self.valence) not in (float, int)
                or not math.isfinite(self.valence)
                or not 0 <= self.valence <= 7):
            raise ValueError("Continuous self-report must be in [0, 7]")
        if (not isinstance(self.features, tuple) or not self.features
                or any(type(x) not in (int, float) or not math.isfinite(x)
                       for x in self.features)):
            raise ValueError("Features must be finite numeric tuple")


def validate_rows(rows: Sequence[ContinuousRow]) -> None:
    if not rows or any(not isinstance(r, ContinuousRow) for r in rows):
        raise ValueError("Nonempty ContinuousRow sequence required")
    width = len(rows[0].features)
    subjects: dict[str, dict[str, float]] = {}
    for row in rows:
        row.validate()
        if len(row.features) != width:
            raise ValueError("Feature dimension mismatch")
        trials = subjects.setdefault(row.participant, {})
        if row.trial in trials and not math.isclose(
                trials[row.trial], row.valence, rel_tol=0, abs_tol=1e-12):
            raise ValueError("Conflicting self-report within a trial")
        trials[row.trial] = row.valence
    if len(subjects) < 4 or any(len(trials) < 2 for trials in subjects.values()):
        raise ValueError("At least four participants with two trials each required")


def grouped_loso(rows: Sequence[ContinuousRow]):
    """Every outer fold excludes a complete participant."""
    validate_rows(rows)
    for subject in sorted({r.participant for r in rows}):
        train = tuple(i for i, r in enumerate(rows) if r.participant != subject)
        test = tuple(i for i, r in enumerate(rows) if r.participant == subject)
        yield train, test


def training_weights(rows: Sequence[ContinuousRow]) -> list[float]:
    """Equal per-participant, per-trial, per-window total contribution."""
    if not rows:
        raise ValueError("No training observations")
    counts: dict[str, dict[str, int]] = {}
    for row in rows:
        trials = counts.setdefault(row.participant, {})
        trials[row.trial] = trials.get(row.trial, 0) + 1
    n_subjects = len(counts)
    return [
        1.0 / (n_subjects * len(counts[r.participant])
               * counts[r.participant][r.trial])
        for r in rows
    ]


def trial_predictions(rows: Sequence[ContinuousRow],
                      predictions: Sequence[float]):
    """Mean window prediction per (participant, trial), in insertion order."""
    if not rows or len(rows) != len(predictions):
        raise ValueError("Aligned nonempty rows and predictions required")
    by_trial: dict[tuple[str, str], tuple[float, list[float]]] = {}
    for row, pred in zip(rows, predictions):
        row.validate()
        if type(pred) not in (int, float) or not math.isfinite(pred):
            raise ValueError("Nonfinite regression prediction")
        key = (row.participant, row.trial)
        if key not in by_trial:
            by_trial[key] = (row.valence, [])
        target, values = by_trial[key]
        if not math.isclose(target, row.valence, rel_tol=0, abs_tol=1e-12):
            raise ValueError("Conflicting trial targets")
        values.append(pred)
    return ([target for target, _ in by_trial.values()],
            [sum(vals) / len(vals) for _, vals in by_trial.values()])


@dataclass(frozen=True)
class RidgeModel:
    means: tuple[float, ...]
    scales: tuple[float, ...]
    coefficients: tuple[float, ...]
    intercept: float

    def predict(self, features: tuple[float, ...]) -> float:
        if len(features) != len(self.means):
            raise ValueError("Feature dimension mismatch")
        if any(type(x) not in (int, float) or not math.isfinite(x)
               for x in features):
            raise ValueError("Nonfinite prediction feature")
        return self.intercept + sum(
            c * (x - m) / s
            for x, m, s, c in zip(features, self.means,
                                  self.scales, self.coefficients)
        )


def fit_ridge(rows: Sequence[ContinuousRow], alpha: float) -> RidgeModel:
    """Deterministic, trial/subject-weighted standardized L2 ridge baseline."""
    if not rows or type(alpha) not in (int, float) or not 0 < alpha <= 1:
        raise ValueError("Nonempty train and alpha in (0, 1] required")
    for row in rows:
        row.validate()
    d = len(rows[0].features)
    if any(len(row.features) != d for row in rows):
        raise ValueError("Feature dimension mismatch")
    weights = training_weights(rows)
    means = tuple(sum(w * row.features[j]
                      for row, w in zip(rows, weights)) for j in range(d))
    scales = tuple(max(
        math.sqrt(sum(w * (r.features[j] - means[j]) ** 2
                      for r, w in zip(rows, weights))), 1e-10
    ) for j in range(d))
    xs = [tuple((r.features[j] - means[j]) / scales[j]
                for j in range(d)) for r in rows]
    intercept = sum(w * r.valence for r, w in zip(rows, weights))
    coefficients = [0.0] * d
    for _ in range(450):
        gradient = [0.0] * d
        for x, row, weight in zip(xs, rows, weights):
            error = intercept + sum(c * value for c, value
                                    in zip(coefficients, x)) - row.valence
            for j in range(d):
                gradient[j] += weight * error * x[j]
        for j in range(d):
            coefficients[j] -= 0.1 * (gradient[j] + alpha * coefficients[j])
    return RidgeModel(means, scales, tuple(coefficients), intercept)


def concordance(y_true: Sequence[float],
                y_pred: Sequence[float]) -> float | None:
    """Lin CCC = 2cov/(var_true + var_pred + mean_diff squared).

    One or zero trials, or a constant true target, yield undefined CCC.
    Constant predictions with varying true targets legitimately give CCC=0.
    """
    if not y_true or len(y_true) != len(y_pred):
        raise ValueError("Aligned nonempty targets required")
    if any(type(x) not in (int, float) or not math.isfinite(x)
           for x in (*y_true, *y_pred)):
        raise ValueError("CCC expects finite real values")
    if len(y_true) < 2:
        return None
    n = len(y_true)
    mean_y = sum(y_true) / n
    mean_p = sum(y_pred) / n
    var_y = sum((y - mean_y) ** 2 for y in y_true) / n
    var_p = sum((p - mean_p) ** 2 for p in y_pred) / n
    if var_y <= 1e-12:
        return None
    cov = sum((y - mean_y) * (p - mean_p)
              for y, p in zip(y_true, y_pred)) / n
    return 2 * cov / (var_y + var_p + (mean_y - mean_p) ** 2)


def mse(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    if not y_true or len(y_true) != len(y_pred):
        raise ValueError("Aligned nonempty predictions required")
    if any(type(x) not in (int, float) or not math.isfinite(x)
           for x in (*y_true, *y_pred)):
        raise ValueError("Nonfinite MSE input")
    return sum((y - p) ** 2 for y, p in zip(y_true, y_pred)) / len(y_true)


def choose_alpha(rows: Sequence[ContinuousRow]) -> float:
    """Nested grouped inner validation; select via held-out subject-level MSE.

    CCC is *not* optimized in inner folds because it can be undefined for
    constant-target subjects. Inner selection never observes outer test rows.
    """
    subjects = sorted({row.participant for row in rows})
    if len(subjects) < 2:
        raise ValueError("Inner subject CV needs >=2 subjects")
    ranking = []
    for alpha in ALPHAS:
        scores = []
        for subject in subjects:
            train = [r for r in rows if r.participant != subject]
            test = [r for r in rows if r.participant == subject]
            model = fit_ridge(train, alpha)
            y, p = trial_predictions(
                test, [model.predict(r.features) for r in test])
            scores.append(mse(y, p))
        ranking.append((sum(scores) / len(scores), alpha))
    return min(ranking)[1]


def evaluate(rows: Sequence[ContinuousRow]) -> dict:
    """Outer participant LOSO; no per-trial targets or identity exported."""
    rows = list(rows)
    folds = []
    for index, (train_i, test_i) in enumerate(grouped_loso(rows), 1):
        train = [rows[i] for i in train_i]
        test = [rows[i] for i in test_i]
        alpha = choose_alpha(train)
        model = fit_ridge(train, alpha)
        prior_weights = training_weights(train)
        train_mean = sum(r.valence * w for r, w in zip(train, prior_weights))
        y, pred = trial_predictions(
            test, [model.predict(r.features) for r in test])
        comparison = [train_mean] * len(y)
        folds.append({
            "fold": index,
            "test_trials": len(y),
            "test_windows": len(test),
            "alpha_from_inner_mse": alpha,
            "ridge_mse": mse(y, pred),
            "train_mean_mse": mse(y, comparison),
            "ridge_ccc": concordance(y, pred),
            "train_mean_ccc": concordance(y, comparison),
            "ridge_out_of_range_trials": sum(p < 0 or p > 7 for p in pred),
        })
    def mean(key):
        valid = [f[key] for f in folds if f[key] is not None]
        return sum(valid) / len(valid) if valid else None
    return {
        "schema_version": 1,
        "evidence": EVIDENCE,
        "real_eeg_used": False,
        "protocol_frozen": False,
        "external_validation": False,
        "original_rating_alignment_verified": False,
        "recording_rights_verified": False,
        "target": "synthetic_continuous_valence_0_7",
        "selection": "nested_group_loso_subject_mean_mse",
        "statistical_unit": "synthetic_participant",
        "prediction_unit": "trial_mean_of_window_predictions",
        "train_weighting": "equal_participant_trial_window",
        "participants": len(folds),
        "ccc_folds_evaluable": sum(f["ridge_ccc"] is not None for f in folds),
        "mean_participant_ridge_ccc": mean("ridge_ccc"),
        "mean_participant_train_mean_ccc": mean("train_mean_ccc"),
        "mean_participant_ridge_mse": mean("ridge_mse"),
        "mean_participant_train_mean_mse": mean("train_mean_mse"),
        "confidence_intervals": None,
        "folds": folds,
    }


def synthetic_fixture(subjects: int = 5, trials: int = 5, seed: int = 7):
    if (type(subjects) is not int or type(trials) is not int
            or type(seed) is not int or subjects < 4 or trials < 2):
        raise ValueError("At least four synthetic participants and two trials")
    rng = random.Random(seed)
    rows = []
    for s in range(subjects):
        offset = rng.uniform(-0.4, 0.4)
        for trial in range(trials):
            valence = max(0.0, min(
                7.0, 2.0 + (trial * 0.7) + offset + rng.gauss(0, 0.1)))
            for _ in range(2):
                rows.append(ContinuousRow(
                    participant=f"synthetic-{s:03d}",
                    trial=f"trial-{trial:03d}",
                    features=(
                        valence + rng.gauss(0, 0.4),
                        rng.gauss(0, 1) + offset,
                    ),
                    valence=valence,
                ))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subjects", type=int, default=5)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    print(json.dumps(
        evaluate(synthetic_fixture(args.subjects, args.trials, args.seed)),
        sort_keys=True, indent=2, allow_nan=False,
    ))


if __name__ == "__main__":
    main()
