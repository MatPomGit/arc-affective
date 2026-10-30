"""P01 FACED source-vs-BIDS provenance and cohort-montage conflict gate.

No EEG samples are read. Author metadata are documentary expectations only.
Passing metadata cannot verify the actual digital reference transformation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .p01_bids_qc import MISSING, read_json, read_tsv

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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eeg-json", type=Path, required=True)
    parser.add_argument("--channels-tsv", type=Path, required=True)
    parser.add_argument("--other-eeg-json", type=Path)
    parser.add_argument("--other-channels-tsv", type=Path)
    args = parser.parse_args()
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
