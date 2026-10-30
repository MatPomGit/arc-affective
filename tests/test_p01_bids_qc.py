"""Synthetic BIDS sidecar contracts; no patient/participant data."""
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from arc_affective.p01_bids_qc import (
    compare_metadata, inspect_sidecars, read_tsv, read_json,
)


def sample():
    eeg = {"SamplingFrequency": 250, "EEGReference": "Cz"}
    channels = [
        {"name": n, "type": "EEG", "units": "uV"}
        for n in ("Fp1", "F3", "C3", "P3")
    ]
    events = [
        {"onset": str(i * 4), "duration": "3.2", "Valence": str(i + 1)}
        for i in range(4)
    ]
    electrodes = [
        {"name": n, "x": str(i * 2), "y": "0", "z": "10"}
        for i, n in enumerate(("Fp1", "F3", "C3", "P3"))
    ]
    frame = {"EEGCoordinateSystem": "CapTrak", "EEGCoordinateUnits": "mm"}
    return eeg, channels, events, electrodes, frame


class BidsMetadataQATests(unittest.TestCase):
    def test_valid_report_never_claims_rights_or_montage(self):
        eeg, channels, events, electrodes, frame = sample()
        r = inspect_sidecars(eeg, channels, events,
                             electrodes=electrodes, coordsystem=frame)
        self.assertEqual(r["events_with_ratings"], 4)
        self.assertEqual(r["eeg_channel_count"], 4)
        self.assertEqual(r["sample_hz"], 250)
        self.assertFalse(r["analysis_ready"])
        self.assertFalse(r["dataset_rights_verified"])
        self.assertFalse(r["event_rating_alignment_verified"])
        self.assertFalse(r["signal_files_read"])
        self.assertEqual(r["coordinates_m"]["F3"], [0.002, 0, 0.01])

    def test_matching_metadata_is_only_candidate(self):
        a = sample()
        l = inspect_sidecars(*a[:3], electrodes=a[3], coordsystem=a[4])
        result = compare_metadata(l, l)
        self.assertEqual(result["status"], "candidate_metadata_match_only")
        self.assertEqual(result["position_matched_channel_count"], 4)
        self.assertFalse(result["cross_corpus_transfer_authorized"])

    def test_blocks_reference_and_frame_mismatches(self):
        a = sample()
        l = inspect_sidecars(*a[:3], electrodes=a[3], coordsystem=a[4])
        b = sample()
        b[0]["EEGReference"] = "Average"
        r = inspect_sidecars(*b[:3], electrodes=b[3], coordsystem=b[4])
        self.assertIn("reference_mismatch", compare_metadata(l, r)["reasons"])
        frame = {"EEGCoordinateSystem": "Other", "EEGCoordinateUnits": "mm"}
        r = inspect_sidecars(*a[:3], electrodes=a[3], coordsystem=frame)
        self.assertIn("coordinate_frame_mismatch", compare_metadata(l, r)["reasons"])

    def test_missing_positions_block_comparison(self):
        eeg, channels, events, _, _ = sample()
        report = inspect_sidecars(eeg, channels, events)
        self.assertEqual(report["events_with_ratings"], 4)
        self.assertIn("coordinate_frame_unknown",
                      compare_metadata(report, report)["reasons"])

    def test_rejects_duplicate_and_unknown_channel_names(self):
        eeg, channels, events, *_ = sample()
        with self.assertRaises(ValueError):
            inspect_sidecars(eeg, channels + [dict(channels[0])], events)
        channels[0]["name"] = "n/a"
        with self.assertRaises(ValueError):
            inspect_sidecars(eeg, channels, events)

    def test_rejects_bad_frequency_and_unreadable_events(self):
        eeg, channels, events, *_ = sample()
        for invalid in (float("nan"), True, -1, "unknown"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                inspect_sidecars({"SamplingFrequency": invalid}, channels, events)
        with self.assertRaises(ValueError):
            inspect_sidecars(eeg, channels, [dict(events[0], onset="-1")])
        with self.assertRaises(ValueError):
            inspect_sidecars(eeg, channels, [dict(events[0], Valence="broken")])

    def test_rejects_ambiguous_electrode_metadata(self):
        eeg, channels, events, positions, frame = sample()
        with self.assertRaises(ValueError):
            inspect_sidecars(eeg, channels, events, electrodes=positions)
        with self.assertRaises(ValueError):
            inspect_sidecars(eeg, channels, events, coordsystem=frame)
        bad = [dict(positions[0]), dict(positions[0])]
        with self.assertRaises(ValueError):
            inspect_sidecars(eeg, channels, events, electrodes=bad,
                             coordsystem=frame)

    def test_comparison_blocks_shifted_positions(self):
        a = sample()
        left = inspect_sidecars(*a[:3], electrodes=a[3], coordsystem=a[4])
        shifted = [dict(p, x=str(float(p["x"]) + 30)) for p in a[3]]
        right = inspect_sidecars(*a[:3], electrodes=shifted, coordsystem=a[4])
        report = compare_metadata(left, right)
        self.assertEqual(report["status"], "blocked")
        self.assertIn("too_few_position_matched_channels", report["reasons"])

    def test_reads_text_sidecars_and_rejects_signal_files(self):
        with tempfile.TemporaryDirectory() as root:
            tsv = Path(root) / "channels.tsv"
            tsv.write_text("name\ttype\tunits\nCz\tEEG\tuV\n", encoding="utf-8")
            self.assertEqual(read_tsv(tsv)[0]["name"], "Cz")
            info = Path(root) / "info.json"
            info.write_text('{"SamplingFrequency":250}', encoding="utf-8")
            self.assertEqual(read_json(info)["SamplingFrequency"], 250)
            for path in (Path(root) / "sample.bdf", Path(root) / "sample.edf"):
                path.write_bytes(b"NON-EGG-DUMMY")
                with self.assertRaises(ValueError):
                    read_tsv(path)
                with self.assertRaises(ValueError):
                    read_json(path)

    def test_missing_ratings_do_not_become_zero(self):
        eeg, channels, events, *_ = sample()
        events[0]["Valence"] = "n/a"
        r = inspect_sidecars(eeg, channels, events)
        self.assertEqual(r["events_with_ratings"], 3)
        self.assertEqual(r["events_without_ratings"], 1)

    def test_invalid_comparison_tolerance(self):
        a = sample()
        l = inspect_sidecars(*a[:3], electrodes=a[3], coordsystem=a[4])
        for invalid in (0, float("nan"), True):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                compare_metadata(l, l, position_tolerance_m=invalid)


if __name__ == "__main__":
    unittest.main()
