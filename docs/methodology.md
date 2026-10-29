# Common evaluation and reproducibility protocol

## Problem definitions
- **Affective state:** operationalized against explicitly timed self-report (valence/arousal) or dataset annotations, not claimed to be directly read from physiology.
- **Cognitive workload:** task-demand manipulation plus behavioral outcome, subjective report (e.g., NASA-TLX where appropriate) and optional sensor proxies; difficulty condition is *not* ground-truth internal workload.
- **Expression/kinematics:** observable behavior; cannot automatically be equated with emotional state or diagnosis.
- **Engineering utility:** latency, jitter, device uptime, missingness, CPU/GPU/RAM, workload and robot safety metrics.

## Splits, leakage and statistics
1. Freeze the primary hypothesis, comparator, primary outcome and exclusion rules before evaluating held-out data.
2. Public data: leave-one-subject-out or subject-grouped cross-validation as appropriate; external corpus test when compatible. Session/trial grouping required. All scaling, feature selection, imputation and hyperparameter selection fit within train folds only.
3. Single-person: multiple dated sessions, pre-specified block randomization/counterbalancing, washout for adaptation, uncertainty reported across sessions/days, permutation/randomization inference over assigned blocks where justified. No inflated N from frames/windows.
4. Report effect sizes, subject- or session-clustered confidence intervals, calibration (ECE/Brier), coverage/risk under abstention, base rate, class imbalance, and negative controls. Mark exploratory endpoints explicitly and correct multiplicity when applicable.
5. Main baselines: majority, simple regularized linear models, time/frequency handcrafted features, unimodal models, no-adaptation/no-abstention control and a literature-appropriate strong method after review.
6. Reproduce seed, hardware/software hashes, data versions, preprocessing graph, timing origin, fixed splits and full evaluation tables. Evaluate latency p50/p95/p99, packet loss and missing modalities, not only mean throughput.

## N=1–3 claims and ethics
Strong within-person repeatability and intervention engineering are publishable directions, but no population effects, clinical validity, diagnostic validity or robust between-person generalization can be inferred. Check institutional requirements for consent, researcher self-participation, documentation and publication before recording. Simulation is not a human study. No participant recruitment is needed for secondary analysis of existing licensed datasets.

## Gates
G0 access/legal/data provenance verified; G1 protocol and baseline frozen; G2 tests, quality and baselines reproduced; G3 primary experiment evaluated with uncertainty and negative controls; G4 independent check of novelty/limitations, manuscript and artifacts ready. If a gate fails, revise research question rather than present unsupported results.