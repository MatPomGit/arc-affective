# Agent instructions — arc-affective

1. Follow [research scope](README.md), [roadmap](docs/roadmap.md), [methods](docs/methodology.md), [ethics](docs/governance.md) and [hardware licence matrix](docs/hardware.md).
2. Treat each paper in [portfolio](docs/portfolio.md) as a distinct evidence/novelty package. No duplicated primary finding across manuscripts.
3. Never collect/export raw gaze streams from Tobii Eye Tracker 5 under its consumer licence. Do not invoke Tobii Pro SDK for this consumer tracker. Do not access raw Muse Athena signals unless the permitted research workflow is confirmed; do not circumvent licensing.
4. Never add real EEG, pupil, face videos, hand trajectories linked to identifiable people, consent documents, API keys, or restricted benchmark datasets to Git. See .gitignore.
5. No paid services or GitHub-hosted workflows without explicit cost review. Tests must run locally using standard Python and synthetic fixtures.
6. N=1 to N=3 research is for within-person, feasibility and engineering validation only. Public dataset evaluations must avoid participant, session and temporal leakage.
7. Maintain a hypothesis/protocol, reference baselines, sensitivity analysis, uncertainty, and pass/fail evidence gate for every manuscript. Distinguish task condition from measured mental state and avoid clinical claims.
8. For robotics, use simulation first, separate intent estimation from safety supervision and require a deterministic abort/hold path.
9. Keep README, papers, docs and issue acceptance criteria consistent. Version actual code/artifacts; preserve provenance. No untrusted code on persistent self-hosted runners.
