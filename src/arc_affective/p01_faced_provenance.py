"""P01 FACED source-vs-BIDS provenance and cohort-montage conflict gate.

No EEG samples are read. Author metadata are documentary expectations only.
Passing metadata cannot verify the actual digital reference transformation.
"""
from __future__ import annotations

import argparse
from collections import Counter
import math
import json
from pathlib import Path

from .p01_bids_qc import MISSING, read_json, read_tsv
from .p01_faced_preprocessing_order import BIDS_COHORT1, BIDS_COHORT2, BIDS_COMMIT

# The pinned upstream README and code/faced.py *describe* a different
# sampling-rate distribution from that observed in public BIDS JSON metadata.
# This is a documentation/metadata consistency check, not verification
# of source acquisition rates or raw EEG samples.
PINNED_README_BLOB = "55b05cc3c3b6d92acbf216a4bc1bfa6eb66f3305"
README_REPORTED_FREQUENCY_COUNTS = {"250": 31, "1000": 92}

EXPECTED = {
    "eeg_device": "Neuracle NeuSen.W32",
    "acquisition_reference": "CPz",
    "acquisition_ground": "AFz",
    "eeg_channel_count": 32,
    "source_doi": "10.1038/s41597-023-02650-w",
}


def _value(text: object) -> str | None:
    if not isinstance(text, str) or text.strip().lower() in MISSING:
        return None
    return text.strip()


def audit_recording(eeg: dict, channels: list[dict]) -> dict:
    """Identify source-versus-derivative disagreements; never fix automatically."""
    if not isinstance(eeg, dict) or not isinstance(channels, list) or not channels:
        raise ValueError("Missing recording sidecars")
    names = []
    for row in channels:
        if not isinstance(row, dict) or "name" not in row or "type" not in row:
            raise ValueError("Malformed channel metadata")
        label = _value(row["name"])
        if label is None or not isinstance(row["type"], str):
            raise ValueError("Invalid channel name/type")
        if row["type"].upper() == "EEG":
            names.append(label)
    if len(names) != EXPECTED["eeg_channel_count"] or len(set(x.lower() for x in names)) != len(names):
        raise ValueError("Unexpected or duplicate EEG channel inventory")
    if (type(eeg.get("EEGChannelCount")) is not int or
            eeg["EEGChannelCount"] != len(names)):
        raise ValueError("Declared EEGChannelCount mismatch")
    manufacturer = _value(eeg.get("Manufacturer"))
    reference = _value(eeg.get("EEGReference"))
    ground = _value(eeg.get("EEGGround"))
    issues = []
    # The original data descriptor names Neuracle's NeuSen.W32.
    # 'Biosemi' is not a synonym for it.
    if manufacturer is None:
        issues.append("derived_manufacturer_unknown")
    elif not ("neuracle" in manufacturer.casefold() or
              "neusen" in manufacturer.casefold()):
        issues.append("derived_manufacturer_disagrees_with_source")
    if reference is None:
        issues.append("derived_reference_undocumented")
    elif reference.casefold() != EXPECTED["acquisition_reference"].casefold():
        issues.append("derived_reference_disagrees_with_source")
    if ground is None:
        issues.append("derived_ground_undocumented")
    elif ground.casefold() != EXPECTED["acquisition_ground"].casefold():
        issues.append("derived_ground_disagrees_with_source")
    if _value(eeg.get("EEGPlacementScheme")) is None:
        issues.append("derived_placement_scheme_undocumented")
    return {
        "schema_version": 1,
        "source": "author_published_acquisition_description",
        "source_doi": EXPECTED["source_doi"],
        "published_device": EXPECTED["eeg_device"],
        "published_reference": EXPECTED["acquisition_reference"],
        "published_ground": EXPECTED["acquisition_ground"],
        "derived_manufacturer": manufacturer,
        "derived_reference": reference,
        "derived_ground": ground,
        "eeg_channels": sorted(names),
        "conflicts": issues,
        "source_to_bids_transform_verified": False,
        "raw_amplifier_reference_verified": False,
        "physical_montage_equivalence_verified": False,
        "cross_corpus_claim_authorized": False,
        "analysis_ready": False,
    }


def compare_cohorts(left: dict, right: dict) -> dict:
    """Report naming discrepancies; never assume an electrode is equivalent."""
    for report in (left, right):
        if not isinstance(report, dict) or report.get("schema_version") != 1:
            raise ValueError("Invalid provenance report")
        labels = report.get("eeg_channels")
        if (not isinstance(labels, list) or
                len(labels) != EXPECTED["eeg_channel_count"] or
                len(set(labels)) != len(labels)):
            raise ValueError("Invalid channel inventory")
    a, b = set(left["eeg_channels"]), set(right["eeg_channels"])
    only_left, only_right = sorted(a - b), sorted(b - a)
    blockers = []
    if only_left or only_right:
        blockers.append("cohort_channel_naming_or_topology_differs")
    if left.get("conflicts") or right.get("conflicts"):
        blockers.append("source_derivative_provenance_discrepancy")
    # Even an identical pair of names is not proof that positions/reference
    # are identical or that 32-channel data have been properly rereferenced.
    blockers.append("physical_positions_and_reference_transforms_unverified")
    return {
        "status": "blocked",
        "unmatched_left_names": only_left,
        "unmatched_right_names": only_right,
        "common_name_count": len(a & b),
        "blockers": blockers,
        "automatic_electrode_aliasing_allowed": False,
        "cross_cohort_equivalence_verified": False,
        "cross_corpus_transfer_authorized": False,
    }



def _channel_frequency_matches(value: object, expected: float) -> bool:
    """Safely compare numeric per-channel frequency to recording rate."""
    if type(value) not in (str, float, int):
        return False
    try:
        parsed = float(value)
    except ValueError:
        return False
    return math.isfinite(parsed) and parsed == expected


def audit_recording_sample(records: list[dict]) -> dict:
    """Audit multiple local BIDS sidecar pairs, output aggregate counts only.

    Each record requires numeric subject_number, eeg_json dict and channels
    TSV rows. The two known inventories are pinned to public NEMAR text
    sidecars; one sampled person cannot certify every cohort recording.
    """
    if not isinstance(records, list) or not records or len(records) > 123:
        raise ValueError("One to 123 metadata-only recordings required")
    seen = set()
    cohort_counts = Counter()
    sampling = Counter()
    mismatched = 0
    unexpected_frequencies = 0
    nonstandard_units = 0
    channel_frequency_mismatch = 0
    eog_named_eeg = 0
    provenance_conflicts = Counter()
    for item in records:
        if not isinstance(item, dict) or set(item) != {
            "subject_number", "eeg_json", "channels"
        }:
            raise ValueError("Expected strict metadata record structure")
        sid = item["subject_number"]
        if type(sid) is not int or sid < 0 or sid > 122 or sid in seen:
            raise ValueError("Invalid or repeated source participant number")
        seen.add(sid)
        cohort = 1 if sid <= 60 else 2
        expected = BIDS_COHORT1 if cohort == 1 else BIDS_COHORT2
        eeg, channels = item["eeg_json"], item["channels"]
        details = audit_recording(eeg, channels)
        for conflict in details["conflicts"]:
            provenance_conflicts[conflict] += 1
        names = [row["name"] for row in channels if row["type"].upper() == "EEG"]
        if names != expected:
            mismatched += 1
        cohort_counts[str(cohort)] += 1
        frequency = eeg.get("SamplingFrequency")
        if (type(frequency) not in (int, float) or
                not math.isfinite(frequency) or frequency not in (250, 1000)):
            unexpected_frequencies += 1
        else:
            sampling[str(int(frequency))] += 1
        if any(row.get("units") not in ("µV", "uV")
               for row in channels if row["type"].upper() == "EEG"):
            nonstandard_units += 1
        if (type(frequency) not in (int, float) or
                not math.isfinite(frequency) or any(
                    row.get("sampling_frequency") in (None, "", "n/a")
                    or not str(row.get("sampling_frequency")).strip()
                    or not _channel_frequency_matches(
                        row.get("sampling_frequency"), frequency
                    )
                    for row in channels if row["type"].upper() == "EEG"
                )):
            channel_frequency_mismatch += 1
        if any(name in ("HEOR", "HEOL") for name in names):
            eog_named_eeg += 1

    checked = len(records)
    complete_census = seen == set(range(123))
    blockers = [
        "source_to_bids_reference_unverified",
        "original_electrode_coordinates_unverified",
        "original_recording_data_not_examined",
    ]
    if not complete_census:
        blockers.append("incomplete_sidecar_population_census")
    if mismatched:
        blockers.append("unexpected_cohort_channel_signature")
    if unexpected_frequencies:
        blockers.append("unexpected_sampling_frequency")
    if nonstandard_units:
        blockers.append("nonstandard_or_missing_channel_unit")
    if channel_frequency_mismatch:
        blockers.append("per_channel_sampling_frequency_mismatch")
    if provenance_conflicts:
        blockers.append("source_to_derivative_metadata_conflicts")
    distribution_comparable = (
        complete_census and not unexpected_frequencies
    )
    frequency_documentation_discrepancy = (
        distribution_comparable and
        dict(sampling) != README_REPORTED_FREQUENCY_COUNTS
    )
    if frequency_documentation_discrepancy:
        blockers.append("source_readme_vs_BIDS_frequency_count_discrepancy")
    return {
        "schema_version": 1,
        "status": "blocked_for_signal_inference",
        "evidence_type": "public_or_local_metadata_sidecars_only",
        "source_commit": BIDS_COMMIT,
        "recordings_checked": checked,
        "cohort_1_checked": cohort_counts["1"],
        "cohort_2_checked": cohort_counts["2"],
        "full_123_recording_census": complete_census,
        "sampling_frequency_counts_hz": dict(sorted(sampling.items())),
        "sampling_frequency_counts_by_cohort_hz": {
            str(cohort): {
                rate: sum(
                    1 for item in records
                    if (1 if item["subject_number"] <= 60 else 2) == cohort
                    and item["eeg_json"].get("SamplingFrequency") == int(rate)
                    and type(item["eeg_json"].get("SamplingFrequency")) in (int, float)
                )
                for rate in ("250", "1000")
            }
            for cohort in (1, 2)
        },
        "source_readme_git_blob": PINNED_README_BLOB,
        "source_readme_reported_counts_hz": dict(
            README_REPORTED_FREQUENCY_COUNTS
        ),
        "complete_census_frequency_comparison_possible":
            distribution_comparable,
        "source_readme_vs_BIDS_frequency_counts_disagree":
            frequency_documentation_discrepancy,
        "unexpected_sampling_frequency_recordings": unexpected_frequencies,
        "unexpected_channel_signature_recordings": mismatched,
        "missing_or_nonstandard_unit_recordings": nonstandard_units,
        "per_channel_frequency_mismatch_recordings": channel_frequency_mismatch,
        "eog_named_channels_typed_eeg_recordings": eog_named_eeg,
        "provenance_conflict_record_counts": dict(
            sorted(provenance_conflicts.items())
        ),
        "blockers": blockers,
        "participant_identifiers_exported": False,
        "electrode_aliasing_allowed": False,
        "actual_montage_verified": False,
        "original_signal_units_verified": False,
        "analysis_ready": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cohort-manifest-json", type=Path)
    parser.add_argument("--eeg-json", type=Path)
    parser.add_argument("--channels-tsv", type=Path)
    parser.add_argument("--other-eeg-json", type=Path)
    parser.add_argument("--other-channels-tsv", type=Path)
    args = parser.parse_args()
    if args.cohort_manifest_json is not None:
        if any((args.eeg_json, args.channels_tsv,
                args.other_eeg_json, args.other_channels_tsv)):
            parser.error("Use either the cohort manifest or a pair of sidecars")
        raw = read_json(args.cohort_manifest_json)
        if type(raw) is not list:
            parser.error("Cohort manifest must contain an array of entries")
        records = []
        for entry in raw:
            if not isinstance(entry, dict) or set(entry) != {
                "subject_number", "eeg_json", "channels_tsv"
            }:
                parser.error("Invalid cohort manifest entry")
            num = entry["subject_number"]
            if type(num) is not int or not 0 <= num <= 122:
                parser.error("Invalid subject_number")
            eeg_path = Path(entry["eeg_json"])
            channels_path = Path(entry["channels_tsv"])
            expected = f"sub-{num:03d}_task-watchingVideoClips"
            if (eeg_path.name != expected + "_eeg.json" or
                    channels_path.name != expected + "_channels.tsv"):
                parser.error("Sidecar names must match the stated subject")
            records.append({
                "subject_number": num,
                "eeg_json": read_json(eeg_path),
                "channels": read_tsv(channels_path),
            })
        result = audit_recording_sample(records)
    else:
        if not args.eeg_json or not args.channels_tsv:
            parser.error("Both --eeg-json and --channels-tsv are required")
        if bool(args.other_eeg_json) != bool(args.other_channels_tsv):
            parser.error("Both sidecars of the second recording are required")
        result = audit_recording(read_json(args.eeg_json),
                                 read_tsv(args.channels_tsv))
        if args.other_eeg_json:
            second = audit_recording(read_json(args.other_eeg_json),
                                     read_tsv(args.other_channels_tsv))
            result = {"source": "pinned_public_sidecars_only",
                      "recordings": [result, second],
                      "cohort_comparison": compare_cohorts(result, second)}
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
