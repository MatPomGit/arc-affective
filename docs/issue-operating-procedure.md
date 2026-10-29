# Standard operating procedure for publication issues and JRA work
Version 1.0.0 · 2026-10-29

## Workflow and naming

- Publication epic `[Pxx]`: one umbrella issue per distinct paper, #5–#12.
- Seven child work issues `[Pxx/M0] ...` through `[Pxx/M6]`, indexed by [publication-milestones.md](publication-milestones.md).
- One checkbox = one **JRA**, a single independently inspectable agent work item; split larger units into smaller explicit tasks in the same issue before work.
- No task is marked completed because code was proposed: cite the exact PR, merge SHA, test command, logs/metrics and supporting documentation.
- Epics and their checklists are the source of truth for milestone status. Native GitHub Milestone entities are not created in this iteration.

## Definition of ready (DoR)

1. Confirm upstream gate/issue complete, or document an independently safe mock/simulator task.
2. Identify rights, privacy and ethical clearance for **any** prospective human recording, including self-experiment.
3. Define deliverable paths, one objective primary acceptance test and relevant negative control.
4. Specify local CPU/GPU/OS and zero-cost reproducibility route; prohibit metered compute by default.
5. Confirm working branch isolation, no open overlapping PR and no persistent runner execution of untrusted code.

## Definition of done (DoD)

- [ ] Implementation or experiment actually ran; no invented timing/accuracy/permissions.
- [ ] Unit/integration tests and grouped-split/retention/safety checks pass for the changed path.
- [ ] Results include data/protocol version, source rights, seeds, baseline, units, statistical unit and limits.
- [ ] PR reviewed and merged; README/paper/milestone tracker consistent and exact SHA linked.
- [ ] If gate failed, issue remains blocked with recorded evidence and narrower fallback; not silently closed.
- [ ] Corresponding parent-epic checklist item manually marked done when the issue is verifiably closed.

## Research claims and boundaries

- Primary fields: AEEiTK, ITiT, computer science. Not diagnosis, clinical validity, psychiatric inference or psychological effectiveness.
- Separate observable movement, experimental task demand, subjective valence/arousal and internal latent cognitive state.
- N=1–3 voluntary local prospective participants (up to 3 staff), public-data cohorts may be larger but must be person/session independent.
- No unlicensed gaze extraction from Tobii 5; Muse Athena raw EEG/fNIRS/PPG blocked until valid research access proven.
- For robot work simulation constraints are not certification; no estimator can directly bypass safety governor.

## G0–G4 crosswalk

| Common gate | Paper milestones | Proof |
|---|---|---|
| G0 lawful data/device and novelty feasible | M0 | Access and literature audit, explicit fallback |
| G1 preregistered hypothesis and splits | M1 | Frozen metrics, controls, stop criteria |
| G2 runnable data QA + reference comparators | M2–M3 | Tests, exact data splits and baseline tables |
| G3 credible experimental evidence | M4–M5 | Algorithm, negative controls, intervals and failure analysis |
| G4 ready for independent review/venue | M6 | Manuscript, disclosures, figures, scripts and reproducibility manifest |

## Versioning and issues
Use SemVer for actual released code (not aspirational milestone completions) and date all protocol/manuscript exports. Paper source lives in `papers/`; ephemeral raw data in ignored local `data/`; derived non-identifying results can be committed only when rights allow. All images/plots have axes, units, source and cited method.
