"""FACED preprocessed-channel code-path audit; no raw EEG or alias approval.

This reads a pinned *third-party public copy* of a preprocessing program.
Its index permutation is evidence of a software operation, not proof of
physical electrode locations in acquisition or BIDS.
"""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

from .p01_converter_qc import git_blob_sha

MIRROR_COMMIT = "8aa55c1b6d503d92b5db5a87b576a361115a6a02"
MIRROR_BLOB = "d59f503029cc75451284040f3adfe3ca3f95c63f"
# This BIDS-sidecar name ordering was read from two files at a separately
# pinned upstream NEMAR commit. No EEG signals were accessed.
BIDS_COMMIT = "2577b0bbc089b49e828cd98d80445133634b6d34"
BIDS_COHORT1 = (
    "Fp1 Fp2 Fz F3 F4 F7 F8 FC1 FC2 FC5 FC6 Cz C3 C4 "
    "T3 T4 A1 A2 CP1 CP2 CP5 CP6 Pz P3 P4 T5 T6 PO3 PO4 Oz O1 O2"
).split()
BIDS_COHORT2 = (
    "Fp1 Fp2 Fz F3 F4 F7 F8 FC1 FC2 FC5 FC6 Cz C3 C4 "
    "T7 T8 CP1 CP2 CP5 CP6 Pz P3 P4 P7 P8 PO3 PO4 Oz O1 O2 HEOR HEOL"
).split()


def _calls(node: ast.AST) -> set[str]:
    names = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            fun = child.func
            if isinstance(fun, (ast.Attribute, ast.Name)):
                names.add(fun.attr if isinstance(fun, ast.Attribute) else fun.id)
    return names


def audit_preprocessing_code(
    source: bytes, *, expected_blob: str = MIRROR_BLOB,
) -> dict:
    """Read AST only, requiring exact fingerprint before claiming pin validity."""
    if not isinstance(source, bytes) or not source:
        raise ValueError("Nonempty UTF-8 Python bytes required")
    if (not isinstance(expected_blob, str) or len(expected_blob) != 40
            or any(ch not in "0123456789abcdef" for ch in expected_blob)):
        raise ValueError("Expected 40 lowercase hex digits for Git blob")
    observed = git_blob_sha(source)
    try:
        tree = ast.parse(source.decode("utf-8"))
    except (SyntaxError, UnicodeDecodeError) as exc:
        raise ValueError("Invalid UTF-8 Python code") from exc
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)
               and n.name == "Preprocessing"]
    modify = [n for n in tree.body if isinstance(n, ast.FunctionDef)
              and n.name == "channel_modify"]
    if len(classes) != 1 or len(modify) != 1:
        raise ValueError("Missing expected original processing structure")
    methods = {m.name: m for m in classes[0].body
               if isinstance(m, ast.FunctionDef)}
    init = methods.get("__init__")
    average = methods.get("average_ref")
    if init is None or average is None:
        raise ValueError("Missing original montage/reference methods")
    permutation = None
    for statement in modify[0].body:
        if isinstance(statement, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "new_order"
            for t in statement.targets
        ):
            try:
                permutation = ast.literal_eval(statement.value)
            except (TypeError, ValueError, SyntaxError):
                permutation = None
    if not isinstance(permutation, list) or len(permutation) != 33:
        raise ValueError("Expected explicit 33-index array (32 EEG + event)")
    if (any(type(x) is not int for x in permutation) or
            sorted(permutation) != list(range(33)) or permutation[-1] != 32):
        raise ValueError("Invalid 32 EEG + 1 event permutation")
    rename_targets = {}
    for statement in ast.walk(init):
        if not isinstance(statement, ast.Assign):
            continue
        for target in statement.targets:
            if (isinstance(target, ast.Subscript) and
                    isinstance(target.value, ast.Name) and
                    target.value.id == "new_chn_names"):
                try:
                    index = ast.literal_eval(target.slice)
                    label = ast.literal_eval(statement.value)
                except (TypeError, ValueError, SyntaxError):
                    continue
                if type(index) is int and isinstance(label, str):
                    rename_targets[index] = label
    calls_init, calls_average = _calls(init), _calls(average)
    checks = {
        "pinned_git_blob": observed == expected_blob,
        "renames_last_two_to_A2_A1":
            rename_targets.get(-2) == "A2" and
            rename_targets.get(-1) == "A1",
        "permutation_holds_event_channel_at_last": permutation[-1] == 32,
        "init_applies_renaming": "rename_channels" in calls_init,
        "init_assigns_template_montage": "set_montage" in calls_init,
        "average_ref_is_explicit": "set_eeg_reference" in calls_average,
    }
    failed = sorted(k for k, value in checks.items() if not value)
    return {
        "schema_version": 1,
        "source": "third_party_mirror_static_python_AST",
        "mirror_commit": MIRROR_COMMIT,
        "observed_blob": observed,
        "expected_blob": expected_blob,
        "code_checks": checks,
        "status": "software_source_pass_only" if not failed else "blocked",
        "failed_checks": failed,
        "eeg_order_with_event": permutation,
        "cohort2_tail_relabel": [
            rename_targets.get(-2), rename_targets.get(-1)
        ],
        "authoritative_original_code_verified": False,
        "supplementary_S2_S3_verified": False,
        "runtime_data_transform_verified": False,
        "physical_electrode_equivalence_verified": False,
        "bids_signal_reference_verified": False,
        "analysis_ready": False,
    }


def candidate_index_alignment(
    cohort1: list[str], cohort2: list[str], audit: dict,
) -> dict:
    """Enumerate code-implied index positions, NOT physical aliases.

    Fail closed if both lists are not an exact match to pinned sidecar names.
    Refuse to use a failing AST audit. This is intentionally NOT an
    EEG-channel mapper or a data-transform implementation.
    """
    if (type(cohort1) is not list or type(cohort2) is not list or
            cohort1 != BIDS_COHORT1 or cohort2 != BIDS_COHORT2):
        raise ValueError("Sidecar labels differ from pinned read-back")
    if (not isinstance(audit, dict) or
            audit.get("status") != "software_source_pass_only" or
            audit.get("authoritative_original_code_verified") is not False or
            audit.get("supplementary_S2_S3_verified") is not False):
        raise ValueError("Unverified/missing code audit")
    perm = audit.get("eeg_order_with_event")
    if (not isinstance(perm, list) or len(perm) != 33 or
            sorted(perm) != list(range(33)) or perm[-1] != 32 or
            audit.get("cohort2_tail_relabel") != ["A2", "A1"]):
        raise ValueError("Incompatible original processing rules")
    aligned_left = [cohort1[i] for i in perm[:32]]
    aligned_right = [*cohort2[:30], "A2", "A1"]
    mismatches = [
        {"output_index_zero_based": i, "cohort1_source": l,
         "cohort2_source": cohort2[i], "cohort2_processing_label": r}
        for i, (l, r) in enumerate(zip(aligned_left, aligned_right))
        if l != cohort2[i]
    ]
    return {
        "schema_version": 1,
        "status": "index_correspondence_only_not_spatial_validation",
        "code_mirror_commit": MIRROR_COMMIT,
        "bids_source_commit": BIDS_COMMIT,
        "common_original_name_count": len(set(cohort1) & set(cohort2)),
        "index_link_count": len(mismatches),
        "index_links": mismatches,
        "fully_aligned_postprocessing_names":
            aligned_left == aligned_right,
        "remaining_name_mismatch_count": sum(
            left != right for left, right in
            zip(aligned_left, aligned_right)),
        "authoritative_code_provenance_verified": False,
        "original_electrode_table_verified": False,
        "sensor_locations_verified": False,
        "bids_to_preprocessed_signal_identity_verified": False,
        "apply_to_raw_or_BIDS_allowed": False,
        "physically_equivalent": False,
        "analysis_ready": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preprocessing-python", type=Path, required=True)
    args = parser.parse_args()
    audited = audit_preprocessing_code(args.preprocessing_python.read_bytes())
    if audited["status"] == "software_source_pass_only":
        audited["candidate_indices"] = candidate_index_alignment(
            BIDS_COHORT1, BIDS_COHORT2, audited)
    print(json.dumps(audited, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
