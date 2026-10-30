"""Offline manuscript source contract. Does not replace a LaTeX compiler."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAPERS = ("P01", "P08")
PARTS = ("introduction", "methods", "results", "discussion")


class ManuscriptTests(unittest.TestCase):
    def test_ieee_source_and_section_files(self):
        for paper in PAPERS:
            with self.subTest(paper=paper):
                base = ROOT / "manuscripts" / paper
                main = (base / "main.tex").read_text(encoding="utf-8")
                self.assertIn(r"\documentclass[conference]{IEEEtran}", main)
                self.assertIn(r"\bibliography{references}", main)
                self.assertIn(r"\begin{document}", main)
                self.assertIn(r"\end{document}", main)
                for part in PARTS:
                    self.assertIn(fr"\input{{sections/{part}}}", main)
                    section = (base / "sections" / f"{part}.tex").read_text(
                        encoding="utf-8"
                    )
                    self.assertIn(r"\section{", section)
                    self.assertEqual(
                        section.count("{"), section.count("}"),
                        f"{paper}/{part}: unbalanced braces",
                    )

    def test_all_bibliography_citations_resolve(self):
        for paper in PAPERS:
            with self.subTest(paper=paper):
                base = ROOT / "manuscripts" / paper
                bibliography = (base / "references.bib").read_text(
                    encoding="utf-8"
                )
                keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bibliography))
                self.assertGreaterEqual(len(keys), 3)
                for part in PARTS:
                    content = (base / "sections" / f"{part}.tex").read_text(
                        encoding="utf-8"
                    )
                    for group in re.findall(r"\\cite\{([^}]+)\}", content):
                        for citation in group.split(","):
                            self.assertIn(citation.strip(), keys, paper)

    def test_unverified_results_are_labelled(self):
        for paper in PAPERS:
            with self.subTest(paper=paper):
                results = (
                    ROOT / "manuscripts" / paper / "sections" / "results.tex"
                ).read_text(encoding="utf-8")
                self.assertIn("empirical", results.lower())
                self.assertIn("Pending", results)
                protocol = (
                    ROOT / "papers" / f"{paper}-protocol.md"
                ).read_text(encoding="utf-8")
                self.assertIn("NOT preregistered", protocol)


if __name__ == "__main__":
    unittest.main()
