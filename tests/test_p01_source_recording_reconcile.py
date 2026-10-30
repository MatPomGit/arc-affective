"""Synthetic original Recording_info.csv fixtures, no subjects' records."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arc_affective.p01_source_recording_reconcile import (
    PINNED_BIDS_250_SUBJECTS, reconcile_recording_info,
)


def fixture(rates=None, unit="uV", subjects=range(123)):
    rates = rates or {}
    text = ["sub,Sample_rate,Unit,Gender,Age"]
    for sid in subjects:
        sample_rate = rates.get(sid, (
            250 if sid in PINNED_BIDS_250_SUBJECTS else 1000
        ))
        text.append(f"sub{sid:03d},{sample_rate},{unit},NOT_PUBLIC,999")
    return ("\n".join(text) + "\n").encode("utf-8")


class SourceCsvReconciliationTests(unittest.TestCase):
    def test_exact_pinned_bids_rate_pattern_has_no_mismatches(self):
        result = reconcile_recording_info(fixture())
        self.assertEqual(result["source_csv_rows"], 123)
        self.assertTrue(result["complete_source_csv_census"])
        self.assertEqual(
            result["source_sampling_frequency_counts_hz"],
            {"250": 55, "1000": 68})
        self.assertEqual(
            result["source_csv_to_pinned_BIDS_frequency_mismatch_count"], 0)
        self.assertTrue(result["source_csv_vs_README_global_counts_disagree"])
        self.assertFalse(result["analysis_ready"])
        self.assertFalse(result["raw_BDF_headers_verified"])

    def test_pinned_recording_rates_not_inferred_from_cohort_range(self):
        # Real, public BIDS JSON sidecars at pinned NEMAR commit:
        # 000-003 = 1000; 004-005 = 250; 006-007 = 1000;
        # 008-060 = 250; 061-122 = 1000.
        self.assertEqual(len(PINNED_BIDS_250_SUBJECTS), 55)
        self.assertEqual(
            set(PINNED_BIDS_250_SUBJECTS),
            {4, 5} | set(range(8, 61)))
        self.assertNotIn(6, PINNED_BIDS_250_SUBJECTS)
        self.assertNotIn(7, PINNED_BIDS_250_SUBJECTS)

    def test_partial_csv_exact_boundary_record_alignment(self):
        # Aggregate rates would remain 55/68 under the previous WRONG
        # contiguous mapping; compare records, not just count totals.
        records = fixture(subjects=[4, 5, 6, 7])
        result = reconcile_recording_info(records)
        self.assertEqual(result["source_csv_rows"], 4)
        self.assertEqual(
            result["source_csv_to_pinned_BIDS_frequency_mismatch_count"], 0)
        self.assertFalse(result["complete_source_csv_census"])

        inverted = fixture({4: 1000, 6: 250}, subjects=[4, 5, 6, 7])
        mismatched = reconcile_recording_info(inverted)
        self.assertEqual(
            mismatched["source_csv_to_pinned_BIDS_frequency_mismatch_count"],
            2)
        self.assertEqual(
            mismatched["frequency_mismatch_directions"],
            {"source_250_bids_1000": 1, "source_1000_bids_250": 1})
        self.assertFalse(
            mismatched["source_csv_vs_README_global_counts_disagree"])

    def test_source_matching_readme_still_disagrees_with_bids(self):
        rates = {i: 250 if i < 31 else 1000 for i in range(123)}
        result = reconcile_recording_info(fixture(rates))
        self.assertFalse(result["source_csv_vs_README_global_counts_disagree"])
        self.assertEqual(
            result["source_sampling_frequency_counts_hz"],
            {"250": 31, "1000": 92})
        self.assertEqual(
            result["source_csv_to_pinned_BIDS_frequency_mismatch_count"], 36)
        self.assertEqual(
            result["frequency_mismatch_directions"],
            {"source_250_bids_1000": 6, "source_1000_bids_250": 30})

    def test_partial_csv_never_certifies_global_counts(self):
        report = reconcile_recording_info(fixture(subjects=range(8)))
        self.assertFalse(report["complete_source_csv_census"])
        self.assertFalse(report["complete_count_comparison_possible"])
        self.assertFalse(report["source_csv_vs_README_global_counts_disagree"])
        self.assertIn("partial_source_CSV", report["blockers"])

    def test_upstream_unit_is_not_bdf_scaling_instruction(self):
        for unit in ("V", "uV", "µV", "μV"):
            with self.subTest(unit=unit):
                result = reconcile_recording_info(fixture(unit=unit))
                self.assertFalse(
                    result["source_csv_unit_is_BDF_amplitude_scaling_instruction"])
                self.assertFalse(result["source_csv_unit_proves_BDF_physical_dimension"])
                self.assertEqual(result["source_upstream_unit_labels"]["unrecognized"], 0)

    def test_unsupported_unit_does_not_allow_empirical_conversion(self):
        report = reconcile_recording_info(fixture(unit="mV"))
        self.assertEqual(report["source_upstream_unit_labels"]["unrecognized"], 123)
        self.assertIn("unrecognized_source_upstream_unit", report["blockers"])

    def test_malformed_and_duplicate_source_rows_are_blocked(self):
        invalid = [
            fixture(subjects=[0, 0]),
            fixture(subjects=[123]),
            b"sub,Sample_rate\nsub000,250\n",
            b"sub,Sample_rate,Unit\n",
            b"sub,Sample_rate,Unit\nsubx,250,uV\n",
            b"sub,Sample_rate,Unit\nsub000,250,uV,extra\n",
            b"",
            b"sub,Sample_rate,Unit\nsub000,250,uV\xff",
        ]
        for content in invalid:
            with self.subTest(content=content[:40]):
                with self.assertRaises(ValueError):
                    reconcile_recording_info(content)

    def test_unrecognized_frequency_stays_unverifiable(self):
        text = fixture({0: "NOT_A_RATE"})
        r = reconcile_recording_info(text)
        self.assertEqual(r["unrecognized_source_sampling_rate_rows"], 1)
        self.assertFalse(r["complete_count_comparison_possible"])
        self.assertIn("unrecognized_source_sampling_rate", r["blockers"])

    def test_csv_bytes_are_pinned_and_demographics_not_reproduced(self):
        content = fixture(subjects=[0, 61])
        result = reconcile_recording_info(content)
        self.assertEqual(len(result["source_csv_sha256"]), 64)
        self.assertNotIn("NOT_PUBLIC", str(result))
        self.assertNotIn("999", str(result))
        self.assertNotIn("sub000", str(result))
        self.assertFalse(result["participant_identity_or_demographics_exported"])

    def test_no_automatically_validated_physical_reference_even_if_rates_match(self):
        result = reconcile_recording_info(fixture())
        self.assertFalse(result["eeg_reference_verified"])
        self.assertFalse(result["physical_montage_verified"])
        self.assertEqual(result["status"], "metadata_only_not_signal_ready")


if __name__ == "__main__":
    unittest.main()
