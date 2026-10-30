"""P01: local FACED BIDS event-to-stimulus metadata checks (no EEG signals).

Audit stimulus IDs, trial annotations, event timing and self-report presence.
A structurally consistent report never certifies EEG synchronization, legal
access, reference equivalence or correct raw self-report provenance.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from .p01_bids_qc import MISSING, numeric, read_tsv


def _optional(value: Any) -> bool:
    return value is None or str(value).strip().lower() in MISSING


def _stimulus_number(value: Any) -> int:
    if type(value) not in (str, int):
        raise ValueError("Invalid video_index/stim_id")
    try:
        number = int(value)
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid video_index/stim_id") from exc
    if number < 1 or str(value).strip() != str(number):
        raise ValueError("Invalid video_index/stim_id")
    return number


def audit_event_linkage(
    events: list[dict[str, str]],
    stimuli: list[dict[str, str]],
    *,
    expected_clips: int = 28,
    rating_column: str = "Valence",
    duration_tolerance_s: float = 0.5,
    sampling_hz: float | None = None,
    sample_tolerance: float = 2.0,
) -> dict:
    """Check metadata join without exporting titles, per-trial ratings or IDs.

    Variants in `presented_duration_alt_s` are accepted when documented.
    `targeted_valence` is a stimulus-design category, not ground-truth affect.
    """
    if type(expected_clips) is not int or expected_clips < 1:
        raise ValueError("Expected clip count must be a positive integer")
    if rating_column != "Valence":
        raise ValueError("FACED audit currently supports explicit Valence only")
    for key, val in (("duration_tolerance_s", duration_tolerance_s),
                     ("sample_tolerance", sample_tolerance)):
        if type(val) not in (int, float) or not math.isfinite(val) or val < 0:
            raise ValueError(f"Invalid {key}")
    if sampling_hz is not None:
        if (type(sampling_hz) not in (int, float) or
                not math.isfinite(sampling_hz) or sampling_hz <= 0):
            raise ValueError("Invalid sampling_hz")
    if not isinstance(events, list) or not isinstance(stimuli, list):
        raise ValueError("Expected BIDS event and stimuli lists")
    if not events or not stimuli:
        raise ValueError("Missing events or stimuli metadata")
    indexed = {}
    for row in stimuli:
        if not isinstance(row, dict) or not all(
            field in row for field in
            ("stim_id", "targeted_valence", "presented_duration_s")
        ):
            raise ValueError("Invalid stimuli.tsv row")
        key = _stimulus_number(row["stim_id"])
        if key in indexed:
            raise ValueError("Duplicate stimulus ID")
        valence = str(row["targeted_valence"]).strip().lower()
        if valence not in {"positive", "negative", "neutral"}:
            raise ValueError("Unknown targeted stimulus category")
        durations = [numeric(row["presented_duration_s"],
                             "presented_duration_s", minimum=0)]
        if durations[0] <= 0:
            raise ValueError("Nonpositive stimulus duration")
        if not _optional(row.get("presented_duration_alt_s")):
            durations.append(numeric(row["presented_duration_alt_s"],
                                     "presented_duration_alt_s", minimum=0))
            if durations[-1] <= 0:
                raise ValueError("Nonpositive alternate duration")
        indexed[key] = (valence, tuple(durations))
    # Complete pinned FACED stimulus inventory, no subset silently passed off
    # as a valid 28-video session.
    if set(indexed) != set(range(1, expected_clips + 1)):
        raise ValueError("Incomplete or unexpected stimulus inventory")
    seen = set()
    video_spans = []
    missing_rating = 0
    wrong_target_category = 0
    duration_outliers = 0
    sample_mismatches = 0
    technical_markers = 0
    for row in events:
        if not isinstance(row, dict) or not {"onset", "duration",
                                             "video_index"}.issubset(row):
            raise ValueError("Malformed event")
        onset = numeric(row["onset"], "onset")
        if _optional(row["duration"]):
            duration = None
        else:
            duration = numeric(row["duration"], "duration", minimum=0)
        video_id = row["video_index"]
        if _optional(video_id):
            if not _optional(row.get(rating_column)):
                raise ValueError("Unlinked event contains a rating")
            technical_markers += 1
            continue
        key = _stimulus_number(video_id)
        if key not in indexed:
            raise ValueError("Unknown video_index")
        if key in seen:
            raise ValueError("Repeated video_index in one recording")
        seen.add(key)
        if duration is None or duration == 0:
            raise ValueError("Video event lacks a positive duration")
        stimulus_category, durations = indexed[key]
        if min(abs(duration - d) for d in durations) > duration_tolerance_s:
            duration_outliers += 1
        observed_cat = row.get("binary_label")
        if not _optional(observed_cat) and (
            str(observed_cat).strip().lower() != stimulus_category
        ):
            wrong_target_category += 1
        if _optional(row.get(rating_column)):
            missing_rating += 1
        else:
            rating = numeric(row[rating_column], rating_column)
            if not 0 <= rating <= 7:
                raise ValueError("Valence outside documented 0-7 scale")
        if sampling_hz is not None and not _optional(row.get("sample")):
            sample = numeric(row["sample"], "sample")
            if abs(sample - onset * sampling_hz) > sample_tolerance:
                sample_mismatches += 1
        video_spans.append((onset, onset + duration))
    video_spans.sort()
    overlapping = sum(
        video_spans[i][0] < video_spans[i-1][1] - 1e-6
        for i in range(1, len(video_spans))
    )
    missing_clips = expected_clips - len(seen)
    blockers = []
    if missing_clips:
        blockers.append("missing_video_events")
    if missing_rating:
        blockers.append("missing_trial_ratings")
    if duration_outliers:
        blockers.append("duration_outliers")
    if wrong_target_category:
        blockers.append("stimulus_category_mismatch")
    if sample_mismatches:
        blockers.append("sample_onset_mismatch")
    if overlapping:
        blockers.append("overlapping_video_events")
    return {
        "schema_version": 1,
        "evidence_type": "public_or_local_metadata_only",
        "status": "structurally_consistent_only" if not blockers else "blocked",
        "blockers": blockers,
        "expected_videos": expected_clips,
        "observed_unique_videos": len(seen),
        "missing_video_count": missing_clips,
        "unlinked_technical_events": technical_markers,
        "missing_rating_count": missing_rating,
        "duration_outlier_count": duration_outliers,
        "stimulus_category_mismatch_count": wrong_target_category,
        "sample_onset_mismatch_count": sample_mismatches,
        "video_overlap_count": overlapping,
        "duration_tolerance_s": duration_tolerance_s,
        "sample_tolerance": sample_tolerance,
        "targeted_valence_is_not_self_report": True,
        "original_rating_provenance_verified": False,
        "raw_eeg_trigger_alignment_verified": False,
        "eeg_reference_verified": False,
        "original_signal_access_verified": False,
        "analysis_ready": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events-tsv", type=Path, required=True)
    parser.add_argument("--stimuli-tsv", type=Path, required=True)
    parser.add_argument("--expected-clips", type=int, default=28)
    parser.add_argument("--sampling-hz", type=float)
    parser.add_argument("--duration-tolerance-s", type=float, default=0.5)
    args = parser.parse_args()
    result = audit_event_linkage(
        read_tsv(args.events_tsv),
        read_tsv(args.stimuli_tsv),
        expected_clips=args.expected_clips,
        sampling_hz=args.sampling_hz,
        duration_tolerance_s=args.duration_tolerance_s,
    )
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
