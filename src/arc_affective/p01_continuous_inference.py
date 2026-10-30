"""Descriptive paired participant-cluster intervals for P01 continuous E0.

Use only with synthetic grouped-LOSO fold reports. This cannot establish
statistical inference for correlated LOSO training sets or actual EEG.
"""
from __future__ import annotations

import argparse
import json
import math
import random
from typing import Sequence

EVIDENCE = "E0_synthetic_software_test_only"
FIELDS = {
    "ccc": ("ridge_ccc", "train_mean_ccc", 1, "candidate_minus_reference"),
    "mse": ("ridge_mse", "train_mean_mse", -1, "reference_minus_candidate"),
}


def _percentile(values: list[float], quantile: float) -> float:
    values = sorted(values)
    location = (len(values) - 1) * quantile
    low = math.floor(location)
    high = math.ceil(location)
    return (values[low] +
            (location - low) * (values[high] - values[low]))


def paired_interval(
    folds: Sequence[dict], *, metric: str, confidence: float = 0.95,
    resamples: int = 2000, seed: int = 7,
) -> dict:
    """Bootstrap paired *whole held-out participant* score differences.

    Positive is better candidate performance. The percentile interval is
    descriptive only: different LOSO folds use overlapping training sets.
    No null-hypothesis p-value and no external generalization are asserted.
    Missing/undefined CCC is a hard blocker for its aggregate interval,
    never silently removed from the resampling population.
    """
    if metric not in FIELDS:
        raise ValueError("Metric must be 'ccc' or 'mse'")
    if not isinstance(folds, (list, tuple)) or len(folds) < 4:
        raise ValueError("At least four participant folds required")
    if (type(confidence) not in (int, float) or not math.isfinite(confidence)
            or not 0 < confidence < 1):
        raise ValueError("Confidence outside (0,1)")
    if type(resamples) is not int or not 200 <= resamples <= 100000:
        raise ValueError("Resamples outside [200,100000]")
    if type(seed) is not int:
        raise ValueError("Seed must be integer")
    candidate_key, baseline_key, direction, label = FIELDS[metric]
    identities = set()
    differences = []
    missing = 0
    for fold in folds:
        if not isinstance(fold, dict) or type(fold.get("fold")) is not int:
            raise ValueError("Expected numbered participant folds")
        ordinal = fold["fold"]
        if ordinal <= 0 or ordinal in identities:
            raise ValueError("Invalid or duplicate participant fold")
        identities.add(ordinal)
        candidate = fold.get(candidate_key)
        baseline = fold.get(baseline_key)
        if candidate is None or baseline is None:
            if metric != "ccc":
                raise ValueError("Missing MSE score")
            missing += 1
            continue
        if any(type(v) not in (float, int) or not math.isfinite(v)
               for v in (candidate, baseline)):
            raise ValueError("Nonfinite or nonnumeric metric")
        if metric == "ccc" and any(not -1.0000000001 <= v <= 1.0000000001
                                   for v in (candidate, baseline)):
            raise ValueError("CCC outside [-1,1]")
        if metric == "mse" and (candidate < 0 or baseline < 0):
            raise ValueError("Negative MSE")
        differences.append(direction * (candidate - baseline))
    head = {
        "metric": metric,
        "direction": label,
        "participants": len(folds),
        "complete_cases": len(differences),
        "undefined_or_missing_participants": missing,
        "statistical_unit": "whole_held_out_participant",
        "method": "paired_subject_percentile_bootstrap",
        "confidence": confidence,
        "resamples": resamples,
        "seed": seed,
        "exported_participant_identifiers": False,
        "confirmatory_inference_validated": False,
        "overlapping_loso_training_dependency_unresolved": True,
        "p_value": None,
    }
    if missing:
        return {
            **head, "status": "blocked_undefined_participant_ccc",
            "mean_difference": None,
            "interval_lower": None, "interval_upper": None,
        }
    n = len(differences)
    observed = sum(differences) / n
    rng = random.Random(seed)
    boot = [
        sum(differences[rng.randrange(n)] for _ in range(n)) / n
        for _ in range(resamples)
    ]
    tail = (1 - confidence) / 2
    return {
        **head,
        "status": "descriptive_interval_only",
        "mean_difference": observed,
        "interval_lower": _percentile(boot, tail),
        "interval_upper": _percentile(boot, 1 - tail),
    }


def synthetic_demo() -> dict:
    from .p01_continuous import evaluate, synthetic_fixture

    evaluation = evaluate(synthetic_fixture(subjects=5, trials=5, seed=7))
    return {
        "evidence": EVIDENCE,
        "real_eeg_used": False,
        "protocol_frozen": False,
        "external_validation": False,
        "rights_verified": False,
        "ccc": paired_interval(evaluation["folds"], metric="ccc"),
        "mse": paired_interval(evaluation["folds"], metric="mse"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(synthetic_demo(), indent=2, sort_keys=True,
                     allow_nan=False))


if __name__ == "__main__":
    main()
