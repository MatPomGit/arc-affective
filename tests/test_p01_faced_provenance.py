"""P01 source/derivative metadata conflict tests with synthetic fixtures."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from arc_affective.p01_faced_provenance import audit_recording, compare_cohorts


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


if __name__ == "__main__":
    unittest.main()
