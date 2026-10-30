# P01: original FACED Recording_info.csv reconciliation bridge

Version 0.1.0, 2026-10-30. Status: **implemented and synthetically tested; original source CSV NOT obtained**. Issue #30, also #14 and #22.

The [original FACED data descriptor](https://doi.org/10.1038/s41597-023-02650-w) identifies `Recording_info.csv` in the Synapse project `syn50614194`, containing acquisition sample rates and per-subject upstream units. The [pinned public NEMAR conversion script](https://github.com/nemarDatasets/nm000112/blob/2577b0bbc089b49e828cd98d80445133634b6d34/code/faced.py) reads that source table with exact field names `sub`, `Sample_rate`, `Unit`, `Gender`, and `Age` (see `code/faced.py` lines 548–562). The converter comments at lines 88–109 warn that **`Unit` describes upstream raw recording units, not the BDF output header**; it explicitly says 33 BDF headers had a `?V` unit-label corruption that needed textual correction, rather than recalibrating sample values. This comment remains **unverified against original BDF**.

## New read-only bridge

`src/arc_affective/p01_source_recording_reconcile.py` accepts the authentic original `Recording_info.csv`, *only when obtained under the correct Synapse access conditions*. It checks the source `subXXX` rows, `Sample_rate` and `Unit`; compares per-participant **metadata** sampling rates against the complete, immutable, previously audited NEMAR sidecar inventory at Git commit `2577b0bbc089b49e828cd98d80445133634b6d34`. For this pinned BIDS commit the **correct, individually verified** sidecar frequency pattern is 250 Hz for suffixes **004–005 and 008–060** (55 entries) and 1000 Hz for **000–003, 006–007 and 061–122** (68 entries). It reports only aggregate mismatch directions, totals, source-unit labels and SHA-256 of the CSV, never age, gender or subject identity.

The tool **does not** access raw EEG, inspect BDF headers, perform resampling, change signal amplitude or update sidecars. A full 123-row valid source CSV enables a 123-row metadata count comparison with the pinned upstream README's stated counts (31 at 250 Hz, 92 at 1000 Hz). A partial source CSV is **not** considered evidence for or against that global count. Even if every rate matches, the BIDS reference is unknown and physical montage remains unverified. The `Unit` column is NEVER a scaling instruction.

```bash
PYTHONPATH=src python -m arc_affective.p01_source_recording_reconcile \
  --recording-info-csv /authorized/source/Recording_info.csv
python -m unittest discover -s tests -p test_p01_source_recording_reconcile.py -v
```

The CSV must be the authentic source. Do not commit the source file or any demographics to Git. Report only aggregate rates, mismatch counts and SHA-256. The synthetic tests use imaginary ages/gender and exact source CSV schema; **they do not prove what the original CSV contains**.

## Evidence and next step

Original source `Recording_info.csv` and supplementary S2/S3 / `Electrode_Location.xlsx` remain **not obtained** in this run. Therefore the prior documented conflict of **BIDS 55/68 versus README 31/92** is still a source-to-derivative metadata discrepancy, *not validated signal corruption*. The latest public [NEMAR release v1.1.4](https://nemar.org/dataset/nm000112?v=v1.1.4) reports a CC-BY-4.0 derivative licence, which is distinct from the original source dataset access requirements. Source permission and version must be independently verified.

The next scientific work item is to obtain `Recording_info.csv` through the official Synapse project access process, use this tool to establish a source metadata SHA and discrepancy count, then independently check BDF header sampling rates and unit-scale provenance before the prospective M1 freeze. Original coordinates and digital reference transformation remain separate blockers.

## Corrective read-back of participant-rate alignment (2026-10-30)

An independent comparison of the original source-reconciliation software against
the actual [pinned public sidecars](https://github.com/nemarDatasets/nm000112/tree/2577b0bbc089b49e828cd98d80445133634b6d34)
found a substantive **bug in the previously merged PR #94**: its
`PINNED_BIDS_250_SUBJECTS = range(6, 61)` assumed a contiguous run
of 250-Hz recordings and silently misassigned **four participant rows**.
The BIDS sidecars directly report:

| Source suffix | BIDS `SamplingFrequency` |
| --- | --- |
| 000–003 | 1000 Hz |
| 004–005 | 250 Hz |
| 006–007 | 1000 Hz |
| 008–060 | 250 Hz |
| 061–122 | 1000 Hz |

The aggregate distribution remains **55 at 250 Hz and 68 at 1000 Hz**, so
previous census totals and the README-to-sidecar **31/92 vs 55/68**
discrepancy are unchanged. Critically, the old **row-level** comparison
could falsely report mismatches, or matches, against an original CSV even
with apparently correct global totals.

The read-only reconciliation now uses a source-pinned exact membership
set: `{004,005} ∪ {008,…,060}`. Two new boundary-case regression tests
assert both exact membership and that source CSV rates matching the
public sidecars for 004–007 yield zero differences, while two reversed
rates yield exactly one mismatch in each direction. The synthetic
original CSV still must never be confused with genuine original
`Recording_info.csv`, which remains **unobtained**.

No raw BDF frequency or signal content was read; this fixes the
comparison contract at the *text metadata* level only.
