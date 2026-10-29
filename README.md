# ARC Affective — Multimodal Affective and Cognitive State Computing

Engineering research programme on **affective and cognitive state monitoring**, uncertainty-aware multimodal sensing, adaptive games, human–computer interaction and safe robot control.

**Scope:** Polish engineering/science disciplines AEEiTK (automation, electronics, electrical engineering and space technologies), ITiT (computer engineering and telecommunications), and informatics; signal processing, machine learning, control and embedded systems. Not clinical diagnosis, psychological test validation, medical monitoring or emotion mind-reading.

## Research constraints

- **Local studies:** 1 researcher by default, at most 3 adult university staff volunteers; repeated-measures/N-of-1 experiments and engineering benchmarks.
- **Generalisation:** only external datasets with verified access/terms and participant-disjoint evaluation. N=1 is never evidence of population-level accuracy.
- **Hardware:** Muse S Athena (EEG/optional fNIRS/PPG; research-data access unverified), Tobii Eye Tracker 5 (**gaming interaction only under the standard licence**, not raw-data capture), Leap Motion (exact revision/SDK to verify), RGB webcams.
- **No paid dependencies:** if data/software licence is paid or inaccessible, disable that modality or use an open-data/engineering fallback. No paid API, hosted GPU or subscription required.
- **Reproducibility:** preregistered primary endpoints and splits; leakage checks, baselines, uncertainty, ablations, data provenance and local offline tests.
- **Privacy:** no raw biometric recordings or third-party datasets in Git; use consent, controlled local storage and publish only licensed, de-identified outputs.

## Eight publication tracks

| ID | Paper / distinctive contribution | Validation |
|---|---|---|
| [P01](papers/P01-low-channel-transfer.md) | Sparse EEG representations under dataset and montage shift | Public EEG datasets, 0 local participants |
| [P02](papers/P02-robust-fusion.md) | Uncertainty- and missing-modality-aware multimodal fusion | Licensed multimodal public data, 0 local participants |
| [P03](papers/P03-personal-drift.md) | Personalised, drift-aware workload estimation over sessions | Repeated self-study, N=1 (up to 3) |
| [P04](papers/P04-private-vision.md) | Privacy-preserving on-device facial-behaviour modelling | Public video + local non-retained webcam sessions |
| [P05](papers/P05-hand-workload.md) | Hand-kinematic quality and task-demand estimation | Leap Motion N=1–3 |
| [P06](papers/P06-adaptive-game.md) | Uncertainty-gated adaptation of game difficulty | Offline evaluation + randomised N-of-1 blocks |
| [P07](papers/P07-safe-hri.md) | Gaze/hand intent and fail-safe robot teleoperation | ROS 2/Gazebo simulated robot + N=1–3 |
| [P08](papers/P08-edge-systems.md) | Real-time, fault-tolerant multimodal edge inference | Repeatable CPU/GPU device benchmarks, N=0–1 |

See [scientific-discipline mapping](docs/discipline-map.md), [portfolio and non-overlap rules](docs/portfolio.md), [architecture](docs/architecture.md), [hardware rights](docs/hardware.md), [dataset registry](docs/datasets.md), [experimental methods](docs/methodology.md), [privacy and ethics](docs/governance.md), [execution order](docs/roadmap.md), [56 detailed issue milestones](docs/publication-milestones.md), [dependency graph](docs/research-dependencies.md) and [conditional schedule](docs/research-schedule.md).

**Work tracking:** [P01](https://github.com/MatPomGit/arc-affective/issues/5) · [P02](https://github.com/MatPomGit/arc-affective/issues/6) · [P03](https://github.com/MatPomGit/arc-affective/issues/7) · [P04](https://github.com/MatPomGit/arc-affective/issues/8) · [P05](https://github.com/MatPomGit/arc-affective/issues/9) · [P06](https://github.com/MatPomGit/arc-affective/issues/10) · [P07](https://github.com/MatPomGit/arc-affective/issues/11) · [P08](https://github.com/MatPomGit/arc-affective/issues/12). Shared foundation: [hardware #1](https://github.com/MatPomGit/arc-affective/issues/1), [datasets #2](https://github.com/MatPomGit/arc-affective/issues/2), [platform #3](https://github.com/MatPomGit/arc-affective/issues/3), [governance #4](https://github.com/MatPomGit/arc-affective/issues/4).

**Publication planning:** eight paper epics each have seven verified evidence-gates M0–M6 (56 canonical implementation issues). Current status is PLANNED, not 56 completed experiments. Native GitHub Milestones entities have not been set; stage tracking is done via linked issues.

## Documentation — MkDocs / GitHub Pages

The browsable research handbook is configured for [GitHub Pages](https://matpomgit.github.io/arc-affective/) (available after Pages is enabled and the deployment workflow succeeds). It includes all eight paper protocols, evidence gates M0–M6, diagrams, datasets, sensors and the complete issue register.

**Local build (Python 3.11+):**

```bash
python -m pip install -r requirements-docs.txt
python scripts/sync_mkdocs.py
python -m unittest discover -s tests -p 'test_docs.py' -v
mkdocs build --strict
mkdocs serve
```

Sources for paper documentation remain in `papers/`; `docs/papers/` is a generated, ignored directory. Deployment uses [Docs / MkDocs](.github/workflows/docs.yml) on GitHub Actions (public-repository standard runner; no metered API). [Publishing instructions](docs/operations/pages.md).

## Project layout

```text
papers/             Eight research protocols and publication gates
docs/               Architecture, sensors, datasets, methods, governance, roadmap
src/arc_affective/   Minimal zero-dependency event-schema and synthetic smoke test
tests/              Offline deterministic unit tests
data/               Local-only, gitignored, never commit raw recordings
```

## First offline smoke test

```bash
python -m unittest discover -s tests -v
PYTHONPATH=src python -m arc_affective.cli --output data/synthetic-demo.jsonl --events 100
```

Windows PowerShell: `$env:PYTHONPATH="src"; python -m arc_affective.cli --output data/synthetic-demo.jsonl --events 100`.

Synthetic events are not physiological data or a trained affect estimator. They verify only schema and local event serialization. **No inference, accuracy, latency benchmark or sensor compatibility is claimed.**

## Governance

Work through issues and focused PRs. Run the offline tests before merge. Do not launch GitHub-hosted paid compute or train on sensitive data by default. Human-subject protocols require institutional ethics/privacy assessment before collection, including an N-of-1 study.