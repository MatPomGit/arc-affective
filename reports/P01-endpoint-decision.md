# P01 primary outcome: unresolved protocol decision

Version 0.1.0 · 2026-10-30 · Status: **candidate decision record, NOT frozen or preregistered** · Owner issue #22

## Inconsistency requiring action

The canonical [M1 issue #22](https://github.com/MatPomGit/arc-affective/issues/22) currently specifies *subject-level macro-F1 or CCC*, conditional on target definition, whereas [P01 protocol](../papers/P01-protocol.md) and the manuscript Methods specify **balanced accuracy** as primary and **Brier** as calibration diagnostic for a derived binary valence classification. This discrepancy must be resolved explicitly, before examining empirical EEG model results.

The original [FACED paper](https://doi.org/10.1038/s41597-023-02650-w) specifies 0–7 continuous self-report ratings on 12 dimensions. The observed BIDS `Valence` is numeric self-report, not the experimental `targeted_valence` positive/neutral/negative category. The manuscript currently proposes binarization only if scientifically supported in advance.

## Decision candidates (not a post hoc optimization)

| Choice | Primary estimand | Primary metric | Required a priori decisions |
| --- | --- | --- | --- |
| **A: continuous self-report valence** | participant-held-out real-valued rating | CCC on trial-level predictions, with participant-aware uncertainty | Scale and time mapping; model family, calibration, handling of baseline/ceiling, how to estimate CCC when subject variance is small; group aggregation |
| **B: categorical valence** | predeclared binary or categorical *self-report* outcome | balanced accuracy at participant level | Physiologically and psychometrically defensible threshold/categories defined from the original rating scale or training data only; do not use stimulus target labels to substitute participant report; rare-class and single-class participant handling |
| **C: standardized discrete category** | evoked target/stimulus category | macro-F1 | A clearly distinct research hypothesis about stimulus category, not an EEG measure of subjective valence |

**Recommendation for scientific review:** Prefer A for FACED's continuous self-reported valence when original label semantics and scoring conditions are confirmed. This prevents unnecessary discretization, but would require new train-only continuous-regression baselines and CCC uncertainty tooling; existing P01 logistic/BA tests are only *software fixtures for B*. The choice cannot be made from observed performance or a search over the held-out data.

For B, ensure the primary endpoint in issue #22, `papers/P01-protocol.md` and `manuscripts/P01/sections/methods.tex` is identical after approval. For A, revise all three to CCC with a prespecified continuous mapping and baseline, and retain BA as a clearly secondary exploratory analysis if scientifically justified.

## Current stop rules

- M1 remains open. Dataset-rights and original EEG reference provenance remain unresolved.
- No original EEG model predictions or empirical confidence intervals have been produced.
- Synthetic code may run to check correctness but not to select the primary estimand by performance.
- Do not use BIDS `binary_label` (video's targeted category) as a proxy for the participant's continuous `Valence`.
