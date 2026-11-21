"""ARC Affective migration provenance and safe partial handover checks."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/"migration/affective_to_arc.json").read_text(encoding="utf-8"))
def git_blob_sha(content:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest()
class MigrationContractTest(unittest.TestCase):
    def test_eight_exact_central_owners(self):
        entries=DATA["papers"]
        self.assertEqual(len(entries),8)
        self.assertEqual(len({e["id"] for e in entries}),8)
        for e in entries:
            expected="arc-neuro" if e["id"].endswith("P05") else "arc-robo" if e["id"].endswith("P07") else "arc-ai"
            self.assertEqual(e["owner_programme"],expected)
            self.assertTrue(e["target_repository"].endswith("/"+expected))
            self.assertNotIn(e["migration_state"],("COMPLETE","MIGRATED","MERGED"))
    def test_all_source_blobs_preserved_byte_for_byte(self):
        self.assertRegex(DATA["source_snapshot_sha"],r"^[0-9a-f]{40}$")
        for paper in DATA["papers"]:
            self.assertGreaterEqual(len(paper["source_paths"]),1)
            for p in paper["source_paths"]:
                with self.subTest(path=p["path"]):
                    actual=(ROOT/p["path"]).read_bytes()
                    self.assertEqual(len(actual),p["size"])
                    self.assertEqual(git_blob_sha(actual),p["blob_sha"])
        for p in DATA["software_inventory"]:
            self.assertEqual(git_blob_sha((ROOT/p["path"]).read_bytes()),p["blob_sha"])
    def test_six_ai_blockers_and_two_prs(self):
        entries=DATA["papers"]
        self.assertEqual(sum(p["migration_state"]=="BLOCKED_TARGET_REPOSITORY_ABSENT" for p in entries),6)
        self.assertEqual(sum(p["migration_state"]=="STAGED_IN_OPEN_PR" for p in entries),2)
        for p in entries:
            if p["target_pr"]:
                self.assertTrue(p["target_pr"].startswith("https://github.com/MatPomGit/"))
                self.assertRegex(p["target_pr_head_sha"],r"^[0-9a-f]{40}$")
        self.assertTrue((ROOT/"pages/index.md").exists())
if __name__=="__main__":
    unittest.main()
