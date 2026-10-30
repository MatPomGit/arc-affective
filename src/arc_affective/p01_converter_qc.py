"""Read-only FACED converter source and synthetic BDF-header metadata QC.

Static syntax checks are not proof of the converter's dynamic behaviour.
No full BDF signals, recordings or participant data are loaded.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path

UPSTREAM_COMMIT = "2577b0bbc089b49e828cd98d80445133634b6d34"
PINNED_CONVERTER_BLOB = "cced146163b93fd51d277d66cb7eee6bea55f983"
BAD_UNIT = b"?V      "
GOOD_UNIT = b"uV      "


def git_blob_sha(content: bytes) -> str:
    """Compute the Git SHA-1 blob identity, not a raw file SHA-1."""
    return hashlib.sha1(
        b"blob " + str(len(content)).encode("ascii") + b"\0" + content
    ).hexdigest()


def _call_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def audit_converter(source: bytes, *, expected_blob: str = PINNED_CONVERTER_BLOB) -> dict:
    """Inspect pinned converter source as inert text and never execute it.

    The return value cannot verify what MNE or the original BDF samples do.
    """
    if not isinstance(source, bytes) or not source:
        raise ValueError("Nonempty converter Python bytes required")
    if not isinstance(expected_blob, str) or len(expected_blob) != 40 or any(
        c not in "0123456789abcdef" for c in expected_blob
    ):
        raise ValueError("Expected exact lowercase Git blob SHA-1")
    blob = git_blob_sha(source)
    try:
        tree = ast.parse(source.decode("utf-8"))
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise ValueError("Invalid UTF-8 Python converter") from exc
    # Check actual AST call expressions, not substrings in comments/docs.
    functions = {
        node.name: node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    def calls(name: str) -> set[str]:
        node = functions.get(name)
        return {
            called for part in ast.walk(node) if isinstance(part, ast.Call)
            if (called := _call_name(part)) is not None
        } if node is not None else set()

    conversion = calls("main")
    annotation = calls("_create_annotations_from_evt")
    patch = calls("_maybe_patch_bdf_units")
    all_calls = {
        method for part in ast.walk(tree) if isinstance(part, ast.Call)
        if (method := _call_name(part)) is not None
    }
    constants = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant):
                    constants[target.id] = node.value.value
    checks = {
        "source_blob_exact": blob == expected_blob,
        "bdf_header_unit_literals_recognized":
            constants.get("_BDF_BAD_UNIT_FIELD") == BAD_UNIT
            and constants.get("_BDF_GOOD_UNIT_FIELD") == GOOD_UNIT,
        "read_raw_bdf_in_main": "read_raw_bdf" in conversion,
        "header_patch_called_in_main": "_maybe_patch_bdf_units" in conversion,
        "bids_writer_called_in_main": "write_raw_bids" in conversion,
        "annotations_read_from_event_bdf": "read_annotations" in annotation,
        "self_report_mat_read": "loadmat" in calls("_load_all_ratings"),
        "temporary_header_copy_patch":
            {"mkstemp", "copy"}.issubset(patch),
    }
    mutation_methods = sorted(
        all_calls.intersection({
            "set_eeg_reference", "set_montage", "rename_channels",
            "set_channel_types", "reorder_channels",
        })
    )
    failures = sorted(k for k, okay in checks.items() if not okay)
    if mutation_methods:
        failures.append("explicit_channel_or_reference_mutation_calls_present")
    return {
        "schema_version": 1,
        "source": "public_converter_python_static_AST",
        "upstream_commit": UPSTREAM_COMMIT,
        "expected_git_blob": expected_blob,
        "observed_git_blob": blob,
        "status": "static_source_checks_pass_only" if not failures else "blocked",
        "failed_checks": failures,
        "checks": checks,
        "explicit_channel_or_reference_mutation_calls": mutation_methods,
        "no_explicit_rereference_observed":
            "set_eeg_reference" not in all_calls,
        "no_explicit_montage_assignment_observed":
            "set_montage" not in all_calls,
        "no_explicit_channel_rename_observed":
            "rename_channels" not in all_calls,
        "header_unit_patch_does_not_prove_amplitude_scale": True,
        "original_bdf_sample_bytes_verified": False,
        "original_reference_operator_verified": False,
        "converter_runtime_equivalence_verified": False,
        "cross_cohort_equivalence_verified": False,
        "data_analysis_ready": False,
    }


def inspect_bdf_header(header: bytes) -> dict:
    """Inspect BDF header unit labels, never read any signal data bytes.

    Caller must supply the 256-byte global header and per-signal headers.
    Does not patch or open original files. Unknown unit strings are blockers.
    """
    if not isinstance(header, bytes) or len(header) < 256:
        raise ValueError("BDF general header missing")
    try:
        count_text = header[252:256].decode("ascii").strip()
        if not count_text.isdecimal():
            raise ValueError("Invalid BDF channel count")
        count = int(count_text)
        if not 1 <= count <= 128:
            raise ValueError("Unexpected BDF channel count")
        size_text = header[184:192].decode("ascii").strip()
        if not size_text.isdecimal():
            raise ValueError("Invalid declared BDF header size")
        if int(size_text) != 256 + 256 * count:
            raise ValueError("BDF header length inconsistent")
    except UnicodeDecodeError as exc:
        raise ValueError("Invalid BDF header ASCII") from exc
    if len(header) != 256 + 256 * count:
        raise ValueError("Expected metadata header bytes only")
    start = 256 + count * (16 + 80)
    labels = [
        header[start + 8 * idx: start + 8 * (idx + 1)]
        for idx in range(count)
    ]
    counts = Counter(labels)
    unknown = count - counts[BAD_UNIT] - counts[GOOD_UNIT]
    return {
        "channel_count": count,
        "corrupt_question_mark_unit_labels": counts[BAD_UNIT],
        "normal_microvolt_unit_labels": counts[GOOD_UNIT],
        "unrecognized_unit_labels": unknown,
        "status": "header_needs_source_review"
        if unknown or counts[BAD_UNIT] else "header_labels_recognized_only",
        "any_sample_bytes_read": False,
        "source_recording_calibration_verified": False,
        "unit_label_correction_applied": False,
        "signal_amplitude_verified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--converter-python", type=Path, required=True)
    parser.add_argument("--header-only", type=Path,
                        help="Optional authorized BDF header bytes only")
    args = parser.parse_args()
    report = audit_converter(args.converter_python.read_bytes())
    if args.header_only is not None:
        report["bdf_header"] = inspect_bdf_header(
            args.header_only.read_bytes()
        )
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
