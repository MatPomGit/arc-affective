"""Read-only P01 EEG BIDS sidecar QC; no EEG signal access or download.

The report establishes only local metadata structure and tentative comparability.
It never certifies dataset rights or physical electrode/reference equivalence.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

MISSING = {"", "n/a", "na", "unknown", "unspecified"}
COORD_UNITS = {"m": 1.0, "cm": 0.01, "mm": 0.001}
REQUIRED_CHANNEL_COLUMNS = {"name", "type", "units"}
REQUIRED_EVENT_COLUMNS = {"onset", "duration"}


def known(value: Any) -> bool:
    return isinstance(value, str) and value.strip().lower() not in MISSING


def numeric(value: Any, field: str, *, minimum: float | None = None) -> float:
    if type(value) not in (str, int, float):
        raise ValueError(f"Invalid numeric {field}")
    try:
        v = float(value)
    except (ValueError, TypeError) as error:
        raise ValueError(f"Invalid numeric {field}") from error
    if not math.isfinite(v) or (minimum is not None and v < minimum):
        raise ValueError(f"Invalid numeric {field}")
    return v


def read_tsv(path: Path) -> list[dict[str, str]]:
    """Load only small text sidecars; callers must not pass EEG signal files."""
    if path.suffix.lower() != ".tsv":
        raise ValueError("Only BIDS TSV sidecars are allowed")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Empty or repeated TSV header")
        rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError("Malformed TSV row")
    return rows


def read_json(path: Path) -> dict:
    if path.suffix.lower() != ".json":
        raise ValueError("Only JSON sidecars are allowed")
    with path.open("r", encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object")
    return data


def inspect_sidecars(
    eeg: dict, channels: list[dict], events: list[dict], *,
    electrodes: list[dict] | None = None,
    coordsystem: dict | None = None,
    rating_column: str = "Valence",
) -> dict:
    """Fail closed on invalid structure; unknown montage != incompatible montage.

    The data-rights and clinical-research suitability gates always remain open.
    """
    if not isinstance(eeg, dict) or not isinstance(channels, list) or not isinstance(events, list):
        raise ValueError("Incorrect sidecar container")
    if not known(rating_column) or rating_column.lower() in ("binary_label", "emotion_label"):
        raise ValueError("Explicit continuous self-report rating column needed")
    sample_hz = numeric(eeg.get("SamplingFrequency"), "SamplingFrequency", minimum=1)
    reference = eeg.get("EEGReference")
    reference_known = known(reference)
    if not channels:
        raise ValueError("channels.tsv is empty")
    if any(not isinstance(row, dict) or
           not REQUIRED_CHANNEL_COLUMNS.issubset(row) for row in channels):
        raise ValueError("Missing channel columns")
    names = []
    eeg_units = set()
    for row in channels:
        name = row["name"]
        if not known(name):
            raise ValueError("Missing channel name")
        names.append(name.casefold().strip())
        if str(row["type"]).upper() == "EEG":
            if not known(row["units"]):
                raise ValueError("Unknown EEG voltage units")
            eeg_units.add(row["units"].strip().lower())
    if len(set(names)) != len(names):
        raise ValueError("Duplicate channel names")
    eeg_names = {
        row["name"].strip(): row
        for row in channels if str(row["type"]).upper() == "EEG"
    }
    if not eeg_names:
        raise ValueError("No EEG channels")
    if "EEGChannelCount" in eeg:
        count = eeg["EEGChannelCount"]
        if type(count) is not int or count != len(eeg_names):
            raise ValueError("EEGChannelCount differs from channel table")
    for row in eeg_names.values():
        frequency = row.get("sampling_frequency")
        if frequency is not None and str(frequency).strip().lower() not in MISSING:
            if not math.isclose(numeric(frequency, "channel sampling frequency", minimum=1),
                                sample_hz, rel_tol=1e-8, abs_tol=1e-8):
                raise ValueError("EEG channel sampling frequency mismatch")
    if any(not isinstance(row, dict) or
           not REQUIRED_EVENT_COLUMNS.issubset(row) for row in events):
        raise ValueError("Invalid event table")
    if not events:
        raise ValueError("No event metadata")
    labeled = 0
    missing = 0
    unknown_duration = 0
    for row in events:
        # BIDS permits onsets prior to the start of recording.
        numeric(row["onset"], "onset")
        if str(row["duration"]).strip().lower() in MISSING:
            unknown_duration += 1
        else:
            numeric(row["duration"], "duration", minimum=0)
        val = row.get(rating_column)
        if val is None or str(val).strip().lower() in MISSING:
            missing += 1
            continue
        numeric(val, rating_column)
        labeled += 1
    if electrodes is None and coordsystem is not None:
        raise ValueError("Coordinate system without electrodes")
    if electrodes is not None and coordsystem is None:
        raise ValueError("Electrodes without coordinate system")
    positions: dict[str, tuple[float, float, float]] = {}
    frame = None
    if electrodes is not None:
        if not isinstance(electrodes, list) or not isinstance(coordsystem, dict):
            raise ValueError("Incorrect electrode metadata")
        frame = coordsystem.get("EEGCoordinateSystem")
        units = coordsystem.get("EEGCoordinateUnits")
        if not known(frame) or units not in COORD_UNITS:
            raise ValueError("Missing or unsupported EEG coordinate frame/units")
        factor = COORD_UNITS[units]
        for item in electrodes:
            if not isinstance(item, dict) or not {"name", "x", "y", "z"}.issubset(item):
                raise ValueError("Malformed electrode coordinate row")
            name = item["name"]
            if not known(name) or name in positions:
                raise ValueError("Duplicate/invalid electrode coordinate")
            if all(str(item[key]).strip().lower() in MISSING for key in ("x", "y", "z")):
                continue
            positions[name] = tuple(
                numeric(item[key], key) * factor for key in ("x", "y", "z")
            )
    return {
        "schema_version": 1,
        "source": "local_BIDS_text_sidecars_only",
        "sample_hz": sample_hz,
        "eeg_channel_count": len(eeg_names),
        "eeg_channels": sorted(eeg_names),
        "eeg_units": sorted(eeg_units),
        "reference": reference.strip() if reference_known else None,
        "reference_documented": reference_known,
        "spatial_frame": frame,
        "coordinates_m": {name: list(pos) for name, pos in positions.items()
                          if name in eeg_names},
        "event_rows": len(events),
        "events_with_ratings": labeled,
        "events_without_ratings": missing,
        "events_with_unknown_duration": unknown_duration,
        "rating_column": rating_column,
        "event_rating_alignment_verified": False,
        "dataset_rights_verified": False,
        "signal_files_read": False,
        "physical_montage_equivalence_verified": False,
        "analysis_ready": False,
    }


def compare_metadata(left: dict, right: dict, *,
                     minimum_channels: int = 4,
                     position_tolerance_m: float = 0.012) -> dict:
    """Potential same-frame match only; never asserts physical equivalence."""
    if type(minimum_channels) is not int or minimum_channels < 1:
        raise ValueError("Invalid minimum channel count")
    if type(position_tolerance_m) not in (int, float) or not math.isfinite(position_tolerance_m) or position_tolerance_m <= 0:
        raise ValueError("Invalid position tolerance")
    for source in (left, right):
        if not isinstance(source, dict) or source.get("schema_version") != 1:
            raise ValueError("Invalid metadata report")
    reasons = []
    if not left.get("reference_documented") or not right.get("reference_documented"):
        reasons.append("reference_unknown")
    elif left["reference"].casefold() != right["reference"].casefold():
        reasons.append("reference_mismatch")
    if not left.get("spatial_frame") or not right.get("spatial_frame"):
        reasons.append("coordinate_frame_unknown")
    elif left["spatial_frame"].casefold() != right["spatial_frame"].casefold():
        reasons.append("coordinate_frame_mismatch")
    if set(left.get("eeg_units", [])) != set(right.get("eeg_units", [])):
        reasons.append("signal_units_differ")
    shared = set(left.get("eeg_channels", [])) & set(right.get("eeg_channels", []))
    positions_left = left.get("coordinates_m", {})
    positions_right = right.get("coordinates_m", {})
    candidates = []
    for name in sorted(shared & positions_left.keys() & positions_right.keys()):
        x, y = positions_left[name], positions_right[name]
        if len(x) != 3 or len(y) != 3:
            raise ValueError("Invalid coordinate vector")
        if math.dist(x, y) <= position_tolerance_m:
            candidates.append(name)
    if len(candidates) < minimum_channels:
        reasons.append("too_few_position_matched_channels")
    return {
        "status": "candidate_metadata_match_only" if not reasons else "blocked",
        "reasons": reasons,
        "position_matched_channel_count": len(candidates),
        "position_matched_channel_names": candidates,
        "source_rights_verified": False,
        "physical_reference_equivalence_verified": False,
        "cross_corpus_transfer_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eeg-json", type=Path, required=True)
    parser.add_argument("--channels-tsv", type=Path, required=True)
    parser.add_argument("--events-tsv", type=Path, required=True)
    parser.add_argument("--electrodes-tsv", type=Path)
    parser.add_argument("--coordsystem-json", type=Path)
    parser.add_argument("--rating-column", default="Valence")
    args = parser.parse_args()
    report = inspect_sidecars(
        read_json(args.eeg_json),
        read_tsv(args.channels_tsv),
        read_tsv(args.events_tsv),
        electrodes=read_tsv(args.electrodes_tsv) if args.electrodes_tsv else None,
        coordsystem=read_json(args.coordsystem_json) if args.coordsystem_json else None,
        rating_column=args.rating_column,
    )
    # Output excludes event observations and participant identifiers by design.
    print(json.dumps(report, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
