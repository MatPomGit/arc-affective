# P01 FACED acquisition provenance and BIDS conflicts

Version 0.1.0, 2026-10-30. This is a **source-document/derivative-metadata review**, not EEG signal verification. Relevant issues #14, #22 and #30.

## Two separate evidence levels

**Authoritative acquisition description:** Chen et al., *Scientific Data* 10:740 (2023), [DOI 10.1038/s41597-023-02650-w](https://doi.org/10.1038/s41597-023-02650-w), section "Data acquisition", explicitly states that FACED was recorded with the **Neuracle NeuSen.W32** wireless EEG system at 250 or 1000 Hz, using **CPz as acquisition reference** and **AFz as ground**, with 32 wet electrodes. The authors explicitly state that two nonoverlapping cohorts used the same placement but had six differently named electrodes; Supplementary Tables S2 and S3 must be consulted for physical correspondence. A subsequent average or mastoid reference is possible but must not be presumed to have been applied.

**Public derivative metadata:** `nemarDatasets/nm000112`, upstream [Git commit `2577b0bbc089b49e828cd98d80445133634b6d34`](https://github.com/nemarDatasets/nm000112/tree/2577b0bbc089b49e828cd98d80445133634b6d34), two recording sidecar pairs:
- `sub-000/eeg/sub-000_task-watchingVideoClips_eeg.json`: `Manufacturer=Biosemi`, `EEGReference=n/a`, `EEGGround=n/a`, 32 EEG channels, 1000 Hz.
- `sub-061/eeg/sub-061_task-watchingVideoClips_eeg.json`: the same manufacturer/reference/ground fields, plus `EEGPlacementScheme=n/a`.
- `_channels.tsv` lists 32 EEG channels in each: 26 common names, six unique names per cohort. Cohort sub-000 has `T3,T4,T5,T6,A1,A2`, whereas sub-061 has `T7,T8,P7,P8,HEOR,HEOL`.

These are **conflicts and omissions in the derivative text metadata**, not proof that raw signals used a BioSemi amplifier. The original recording system is Neuracle according to the source paper. Physical channel correspondence is not established by name alone. In particular, do **not** equate `A1/A2` with `HEOR/HEOL`, which may serve different anatomical roles; inspect the original supplementary tables and conversion code before drawing any mapping conclusion.

## Gate implementation

`src/arc_affective/p01_faced_provenance.py` is a source-aware, **read-only** local sidecar auditor. It reports conflicting manufacturer/reference/ground values, unexpected EEG channel inventory and placement omissions. Its two-cohort comparison gives an explicit channel-name diff and blocks automatic aliasing. **It never writes replacement fields, performs rereferencing, downloads raw EEG, or certifies equivalent positions.** If a derivative's metadata were corrected to match the source paper, physical equivalence would still require signal provenance and transformation validation.

```bash
PYTHONPATH=src python -m arc_affective.p01_faced_provenance \
  --eeg-json /private/faced/sub-000/eeg/sub-000_task-watchingVideoClips_eeg.json \
  --channels-tsv /private/faced/sub-000/eeg/sub-000_task-watchingVideoClips_channels.tsv \
  --other-eeg-json /private/faced/sub-061/eeg/sub-061_task-watchingVideoClips_eeg.json \
  --other-channels-tsv /private/faced/sub-061/eeg/sub-061_task-watchingVideoClips_channels.tsv
python -m unittest discover -s tests -p test_p01_faced_provenance.py -v
```

Paths are illustrative; actual public files were read via GitHub, not downloaded locally for end-to-end execution. The automated regressions use only synthetic copies of these public metadata patterns.

**Decision:** The previously marked unknown *acquisition* reference is partly resolved from the **primary publication (CPz/AFz)**. The derivative BIDS fields remain unverified and contradictory. Cross-cohort physical montage/reference and cross-corpus transfer gates remain **BLOCKED**, and no binary EEG was accessed. Next: examine Supplementary Tables S2/S3, exact converter behavior and any raw recording headers with duly authorized signals; document the resulting explicit coordinate/reference operators for each cohort. The manuscript and PR #30 remain unready for empirical transfer claims.

## Pinned converter source read-back (2026-10-30)

The [full static audit](P01-converter-qa.md) distinguishes the original paper's **common-average reference of its preprocessed dataset** from the **separate BIDS conversion**: the latter invokes `read_raw_bdf` and `write_raw_bids` but has no explicit `set_eeg_reference`, channel rename, or montage assignment. The converter handles potentially corrupted `?V` BDF unit headers with a temporary label correction before MNE reading (code comments: 33/123 affected, not independently checked against signal files). Neither the derived signal's true reference nor physical 6-channel aliases can be asserted from this static inspection. S2/S3 and `Electrode_Location.xlsx` still need direct review.

## Public independent preprocessing code read-back (2026-10-30)

A separately pinned [third-party copy of FACED's preprocessed `*.pkl` pipeline](https://github.com/Rmin-cmd/FACED_Code/blob/8aa55c1b6d503d92b5db5a87b576a361115a6a02/Preprocessing/Preprocessing.py) includes `set_eeg_reference(ref_channels='average')`, a cohort-1 channel-index permutation, and renaming of the final cohort-2 channels to A2/A1. This provides a **candidate array-index linkage** between six previously unmatched BIDS name labels. See [preprocessed-order evidence QA](P01-faced-preprocessed-order-qa.md). **The mirror is not independently authenticated** against original Synapse `Code/`, and source-paper S2/S3 positions remain unchecked. Do not apply the candidate links to the independent BIDS signal or claim physical equivalence. E0 software-only validation.

## Six-recording source-pinned sidecar spot check (2026-10-30)

A manual read-back via the GitHub repository connector of **six actual public metadata pairs** at upstream commit `2577b0bbc089b49e828cd98d80445133634b6d34` inspected subject-number suffixes **000, 030, 060, 061, 090 and 122**. This is a 6/123 **sample**, *not* a population census or any EEG sample analysis.

| Property | Cohort 1 (000,030,060) | Cohort 2 (061,090,122) |
| --- | --- | --- |
| `_eeg.json` frequency (Hz) | 1000, 250, 250 | 1000, 1000, 1000 |
| `Manufacturer` | Biosemi in all 3 | Biosemi in all 3 |
| `EEGReference`, `EEGGround` | n/a in all 3 | n/a in all 3 |
| Channel count and ordering | 32, identical to sub-000 | 32, identical to sub-061 |
| Channel types | EEG for all 32 | EEG for all 32, including HEOR/HEOL |

Thus 250 and 1000 Hz both occur **within cohort 1**, and sample rate must **never** be inferred solely from cohort assignment. The channel-name layout was consistent in this six-recording sample, but 117 recordings remain unexamined. The BIDS label `EEG` for `HEOR/HEOL` is a **derivative metadata classification**, not proof of physical EEG-sensor type or mastoid location. This sample does not verify source raw amplitude units or original reference. <https://github.com/nemarDatasets/nm000112/tree/2577b0bbc089b49e828cd98d80445133634b6d34>

`audit_recording_sample()` and the existing provenance CLI now accept an optional *local, explicitly specified* JSON manifest listing `subject_number`, `eeg_json` path and `channels_tsv` path for as many as 123 observations. They validate strict channel order, sampling rates, unit labels and sample coverage **without exporting participant IDs or reading raw BDF**. Even a full 123-recording sidecar census cannot approve scientific equivalence.

Illustrative locally reviewed manifest (paths must be to permitted **text metadata**):

```json
[
  {
    "subject_number": 0,
    "eeg_json": "/authorized/sub-000_task-watchingVideoClips_eeg.json",
    "channels_tsv": "/authorized/sub-000_task-watchingVideoClips_channels.tsv"
  }
]
```

```bash
PYTHONPATH=src python -m arc_affective.p01_faced_provenance --cohort-manifest-json /authorized/sidecar_manifest.json
python -m unittest discover -s tests -p test_p01_faced_provenance.py -v
```

This work could not retrieve the original supplementary S2/S3 tables (including the linked DOCX) or `Electrode_Location.xlsx` through current public retrieval paths. Source anatomical mapping remains blocked.
