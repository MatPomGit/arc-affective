# P01: pinned FACED converter and BDF header audit

Version 0.1.0 · 2026-10-30 · source-level E0 validation, no EEG data. Related issues #14, #22 and #30.

## Pinned public conversion source

Reviewed the public [`nemarDatasets/nm000112/code/faced.py`](https://github.com/nemarDatasets/nm000112/blob/2577b0bbc089b49e828cd98d80445133634b6d34/code/faced.py) at parent commit `2577b0bbc089b49e828cd98d80445133634b6d34`. Expected **Git blob object SHA-1** `cced146163b93fd51d277d66cb7eee6bea55f983`. Do not treat a current upstream main as identical to this pinned revision.

Static source inspection indicates:

| Code location | Documented action | Evidence boundary |
| --- | --- | --- |
| `_maybe_patch_bdf_units`, lines 90–147 | For the BDF `physical_dimension` header, temporarily change corrupted `?V` text to `uV`; samples are not intentionally rewritten | The code comments describe 33 affected files and 90 unaffected, but **we have not independently counted or verified BDF headers** |
| `main`, lines 585–632 | Calls header patcher, `read_raw_bdf(..., preload=False)`, `_create_annotations_from_evt`, then `write_raw_bids` | No explicit `raw.set_eeg_reference`, `raw.set_montage` or `raw.rename_channels` in this converter. This says nothing about implicit BDF/MNE metadata interpretations |
| `_create_annotations_from_evt`, lines 368–451 | Reads `evt.bdf` triggers, imports `After_remarks.mat` ratings and associates video IDs | The upstream conversion code may contain mistakes; real original EEG/ratings and complete run-level checksums have **not** been cross-validated |
| `_finalize_dataset`, lines 636–663 | Marks BIDS output `dataset_type='derivative'` and sets a CC-BY-4.0 metadata field | That field is not independent proof of access rights for every source binary |

The [original Chen et al. publication](https://doi.org/10.1038/s41597-023-02650-w) documents the acquisition device Neuracle NeuSen.W32 and **CPz reference / AFz ground**. Its *separate, author-provided preprocessed EEG* applies bandpass, artifact mitigation, common-average reference, resampling to 250 Hz and cohort-channel reordering. **These transformations must not be attributed automatically to the independent BIDS conversion script**. In the public BIDS sidecars, `Manufacturer=Biosemi` and `EEGReference=n/a` remain unexplained. Additionally, cohort-1 and cohort-2 channel naming differs: see [provenance QA](P01-faced-provenance-qa.md).

## Offline fail-closed tool

`src/arc_affective/p01_converter_qc.py` inspects inert Python source using the standard-library AST, checks the exact Git blob fingerprint, detects the calls `read_raw_bdf`, `write_raw_bids`, metadata annotation loaders and optional reference/montage mutations. It flags any source mismatch. It does **not** import or execute upstream code.

A second function inspects **BDF metadata header bytes only**: global first 256 bytes plus 256 bytes per channel, including `physical_dimension` field. It distinguishes canonical `uV` from corrupted `?V`, recognizes other units as requiring review, checks declared header length and returns counts without samples or a modified file.

For a locally reviewed copy of the exact source, after verifying upstream access and license:

```bash
PYTHONPATH=src python -m arc_affective.p01_converter_qc \
  --converter-python /authorized/public/code/faced.py
python -m unittest discover -s tests -p test_p01_converter_qc.py -v
```

Option `--header-only /authorized/header.bin` takes an **explicitly extracted metadata-only header**, never a complete raw EEG file. No original data or converter source is copied into the P01 repository.

The source checks establish only source-level structure. Even a PASS **never proves** the digital reference, true electrode positions, sensor equivalence, physically meaningful amplitude scale, or actual source-to-derivative signal identity.

## Pending authoritative material

The original paper cites Supplementary Tables S2/S3 and `Electrode_Location.xlsx` for the two cohorts. The canonical [article supplementary-material entry](https://www.nature.com/articles/s41597-023-02650-w) identifies a DOCX, but the tables could not be retrieved and inspected in this work. **No six-channel alias mapping has been inferred.** The upstream public Git tree (1004 entries, `truncated=false`) does not contain `electrodes.tsv` or `coordsystem.json`.

To authorize cross-cohort or external-corpus inference, obtain original tables and approved recording metadata, verify unit header corrections against source headers, compare output and original sample amplitudes/references, and freeze a versioned channel-identity/position mapping. Main P01 M0/M1/M2 issues stay open.
