# ARC Affective — Research roadmap and implementation priorities

Current operating plan: [56 milestone issues and eight paper epics](publication-milestones.md) · [dependency graph](research-dependencies.md) · [conditional work waves](research-schedule.md) · [JRA workflow](issue-operating-procedure.md).

## Common foundation: cross-publication epics
1. [#1 hardware/legal](https://github.com/MatPomGit/arc-affective/issues/1): Tobii 5 licensed interaction only, Muse Athena raw research access gate, Leap generation/SDK, RGB camera privacy.
2. [#2 dataset evidence](https://github.com/MatPomGit/arc-affective/issues/2): DEAP/DREAMER/AMIGOS and facial corpora rights, pairing/montage/splits and hash manifests.
3. [#3 platform](https://github.com/MatPomGit/arc-affective/issues/3): timestamped monotonic JSONL schema, QA masks, synthetic data, replay and grouped evaluation.
4. [#4 governance](https://github.com/MatPomGit/arc-affective/issues/4): ethics, minimization/retention, no biological data in Git, G0–G4 evidence gates.

## Execution order (paper plan)
- **Start P08/P01/P04 M0–M2:** architecture and public-data works have no mandatory local participants.
- **Enable P02/P05 after true access gates:** paired temporal data for P02, verified Leap SDK and self-study approval for P05.
- **Enable P03/P06/P07 using verified components:** a validated data stream and reviewed protocol, not completion of another manuscript.
- **Proceed M3 baseline → M4 method → M5 evidence → M6 submission-ready source** for every paper; no promotion without demonstrated gate evidence.
- **Publication decision:** if results or novelty are weak, narrow claim and rerun permitted experiments; retain negative outcome if scientifically informative.

## Resource model
- The programme never requires more than 3 staff volunteers; N=1 or secondary public data preferred. Do not treat time windows as extra participants.
- Python/NumPy/MNE, OpenCV, Unity and ROS 2 where licences permit. Core synthetic tests require only local standard Python.
- No paid API, journal subscription, paid SDK, GitHub-hosted compute or new backend API required by this plan.
- Use one issue/PR per reviewable JRA when practical; no untrusted external PR builds on permanent self-hosted runners.
