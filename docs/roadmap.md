# Implementation roadmap — execution units (JRA)

**JRA = Jednostka Realizacji Agenta:** one self-contained, reviewable ChatGPT implementation session with a defined input, files changed, tests and acceptance evidence. Tasks should be split when they cannot be verified in one session.

## Phase A: foundation (first)
- A1 [1 JRA] Repo governance, eight protocols, licence/data gates, event schema and offline test.
- A2 [1 JRA] Local device inventory and compatibility report (Tobii licence, Athena research access, Leap revision); no collection until gates pass.
- A3 [1 JRA] Audit actual dataset access/licences and freeze reproducible split manifests.
- A4 [1 JRA] Clock-sync and recording design: synthetic signal injection, timestamp audit, fault injection. No sensor integrations assumed.

## Phase B: algorithms and datasets
- B1–B3 [3 JRA] P01 preprocessing, sparse-channel baselines, grouped/cross-corpus evaluation.
- B4–B6 [3 JRA] P04 local facial-feature extractor, privacy benchmark and held-out annotations.
- B7–B9 [3 JRA] P02 masks/fusion/calibration, systematic corruption and ablations.

## Phase C: N-of-1 device research
- C1–C3 [3 JRA] P05 validated Leap interface, controlled hand task and session-split analysis.
- C4–C6 [3 JRA] P03 repeated-session protocol, adaptive recalibration, drift tests.
- C7–C9 [3 JRA] P06 deterministic game baseline, preregistered randomized N-of-1 blocks, offline safety/utility analysis.

## Phase D: robotics and edge
- D1–D3 [3 JRA] P07 simulated ROS 2 scene, intent/safety separation, fault trials.
- D4–D6 [3 JRA] P08 end-to-end p95/p99 latency, scheduler/queue-policy ablation, multi-device CPU fallback.

## Phase E: publications
Per manuscript: literature/novelty audit, G0–G4 evidence, figures/tables with units, IEEE-style bibliography, artifact availability and limitations. The eight tracks can proceed asynchronously but cannot claim completion based on a paper outline.

**No-cost rule:** do not enable metered GitHub Actions, third-party paid APIs, extra hardware purchases or paid data licences. Work locally or use existing authorized self-hosted infrastructure after safety review.