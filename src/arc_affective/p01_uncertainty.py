"""P01 paired participant-level bootstrap, without window pseudoreplication.

This estimates uncertainty over independent subject units, not over epochs.
Functions are independent of EEG acquisition and make no population claims.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
import random
from typing import Sequence

EVIDENCE = "E0_synthetic_software_test_only"


@dataclass(frozen=True)
class SubjectPair:
    """One participant's trial-aggregated Brier scores for two models."""

    participant: str
    reference_brier: float
    candidate_brier: float

    def validate(self) -> None:
        if not isinstance(self.participant, str) or not self.participant.strip():
            raise ValueError("Participant key must be nonempty")
        for score in (self.reference_brier, self.candidate_brier):
            if (type(score) not in (int, float) or not math.isfinite(score)
                    or not 0 <= score <= 1):
                raise ValueError("Brier scores must be finite within [0, 1]")


def _percentile(values: Sequence[float], q: float) -> float:
    """Type-7 linearly interpolated empirical percentile."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    return (ordered[lower] +
            (position - lower) * (ordered[upper] - ordered[lower]))


def paired_subject_interval(
    pairs: Sequence[SubjectPair], *, confidence: float = 0.95,
    resamples: int = 2000, seed: int = 7,
) -> dict:
    """Paired percentile bootstrap by subject, preserving model pairing.

    A positive difference means candidate Brier is lower (better).
    Test/participant-level samples must be independent; the caller must
    aggregate all window predictions to labelled trials beforehand.
    """
    pairs = tuple(pairs)
    if len(pairs) < 4:
        raise ValueError("At least four independent participants required")
    if any(not isinstance(pair, SubjectPair) for pair in pairs):
        raise ValueError("Expected SubjectPair records")
    for pair in pairs:
        pair.validate()
    ids = [pair.participant for pair in pairs]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate participant cluster")
    if type(confidence) not in (float, int) or not 0 < confidence < 1:
        raise ValueError("Confidence must be strictly between zero and one")
    if type(resamples) is not int or not 200 <= resamples <= 100000:
        raise ValueError("Resamples must be an integer in [200, 100000]")
    if type(seed) is not int:
        raise ValueError("Seed must be an integer")
    differences = [pair.reference_brier - pair.candidate_brier
                   for pair in pairs]
    size = len(differences)
    observed = sum(differences) / size
    rng = random.Random(seed)
    samples = [sum(differences[rng.randrange(size)] for _ in range(size)) / size
               for _ in range(resamples)]
    tail = (1 - confidence) / 2
    return {
        "method": "paired_participant_percentile_bootstrap",
        "metric": "reference_brier_minus_candidate_brier",
        "positive_means_candidate_better": True,
        "statistical_unit": "independent_participant",
        "participants": size,
        "confidence_level": confidence,
        "resamples": resamples,
        "seed": seed,
        "mean_delta": observed,
        "interval_lower": _percentile(samples, tail),
        "interval_upper": _percentile(samples, 1 - tail),
        "participant_identifiers_exported": False,
        "multiple_testing_adjustment": "not_applied",
    }


def synthetic_demo() -> dict:
    """Validate statistical plumbing only. Never interpret as EEG findings."""
    from .p01_evaluation import evaluate, synthetic_fixture

    evaluation = evaluate(synthetic_fixture(subjects=6, trials=8, seed=7))
    records = [
        SubjectPair(
            participant=f"fold-{fold['fold']}",
            reference_brier=fold["majority_brier"],
            candidate_brier=fold["linear_brier"],
        )
        for fold in evaluation["folds"]
    ]
    return {
        "evidence": EVIDENCE,
        "real_eeg_used": False,
        "dataset_licence_verified": False,
        "clinical_inference": False,
        "result": paired_subject_interval(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(synthetic_demo(), sort_keys=True, indent=2,
                     allow_nan=False))


if __name__ == "__main__":
    main()
