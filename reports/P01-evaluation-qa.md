# P01: subject-disjoint synthetic baseline evaluation

Version 0.1.0 · 2026-10-30 · Related issues: #30, #42, #22, #5.

**Evidence status: E0, synthetic software validation ONLY.** This is not an EEG decoding experiment or a completed P01/M3 milestone. No DEAP/DREAMER/AMIGOS, FACED, GAMEEMO or consumer Muse raw data are loaded. Rights, electrode reference and label compatibility gates from [P01 data audit](P01-data-audit.md) remain unresolved.

## Implemented

- Outer leave-one-participant-out (LOSO) folds, grouped by participant, never splitting a participant's trial windows between train and test.
- A train-only majority/prevalence comparator and simple batch-gradient L2-regularized logistic regression with train-only z-scoring.
- Nested, subject-grouped hyperparameter choice using training-fold Brier score; outer held-out labels and feature distributions are not consulted during training, scaling or regularization selection.
- Per-participant Brier and balanced accuracy; if a held-out participant contains only one class, balanced accuracy is **not estimable** and remains null. Fold ordinal and counts are reported without exporting participant IDs.
- Deterministic synthetic fixtures with multiple windows per trial to exercise leakage checks. Eight regression tests cover access boundaries, class degeneracy, trial consistency and invariance to altered outer-test observations.

## Reproduction

```bash
PYTHONPATH=src python -m arc_affective.p01_evaluation --subjects 6 --trials 8 --seed 7
python -m unittest discover -s tests -p test_p01_evaluation.py -v
```

Results can be written using `--output results/p01-synthetic.json`; existing files are not overwritten. Synthetic report fields explicitly state `real_eeg_used=false`, `external_validation=false`, `protocol_frozen=false`, `recording_rights_verified=false`, `confidence_intervals=null`.

## Limits and next steps

This is an algorithmic fixture, not a full EEG pipeline. Input features are fabricated scalar vectors; no EEG filtering, channel interpolation, montage harmonization, artifact removal, train-validated label binarization or externally licensed dataset adapter is implemented. Mean participant-level scores here are only synthetic QA quantities, not accuracy estimates for any human population. Do not derive scientific findings or claim novelty from them.

Next: verify rights and original signal metadata, freeze candidate dataset and valence coding before any held-out data run, implement corpus adapter with checksums and explicit reference/coordinate QA, then perform fully grouped baseline reproduction, calibration and participant-clustered uncertainty analyses. M1 and M2/M3 acceptance criteria remain open.
