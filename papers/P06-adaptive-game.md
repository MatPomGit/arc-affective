# P06 — Uncertainty-Gated Affective Adaptation for Single-User Digital Games

**Discipline:** game AI, adaptive control, HCI. **Authors/participants:** up to 3 authors; prospective participants N<=3 (default N=0 or N=1).

## Research question
Does a confidence-gated controller improve a pre-specified game outcome compared with static and random difficulty policies for one player?

## Distinct technical contribution
Closed-loop difficulty control conditioned on uncertainty/quality and explicit abstention, evaluated against matched non-affective policies.

## Data and feasible instrumentation
Unity or lightweight open game; N=1 cross-over blocks, N<=3 optional; webcam/Leap behavioral features, optional licensed Athena; Tobii 5 may only be used interactively within permitted use (no gaze logs).

## Experimental design and baselines
Offline policy replay on public data or synthetic events; randomized/counterbalanced fixed, performance-only, shuffled-input and uncertainty-gated conditions; predefined washout and safety limits. Do not claim emotion detection from game performance alone.

## Primary evaluation metrics
Task completion, error rate, challenge target deviation, control stability, intervention frequency, p95 feedback latency, self-report as secondary.

## Threats to validity
Strong carryover/learning confounds, implicit leakage from success to game controller and sample limitation.

## Go/no-go publication gate
Gated policy stable under missingness; randomized evidence of within-person engineering effect with negative controls, no generalisation claim.

## Agent-sized implementation steps (one JRA each)
- [ ] 1. Implement deterministic game metrics and non-affective baseline.
- [ ] 2. Integrate quality/uncertainty-gated policy with failsafe fixed mode.
- [ ] 3. Pre-register and run randomized within-person blocks.
- [ ] 4. Analyze block effects and draft P06.

## Status
**PLANNED — no measurements, experiments or publication claims completed.** Follow [methods](../docs/methodology.md), [privacy](../docs/governance.md), [hardware limits](../docs/hardware.md), and [portfolio boundaries](../docs/portfolio.md).
