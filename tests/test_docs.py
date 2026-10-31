"""Offline document-link and source synchronization regression tests."""
from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNC_FILE = ROOT / "scripts" / "sync_mkdocs.py"
spec = importlib.util.spec_from_file_location("sync_mkdocs", SYNC_FILE)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class DocumentationTests(unittest.TestCase):
    def test_all_eight_canonical_proposals_exist(self):
        self.assertEqual(len(module.PAPERS), 8)
        for code, slug, _, stages, _ in module.PAPERS:
            self.assertEqual(len(stages), 7, code)
            self.assertTrue((ROOT / "papers" / f"{code}-{slug}.md").is_file())

    def test_generator_is_deterministic_and_does_not_modify_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            first = module.generate(docs=target)
            a = {x.name: x.read_bytes() for x in first}
            second = module.generate(docs=target)
            b = {x.name: x.read_bytes() for x in second}
            self.assertEqual(a, b)
            self.assertEqual(len(first), 9)
            self.assertEqual(len({x for p in module.PAPERS for x in p[3]}), 56)
            for out in first:
                self.assertNotIn("](../docs/", out.read_text(encoding="utf-8"))

    def test_nav_markdown_targets_exist_after_sync(self):
        module.generate()
        config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
        # All site Markdown nav entries are indented scalar paths.
        targets = re.findall(r"^\s+-\s+[^\n:]+:\s+([\w./-]+\.md)\s*$", config, re.MULTILINE)
        self.assertEqual(len(targets), 26, "Expected all navigation pages")
        for item in targets:
            with self.subTest(page=item):
                self.assertTrue((ROOT / "docs" / item).is_file())

    def test_internal_markdown_links_resolve(self):
        module.generate()
        for doc in (ROOT / "docs").rglob("*.md"):
            content = doc.read_text(encoding="utf-8")
            for dest in re.findall(r"\]\(([^)]+)\)", content):
                dest = dest.split("#", 1)[0].split("?", 1)[0]
                if not dest or "://" in dest or dest.startswith(("mailto:", "/")):
                    continue
                if not dest.endswith(".md"):
                    continue
                with self.subTest(file=str(doc.relative_to(ROOT)), target=dest):
                    self.assertTrue((doc.parent / dest).is_file(), f"Missing {dest} from {doc}")


if __name__ == "__main__":
    unittest.main()
