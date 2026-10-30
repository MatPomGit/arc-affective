# P01 negative controls and feature sensitivity (E0)

Version 0.1.0, 2026-10-30. Related issues: #42 (M3), #50 (M4), #5.

The executable `src/arc_affective/p01_controls.py` adds two **synthetic software-validation procedures**, not affect classification findings.

**Training-only label permutation:** In each outer participant-disjoint LOSO fold, shuffle the labels of *complete trials* within each training participant. Preserve all repeated window labels belonging to the same trial, plus each participant's label prevalence. Fit the trial-weighted linear baseline and select regularization in nested inner grouped folds using only shuffled training labels. Evaluate the fixed original outer-test trials without changing their labels. Different outer folds use deterministic fold-specific seeds.

This tests sensitivity to the feature/label relationship under a specifically conditional null. It does not generate a valid statistical $p$-value for real EEG, provide a general permutation test over nonexchangeable trials or guarantee removal of confounds. Temporal structure and blocked experimental design may require a different exchangeability scheme.

**Leave-one-feature-out sensitivity:** Run the same grouped baseline evaluation for the original synthetic feature vector and each removal of one synthetic feature. Report **all** cases rather than selecting the best on the outer-test metrics. These fabricated scalar features are **not** EEG electrodes; deleting a feature is not equivalent to simulating a new physical montage/reference and cannot support a channel-sparsity claim.

Reproduce, without data downloads or paid dependencies:

```bash
PYTHONPATH=src python -m arc_affective.p01_controls --seed 7 --subjects 5 --trials 4
python -m unittest discover -s tests -p test_p01_controls.py -v
```

No original EEG is acquired or processed. Results are marked `E0_synthetic_software_test_only`, `real_eeg_used=false`, `external_validation=false`, `rights_verified=false`. The output includes fold ordinal and aggregate statistics only, never participant IDs. No significance claims, confidence intervals from synthetic controls or publication-ready results are established.

Next for P01: freeze the label/score and montage protocol, check original dataset permissions, validate original channel coordinates/reference and demonstrate the same controls on a lawfully usable dataset. Maintain M3/M4 as open.
