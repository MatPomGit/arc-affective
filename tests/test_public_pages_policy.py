"""Public Pages policy regression tests; isolated, offline, no secrets."""
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "affective_public_pages", ROOT / "scripts/validate_public_pages.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class CuratedPagesTests(unittest.TestCase):
    def fixture(self, directory):
        base = directory / "repo"
        shutil.copytree(ROOT / "pages", base / "pages")
        (base / "config").mkdir()
        shutil.copy2(ROOT / "config/pages-policy.json",
                     base / "config/pages-policy.json")
        return base

    def test_curated_index_passes(self):
        self.assertEqual([], validator.validate(ROOT))
        self.assertNotIn("docs/index.md", json.loads(
            (ROOT / "config/pages-policy.json").read_text())["allowed_files"])

    def test_no_extra_files(self):
        with tempfile.TemporaryDirectory() as temp:
            base = self.fixture(Path(temp))
            (base / "pages/AGENTS.md").write_text("Agent prompt")
            self.assertIn("PAGES_UNAPPROVED: AGENTS.md",
                          validator.validate(base))

    def test_no_agent_directives(self):
        with tempfile.TemporaryDirectory() as temp:
            base = self.fixture(Path(temp))
            (base / "pages/index.md").write_text(
                "Agent: popraw dokument", encoding="utf-8")
            self.assertIn("PAGES_EDITORIAL_CONTENT: index.md",
                          validator.validate(base))

    def test_no_editorial_notes(self):
        with tempfile.TemporaryDirectory() as temp:
            base = self.fixture(Path(temp))
            (base / "pages/index.md").write_text(
                "Uwagi redakcyjne: napisz dalej", encoding="utf-8")
            self.assertIn("PAGES_EDITORIAL_CONTENT: index.md",
                          validator.validate(base))

    def test_no_internal_workflow(self):
        with tempfile.TemporaryDirectory() as temp:
            base = self.fixture(Path(temp))
            (base / "pages/index.md").write_text(
                "PROJECT_STATE.yaml", encoding="utf-8")
            self.assertIn("PAGES_INTERNAL_CONTENT: index.md",
                          validator.validate(base))

    def test_no_unapproved_allowlist_expansion(self):
        with tempfile.TemporaryDirectory() as temp:
            base = self.fixture(Path(temp))
            p = base / "config/pages-policy.json"
            obj = json.loads(p.read_text())
            obj["allowed_files"].append("research.json")
            p.write_text(json.dumps(obj))
            self.assertIn(
                "PAGES_POLICY: public source expansion requires independent review",
                validator.validate(base))

    def test_symlinks_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = self.fixture(Path(temp))
            (base / "pages/extra.html").symlink_to(ROOT / "docs/index.md")
            self.assertIn("PAGES_SYMLINK: extra.html",
                          validator.validate(base))

    def test_approval_required(self):
        with tempfile.TemporaryDirectory() as temp:
            base = self.fixture(Path(temp))
            p = base / "config/pages-policy.json"
            obj = json.loads(p.read_text())
            obj["publication_requires_owner_approval"] = False
            p.write_text(json.dumps(obj))
            self.assertIn("PAGES_POLICY: explicit approval is required",
                          validator.validate(base))


if __name__ == "__main__":
    unittest.main()
