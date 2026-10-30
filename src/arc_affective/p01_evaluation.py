"""P01: leakage-resistant, grouped baseline evaluation on synthetic features only.

No EEG recordings, real participants, clinical inference or dataset access.
Research-grade outer validation requires separately approved original data,
pre-registered targets and corpus-appropriate metadata.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
import random
from typing import Sequence

ALPHAS = (0.01, 0.1, 1.0)
EVIDENCE = "E0_synthetic_software_test_only"


@dataclass(frozen=True)
class Observation:
    participant: str
    trial: str
    features: tuple[float, ...]
    label: int
    synthetic: bool = True

    def validate(self) -> None:
        if not self.participant or not isinstance(self.participant, str):
            raise ValueError("Participant key required")
        if not self.trial or not isinstance(self.trial, str):
            raise ValueError("Trial key required")
        if type(self.synthetic) is not bool or not self.synthetic:
            raise ValueError("Only synthetic fixtures are accepted")
        if type(self.label) is not int or self.label not in (0, 1):
            raise ValueError("Binary target must be explicitly 0/1")
        if not isinstance(self.features, tuple) or not self.features:
            raise ValueError("Numeric features must be a nonempty tuple")
        if any(type(x) not in (float, int) or not math.isfinite(x)
               for x in self.features):
            raise ValueError("Features must be finite real values")


def validate_rows(rows: Sequence[Observation]) -> None:
    if not rows:
        raise ValueError("No observations")
    if any(not isinstance(row, Observation) for row in rows):
        raise ValueError("Expected Observation objects")
    width = len(rows[0].features)
    for row in rows:
        row.validate()
        if len(row.features) != width:
            raise ValueError("Inconsistent feature dimensions")
    if len({row.participant for row in rows}) < 4:
        raise ValueError("At least four synthetic participants required")
    # One trial is never permitted to represent conflicting labels.
    seen = {}
    for row in rows:
        key = (row.participant, row.trial)
        if key in seen and seen[key] != row.label:
            raise ValueError("Conflicting labels in a trial")
        seen[key] = row.label
    if len({row.label for row in rows}) != 2:
        raise ValueError("Both classes are required")


def grouped_loso(rows: Sequence[Observation]):
    """Deterministic partitions; subject+trial never straddle a split."""
    validate_rows(rows)
    for participant in sorted({row.participant for row in rows}):
        train = tuple(i for i, row in enumerate(rows)
                      if row.participant != participant)
        test = tuple(i for i, row in enumerate(rows)
                     if row.participant == participant)
        assert train and test and not (set(train) & set(test))
        yield train, test


def sigmoid(z: float) -> float:
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    exponent = math.exp(z)
    return exponent / (1.0 + exponent)


@dataclass(frozen=True)
class LinearBaseline:
    means: tuple[float, ...]
    scales: tuple[float, ...]
    weights: tuple[float, ...]
    intercept: float

    def predict(self, x: tuple[float, ...]) -> float:
        if len(x) != len(self.means):
            raise ValueError("Feature dimension mismatch")
        if any(type(v) not in (int, float) or not math.isfinite(v) for v in x):
            raise ValueError("Nonfinite or nonnumeric features")
        z = self.intercept + sum(
            w * ((v - m) / s)
            for v, m, s, w in zip(x, self.means, self.scales, self.weights)
        )
        return sigmoid(z)


def trial_weights(rows: Sequence[Observation]) -> list[float]:
    """Each (participant, trial) contributes equal total training weight."""
    counts: dict[tuple[str, str], int] = {}
    for row in rows:
        key = (row.participant, row.trial)
        counts[key] = counts.get(key, 0) + 1
    n_trials = len(counts)
    if not n_trials:
        raise ValueError("Cannot weight an empty training set")
    return [1.0 / (n_trials * counts[(row.participant, row.trial)])
            for row in rows]


def trial_predictions(rows: Sequence[Observation],
                      probabilities: Sequence[float]):
    """Collapse windows into one prediction per participant and labelled trial."""
    if not rows or len(rows) != len(probabilities):
        raise ValueError("Aligned, nonempty trial predictions required")
    grouped: dict[tuple[str, str], tuple[int, list[float]]] = {}
    for row, probability in zip(rows, probabilities):
        if type(probability) not in (float, int) or not math.isfinite(probability):
            raise ValueError("Nonfinite trial probability")
        if not 0 <= probability <= 1:
            raise ValueError("Probability outside [0,1]")
        key = (row.participant, row.trial)
        if key not in grouped:
            grouped[key] = (row.label, [])
        label, values = grouped[key]
        if label != row.label:
            raise ValueError("Conflicting trial labels")
        values.append(probability)
    return ([label for label, _ in grouped.values()],
            [sum(values) / len(values) for _, values in grouped.values()])


def fit_linear(rows: Sequence[Observation], alpha: float) -> LinearBaseline:
    """Train-only z-score and L2 logistic model, deterministic batch gradient."""
    if not rows or type(alpha) not in (float, int) or not 0 < alpha <= 1:
        raise ValueError("Nonempty train and alpha in (0,1] required")
    for row in rows:
        row.validate()
    d = len(rows[0].features)
    if any(len(row.features) != d for row in rows):
        raise ValueError("Different dimensions")
    weights_for_rows = trial_weights(rows)
    means = tuple(sum(weight * row.features[j]
                      for weight, row in zip(weights_for_rows, rows))
                  for j in range(d))
    scales = tuple(max(
        math.sqrt(sum(weight * (row.features[j] - means[j]) ** 2
                      for weight, row in zip(weights_for_rows, rows))), 1e-10
    ) for j in range(d))
    xs = [tuple((row.features[j] - means[j]) / scales[j]
                for j in range(d)) for row in rows]
    weights = [0.0] * d
    intercept = 0.0
    for _ in range(300):
        dw = [0.0] * d
        db = 0.0
        for x, row, weight in zip(xs, rows, weights_for_rows):
            residual = sigmoid(intercept + sum(w * v for w, v in zip(weights, x))) - row.label
            db += weight * residual
            for j in range(d):
                dw[j] += weight * residual * x[j]
        for j in range(d):
            weights[j] -= 0.12 * (dw[j] + alpha * weights[j])
        intercept -= 0.12 * db
    return LinearBaseline(means, scales, tuple(weights), intercept)


def brier(labels: Sequence[int], probabilities: Sequence[float]) -> float:
    if not labels or len(labels) != len(probabilities):
        raise ValueError("Aligned nonempty predictions required")
    return sum((p - y) ** 2 for y, p in zip(labels, probabilities)) / len(labels)


def balanced_accuracy(labels: Sequence[int], probabilities: Sequence[float]):
    """Return None when a held-out participant contains only one class."""
    if not {0, 1}.issubset(set(labels)):
        return None
    return sum(
        sum((int(p >= 0.5) == cls)
            for y, p in zip(labels, probabilities) if y == cls)
        / sum(y == cls for y in labels)
        for cls in (0, 1)
    ) / 2


def tune_alpha(rows: Sequence[Observation]) -> float:
    """Inner participant-held-out selection uses only the OUTER training set."""
    participants = sorted({row.participant for row in rows})
    if len(participants) < 2:
        raise ValueError("Inner CV needs at least two training participants")
    scores = []
    for alpha in ALPHAS:
        fold_scores = []
        for participant in participants:
            tr = [r for r in rows if r.participant != participant]
            te = [r for r in rows if r.participant == participant]
            fitted = fit_linear(tr, alpha)
            labels, probabilities = trial_predictions(
                te, [fitted.predict(r.features) for r in te])
            fold_scores.append(brier(labels, probabilities))
        scores.append((sum(fold_scores) / len(fold_scores), alpha))
    return min(scores)[1]


def evaluate(rows: Sequence[Observation]) -> dict:
    """Outer LOSO; returns only nonidentifying aggregate and ordinal fold metrics."""
    rows = list(rows)
    folds = list(grouped_loso(rows))
    per_fold = []
    for fold_index, (train_ids, test_ids) in enumerate(folds, 1):
        train = [rows[i] for i in train_ids]
        test = [rows[i] for i in test_ids]
        # Nested selection is strictly restricted to outer-training people.
        alpha = tune_alpha(train)
        model = fit_linear(train, alpha)
        train_labels, _ = trial_predictions(
            train, [float(row.label) for row in train])
        prior = sum(train_labels) / len(train_labels)
        labels, probs = trial_predictions(
            test, [model.predict(row.features) for row in test])
        baseline = [prior] * len(labels)
        per_fold.append({
            "fold": fold_index, "test_trials": len(labels),
            "test_windows": len(test), "training_participants": len({
                r.participant for r in train}),
            "alpha_from_inner_cv": alpha,
            "linear_brier": brier(labels, probs),
            "majority_brier": brier(labels, baseline),
            "linear_balanced_accuracy": balanced_accuracy(labels, probs),
            "majority_balanced_accuracy": balanced_accuracy(labels, baseline),
        })
    def average(key):
        values = [f[key] for f in per_fold if f[key] is not None]
        return sum(values) / len(values) if values else None
    return {
        "schema_version": 1, "evidence": EVIDENCE,
        "real_eeg_used": False, "external_validation": False,
        "recording_rights_verified": False, "protocol_frozen": False,
        "statistical_unit": "synthetic_participant",
        "score_unit": "trial_means_within_participant",
        "train_weight_unit": "participant_trial",
        "participants": len(folds), "windows": len(rows),
        "baseline": "train_only_prevalence",
        "model": "train_only_standardized_l2_logistic",
        "selection": "nested_group_loso_brier",
        "balanced_accuracy_folds_evaluable": sum(
            f["linear_balanced_accuracy"] is not None for f in per_fold),
        "mean_participant_linear_brier": average("linear_brier"),
        "mean_participant_majority_brier": average("majority_brier"),
        "mean_participant_linear_balanced_accuracy": average("linear_balanced_accuracy"),
        "mean_participant_majority_balanced_accuracy": average("majority_balanced_accuracy"),
        "folds": per_fold,
        "confidence_intervals": None,
    }


def synthetic_fixture(subjects: int = 6, trials: int = 8, seed: int = 7):
    if type(subjects) is not int or type(trials) is not int or subjects < 4 or trials < 2:
        raise ValueError("Need >=4 subjects and >=2 trials")
    rng = random.Random(seed)
    rows = []
    for s in range(subjects):
        offset = rng.uniform(-0.4, 0.4)
        for trial in range(trials):
            label = (trial + s) % 2
            for window in range(2):
                rows.append(Observation(
                    participant=f"synthetic-{s:03d}", trial=f"trial-{trial:03d}",
                    features=(label * 0.7 + offset + rng.gauss(0, 0.25),
                              rng.gauss(0, 1.0) + offset,
                              float(s % 3) + rng.gauss(0, 0.1)),
                    label=label,
                ))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subjects", type=int, default=6)
    parser.add_argument("--trials", type=int, default=8)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate(synthetic_fixture(args.subjects, args.trials, args.seed))
    serialized = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        if args.output.exists():
            parser.error("Refusing to overwrite existing report")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
