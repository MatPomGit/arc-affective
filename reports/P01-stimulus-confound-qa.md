# P01: stimulus-identity confounding and dual-disjoint evaluation gate

Version 0.1.0, 2026-10-30. **E0 synthetic pipeline validation only. No EEG was analyzed.** Issues #14, #22 and #42.

## New 2026 evidence

Gerster, Sirotina, Orlovskii, Hertz, Champaud, Guarino and Tulli, *Stimulus identity rather than emotion drives EEG classification on the FACED dataset*, bioRxiv, first posted **16 June 2026**, DOI [10.64898/2026.06.12.731889](https://doi.org/10.64898/2026.06.12.731889), [reproducibility code](https://github.com/moritz-gerster/faced-stimulus-confound). **This is a preprint, not a confirmed peer-reviewed result.** The authors report that cross-subject classification of stimulus-assigned emotion categories may reflect specific films and repeated temporal patterns; performance drops with individual self-report labels, and retaining only one video per emotion increases accuracy. Their reported LinearSVC cross-subject nine-class accuracy is 39.4% for the baseline and 26.8% using self-report categories. These are **their results, not P01 experiments**, and these nine-class results do not directly quantify bias for P01's continuous 0–7 valence CCC.

The FACED design repeats the **same 28 videos** across participants. Thus a participant-only LOSO fold can legitimately hold out the participant while **retaining every film in training**. This tests adaptation to a new *person watching known films*, **not generalization to new stimuli**. Overlapping 1-second EEG windows within a trial are also not independent test samples. Nine-class stimulus-assigned targets may be ill-posed for leave-video-out tests when an emotion category becomes absent from training; do not use a test-derived remapping to hide this problem.

## Proposed scientific controls before empirical inference

1. **Stimulus-identity-only baseline:** predict the continuous participant-reported `Valence` from the identity of the film using mean ratings of that film in training participants only. Compare its participant-level MSE/CCC with EEG models under **exactly the same LOSO splits** and with an overall training-only response-mean baseline. It uses no EEG. A strong clip-only comparator would constrain attribution to neural features rather than establish that emotion is unobservable.
2. **Jointly participant- and film-disjoint sensitivity experiment:** hold out a participant and a film. Train on the rectangular complement (other people and other films), excluding the two cross-cells from model fitting, calibration, normalization and any hyperparameter choice. The intersection contains a **single rated film trial** in a fully crossed design; CCC is undefined for that single trial. Pooling predictions into a properly prespecified larger outer test collection or an independent new-stimulus corpus is required before CCC inference. This check is a sensitivity analysis and has a *different estimand* from ordinary person-held-out LOSO.
3. **Preplanned failure and scarcity handling:** log the number of training films in each emotion category, clip coverage, missing participant-film pairs, and test target distributions. Do not select a stimulus subset after inspecting test performance. If a category is not identifiable in training, report **not estimable** instead of conflating movie identity with category.

The `src/arc_affective/p01_stimulus_control.py` module validates a *synthetic* participant/film/trial self-report table, reports train-only film-prior MSE against the overall train mean in participant-LOSO, and enumerates jointly disjoint folds that hold out both axes without using the cross-cells for training. It reports only aggregate metrics, not identities or individual ratings. **It does not use EEG, fit neural models, or claim new-stimulus generalization.**

```bash
PYTHONPATH=src python -m arc_affective.p01_stimulus_control
python -m unittest discover -s tests -p test_p01_stimulus_control.py -v
```

All results from this invocation are synthetic software invariants. Existing participant-only P01 continuous ridge baselines remain valid *software demonstrations*, **not demonstrated emotion decoding**. No existing inferential results have been reclassified or frozen.

## Gate consequences

- M1: Declare whether the primary estimand is **new participant / previously seen film** or **new participant / unseen film**. Decide whether CCC is evaluable on the resulting held-out units. Prespecify clip-only and train-prior comparators, balancing across participants and films, and exact split manifests before empirical fitting.
- M2: Record film/video ID and repeated presentation per participant as mandatory provenance fields. Maintain independent person, film and trial keys and prevent same-trial window reuse.
- M3: Do not claim an EEG-specific signal effect without comparing against the film-only self-report prior under identical test folds, and treating the three task definitions as separate outcomes.

**Still blocked:** authentic source `Recording_info.csv`, physical channel mapping S2/S3, digital reference of BIDS, original rating provenance, dataset rights, empirically validated EEG and a frozen protocol.
