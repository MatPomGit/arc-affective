# P01: candidate channel-order links in FACED's original preprocessing path

Version 0.1.0, 2026-10-30. **Code-path evidence only, not original EEG or validated spatial mapping.** Issues #14, #22, #30.

## Separating three processing paths

1. **Original FACED acquisition:** the 2023 [Scientific Data descriptor](https://doi.org/10.1038/s41597-023-02650-w) describes Neuracle NeuSen.W32 (CPz reference, AFz ground), two acquisition cohorts, six channel-name differences and electrode positions deferred to supplementary Tables S2/S3.
2. **Original preprocessed EEG (*.pkl) route:** a [public third-party copy of preprocessing code](https://github.com/Rmin-cmd/FACED_Code/blob/8aa55c1b6d503d92b5db5a87b576a361115a6a02/Preprocessing/Preprocessing.py), pinned mirror commit `8aa55c1b6d503d92b5db5a87b576a361115a6a02`, Git blob `d59f503029cc75451284040f3adfe3ca3f95c63f`, includes `set_eeg_reference(ref_channels='average')`. It also relabels the final two original cohort-2 channels to `A2` and `A1`, and in `channel_modify` reorders cohort 1 using indices `[0..15,18..31,17,16,32]` (last index 32 is a marker channel, **not EEG**). The [public `main.py`](https://github.com/Rmin-cmd/FACED_Code/blob/8aa55c1b6d503d92b5db5a87b576a361115a6a02/Preprocessing/main.py) calls `average_ref` and `channel_modify`.
3. **NEMAR BIDS derivative:** pinned [`nemarDatasets/nm000112`](https://github.com/nemarDatasets/nm000112/tree/2577b0bbc089b49e828cd98d80445133634b6d34) converter uses `read_raw_bdf` and `write_raw_bids` without explicit channel reordering or rereferencing. The declared 32 EEG channel labels of sub-000 and sub-061 are as observed from their public `channels.tsv` sidecars. The two paths **must not be treated as interchangeable**.

## Code-implied index linkage, not spatial sensor verification

Reconstructing the preprocessed array's channel indexing from the two public BIDS name inventories yields the following **candidate index pairs**. This is not an applied transformation and not an approved electrode alias file.

| Cohort-1 recorded label | Cohort-2 recorded label | Basis |
| --- | --- | --- |
| T3 | T7 | Source positions correspond after array alignment |
| T4 | T8 | Source positions correspond after array alignment |
| T5 | P7 | Array reorder of cohort 1 |
| T6 | P8 | Array reorder of cohort 1 |
| A2 | HEOR | Final channel relabeled `A2` in cohort 2 |
| A1 | HEOL | Final channel relabeled `A1` in cohort 2 |

Both raw-label inventories contain 32 names, 26 common and six nonmatching per cohort. **Code operations do not verify physical topology**. In particular EOG-like `HEOR/HEOL` labels versus mastoid-like `A1/A2` are clinically/anatomically nontrivial; no inference of real scalp positions follows from their software alignment. No authority of the mirror has been established by comparing it with the original Synapse `Code/` release. The original author-provided `Electrode_Location.xlsx` and Tables S2/S3 were not obtained in this review, although an online supplementary DOCX filename has been identified: `41597_2023_2650_MOESM1_ESM.docx`.

## Fail-closed source inspector

The new `src/arc_affective/p01_faced_preprocessing_order.py` reads the pinned Python text as an AST, checks the exact Git blob, explicit cohort reorder and the averaging-reference call, then enumerates *index-level links* only for two unchanged, pinned BIDS channel-name inventories. It cannot load raw EEG, apply channel aliases to recordings, confirm anatomic locations, verify unit handling, or certify sample-level equivalence. All conclusions remain `analysis_ready=false`, `apply_to_raw_or_BIDS_allowed=false`, `physically_equivalent=false`.

To inspect a previously reviewed, local copy of the public script:

```bash
PYTHONPATH=src python -m arc_affective.p01_faced_preprocessing_order \
  --preprocessing-python /authorized/public/Preprocessing.py
python -m unittest discover -s tests -p test_p01_faced_preprocessing_order.py -v
```

No independent source file, original `Electrode_Location.xlsx` or participant EEG was copied into this repository. Test cases use synthetic code text and pinned public channel names.

## Explicit next research gates

Before any physical montage or sparse-channel comparison, verify the original `Code/` release in Synapse or a trusted archival checksum, examine original supplementary S2/S3/electrode spreadsheet and decide whether EOG-like channels belong in the EEG sensor set, and distinguish the author's average-reference processed `*.pkl` from the independently converted BIDS signal. Obtain authorized signals before any amplitude/reference validation. M0/M1/M2 remain OPEN.
