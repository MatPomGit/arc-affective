# P01 BIDS sidecar metadata QC, version 0.1.0 (2026-10-30)

**Evidence: E0 local metadata/synthetic-test validation, not actual EEG experimentation.** Related M0/M1/M2 issues #14, #22 and #30. This gate does not grant access to EEG, certify a valid scalp reference or freeze the paper's preregistration.

## Source facts

The publicly described [FACED NEMAR v1.1.4](https://nemar.org/dataset/nm000112?v=v1.1.4) release (DOI 10.82901/nemar.nm000112) advertises CC BY 4.0, 123 participants, 32-channel EEG and 250/1000 Hz acquisition depending on recording. The [author-maintained BIDS conversion description](https://github.com/nemarDatasets/nm000112) states events include video markers and valence/arousal self-ratings, which must be reconciled against the original trial reports. This is a public catalogue/README review; **no original `_eeg.json`, `_channels.tsv`, `_events.tsv`, `_electrodes.tsv` or raw signal was fetched or inspected in this implementation**. Real BIDS sidecar structure and rating availability must be verified per recording. Large files and identifiable participant information stay outside Git.

## New offline gate

`src/arc_affective/p01_bids_qc.py` reads explicitly provided local BIDS JSON/TSV **text sidecars only**. It checks:
- EEG sampling rate, channel-name uniqueness and units; explicit/non-empty EEGReference, with missing reference held as unknown.
- Event onset/duration, a researcher-selected *continuous self-report* rating column (default `Valence`, subject to actual capitalization in sidecars) and missing-label accounting. It does not assert that ratings are temporally aligned with video stimuli.
- If present, EEG electrode x/y/z and documented coordinate system/units, normalized to metres for cautious metadata comparison. Missing frame, reference, shared electrodes or inconsistent coordinates block even a *candidate* comparison.
- No inference of equivalent devices based on electrode names alone. A successful metadata comparison means only `candidate_metadata_match_only`, not physical montage/reference equivalence or transfer permission.

Local use after separately confirming data access:

```bash
PYTHONPATH=src python -m arc_affective.p01_bids_qc \
  --eeg-json /private/faced/sub-000/eeg/sub-000_task-watchingVideoClips_eeg.json \
  --channels-tsv /private/faced/sub-000/eeg/sub-000_task-watchingVideoClips_channels.tsv \
  --events-tsv /private/faced/sub-000/eeg/sub-000_task-watchingVideoClips_events.tsv \
  --rating-column Valence
python -m unittest discover -s tests -p test_p01_bids_qc.py -v
```

The paths are **illustrative**, not verified actual file names. The CLI never touches EEG signals or outputs trial labels, participant IDs or original event values. An optional `--electrodes-tsv` and `--coordsystem-json` supplies spatial data. Ranges/interpretation of valence and trial-to-rating matching are not established; the tool does not declare a corpus analysis-ready.

## Next empirical gates

1. Authorize access in accordance with actual dataset and institutional terms. Pin version and establish local SHA-256 manifest with existing `p01_registry.py`.
2. Inspect actual pinned sidecars, confirm BIDS inheritance, channel locations/reference, mixed sample rates, unit conversion, rating-column semantics and event/stimulus alignment.
3. Document allowed channel subsets and explicit reference operator. If no 2/4/8-channel positional/reference equivalence exists, mark cross-corpus cell **not estimable**.
4. Freeze M1 protocol before running primary held-out model comparisons; only then run actual corpus-level data analyses.

Unit tests use synthetic BIDS-like JSON/TSV metadata. Never present them as original FACED measurements.
