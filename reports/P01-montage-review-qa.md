# P01 montage proposal evidence gate

Version 0.1.0 (2026-10-30). **Synthetic software and public metadata only**. Issues #14, #22, #30.

## Evidence hierarchy

The original [FACED article](https://doi.org/10.1038/s41597-023-02650-w) states that the acquisition cohorts used the same physical electrode placement with six differently named channels; the authoritative correspondence is described in Supplementary Tables S2/S3. The paper's supplemental file `41597_2023_2650_MOESM1_ESM.docx` is indexed, but **could not be retrieved and read in this audit**. Neither that document nor original `Electrode_Location.xlsx` was processed, and no EEG signal was downloaded. Thus the six individual electrode identities and positions remain *unverified*.

Pinned [NEMAR BIDS metadata](https://github.com/nemarDatasets/nm000112/tree/2577b0bbc089b49e828cd98d80445133634b6d34) for sub-000/sub-061 have 32 names each; **26 labels are textually shared**. A [third-party mirror of the FACED preprocessed code](https://github.com/Rmin-cmd/FACED_Code/blob/8aa55c1b6d503d92b5db5a87b576a361115a6a02/Preprocessing/Preprocessing.py) provides six *candidate index-level* links, not validated anatomical positions. A separate downstream [montage implementation](https://github.com/loopin51/eeg-state-event/blob/5f43afc33428675cfc10bb3052b572ec139035f4/src/ese/data/montage.py) implements `HEOR → A2` and `HEOL → A1` as an **assumption**; it is not independent measurement proof.

The original article documents acquisition reference CPz/ground AFz, but the derivative BIDS reports manufacturer Biosemi and unknown reference. Its conversion script does not explicitly rereference channels. Exact physical equivalence, reference transforms, channel types and signal calibration remain unresolved.

## Implementation

`src/arc_affective/p01_montage_review.py` takes **user-proposed** sets of 2, 4 and 8 channels. It checks exact names in both pinned BIDS channel inventories, flags cohort-specific/unknown labels and describes whether the proposed sets are nested.

Even a shared-name match is `text_only_not_approved`. An entire family can achieve only `design_review_only`, never a physical approval or permission to process EEG. Any nonshared label (notably T3/T7, T5/P7, A1/A2, HEOR/HEOL) blocks the affected subset. The tool deliberately does not guess electrodes, pick a scientifically optimal montage, convert reference, download samples or select a hypothesis after looking at held-out data.

Usage with an *illustrative* candidate file (not a validated scientific configuration):

```json
{"2":["F3","F4"],"4":["F3","F4","C3","C4"],"8":["F3","F4","C3","C4","P3","P4","O1","O2"]}
```

```bash
PYTHONPATH=src python -m arc_affective.p01_montage_review --family-json /private/proposal.json
python -m unittest discover -s tests -p test_p01_montage_review.py -v
```

A pass says only that labels occur in both public sidecars. **No automatically approved physical 2/4/8 montage is generated.**

## Remaining empirical gates

Directly inspect and archive the authoritative S2/S3 / `Electrode_Location.xlsx`, and distinguish scalp EEG channels from mastoid/EOG recording labels. Independently verify the exact raw-to-BIDS reference transform and amplitude units using licensed checksum-pinned data. After that review, predefine valid channel sets and freeze M1 before empirical held-out scoring. M0/M1/M2 remain open.
