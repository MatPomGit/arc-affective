"""Synthetic FACED-style BIDS event/stimulus join regression tests."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from arc_affective.p01_event_linkage import audit_event_linkage


def fixture():
    stimuli = [
        {"stim_id": "1", "targeted_valence": "Negative",
         "presented_duration_s": "60", "presented_duration_alt_s": "n/a"},
        {"stim_id": "2", "targeted_valence": "Neutral",
         "presented_duration_s": "35", "presented_duration_alt_s": "n/a"},
        {"stim_id": "3", "targeted_valence": "Positive",
         "presented_duration_s": "75.80", "presented_duration_alt_s": "83.92"},
    ]
    events = [
        {"onset": "0", "duration": "0", "video_index": "n/a",
         "Valence": "n/a", "trial_type": "Experiment start"},
        {"onset": "10", "duration": "60.2", "video_index": "1",
         "Valence": "5.0", "binary_label": "negative", "sample": "10000"},
        {"onset": "100", "duration": "35", "video_index": "2",
         "Valence": "3.0", "binary_label": "neutral", "sample": "100000"},
        {"onset": "150", "duration": "83.92", "video_index": "3",
         "Valence": "4.0", "binary_label": "positive", "sample": "150000"},
    ]
    return events, stimuli


class EventLinkageTests(unittest.TestCase):
    def test_complete_metadata_only_not_physical_evidence(self):
        events, stimuli = fixture()
        r = audit_event_linkage(events, stimuli, expected_clips=3,
                                sampling_hz=1000)
        self.assertEqual(r["status"], "structurally_consistent_only")
        self.assertEqual(r["observed_unique_videos"], 3)
        self.assertEqual(r["unlinked_technical_events"], 1)
        self.assertFalse(r["raw_eeg_trigger_alignment_verified"])
        self.assertFalse(r["original_rating_provenance_verified"])
        self.assertFalse(r["analysis_ready"])
        self.assertNotIn("trial_type", str(r))
        self.assertNotIn("100000", str(r))

    def test_stimulus_design_label_not_used_as_self_report(self):
        events, stimuli = fixture()
        # Neutral self-report can differ from targeted category, as can negative.
        events[1]["Valence"] = "6.99"
        self.assertEqual(audit_event_linkage(
            events, stimuli, expected_clips=3
        )["status"], "structurally_consistent_only")

    def test_unlinked_rating_rejected(self):
        events, stimuli = fixture()
        events[0]["Valence"] = "2.5"
        with self.assertRaisesRegex(ValueError, "Unlinked"):
            audit_event_linkage(events, stimuli, expected_clips=3)

    def test_unknown_or_duplicate_stimulus_id_rejected(self):
        events, stimuli = fixture()
        events[1]["video_index"] = "99"
        with self.assertRaisesRegex(ValueError, "Unknown"):
            audit_event_linkage(events, stimuli, expected_clips=3)
        events, stimuli = fixture()
        events[2]["video_index"] = "1"
        with self.assertRaisesRegex(ValueError, "Repeated"):
            audit_event_linkage(events, stimuli, expected_clips=3)

    def test_missing_rating_and_video_blocked(self):
        events, stimuli = fixture()
        events[1]["Valence"] = "n/a"
        r = audit_event_linkage(events[:-1], stimuli, expected_clips=3)
        self.assertIn("missing_trial_ratings", r["blockers"])
        self.assertIn("missing_video_events", r["blockers"])
        self.assertEqual(r["missing_video_count"], 1)

    def test_mismatched_category_duration_sample_and_overlap(self):
        events, stimuli = fixture()
        events[1]["binary_label"] = "positive"
        events[1]["duration"] = "200"
        events[2]["sample"] = "98000"
        r = audit_event_linkage(events, stimuli, expected_clips=3,
                                sampling_hz=1000)
        self.assertEqual(set(r["blockers"]), {
            "stimulus_category_mismatch", "duration_outliers",
            "sample_onset_mismatch", "overlapping_video_events"
        })

    def test_alternate_stimulus_duration_accepted(self):
        events, stimuli = fixture()
        self.assertEqual(audit_event_linkage(
            events, stimuli, expected_clips=3
        )["duration_outlier_count"], 0)

    def test_missing_inventory_and_duplicate_id_rejected(self):
        events, stimuli = fixture()
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            audit_event_linkage(events, stimuli[:-1], expected_clips=3)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            audit_event_linkage(events, stimuli + [stimuli[0]], expected_clips=3)

    def test_invalid_rating_and_numerics_rejected(self):
        events, stimuli = fixture()
        for rating in ("7.1", "-0.1", "nan", "inf", "bad"):
            events[1]["Valence"] = rating
            with self.subTest(rating=rating), self.assertRaises(ValueError):
                audit_event_linkage(events, stimuli, expected_clips=3)
        events, stimuli = fixture()
        with self.assertRaises(ValueError):
            audit_event_linkage(events, stimuli, expected_clips=3,
                                duration_tolerance_s=float("nan"))
        with self.assertRaises(ValueError):
            audit_event_linkage(events, stimuli, expected_clips=3,
                                sampling_hz=0)
        with self.assertRaises(ValueError):
            audit_event_linkage(events, stimuli, expected_clips=True)

    def test_technical_marker_alert_is_independent_of_rated_video_count(self):
        events, stimuli = fixture()
        marker = dict(events[0])
        # 3 expected videos => 6 unlinked markers is the review boundary.
        boundary = events + [dict(marker) for _ in range(5)]
        normal = audit_event_linkage(boundary, stimuli, expected_clips=3)
        self.assertEqual(normal["unlinked_technical_events"], 6)
        self.assertFalse(normal["technical_event_review_required"])
        self.assertEqual(normal["status"], "structurally_consistent_only")

        flagged = audit_event_linkage(
            boundary + [dict(marker)], stimuli, expected_clips=3)
        self.assertEqual(flagged["observed_unique_videos"], 3)
        self.assertEqual(flagged["missing_rating_count"], 0)
        self.assertEqual(flagged["unlinked_technical_events"], 7)
        self.assertEqual(flagged["technical_event_excess_count"], 1)
        self.assertTrue(flagged["technical_event_review_required"])
        self.assertIn("excessive_unlinked_technical_event_burden",
                      flagged["blockers"])
        self.assertEqual(flagged["status"], "blocked")
        self.assertFalse(flagged["automatic_exclusion_from_EEG_analysis"])

    def test_large_unlinked_marker_burden_stays_a_review_not_signal_proof(self):
        events, stimuli = fixture()
        events += [dict(events[0]) for _ in range(1000)]
        report = audit_event_linkage(events, stimuli, expected_clips=3)
        self.assertEqual(report["observed_unique_videos"], 3)
        self.assertEqual(report["unlinked_technical_events"], 1001)
        self.assertTrue(report["technical_event_review_required"])
        self.assertFalse(report["raw_eeg_trigger_alignment_verified"])
        self.assertFalse(report["analysis_ready"])
        self.assertFalse(report["automatic_exclusion_from_EEG_analysis"])
        self.assertNotIn("Experiment start", str(report))

    def test_negative_technical_onset_is_permitted(self):
        events, stimuli = fixture()
        events[0]["onset"] = "-2.4"
        self.assertEqual(audit_event_linkage(events, stimuli, expected_clips=3)
                         ["status"], "structurally_consistent_only")


if __name__ == "__main__":
    unittest.main()
