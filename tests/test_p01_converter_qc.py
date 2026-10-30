"""Fully synthetic QC for FACED Python converter and BDF header handling."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arc_affective.p01_converter_qc import (
    BAD_UNIT, GOOD_UNIT, audit_converter, git_blob_sha, inspect_bdf_header,
)


def dummy_script(*, rereference=False, rename=False):
    mutation = ("raw.set_eeg_reference('average')\n" if rereference else "")
    mutation += ("    raw.rename_channels({'T3':'T7'})\n" if rename else "")
    if rereference:
        mutation = "    " + mutation
    return ('''
_BDF_BAD_UNIT_FIELD = b"?V      "
_BDF_GOOD_UNIT_FIELD = b"uV      "
def _maybe_patch_bdf_units(path):
    tempfile.mkstemp()
    shutil.copy(path, path)
def _load_all_ratings(root, subject):
    return loadmat("rating.mat")
def _create_annotations_from_evt(raw):
    read_annotations("evt.bdf")
def main():
    raw = read_raw_bdf(_maybe_patch_bdf_units("source.bdf"))
    raw.set_annotations("test")
''' + mutation + '''    write_raw_bids(raw, "bids")
''').encode("utf-8")


def bdf_header(units):
    n = len(units)
    data = bytearray(b" " * (256 + 256 * n))
    data[184:192] = str(len(data)).encode("ascii").ljust(8, b" ")
    data[252:256] = str(n).encode("ascii").ljust(4, b" ")
    start = 256 + n * (16 + 80)
    for i, label in enumerate(units):
        data[start + 8 * i:start + 8 * (i + 1)] = label
    return bytes(data)


class ConverterReviewTests(unittest.TestCase):
    def test_static_source_checks_all_pass_without_runtime_claims(self):
        source = dummy_script()
        report = audit_converter(source, expected_blob=git_blob_sha(source))
        self.assertEqual(report["status"], "static_source_checks_pass_only")
        self.assertFalse(report["data_analysis_ready"])
        self.assertFalse(report["original_bdf_sample_bytes_verified"])
        self.assertFalse(report["converter_runtime_equivalence_verified"])
        self.assertTrue(report["no_explicit_rereference_observed"])

    def test_wrong_blob_is_blocked_even_for_structurally_correct_code(self):
        source = dummy_script()
        report = audit_converter(source)
        self.assertEqual(report["status"], "blocked")
        self.assertIn("source_blob_exact", report["failed_checks"])

    def test_executable_reference_mutation_is_detected(self):
        source = dummy_script(rereference=True, rename=True)
        report = audit_converter(source, expected_blob=git_blob_sha(source))
        self.assertEqual(report["status"], "blocked")
        self.assertIn("set_eeg_reference",
                      report["explicit_channel_or_reference_mutation_calls"])
        self.assertIn("rename_channels",
                      report["explicit_channel_or_reference_mutation_calls"])

    def test_comment_only_does_not_count_as_signal_mutation(self):
        source = dummy_script() + b"# raw.set_eeg_reference('average')\n"
        report = audit_converter(source, expected_blob=git_blob_sha(source))
        self.assertTrue(report["no_explicit_rereference_observed"])

    def test_missing_write_or_header_patch_is_blocked(self):
        source = dummy_script().replace(b"write_raw_bids", b"other_writer")
        report = audit_converter(source, expected_blob=git_blob_sha(source))
        self.assertIn("bids_writer_called_in_main", report["failed_checks"])
        source = dummy_script().replace(
            b"_maybe_patch_bdf_units(\"source.bdf\")", b"\"source.bdf\"")
        report = audit_converter(source, expected_blob=git_blob_sha(source))
        self.assertIn("header_patch_called_in_main", report["failed_checks"])

    def test_invalid_python_blob_arguments_are_rejected(self):
        with self.assertRaises(ValueError):
            audit_converter(b"not valid python @")
        with self.assertRaises(ValueError):
            audit_converter(b"")
        with self.assertRaises(ValueError):
            audit_converter(dummy_script(), expected_blob="bad")

    def test_bdf_header_mixed_labels_are_flagged_without_modification(self):
        header = bdf_header([GOOD_UNIT, BAD_UNIT, GOOD_UNIT])
        report = inspect_bdf_header(header)
        self.assertEqual(report["channel_count"], 3)
        self.assertEqual(report["corrupt_question_mark_unit_labels"], 1)
        self.assertEqual(report["normal_microvolt_unit_labels"], 2)
        self.assertEqual(report["unrecognized_unit_labels"], 0)
        self.assertEqual(report["status"], "header_needs_source_review")
        self.assertFalse(report["unit_label_correction_applied"])
        self.assertFalse(report["any_sample_bytes_read"])

    def test_normal_header_is_not_physical_amplitude_proof(self):
        report = inspect_bdf_header(bdf_header([GOOD_UNIT] * 32))
        self.assertEqual(report["status"], "header_labels_recognized_only")
        self.assertFalse(report["signal_amplitude_verified"])
        self.assertEqual(report["normal_microvolt_unit_labels"], 32)

    def test_unrecognized_unit_and_invalid_length_fail_closed(self):
        report = inspect_bdf_header(bdf_header([b"mV      "]))
        self.assertEqual(report["unrecognized_unit_labels"], 1)
        self.assertEqual(report["status"], "header_needs_source_review")
        h = bdf_header([GOOD_UNIT])
        for bad in (h[:-1], h + b"data", h[:253] + b"999" + h[256:]):
            with self.subTest(n=len(bad)), self.assertRaises(ValueError):
                inspect_bdf_header(bad)

    def test_no_raw_eeg_or_participant_data_in_report(self):
        source = dummy_script()
        report = audit_converter(source, expected_blob=git_blob_sha(source))
        self.assertNotIn("sub-000", str(report))
        self.assertFalse(report["cross_cohort_equivalence_verified"])
        self.assertIn("expected_git_blob", report)


if __name__ == "__main__":
    unittest.main()
