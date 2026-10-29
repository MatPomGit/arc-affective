# P02 — Calibrated Multimodal Affect Fusion Under Asynchrony and Missing Sensors

**Discipline:** multimodal ML, reliability engineering. **Authors/participants:** up to 3 authors; prospective participants N<=3 (default N=0 or N=1).

## Research question
Does calibrated reliability-gated fusion degrade more safely than naive concatenation on synchronized multimodal corpora?

## Distinct technical contribution
Reliability-masked late fusion that detects absent, delayed or corrupted sensor modalities and abstains under untrusted inference.

## Data and feasible instrumentation
AMIGOS facial video+EEG only if actually accessible and synchronized; alternative auditable multimodal corpus. N=0 local.

## Experimental design and baselines
Verify time alignment and shared valence/arousal annotations; compare unimodal, concatenation, attention, reliability-gated late fusion. Simulate realistic dropouts, delay and degradation at evaluation time, with train-only calibrator.

## Primary evaluation metrics
CCC/RMSE for valence-arousal, AUROC if binarized a priori, coverage-risk AUC, Brier/ECE, p95 inference latency, corruption robustness.

## Threats to validity
Public dataset may not distribute all modalities; label aggregation and synchronization may make a joint comparison invalid.

## Go/no-go publication gate
G0 must confirm licensed paired synchronized streams. Otherwise change dataset/claim before experimental runs.

## Agent-sized implementation steps (one JRA each)
- [ ] 1. Audit actual paired synchronized multimodal data and permissions.
- [ ] 2. Implement masked fusion with explicit quality channels and no-leak splits.
- [ ] 3. Compare dropout/delay/abstention ablations and confidence intervals.
- [ ] 4. Independent reproducibility and manuscript package.

## Status
**PLANNED — no measurements, experiments or publication claims completed.** Follow [methods](../docs/methodology.md), [privacy](../docs/governance.md), [hardware limits](../docs/hardware.md), and [portfolio boundaries](../docs/portfolio.md).
