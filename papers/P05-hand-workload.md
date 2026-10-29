# P05 — Motion-Confound-Controlled Hand-Kinematic Proxies of Task Demand

**Discipline:** 3D perception, signal processing, HCI. **Authors/participants:** up to 3 authors; prospective participants N<=3 (default N=0 or N=1).

## Research question
Do hand-joint features add task-demand information after controlling for movement volume and gesture identity?

## Distinct technical contribution
Disentangle hand-motion intensity from task-demand effect using controlled interaction trials and invariant kinematic descriptors.

## Data and feasible instrumentation
Leap Motion hand joints after hardware/SDK/licence probe; N=1 repeated sessions, optional N<=3; no EEG needed.

## Experimental design and baselines
Randomized matching of similar motor tasks at different cognitive complexity, plus motor-only negative control; model velocity, jerk, tremor-band proxies and pose entropy without clinical labels. Test over days/held-out task types.

## Primary evaluation metrics
Incremental prediction over movement-only baseline, AUROC/Balanced Accuracy for task condition, session-level effect sizes, tracking dropout, jitter.

## Threats to validity
Hand kinematics primarily reflect movement; risk of spurious cognitive claims and SDK version incompatibility.

## Go/no-go publication gate
Show added value over speed/path-length baseline and negative control with session-based uncertainty; otherwise report motion-tracking study.

## Agent-sized implementation steps (one JRA each)
- [ ] 1. Identify exact Leap revision, legal Gemini/Orion SDK and export format.
- [ ] 2. Implement joint quality metrics and motor-demand-matched tasks.
- [ ] 3. Run N=1 counterbalanced trials and test task-held-out results.
- [ ] 4. Analyze confounds, reproducibility and write P05.

## Status
**PLANNED — no measurements, experiments or publication claims completed.** Follow [methods](../docs/methodology.md), [privacy](../docs/governance.md), [hardware limits](../docs/hardware.md), and [portfolio boundaries](../docs/portfolio.md).
