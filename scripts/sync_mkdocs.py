"""Project source-to-MkDocs synchronizer: papers/ is canonical; docs/papers/ is generated.

Usage: python scripts/sync_mkdocs.py
No third-party dependencies, network calls or source modification.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPERS = (
    ("P01", "low-channel-transfer", 5, (14, 22, 30, 42, 50, 58, 66), "EEG / sparse transfer"),
    ("P02", "robust-fusion", 6, (15, 23, 31, 43, 51, 59, 67), "Asynchrony / sensor fusion"),
    ("P03", "personal-drift", 7, (16, 24, 32, 44, 52, 60, 68), "Longitudinal drift"),
    ("P04", "private-vision", 8, (17, 25, 33, 45, 53, 61, 69), "Private RGB vision"),
    ("P05", "hand-workload", 9, (18, 26, 38, 46, 54, 62, 70), "Hand kinematics"),
    ("P06", "adaptive-game", 10, (19, 27, 39, 47, 55, 63, 71), "Game difficulty adaptation"),
    ("P07", "safe-hri", 11, (20, 28, 40, 48, 56, 64, 72), "Safe HRI"),
    ("P08", "edge-systems", 12, (21, 29, 41, 49, 57, 65, 73), "Real-time edge computing"),
)
STAGES = (
    "M0 · Literatura / wykonalność",
    "M1 · Protokół",
    "M2 · Dane / sensory / QA",
    "M3 · Baseline",
    "M4 · Metoda autorska",
    "M5 · Walidacja",
    "M6 · Manuskrypt",
)
REPO = "https://github.com/MatPomGit/arc-affective"


def generate(docs: Path | None = None, papers: Path | None = None) -> list[Path]:
    """Generate documentation pages from paper sources, without changing sources."""
    docs = docs or ROOT / "docs"
    papers = papers or ROOT / "papers"
    target = docs / "papers"
    target.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []
    summary = [
        "# Osiem publikacji naukowych",
        "",
        "Każdy artykuł ma odrębny wkład inżynierski, siedem etapów M0–M6 i niezależne kryteria go/no-go.",
        "Eksperymenty własne: maksymalnie 3 osoby, preferowane N=0–1. Dostępność danych i licencji należy zweryfikować.",
        "",
        "| ID | Temat | Issue publikacyjne | M0–M6 |",
        "| --- | --- | --- | --- |",
    ]
    for code, slug, epic, stages, label in PAPERS:
        filename = f"{code}-{slug}.md"
        source = papers / filename
        if not source.is_file():
            raise FileNotFoundError(f"Missing canonical manuscript proposal: {source}")
        content = source.read_text(encoding="utf-8")
        # papers/Pxx is one directory below repo root, docs/papers/Pxx is two.
        # Translate only the canonical relative references to docs/ pages.
        content = re.sub(r"\]\(\.\./docs/", "](../", content)
        tracker = [
            "",
            "---",
            "",
            "## Plan realizacji w GitHub Issues",
            "",
            f"**[Issue nadrzędne #{epic}]({REPO}/issues/{epic})** · "
            f"[Źródło protokołu]({REPO}/blob/main/papers/{filename})",
            "",
            "| Etap | Zadanie |",
            "| --- | --- |",
        ]
        tracker.extend(
            f"| {name} | [#{issue}]({REPO}/issues/{issue}) |"
            for name, issue in zip(STAGES, stages)
        )
        tracker += [
            "",
            "!!! info \"Status planu\"",
            "    Otwarcie lub opisanie issue nie oznacza wykonania eksperymentu ani gotowości manuskryptu.",
            "",
        ]
        output = target / filename
        output.write_text(content.rstrip() + "\n" + "\n".join(tracker), encoding="utf-8")
        generated.append(output)
        summary.append(
            f"| [**{code}** · {label}]({filename}) | "
            f"[Protokół]({filename}) | [#{epic}]({REPO}/issues/{epic}) | "
            f"[Rejestr etapów](../publication-milestones.md) |"
        )
    summary += [
        "",
        "## Ograniczenia interpretacji",
        "",
        "- Publiczne zbiory danych umożliwiają testy międzypodmiotowe, ale wymagają kontroli licencji i podziału według uczestników.",
        "- N=1–3 służy do walidacji inżynierskiej i badań wewnątrzosobniczych; nie uprawnia do uogólnień populacyjnych.",
        "- Dane z Tobii Eye Tracker 5 i Muse S Athena podlegają osobnym bramkom legalnego dostępu.",
        "",
        "Szczegóły: [metodologia](../methodology.md), "
        "[ograniczenia aparatury](../hardware.md), "
        "[kamienie milowe](../publication-milestones.md).",
        "",
    ]
    index = target / "index.md"
    index.write_text("\n".join(summary), encoding="utf-8")
    generated.append(index)
    return generated


if __name__ == "__main__":
    pages = generate()
    print(f"Generated {len(pages)} MkDocs pages from canonical papers/ sources")
