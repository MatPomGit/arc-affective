"""Static FACED preprocessing index evidence: no real EEG accessed."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arc_affective.p01_faced_preprocessing_order import (
    BIDS_COHORT1, BIDS_COHORT2, MIRROR_BLOB, audit_preprocessing_code,
    candidate_index_alignment,
)
from arc_affective.p01_converter_qc import git_blob_sha


def fake_code():
    p = list(range(16)) + list(range(18, 32)) + [17, 16, 32]
    return ("""
class Preprocessing:
    def __init__(self, raw):
        new_chn_names = raw.info['ch_names'].copy()
        if 'A1' not in new_chn_names:
            new_chn_names[-2] = 'A2'
            new_chn_names[-1] = 'A1'
        raw.rename_channels({})
        raw.set_montage('standard_1020')
    def average_ref(self):
        self.raw.set_eeg_reference(ref_channels='average')
def channel_modify(data, first_or_second):
    new_order = """+repr(p)+"""
    if first_or_second == 1:
        data = data[new_order]
    return data
""").encode("utf-8")


def checked(source=None):
    source = fake_code() if source is None else source
    return audit_preprocessing_code(source, expected_blob=git_blob_sha(source))


class FacedPreprocessedOrderTests(unittest.TestCase):
    def test_inert_ast_finds_source_operations(self):
        report = checked()
        self.assertEqual(report["status"], "software_source_pass_only")
        self.assertTrue(report["code_checks"]["average_ref_is_explicit"])
        self.assertEqual(report["cohort2_tail_relabel"], ["A2", "A1"])
        self.assertEqual(len(report["eeg_order_with_event"]), 33)
        self.assertFalse(report["runtime_data_transform_verified"])
        self.assertFalse(report["authoritative_original_code_verified"])

    def test_mirror_source_sha_mismatch_is_not_a_pass(self):
        report = audit_preprocessing_code(fake_code())
        self.assertEqual(report["status"], "blocked")
        self.assertIn("pinned_git_blob", report["failed_checks"])
        self.assertEqual(report["expected_blob"], MIRROR_BLOB)

    def test_six_pairs_are_only_index_evidence(self):
        report = candidate_index_alignment(
            BIDS_COHORT1, BIDS_COHORT2, checked())
        self.assertEqual(report["status"],
                         "index_correspondence_only_not_spatial_validation")
        self.assertEqual(report["common_original_name_count"], 26)
        self.assertEqual(report["index_link_count"], 6)
        self.assertEqual(
            [(x["cohort1_source"], x["cohort2_source"])
             for x in report["index_links"]],
            [("T3", "T7"), ("T4", "T8"), ("T5", "P7"),
             ("T6", "P8"), ("A2", "HEOR"), ("A1", "HEOL")])
        self.assertTrue(report["fully_aligned_postprocessing_names"])
        self.assertFalse(report["apply_to_raw_or_BIDS_allowed"])
        self.assertFalse(report["physically_equivalent"])

    def test_mutated_sidecar_names_fail_closed(self):
        wrong = list(BIDS_COHORT1)
        wrong[0] = "TEST"
        with self.assertRaises(ValueError):
            candidate_index_alignment(wrong, BIDS_COHORT2, checked())
        with self.assertRaises(ValueError):
            candidate_index_alignment(BIDS_COHORT1, list(reversed(BIDS_COHORT2)),
                                      checked())

    def test_bad_relabel_and_bad_mapping_are_blocked(self):
        src = fake_code().replace(b"new_chn_names[-2] = 'A2'",
                                  b"new_chn_names[-2] = 'X2'")
        self.assertIn("renames_last_two_to_A2_A1", checked(src)["failed_checks"])
        src = fake_code().replace(
            b"new_order = [", b"new_order = [31, ")
        with self.assertRaises(ValueError):
            checked(src)

    def test_missing_average_reference_is_blocked(self):
        src = fake_code().replace(b"set_eeg_reference", b"other_method")
        self.assertIn("average_ref_is_explicit", checked(src)["failed_checks"])
        src = fake_code().replace(b"set_montage", b"other_method")
        self.assertIn("init_assigns_template_montage", checked(src)["failed_checks"])

    def test_invalid_source_and_sha_are_rejected(self):
        with self.assertRaises(ValueError):
            audit_preprocessing_code(b"")
        with self.assertRaises(ValueError):
            audit_preprocessing_code(b"not valid python @")
        with self.assertRaises(ValueError):
            audit_preprocessing_code(fake_code(), expected_blob="missing")
        with self.assertRaises(ValueError):
            audit_preprocessing_code(b"class A: pass")

    def test_only_validated_source_can_give_index_evidence(self):
        with self.assertRaises(ValueError):
            candidate_index_alignment(BIDS_COHORT1, BIDS_COHORT2,
                                      audit_preprocessing_code(fake_code()))
        with self.assertRaises(ValueError):
            candidate_index_alignment(BIDS_COHORT1, BIDS_COHORT2,
                                      dict(checked(), supplementary_S2_S3_verified=True))
        with self.assertRaises(ValueError):
            candidate_index_alignment(BIDS_COHORT1, BIDS_COHORT2, {})

    def test_no_participant_or_raw_signal_in_output(self):
        report = candidate_index_alignment(BIDS_COHORT1, BIDS_COHORT2, checked())
        self.assertNotIn("sub-000", str(report))
        self.assertNotIn("raw_eeg", str(report))
        self.assertFalse(report["sensor_locations_verified"])
        self.assertFalse(report["analysis_ready"])


if __name__ == "__main__":
    unittest.main()
