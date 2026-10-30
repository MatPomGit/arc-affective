# P01 continuous-valence participant uncertainty QA

Version 0.1.0, 2026-10-30. **Only E0 synthetic software evidence.** Relevant issues #22, #42 and #58.

## Estimand and limitations

For the candidate continuous self-report outcome, compute one performance score per held-out participant after collapsing window predictions into trial predictions. Compare the standardized ridge regression and the train-only mean baseline in the *same* participant's evaluation fold. For concordance correlation coefficient (CCC), report $d_i=\mathrm{CCC}_{\mathrm{ridge},i}-\mathrm{CCC}_{\mathrm{baseline},i}$. For mean squared error (MSE), report $d_i=\mathrm{MSE}_{\mathrm{baseline},i}-\mathrm{MSE}_{\mathrm{ridge},i}$. A positive value in either case favors ridge.

The offline `src/arc_affective/p01_continuous_inference.py` forms a **paired participant bootstrap** percentile interval by resampling whole held-out participant folds with replacement (2,000 replicates, seed 7 by default). This is a **descriptive pipeline check, not a confirmatory sampling interval**: LOSO folds overlap in training subjects; the fold differences are not strictly independent estimators of population-level model effects. Pre-registered empirical inference may require full-pipeline participant-cluster resampling with model refitting, an independent held-out cohort, or other defensible analyses of dependence.

**Missing/undefined CCC is not silently dropped.** If even one held-out participant has undefined CCC (for example, constant true ratings across that participant's trials), the complete-case CCC bootstrap is blocked with a count of missing participants and a `null` interval. MSE remains reportable if valid for all folds. This avoids selective exclusion and false confidence, but may render CCC infeasible as a primary endpoint in real datasets. Before freezing M1, choose and pre-specify handling of constant/near-constant participant targets, insufficient trial counts and confidence-interval strategy.

Reproduce without downloading any EEG:

```bash
PYTHONPATH=src python -m arc_affective.p01_continuous_inference
python -m unittest discover -s tests -p test_p01_continuous_inference.py -v
```

Never treat synthetic interval values as empirical measurements. The output explicitly indicates `E0_synthetic_software_test_only`, no real EEG, no rights audit, no frozen protocol, no p-value and no valid confirmatory inference. This tool exports only fold counts and aggregate metrics, not participant IDs or trial ratings.

## Remaining gates

Original signal rights, true EEG reference, channel/montage compatibility, original stimulus rating checks, nonleaky preprocessing, a documented continuous endpoint and prespecified inferential target. Issue #22 remains open.
