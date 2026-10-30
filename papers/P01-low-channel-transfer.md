# P01 — Sparse-Channel EEG Affect Representation Under Cross-Dataset and Montage Shift

**Discipline:** EEG signal processing, domain generalization, statistical learning. **Authors/participants:** up to 3 authors; prospective participants N<=3 (default N=0 or N=1).

## Research question
Does a low-channel model remain calibrated on held-out people and across corpora when reference montage and acquisition domains change?

## Distinct technical contribution
Channel sparsity × corpus shift factorial benchmark with explicit montage-reference compatibility, transfer-risk uncertainty and no false Muse-equivalence claims.

## Data and feasible instrumentation
DEAP, DREAMER and AMIGOS (only after licence/data audit); open-licensed fallback candidates GAMEEMO v3 and FACED NEMAR v1.1.4 (also requiring actual file and reference QA). Public EEG only. No local volunteers necessary.

## Experimental design and baselines
Create montage registry; compare available channel subsets (not claiming Muse channel equivalence), spectral/entropy features and compact CNN; grouped LOSO in each corpus, external corpus only if labels/reference harmonize. Compare with full-channel, linear and shuffled-label baselines.

## Primary evaluation metrics
Macro-F1, balanced accuracy, AUROC where applicable, concordance for continuous targets, ECE, Brier, CPU time, clustered 95% CI.

## Threats to validity
Montage locations may differ; stimulus, sampling and label semantics confound transfer; restricted datasets may not be available.

## Go/no-go publication gate
Show reproducible subject-disjoint evaluation, positive delta against appropriate low-channel baseline with CIs, and explicit limitations for any non-equivalent montage.

## Agent-sized implementation steps (one JRA each)
- [ ] 1. Audit DEAP/DREAMER/AMIGOS licenses, electrodes, reference and labels.
- [ ] 2. Implement harmonized-but-non-equivalent sensor subset experiments with leakage checks.
- [ ] 3. Train baselines and corpus-held-out evaluation with clustered uncertainty.
- [ ] 4. Independently reproduce, literature-check and draft P01.

## Status
**PLANNED — no measurements, experiments or publication claims completed.** Follow [methods](../docs/methodology.md), [privacy](../docs/governance.md), [hardware limits](../docs/hardware.md), and [portfolio boundaries](../docs/portfolio.md).


## Manuscript work in progress (2026-10-30)
A substantive [IEEEtran LaTeX draft](https://github.com/MatPomGit/arc-affective/blob/main/manuscripts/P01/main.tex) now contains a literature-positioned introduction, explicit train-only LOSO evaluation, hardware/montage eligibility rules, negative controls, planned reporting and limitations. The [analysis protocol](https://github.com/MatPomGit/arc-affective/blob/main/papers/P01-protocol.md) is a **candidate**, not a registered study. Newly relevant 2026 work reports severe identity confounding (DOI: [10.3390/s26175327](https://doi.org/10.3390/s26175327)); a generic low-channel result would overlap it. Actual rights/metadata audit, experiment and publication claims remain blocked; the manuscript has no fabricated outcomes.

## P01 grouped baseline software (2026-10-30)

A runnable [synthetic-only nested LOSO evaluation](https://github.com/MatPomGit/arc-affective/blob/main/src/arc_affective/p01_evaluation.py) now includes participant-disjoint outer folds, training-only scaling, train-only prevalence and L2 logistic regression, inner subject-grouped hyperparameter selection and explicit single-class held-out handling. See [QA and limitations](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-evaluation-qa.md). This is software E0, **not** a completed EEG baseline, real corpus result or M3 evidence gate; data rights, original EEG adapters, M1 analysis freeze and empirical validation are still pending.

Evaluation correction (2026-10-30): trial-averaged predictions and equal per-trial training weights address window-level pseudo-replication for trial-labelled outcomes. Final real EEG validation still requires the pre-analysis protocol, dataset and montage gates.

### Participant-level uncertainty tooling (2026-10-30)

[Parowany bootstrap uczestników](https://github.com/MatPomGit/arc-affective/blob/main/src/arc_affective/p01_uncertainty.py) dla prób-aggregated Brier ma osobne [QA i ograniczenia](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-statistics-qa.md). Moduł i demonstracja są wyłącznie syntetyczną walidacją E0. Brak rzeczywistych przedziałów ufności i wyniku eksperymentalnego.

### Synthetic negative controls and feature sensitivity (2026-10-30)

Implemented a [train-only participant-blocked trial-label permutation](https://github.com/MatPomGit/arc-affective/blob/main/src/arc_affective/p01_controls.py) and leave-one-synthetic-feature-out sensitivity matrix. [Software QA and limitations](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-controls-qa.md) identify that a synthetic feature omission is **not** physical EEG montage ablation and that these checks yield no valid p-values or real EEG results. M3/M4 remain open.

### FACED BIDS metadata inspection gate (2026-10-30)

Introduced [offline BIDS sidecar QC](https://github.com/MatPomGit/arc-affective/blob/main/src/arc_affective/p01_bids_qc.py), with synthetic-only unit tests and [metadata-only audit notes](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-bids-metadata-qa.md). Explicitly refuses to equate matching channel names with proven physical montage equivalence. No original EEG signals or actual FACED BIDS sidecars were opened; M0/M1/M2 still require independent verification and source rights.

Source-pinned public FACED BIDS spot-check (2026-10-30): sub-000 `_eeg.json` has `EEGReference: n/a` and `EEGGround: n/a`, 32 EEG channels at 1000 Hz; `events.tsv` has 28 rated video rows and 5 unrated technical entries. Physical reference/montage transfer claims remain **blocked**. See [metadata audit](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-bids-metadata-qa.md). No raw signal used.
