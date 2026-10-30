# P01 participant-cluster uncertainty QA

Version 0.1.0 · 2026-10-30 · Related issues: [#42](https://github.com/MatPomGit/arc-affective/issues/42), [#58](https://github.com/MatPomGit/arc-affective/issues/58).

**E0: statistical software validation only.** New module `src/arc_affective/p01_uncertainty.py` provides paired participant-level percentile bootstrap confidence intervals for *trial-aggregated* Brier scores. It does not read real EEG and cannot establish empirical generalization.

## Statistical estimand and assumptions

For each held-out participant, compute exactly one trial-aggregated Brier score per model on the **same trials and same split**. Define $d_s = B_{s,\mathrm{reference}} - B_{s,\mathrm{candidate}}$. The target is the equally weighted mean $\overline{d}$ across **independent participants**, not a mean over EEG windows. Resample whole participants *with replacement*, preserving their two model scores together. The 95% percentile interval is calculated from the bootstrap distribution. A positive difference indicates a lower (better) Brier score for the candidate.

Participants' raw identifiers are used only in memory for uniqueness checks; result dictionaries contain aggregate counts and statistics, no IDs. This API refuses fewer than four participants, duplicate participant keys, nonfinite scores or unsupported parameters. Bootstrap confidence intervals do **not** establish causal effects, representativeness, or validity of the participant independence assumption. Confidence bounds may be unstable for small samples or dependent datasets. No multiple-comparison correction is applied; an eventual confirmatory claim needs predeclared primary contrast, study design and multiplicity handling.

## Reproduction

```bash
PYTHONPATH=src python -m arc_affective.p01_uncertainty
python -m unittest discover -s tests -p test_p01_uncertainty.py -v
```

The CLI runs a reproducible **synthetic** demonstration and marks `real_eeg_used: false`, `dataset_licence_verified: false` and `evidence: E0_synthetic_software_test_only`. Do not copy synthetic interval values into a manuscript results table.

## Remaining evidence gates

Verify original dataset rights, EEG montage/reference, trial annotations and allowed data use; freeze valence definitions and paired full/sparse comparison; perform independent participant-level held-out inference on approved source files; predeclare the uncertainty procedure and report failures/negative controls. P01 M3 and M5 remain open until real evidence exists.
