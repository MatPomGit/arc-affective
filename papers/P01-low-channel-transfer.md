# P01 — Sparse-Channel EEG Affect Representation Under Cross-Dataset and Montage Shift

**Discipline:** EEG signal processing, domain generalization, statistical learning. **Authors/participants:** up to 3 authors; prospective participants N<=3 (default N=0 or N=1).

## Research question
Does a low-channel model remain calibrated on held-out people and across corpora when reference montage and acquisition domains change?

## Distinct technical contribution
Channel sparsity × corpus shift factorial benchmark with explicit montage-reference compatibility, transfer-risk uncertainty and no false Muse-equivalence claims.

## Data and feasible instrumentation
DEAP, DREAMER and AMIGOS (only after licence/data audit); public EEG only. No local volunteers necessary.

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
