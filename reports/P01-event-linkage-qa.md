# P01 FACED event-to-stimulus linkage audit

Version 0.1.0 · 2026-10-30 · Issues #14, #22, #30

**This work checks text metadata and the event-conversion description, not EEG recordings.** It is an engineering validation gate, not a scientific affect-prediction result.

## Pinned public evidence

Source: [nemarDatasets/nm000112 at commit 2577b0bbc089b49e828cd98d80445133634b6d34](https://github.com/nemarDatasets/nm000112/tree/2577b0bbc089b49e828cd98d80445133634b6d34). Source tables: `stimuli/stimuli.tsv`, `sub-000/eeg/sub-000_task-watchingVideoClips_events.tsv`, and EEG JSON sidecar; provenance narrative: upstream `README.md` and `code/faced.py`.

The original [Scientific Data FACED descriptor](https://doi.org/10.1038/s41597-023-02650-w) documents 28 videos, 123 participants and 12 continuous ratings on 0–7 scales. The upstream conversion account links trigger values 1–28 to video onset/offset markers 101/102 and joins self-report data from `After_remarks.mat`. This is an account of conversion logic, **not a validation of its correctness** against raw `evt.bdf` and original rating files.

At the pinned upstream commit, manual data-derived aggregate checks (no individual ratings reproduced) find:

| Field | sub-000 observed |
| --- | --- |
| `stimuli.tsv` IDs | 28 distinct IDs, 1–28 |
| Rated `events.tsv` video rows | 28, one of each video ID |
| Duplicate/unknown IDs | 0 / 0 |
| Rated video rows with numeric `Valence` | 28 |
| Technical/unlinked events with no rating | 5 |
| Max video-duration deviation from primary or alternate presented duration | 0.361 seconds |
| Max `sample` vs `onset*1000` discrepancy | 0 samples |
| Targeted valence group vs `binary_label` discrepancies | 0 |

**Important distinction:** `stimuli.tsv.targeted_valence` is the film's targeted experimental valence grouping, whereas `events.tsv.Valence` is a participant self-report. They **must not** be conflated, or treated as identical binary targets. Several stimuli have the same film title; match on `video_index=stim_id`, not on film name. Source metadata documents a second clip-duration variant for stimulus 22; a structural QC must allow both supported versions.

The source BIDS sidecar for sub-000 has `EEGReference: n/a` and `EEGGround: n/a`, and the upstream repository does not provide electrode coordinates. Therefore **physical montage/reference equivalence remains blocked**, notwithstanding structural event integrity.

## Software

`src/arc_affective/p01_event_linkage.py` is a standard-library, offline local-sidecar validator. It tests complete stimulus coverage, uniqueness, trial-level valence presence and 0–7 range, missing technical markers, optional sample clock agreement, overlapping videos, targeted-category consistency and stimulus-duration deviations. It never returns per-event ratings, film titles or individual identifiers.

Example with authorized local text files (paths are illustrative):

```bash
PYTHONPATH=src python -m arc_affective.p01_event_linkage \
  --events-tsv /private/faced/sub-000/eeg/sub-000_task-watchingVideoClips_events.tsv \
  --stimuli-tsv /private/faced/stimuli/stimuli.tsv \
  --expected-clips 28 --sampling-hz 1000
python -m unittest discover -s tests -p test_p01_event_linkage.py -v
```

A structurally consistent report always sets `analysis_ready=false`, `original_rating_provenance_verified=false`, and `raw_eeg_trigger_alignment_verified=false`. Durations are checked against source metadata using a tolerance of 0.5 s, not against video bytes; source clip durations and trigger latency can differ.

## Missing evidence

Before claims about signal-label alignment or empirical generalization, obtain approved original EEG and `evt.bdf` access, validate source marker extraction, self-report-to-video association, recording-specific scaling/reference and reproducible dataset checksums. Freeze a primary endpoint and its target mapping in issue #22 *before* applying it to held-out EEG. No primary endpoint or scientific novelty is declared here.
