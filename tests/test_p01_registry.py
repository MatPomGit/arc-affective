"""Synthetic-only tests for local EEG manifest gate."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from arc_affective.p01_registry import validate_manifest


class RegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.file = self.root / "synthetic.bin"
        self.file.write_bytes(b"SYNTHETIC-NO-EEG")
        self.sha = hashlib.sha256(self.file.read_bytes()).hexdigest()
        self.manifest = dict(dataset="TEST", version="1", license="CC0-1.0",
                             approved_use=True, sampling_hz=128, reference="Cz",
                             rating_scale="synthetic", electrodes=["AF7", "AF8"],
                             files=[{"path": "synthetic.bin", "sha256": self.sha}])

    def test_valid_but_not_montage_equivalence(self):
        result = validate_manifest(self.manifest, self.root, True)
        self.assertEqual(result["files_checked"], 1)
        self.assertFalse(result["montage_equivalence_established"])
        self.assertEqual(result["cross_corpus_eligibility"], "unassessed")

    def test_rights_and_licence_gate(self):
        for change in ({"approved_use": False}, {"license": "unknown"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_manifest({**self.manifest, **change}, self.root)

    def test_checksum_and_traversal_rejected(self):
        self.file.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
            validate_manifest(self.manifest, self.root, True)
        with self.assertRaises(ValueError):
            validate_manifest({**self.manifest, "files": [
                {"path": "../escape", "sha256": self.sha}]}, self.root)

    def test_duplicate_electrodes_and_file_entries(self):
        with self.assertRaises(ValueError):
            validate_manifest({**self.manifest, "electrodes": ["AF7", "AF7"]}, self.root)
        with self.assertRaises(ValueError):
            validate_manifest({**self.manifest, "files": self.manifest["files"] * 2}, self.root)

    def test_missing_fields_and_wrong_types(self):
        for change in ({"sampling_hz": True}, {"sampling_hz": float("nan")},
                       {"electrodes": []}, {"reference": ""}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_manifest({**self.manifest, **change}, self.root)
        with self.assertRaises(ValueError):
            validate_manifest({"dataset": "test"}, self.root)

    def test_symlink_escape_rejected(self):
        (self.root / "escape.bin").symlink_to(self.root.parent / "nonexistent.bin")
        with self.assertRaises((ValueError, FileNotFoundError)):
            validate_manifest({**self.manifest, "files": [
                {"path": "escape.bin", "sha256": self.sha}]}, self.root, True)


if __name__ == "__main__":
    unittest.main()
