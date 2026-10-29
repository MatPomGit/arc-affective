# P03 — Longitudinal Drift-Aware Personal Workload Estimation With Label-Efficient Recalibration

**Discipline:** online learning, human-computer interfaces, concept drift. **Authors/participants:** up to 3 authors; prospective participants N<=3 (default N=0 or N=1).

## Research question
Can within-person performance be maintained across sessions with fewer recalibration labels than periodic retraining?

## Distinct technical contribution
Evaluation of drift detection and bounded recalibration cost across days for a personalized, nonclinical workload proxy.

## Data and feasible instrumentation
Repeated webcam/Leap sessions N=1 default, up to 3 university staff; Muse EEG optional only after licence gate.

## Experimental design and baselines
Pre-register sessions on multiple days; randomized n-back/Stroop/visual search task difficulty, no clinical conclusions. Compare frozen, periodic-retrain and drift-triggered models; chronological forward-chaining tests; label budget matched.

## Primary evaluation metrics
Within-person prediction error, latency to recover, labels consumed, drift false alarms, session-level confidence intervals.

## Threats to validity
Practice effects, fatigue, day/time and task difficulty are confounders; label is not latent state truth.

## Go/no-go publication gate
Replicated within-person benefit under chronological evaluation and budget-equivalent controls; no population generalization claim.

## Agent-sized implementation steps (one JRA each)
- [ ] 1. Pre-register longitudinal tasks and approval/privacy pathway.
- [ ] 2. Build webcam/Leap or synthetic pipeline with session manifests.
- [ ] 3. Run randomized, repeated N=1 sessions with strict temporal splits.
- [ ] 4. Evaluate drift, label budgets, uncertainty, manuscript.

## Status
**PLANNED — no measurements, experiments or publication claims completed.** Follow [methods](../docs/methodology.md), [privacy](../docs/governance.md), [hardware limits](../docs/hardware.md), and [portfolio boundaries](../docs/portfolio.md).
