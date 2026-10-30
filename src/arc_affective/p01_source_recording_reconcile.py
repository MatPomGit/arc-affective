"""Read-only FACED original Recording_info.csv versus pinned BIDS metadata.

Does not read EEG samples or ratings, write back to source, or export
individual demographic rows. A CSV-level match does not verify BDF headers.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from io import StringIO
import json
import math
from pathlib import Path
import re

from .p01_faced_preprocessing_order import BIDS_COMMIT
from .p01_faced_provenance import README_REPORTED_FREQUENCY_COUNTS

# Directly checked from all 123 _eeg.json files at immutable NEMAR commit.
# This is a versioned metadata expectation, not original BDF sample evidence.
# The two 250-Hz recordings 004/005 precede two 1000-Hz recordings
# 006/007. Aggregate 55/68 counts alone cannot validate subject alignment.
# Pinned textual EEG JSON sidecars read at the exact BIDS_COMMIT above.
PINNED_BIDS_250_SUBJECTS = frozenset({4, 5}) | frozenset(range(8, 61))
EXPECTED_IDS = frozenset(range(123))
REQUIRED_COLUMNS = frozenset({"sub", "Sample_rate", "Unit"})
MAX_SOURCE_CSV_BYTES = 1024 * 1024


def _source_rate(text: str) -> int | None:
    try:
        rate = float(text)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(rate) or rate not in (250, 1000):
        return None
    return int(rate)


def _source_unit(text: str) -> str | None:
    if not isinstance(text, str):
        return None
    normalized = text.strip().replace("μ", "µ")
    if normalized == "V":
        return "V"
    if normalized.lower() in ("uv", "µv"):
        return "µV"
    return None


def _bids_rate(subject_number: int) -> int:
    return 250 if subject_number in PINNED_BIDS_250_SUBJECTS else 1000


def reconcile_recording_info(content: bytes) -> dict:
    """Reconcile only public-format source acquisition CSV fields.

    Age and Gender may occur in the input but are not inspected or
    emitted. The source 'Unit' column refers to upstream acquisition
    recordings, NOT the exported BDF header unit or amplitude scale.
    """
    if not isinstance(content, bytes) or not 0 < len(content) <= MAX_SOURCE_CSV_BYTES:
        raise ValueError("Expected a nonempty source CSV up to 1 MiB")
    try:
        data = content.decode("utf-8-sig")
    except UnicodeError as exc:
        raise ValueError("Recording_info CSV must be UTF-8") from exc
    try:
        reader = csv.DictReader(StringIO(data, newline=""))
        if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(
            reader.fieldnames
        ) or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Missing or duplicate required CSV headers")
        observed = set()
        rates = {"250": 0, "1000": 0}
        rate_by_cohort = {
            "1": {"250": 0, "1000": 0},
            "2": {"250": 0, "1000": 0},
        }
        units = {"V": 0, "µV": 0, "unrecognized": 0}
        rate_unknown = 0
        mismatch = 0
        transitions = {
            "source_250_bids_1000": 0,
            "source_1000_bids_250": 0,
        }
        for row in reader:
            if None in row or any(row.get(k) is None for k in REQUIRED_COLUMNS):
                raise ValueError("Malformed CSV data row")
            subject = row["sub"]
            match = re.fullmatch(r"sub(\d{3})", subject.strip())
            if match is None:
                raise ValueError("Expected original subXXX identifier")
            idx = int(match.group(1))
            if idx not in EXPECTED_IDS or idx in observed:
                raise ValueError("Invalid or duplicate source subject")
            observed.add(idx)
            cohort = "1" if idx <= 60 else "2"
            rate = _source_rate(row["Sample_rate"])
            if rate is None:
                rate_unknown += 1
            else:
                rates[str(rate)] += 1
                rate_by_cohort[cohort][str(rate)] += 1
                bids_rate = _bids_rate(idx)
                if rate != bids_rate:
                    mismatch += 1
                    transitions[f"source_{rate}_bids_{bids_rate}"] += 1
            unit = _source_unit(row["Unit"])
            units[unit if unit is not None else "unrecognized"] += 1
    except csv.Error as exc:
        raise ValueError("Malformed Recording_info CSV") from exc
    if not observed:
        raise ValueError("No recording records present")
    complete = observed == EXPECTED_IDS
    comparable = complete and not rate_unknown
    global_readme_disagreement = (
        comparable and rates != README_REPORTED_FREQUENCY_COUNTS
    )
    blockers = [
        "original_BDF_headers_and_signal_samples_not_checked",
        "source_to_BIDS_reference_transform_unverified",
        "physical_electrode_positions_unverified",
        "source_CSV_rights_and_version_must_be_verified",
    ]
    if not complete:
        blockers.append("partial_source_CSV")
    if rate_unknown:
        blockers.append("unrecognized_source_sampling_rate")
    if units["unrecognized"]:
        blockers.append("unrecognized_source_upstream_unit")
    if mismatch:
        blockers.append("source_CSV_vs_pinned_BIDS_rate_mismatch")
    if global_readme_disagreement:
        blockers.append("source_CSV_vs_upstream_README_rate_distribution")
    return {
        "schema_version": 1,
        "status": "metadata_only_not_signal_ready",
        "source_csv_sha256": hashlib.sha256(content).hexdigest(),
        "pinned_bids_git_commit": BIDS_COMMIT,
        "source_csv_rows": len(observed),
        "complete_source_csv_census": complete,
        "source_sampling_frequency_counts_hz": rates,
        "source_sampling_frequency_counts_by_cohort_hz": rate_by_cohort,
        "source_upstream_unit_labels": units,
        "unrecognized_source_sampling_rate_rows": rate_unknown,
        "source_csv_to_pinned_BIDS_frequency_mismatch_count": mismatch,
        "frequency_mismatch_directions": transitions,
        "complete_count_comparison_possible": comparable,
        "readme_declared_frequency_counts_hz":
            dict(README_REPORTED_FREQUENCY_COUNTS),
        "source_csv_vs_README_global_counts_disagree":
            global_readme_disagreement,
        "source_csv_unit_is_BDF_amplitude_scaling_instruction": False,
        "source_csv_unit_proves_BDF_physical_dimension": False,
        "raw_BDF_headers_verified": False,
        "eeg_reference_verified": False,
        "physical_montage_verified": False,
        "participant_identity_or_demographics_exported": False,
        "analysis_ready": False,
        "blockers": blockers,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recording-info-csv", required=True, type=Path)
    args = parser.parse_args()
    result = reconcile_recording_info(args.recording_info_csv.read_bytes())
    print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
