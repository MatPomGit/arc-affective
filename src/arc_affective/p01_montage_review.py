"""Fail-closed FACED 2/4/8-channel proposal review; no EEG is accessed.

Identical text labels do not establish spatial or reference equivalence.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .p01_faced_preprocessing_order import (
    BIDS_COHORT1, BIDS_COHORT2, BIDS_COMMIT, MIRROR_COMMIT,
)

COHORT1 = frozenset(BIDS_COHORT1)
COHORT2 = frozenset(BIDS_COHORT2)
SHARED = COHORT1 & COHORT2
DISPUTED = COHORT1 ^ COHORT2
SIZES = (2, 4, 8)
GATES = [
    "authoritative_S2_S3_or_Electrode_Location_unread",
    "physical_electrode_correspondence_unverified",
    "BIDS_reference_operator_unverified",
    "original_signal_calibration_unverified",
]


def audit_subset(names: list[str]) -> dict:
    """Return a name-level audit, never scientific or device authorization."""
    if type(names) is not list or len(names) not in SIZES:
        raise ValueError("Use 2, 4 or 8 channel labels")
    if any(type(name) is not str or not name or
           name.strip() != name for name in names):
        raise ValueError("Names must be nonempty and trimmed")
    if len({name.casefold() for name in names}) != len(names):
        raise ValueError("Duplicate channel labels")
    unknown = sorted(set(names) - COHORT1 - COHORT2)
    disputed = sorted(set(names) & DISPUTED)
    shared = sorted(set(names) & SHARED)
    blockers = list(GATES)
    if unknown:
        blockers.append("labels_not_in_pinned_BIDS")
    if disputed:
        blockers.append("cohort_specific_names_or_roles")
    return {
        "status": ("text_only_not_approved"
                   if not unknown and not disputed else "blocked"),
        "requested_count": len(names),
        "shared_names": shared,
        "unknown_names": unknown,
        "cohort_specific_names": disputed,
        "blockers": blockers,
        "bids_commit": BIDS_COMMIT,
        "unverified_preprocessing_mirror_commit": MIRROR_COMMIT,
        "physical_positions_verified": False,
        "source_reference_verified_in_BIDS": False,
        "automated_alias_mapping_allowed": False,
        "eeg_analysis_allowed": False,
    }


def audit_family(proposals: dict[str, list[str]]) -> dict:
    """Review an explicitly supplied 2/4/8 proposal, not invent a montage."""
    if type(proposals) is not dict or set(proposals) != {"2", "4", "8"}:
        raise ValueError("Exactly keys 2, 4 and 8 required")
    results = {}
    for size in SIZES:
        if type(proposals[str(size)]) is not list or len(proposals[str(size)]) != size:
            raise ValueError("Incorrect requested montage size")
        results[str(size)] = audit_subset(proposals[str(size)])
    a, b, c = (set(proposals[str(n)]) for n in SIZES)
    failures = [n for n in SIZES if results[str(n)]["status"] == "blocked"]
    return {
        "status": "blocked" if failures else "design_review_only",
        "subsets": results,
        "blocked_sizes": failures,
        "nested_by_exact_names": a <= b <= c,
        "nestedness_is_not_a_frozen_requirement": True,
        "reference_transform_verified": False,
        "supplementary_tables_read": False,
        "physical_montage_approved": False,
        "signal_processing_allowed": False,
        "protocol_frozen": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family-json", type=Path, required=True)
    args = parser.parse_args()
    with args.family_json.open("r", encoding="utf-8") as stream:
        family = json.load(stream)
    print(json.dumps(audit_family(family), indent=2, sort_keys=True,
                     allow_nan=False))


if __name__ == "__main__":
    main()
