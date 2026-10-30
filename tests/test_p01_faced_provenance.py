"""P01 source/derivative metadata conflict tests with synthetic fixtures."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arc_affective.p01_faced_provenance import (
    audit_recording, audit_recording_sample, compare_cohorts,
)


COHORT_1 = (
    "Fp1 Fp2 Fz F3 F4 F7 F8 FC1 FC2 FC5 FC6 Cz C3 C4 "
    "T3 T4 A1 A2 CP1 CP2 CP5 CP6 Pz P3 P4 T5 T6 PO3 PO4 Oz O1 O2"
).split()

COHORT_2 = (
    "Fp1 Fp2 Fz F3 F4 F7 F8 FC1 FC2 FC5 FC6 Cz C3 C4 "
    "T7 T8 CP1 CP2 CP5 CP6 Pz P3 P4 P7 P8 PO3 PO4 Oz O1 O2 HEOR HEOL"
).split()


def fixture(names=COHORT_1, *, manufacturer="Biosemi", reference="n/a",
            ground="n/a", placement="extended 10/20"):
    eeg = {
        "Manufacturer": manufacturer,
        "EEGReference": reference,
        "EEGGround": ground,
        "EEGChannelCount": 32,
        "EEGPlacementScheme": placement,
    }
    channels = [{"name": name, "type": "EEG"} for name in names]
    return eeg, channels


class FacedSourceProvenanceTests(unittest.TestCase):
    def test_source_paper_conflicts_with_public_derived_metadata(self):
        report = audit_recording(*fixture())
        self.assertIn("derived_manufacturer_disagrees_with_source",
                      report["conflicts"])
        self.assertIn("derived_reference_undocumented", report["conflicts"])
        self.assertIn("derived_ground_undocumented", report["conflicts"])
        self.assertEqual(report["published_reference"], "CPz")
        self.assertEqual(report["published_ground"], "AFz")
        self.assertFalse(report["analysis_ready"])

    def test_filled_in_reference_does_not_prove_transform(self):
        report = audit_recording(*fixture(
            manufacturer="Neuracle NeuSen.W32", reference="CPz", ground="AFz"))
        self.assertFalse(report["conflicts"])
        self.assertFalse(report["source_to_bids_transform_verified"])
        self.assertFalse(report["physical_montage_equivalence_verified"])
        self.assertFalse(report["cross_corpus_claim_authorized"])

    def test_realistic_two_cohort_label_difference_blocked(self):
        a = audit_recording(*fixture(COHORT_1))
        b = audit_recording(*fixture(COHORT_2, placement="n/a"))
        comparison = compare_cohorts(a, b)
        self.assertEqual(comparison["status"], "blocked")
        self.assertEqual(comparison["common_name_count"], 26)
        self.assertEqual(comparison["unmatched_left_names"],
                         ["A1", "A2", "T3", "T4", "T5", "T6"])
        self.assertEqual(comparison["unmatched_right_names"],
                         ["HEOL", "HEOR", "P7", "P8", "T7", "T8"])
        self.assertFalse(comparison["automatic_electrode_aliasing_allowed"])
        self.assertIn("cohort_channel_naming_or_topology_differs",
                      comparison["blockers"])

    def test_identical_names_still_cannot_prove_equivalence(self):
        report = audit_recording(*fixture(
            manufacturer="Neuracle", reference="CPz", ground="AFz"))
        comparison = compare_cohorts(report, report)
        self.assertEqual(comparison["unmatched_left_names"], [])
        self.assertEqual(comparison["common_name_count"], 32)
        self.assertEqual(comparison["status"], "blocked")
        self.assertIn("physical_positions_and_reference_transforms_unverified",
                      comparison["blockers"])

    def test_unknown_placement_is_flagged(self):
        report = audit_recording(*fixture(placement="n/a"))
        self.assertIn("derived_placement_scheme_undocumented",
                      report["conflicts"])

    def test_wrong_reference_and_ground_are_not_rewritten(self):
        report = audit_recording(*fixture(reference="average", ground="Fpz"))
        self.assertIn("derived_reference_disagrees_with_source",
                      report["conflicts"])
        self.assertIn("derived_ground_disagrees_with_source",
                      report["conflicts"])
        self.assertEqual(report["derived_reference"], "average")

    def test_bad_channel_count_duplicates_or_bad_types_rejected(self):
        with self.assertRaises(ValueError):
            audit_recording(*fixture(COHORT_1[:-1]))
        with self.assertRaises(ValueError):
            audit_recording(*fixture(COHORT_1[:-1] + ["Fp1"]))
        eeg, channels = fixture()
        eeg["EEGChannelCount"] = 31
        with self.assertRaises(ValueError):
            audit_recording(eeg, channels)
        eeg, channels = fixture()
        channels[0]["name"] = "n/a"
        with self.assertRaises(ValueError):
            audit_recording(eeg, channels)

    def test_invalid_cohort_provenance_report_rejected(self):
        a = audit_recording(*fixture())
        with self.assertRaises(ValueError):
            compare_cohorts(a, {})
        with self.assertRaises(ValueError):
            compare_cohorts(a, dict(a, eeg_channels=["C3"]))

    def test_reports_are_deterministic_and_identifiers_not_exported(self):
        first = audit_recording(*fixture())
        self.assertEqual(first, audit_recording(*fixture()))
        self.assertNotIn("sub-000", str(first))
        self.assertNotIn("raw_signal", first)
        self.assertFalse(first["raw_amplifier_reference_verified"])



def sample(n, *, sampling=1000, cohort=None):
    expected_cohort = 1 if n <= 60 else 2
    names = COHORT_1 if (cohort or expected_cohort) == 1 else COHORT_2
    eeg, channels = fixture(names)
    eeg["SamplingFrequency"] = sampling
    for row in channels:
        row["units"] = "µV"
        row["sampling_frequency"] = str(sampling)
    return {"subject_number": n, "eeg_json": eeg, "channels": channels}


class CohortSampleTests(unittest.TestCase):
    def test_six_realistic_source_recordings_summarized_without_identifiers(self):
        r = audit_recording_sample([
            sample(0), sample(30, sampling=250),
            sample(60, sampling=250), sample(61), sample(90), sample(122),
        ])
        self.assertEqual(r["recordings_checked"], 6)
        self.assertEqual((r["cohort_1_checked"], r["cohort_2_checked"]), (3, 3))
        self.assertEqual(r["sampling_frequency_counts_hz"], {"1000": 4, "250": 2})
        self.assertEqual(r["unexpected_channel_signature_recordings"], 0)
        self.assertEqual(r["eog_named_channels_typed_eeg_recordings"], 3)
        self.assertFalse(r["full_123_recording_census"])
        self.assertFalse(r["analysis_ready"])
        self.assertNotIn("sub-000", str(r))

    def test_mislabeled_cohort_channel_order_is_detected(self):
        r = audit_recording_sample([sample(0, cohort=2)])
        self.assertEqual(r["unexpected_channel_signature_recordings"], 1)
        self.assertIn("unexpected_cohort_channel_signature", r["blockers"])

    def test_reordering_without_missing_channels_is_still_detected(self):
        item = sample(0)
        item["channels"][0], item["channels"][1] = (
            item["channels"][1], item["channels"][0]
        )
        r = audit_recording_sample([item])
        self.assertEqual(r["unexpected_channel_signature_recordings"], 1)

    def test_invalid_frequency_is_blocked(self):
        for frequency in (True, float("nan"), 125, "1000"):
            with self.subTest(frequency=frequency):
                r = audit_recording_sample([sample(0, sampling=frequency)])
                self.assertEqual(r["unexpected_sampling_frequency_recordings"], 1)

    def test_missing_units_are_flagged(self):
        item = sample(61)
        item["channels"][0]["units"] = "n/a"
        r = audit_recording_sample([item])
        self.assertEqual(r["missing_or_nonstandard_unit_recordings"], 1)

    def test_duplicate_or_out_of_range_subject_numbers_rejected(self):
        for data in ([sample(0), sample(0)], [sample(-1)],
                     [sample(123)], [sample(True)]):
            with self.subTest(case=str([x["subject_number"] for x in data])):
                with self.assertRaises(ValueError):
                    audit_recording_sample(data)

    def test_malformed_or_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            audit_recording_sample([])
        with self.assertRaises(ValueError):
            audit_recording_sample([{"subject_number": 0}])
        with self.assertRaises(ValueError):
            audit_recording_sample("sidecar")
        with self.assertRaises(ValueError):
            audit_recording_sample([sample(0)] * 124)

    def test_full_public_metadata_pattern_disagrees_with_source_readme(self):
        rows = [
            sample(i, sampling=250 if 6 <= i <= 60 else 1000)
            for i in range(123)
        ]
        result = audit_recording_sample(rows)
        self.assertTrue(result["full_123_recording_census"])
        self.assertEqual(result["sampling_frequency_counts_hz"],
                         {"250": 55, "1000": 68})
        self.assertEqual(result["source_readme_reported_counts_hz"],
                         {"250": 31, "1000": 92})
        self.assertTrue(
            result["source_readme_vs_BIDS_frequency_counts_disagree"])
        self.assertIn("source_readme_vs_BIDS_frequency_count_discrepancy",
                      result["blockers"])
        self.assertEqual(
            result["sampling_frequency_counts_by_cohort_hz"],
            {"1": {"250": 55, "1000": 6},
             "2": {"250": 0, "1000": 62}})
        self.assertFalse(result["analysis_ready"])

    def test_full_census_matching_readme_has_no_distribution_discrepancy(self):
        rows = [
            sample(i, sampling=250 if i < 31 else 1000)
            for i in range(123)
        ]
        result = audit_recording_sample(rows)
        self.assertFalse(
            result["source_readme_vs_BIDS_frequency_counts_disagree"])
        self.assertTrue(
            result["complete_census_frequency_comparison_possible"])

    def test_partial_metadata_never_confirms_distribution_against_readme(self):
        rows = [sample(i, sampling=250) for i in range(10)]
        result = audit_recording_sample(rows)
        self.assertFalse(
            result["complete_census_frequency_comparison_possible"])
        self.assertFalse(
            result["source_readme_vs_BIDS_frequency_counts_disagree"])

    def test_missing_or_inconsistent_per_channel_sampling_frequency_flagged(self):
        row = sample(0)
        row["channels"][0]["sampling_frequency"] = "250"
        for other in row["channels"][1:]:
            other["sampling_frequency"] = "1000"
        result = audit_recording_sample([row])
        self.assertEqual(result["per_channel_frequency_mismatch_recordings"], 1)
        self.assertIn("per_channel_sampling_frequency_mismatch",
                      result["blockers"])
        for channel in row["channels"]:
            channel["sampling_frequency"] = "1000"
        okay = audit_recording_sample([row])
        self.assertEqual(okay["per_channel_frequency_mismatch_recordings"], 0)

    def test_full_census_label_requires_all_123_unique_subjects(self):
        r = audit_recording_sample([sample(i) for i in range(123)])
        self.assertTrue(r["full_123_recording_census"])
        self.assertEqual(r["recordings_checked"], 123)
        self.assertEqual((r["cohort_1_checked"], r["cohort_2_checked"]), (61, 62))
        self.assertFalse(r["actual_montage_verified"])
        self.assertFalse(r["analysis_ready"])


if __name__ == "__main__":
    unittest.main()
