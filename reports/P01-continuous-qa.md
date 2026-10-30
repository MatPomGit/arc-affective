# P01: continuous valence regression software QA

Version 0.1.0, 2026-10-30. Status: **synthetic-only candidate**, not a frozen experimental protocol or EEG result. Relates to #22 (M1), #30 (M2) and #42 (M3).

## Purpose

FACED's `events.tsv.Valence` is a continuous 0–7 self-report. The separate stimulus category `binary_label` / `targeted_valence` does **not** measure each participant's actual self-report and must not substitute as the target. To test prospective endpoint candidate A without consulting EEG data, the new `src/arc_affective/p01_continuous.py` implements a standard-library-only, deterministic, **synthetic** regression harness.

- Independent outer held-out unit: participant (LOSO). All trial windows stay together.
- Inner subject-grouped LOSO chooses L2 penalty via mean held-out *participant* MSE, strictly within the outer training pool.
- Trial and participant-balanced weights in model training (each participant contributes equally, each trial and window equally within participant/trial). Z-scoring and mean-target constant comparator use training data only.
- The model is a standardized L2 ridge regression, compared against the constant prediction equal to the **training** mean self-reported valence. Predictions are not clipped to [0, 7] in order to disclose extrapolation. Out-of-range predictions are counted.
- Window outputs are averaged per trial before scoring. For each outer participant, calculate Lin's concordance correlation coefficient, CCC, and MSE. Report equal-participant averages, eligible CCC fold count and individual fold ordinals with no participant identifiers.
- A constant true target (zero within-participant target variance) produces CCC `null`, not an artificial perfect score. A constant model prediction with variable true targets has CCC 0. For realistic datasets, participant CCC can be unstable with few trials; report exclusions, study-level inference, and uncertainties separately.

**No selection of endpoint was made.** This path tests a feasible continuous alternative to the older synthetic binary logistic classifier. **Do not compare their synthetic CCC and BA results or select a metric after examining test results.** The user must adopt one primary estimand in the prospectively frozen protocol after reviewing acquisition/reference, rating semantics and rights.

### Reproduction

```bash
PYTHONPATH=src python -m arc_affective.p01_continuous --subjects 5 --trials 5 --seed 7
python -m unittest discover -s tests -p test_p01_continuous.py -v
```

The report is marked `E0_synthetic_software_test_only`, `real_eeg_used=false`, `protocol_frozen=false`, `original_rating_alignment_verified=false`, and `recording_rights_verified=false`. No CI values are eligible for manuscript performance tables or scientific confidence intervals.

### Gates before empirical inference

Confirm original legal access and dataset release checksums; verify physical EEG reference and channel geometry; verify event triggers and self-report-to-stimulus linking in original source files; predeclare primary target and CCC handling (including constant-trial participants, participant exclusions and multiple comparisons); select legal data and lock protocols before actual EEG test analysis. Maintain issues #14, #22, #30 and #42 open.
