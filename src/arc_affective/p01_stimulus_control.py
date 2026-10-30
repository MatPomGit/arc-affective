"""P01 stimulus-identity confound controls on synthetic FACED-like trial data.

This is E0 software validation only. Participant-held-out evaluation with
repeated videos is NOT validation on previously unseen stimuli.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
from statistics import mean
from typing import Iterator, Sequence

from .p01_continuous import concordance

EVIDENCE = "E0_synthetic_software_test_only"


@dataclass(frozen=True)
class StimulusTrial:
    participant: str
    trial: str
    stimulus: str
    valence: float
    synthetic: bool = True

    def validate(self) -> None:
        for key in (self.participant, self.trial, self.stimulus):
            if type(key) is not str or not key or key.strip() != key:
                raise ValueError("Nonempty trimmed participant/trial/stimulus required")
        if type(self.synthetic) is not bool or not self.synthetic:
            raise ValueError("Only synthetic trials accepted")
        if (type(self.valence) not in (float, int) or
                not math.isfinite(self.valence) or
                not 0 <= self.valence <= 7):
            raise ValueError("Self-reported valence must be finite in [0,7]")


def validate_trials(rows: Sequence[StimulusTrial]) -> None:
    if (not isinstance(rows, (list, tuple)) or not rows or
            any(not isinstance(r, StimulusTrial) for r in rows)):
        raise ValueError("Nonempty synthetic StimulusTrial sequence required")
    participants: dict[str, set[str]] = {}
    seen: set[tuple[str, str]] = set()
    for row in rows:
        row.validate()
        key = (row.participant, row.trial)
        if key in seen:
            raise ValueError("Duplicate trial within participant")
        seen.add(key)
        clips = participants.setdefault(row.participant, set())
        if row.stimulus in clips:
            raise ValueError("Duplicate stimulus within participant")
        clips.add(row.stimulus)
    if len(participants) < 4 or any(len(clips) < 3 for clips in participants.values()):
        raise ValueError("At least four participants with three clips each required")
    if len({r.stimulus for r in rows}) < 3:
        raise ValueError("At least three distinct stimuli required")


def participant_splits(
    rows: Sequence[StimulusTrial],
) -> Iterator[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Whole-participant LOSO, which may retain test clips in train."""
    validate_trials(rows)
    for subject in sorted({r.participant for r in rows}):
        train = tuple(i for i, r in enumerate(rows) if r.participant != subject)
        test = tuple(i for i, r in enumerate(rows) if r.participant == subject)
        yield train, test


def joint_disjoint_splits(
    rows: Sequence[StimulusTrial],
) -> Iterator[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]]:
    """Hold out both a subject and a clip; cross cells are not usable train.

    All rows with the test subject OR the test clip are excluded from training.
    This is an intersection test, not an ordinary subject-only LOSO fold.
    """
    validate_trials(rows)
    for test_index, held_out in enumerate(rows):
        train, test, excluded = [], [], []
        for i, row in enumerate(rows):
            if i == test_index:
                test.append(i)
            elif (row.participant == held_out.participant or
                  row.stimulus == held_out.stimulus):
                excluded.append(i)
            else:
                train.append(i)
        if (len({rows[i].participant for i in train}) < 2 or
                len({rows[i].stimulus for i in train}) < 2):
            raise ValueError("Insufficient subject/clip support for joint fold")
        yield tuple(train), tuple(test), tuple(excluded)


def blocked_joint_disjoint_splits(
    rows: Sequence[StimulusTrial],
    stimulus_blocks: Sequence[Sequence[str]],
) -> Iterator[tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]]:
    """Hold out one participant with a *prespecified group* of unseen films.

    Each fold partitions trials into train, test and excluded cross-cells.
    The block partition must be fixed from external stimulus IDs before any
    held-out outcome is inspected. This does not perform model fitting.
    """
    validate_trials(rows)
    if (not isinstance(stimulus_blocks, (list, tuple))
            or len(stimulus_blocks) < 2):
        raise ValueError("At least two predeclared film blocks required")
    blocks = []
    for block in stimulus_blocks:
        if (not isinstance(block, (list, tuple))
                or len(block) < 2
                or any(type(name) is not str or not name
                       or name.strip() != name for name in block)
                or len(set(block)) != len(block)):
            raise ValueError("Each block needs two or more distinct clip IDs")
        blocks.append(frozenset(block))
    all_names = [name for block in stimulus_blocks for name in block]
    if (len(set(all_names)) != len(all_names)
            or set(all_names) != {r.stimulus for r in rows}):
        raise ValueError("Film blocks must partition all observed clips once")

    for participant in sorted({r.participant for r in rows}):
        for held_block in blocks:
            train, test, excluded = [], [], []
            for index, row in enumerate(rows):
                participant_test = row.participant == participant
                film_test = row.stimulus in held_block
                if participant_test and film_test:
                    test.append(index)
                elif not participant_test and not film_test:
                    train.append(index)
                else:
                    excluded.append(index)
            if len(test) < 2:
                raise ValueError("A test block needs two independent ratings")
            if (len({rows[i].participant for i in train}) < 2
                    or len({rows[i].stimulus for i in train}) < 2):
                raise ValueError("Insufficient independent training support")
            yield tuple(train), tuple(test), tuple(excluded)


def audit_blocked_stimulus_control(
    rows: Sequence[StimulusTrial],
    stimulus_blocks: Sequence[Sequence[str]],
) -> dict:
    """Synthetic train-only prior on multi-video dual-disjoint folds.

    CCC calculability is a mathematical check, not a confirmatory result.
    Nested folds share train subjects/films and are not independent samples.
    """
    rows = tuple(rows)
    # Materialize folds to fail closed before publishing an aggregate report.
    partitions = list(blocked_joint_disjoint_splits(rows, stimulus_blocks))
    per_fold_mse = []
    ccc_defined = 0
    test_sizes = []
    cross_cell_sizes = []
    tested_indices = []
    for train_i, test_i, excluded_i in partitions:
        train = [rows[i] for i in train_i]
        test = [rows[i] for i in test_i]
        test_targets = [r.valence for r in test]
        mean_prior = _train_mean(train)
        predictions = [mean_prior] * len(test_targets)
        per_fold_mse.append(_mse(test_targets, predictions))
        if concordance(test_targets, predictions) is not None:
            ccc_defined += 1
        test_sizes.append(len(test_i))
        cross_cell_sizes.append(len(excluded_i))
        tested_indices.extend(test_i)
    if sorted(tested_indices) != list(range(len(rows))):
        raise ValueError("Each trial must appear once across outer test folds")
    return {
        "schema_version": 1,
        "evidence": EVIDENCE,
        "control": "jointly_held_out_subject_and_multi_film_block",
        "film_block_count": len(stimulus_blocks),
        "held_out_participant_count": len({r.participant for r in rows}),
        "fold_count": len(partitions),
        "test_trials_total": sum(test_sizes),
        "min_test_trials_per_fold": min(test_sizes),
        "max_test_trials_per_fold": max(test_sizes),
        "ccc_mathematically_defined_folds_for_constant_prior": ccc_defined,
        "ccc_undefined_folds_for_constant_prior":
            len(partitions) - ccc_defined,
        "average_train_mean_mse_per_fold": mean(per_fold_mse),
        "mean_excluded_cross_cell_trials": mean(cross_cell_sizes),
        "each_trial_tested_exactly_once": True,
        "participant_disjoint": True,
        "stimulus_disjoint": True,
        "source_of_blocks": "externally_predeclared_stimulus_ID_partition",
        "block_assignment_outcome_free": True,
        "model_input_eeg": False,
        "model_uses_test_labels_for_fit": False,
        "fold_scores_independent_for_inference": False,
        "confidence_interval": None,
        "p_value": None,
        "confirmatory_inference_authorized": False,
        "original_self_report_alignment_verified": False,
        "recording_rights_verified": False,
        "real_eeg_used": False,
        "protocol_frozen": False,
        "participant_ids_exported": False,
        "stimulus_ids_exported": False,
    }


def _train_mean(rows: Sequence[StimulusTrial]) -> float:
    """Equal weight per training participant, not per available trial."""
    by_subject: dict[str, list[float]] = {}
    for row in rows:
        by_subject.setdefault(row.participant, []).append(row.valence)
    if not by_subject:
        raise ValueError("Training fold cannot be empty")
    return mean([mean(ratings) for ratings in by_subject.values()])


def _clip_prior(rows: Sequence[StimulusTrial]) -> dict[str, float]:
    """Train-only mean self-report for each video (no EEG features)."""
    by_clip: dict[str, list[float]] = {}
    for row in rows:
        by_clip.setdefault(row.stimulus, []).append(row.valence)
    return {clip: mean(ratings) for clip, ratings in by_clip.items()}


def _mse(actual: Sequence[float], predicted: Sequence[float]) -> float:
    return mean([(a - p) ** 2 for a, p in zip(actual, predicted)])


def audit_stimulus_confound(rows: Sequence[StimulusTrial]) -> dict:
    """Descriptive software test of identity-only baseline and joint splits.

    No empirical EEG inference, p-value, confidence interval or held-out
    population generalization is supported by this synthetic diagnostic.
    """
    rows = tuple(rows)
    validate_trials(rows)
    mse_clip, mse_mean = [], []
    test_known, test_total = 0, 0
    for train_i, test_i in participant_splits(rows):
        train = [rows[i] for i in train_i]
        test = [rows[i] for i in test_i]
        fallback = _train_mean(train)
        prior = _clip_prior(train)
        y = [r.valence for r in test]
        pred = [prior.get(r.stimulus, fallback) for r in test]
        mse_clip.append(_mse(y, pred))
        mse_mean.append(_mse(y, [fallback] * len(test)))
        test_known += sum(r.stimulus in prior for r in test)
        test_total += len(test)
    joint_mse = []
    excluded_count = 0
    for train_i, test_i, excluded_i in joint_disjoint_splits(rows):
        train = [rows[i] for i in train_i]
        test = [rows[i] for i in test_i]
        # No held-out stimulus identity is available in the training pool.
        joint_mse.append(_mse(
            [r.valence for r in test],
            [_train_mean(train)] * len(test),
        ))
        excluded_count += len(excluded_i)
    return {
        "schema_version": 1,
        "evidence": EVIDENCE,
        "stimulus_id_used_as_predictor": True,
        "participant_loso": {
            "n_participant_folds": len(mse_clip),
            "test_trials_with_stimulus_seen_in_training": test_known,
            "test_trials_total": test_total,
            "mean_participant_stimulus_prior_mse": mean(mse_clip),
            "mean_participant_train_mean_mse": mean(mse_mean),
            "participant_disjoint": True,
            "stimulus_disjoint": test_known == 0,
        },
        "participant_and_stimulus_disjoint": {
            "n_intersection_folds": len(joint_mse),
            "mean_fold_train_mean_mse": mean(joint_mse),
            "mean_cross_cell_rows_excluded": excluded_count / len(joint_mse),
            "participant_disjoint": True,
            "stimulus_disjoint": True,
            "single_trial_per_intersection": True,
            "ccc_defined_per_intersection": False,
        },
        "rating_source": "synthetic_continuous_self_report_0_7",
        "model_inputs_eeg": False,
        "validates_generalization_of_eeg": False,
        "real_eeg_used": False,
        "protocol_frozen": False,
        "statistical_inference_authorized": False,
        "p_value": None,
        "confidence_interval": None,
        "participant_ids_exported": False,
        "stimulus_ids_exported": False,
    }


def synthetic_fixture(
    participants: int = 5, clips: int = 4,
) -> list[StimulusTrial]:
    if (type(participants) is not int or participants < 4 or
            type(clips) is not int or clips < 3):
        raise ValueError("At least 4 participants and 3 clips required")
    return [
        StimulusTrial(
            participant=f"synthetic-p{p:02d}",
            trial=f"synthetic-trial{clip:02d}",
            stimulus=f"synthetic-film{clip:02d}",
            valence=1.0 + (5.0 * clip / (clips - 1)) +
                    (p - (participants - 1) / 2) * 0.05,
        )
        for p in range(participants) for clip in range(clips)
    ]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(
        audit_stimulus_confound(synthetic_fixture()),
        indent=2, sort_keys=True, allow_nan=False,
    ))


if __name__ == "__main__":
    main()
