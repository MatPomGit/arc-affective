# P01 — prospective analysis plan, candidate v0.1.0 (2026-10-30)

**Status: DRAFT, NOT preregistered or frozen.** This is the decision record to be finalized at issue #22 after rights/metadata audit #14 and #2. Sources: [manuscript](https://github.com/MatPomGit/arc-affective/blob/main/manuscripts/P01/main.tex), [methods](../docs/methodology.md).

**Question:** Does the participant-held-out decrement associated with channel sparsity vary when acquisition corpus, physical electrode montage and reference are controlled? No assumption that EEG reveals an unobservable emotional state; labels are retrospective self-report.

**Population and units:** previously recorded participants in legally accessed DEAP, DREAMER or AMIGOS, subject to audit; no recruitment. Outer unit = participant, inner unit = trial/session; overlapping windows never cross evaluation boundaries.

**Eligibility gates:** audit exact downloadable files, lawful use, original participant/trial IDs, EEG channels/coordinates/reference, signal processing history, ratings and timing. Cross-corpus estimands require comparable labels and defendable sensors/reference. An incompatible pair is reported as not estimable rather than interpolated. No Muse-equivalence claim.

**Candidate design:** for each eligible corpus evaluate actual full montage and valid 2/4/8-channel subsets (only where enough known electrodes exist); nested group-aware LOSO; preprocessing, scaling, artifact filtering, model selection and calibration on training folds only. Methods: constant majority, regularized log-bandpower linear baseline, capacity-matched compact CNN if warranted, full-montage comparator. Negative controls: fold-internal label permutation and identity-prior diagnostic. Inductive transfer is separate from adaptation using target-domain observations.

**Endpoints (prospective candidates, NOT FROZEN):** the preferred *working* outcome for FACED is the original continuous 0–7 participant self-report valence, with trial-level predictions and participant-level Lin concordance correlation coefficient (CCC), plus MSE as a universally defined error diagnostic. A continuous train-only mean and a train-only standardized ridge are reference models. CCC can be undefined for a participant with constant trial ratings; report full missingness and do not silently exclude participants or issue an unqualified CCC interval. The alternative categorical self-report outcome uses a prespecified label mapping, participant balanced accuracy and Brier; stimulus-target `binary_label` is not participant self-report. Confirmatory uncertainty requires a defensible method accounting for overlapping LOSO training sets. Do not use synthetic score values to select endpoints. Report all montage/corpus cells, seeds, checksums, train folds and software versions.

**Stop decisions:** G0 blocks data downloads without rights. No compatible montage/reference -> no cross-corpus transfer claim. No participant-disjoint split -> no primary outcome. Manuscript result tables remain pending until a reproducible run and independent check.

**Scientific overlap check:** Pandilova et al., *Sensors* 2026, DOI [10.3390/s26175327](https://doi.org/10.3390/s26175327), already test identity confounding and compact montage; the proposed novelty must go beyond a generic leakage-free re-evaluation. Cross-dataset transfer literature and consumer EEG baselines also exist ([2024 review](https://doi.org/10.1016/j.neucom.2024.128354), [2025 comparison](https://doi.org/10.3390/s25237262)).

## Access evidence (2026-10-30)

The [dataset-origin desk audit](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-data-audit.md) identifies DREAMER as access-request restricted, and unresolved current download paths for DEAP and AMIGOS. This metadata review **does not pass G0** or authorize any original data download. Keep P01 #14, #22, #30 open; do not mark the planned cross-corpus factorial study as feasible until an original licensed corpus and montage/annotation compatibility are proven. Use existing public paper metadata and synthetic fixtures for implementation preparation only.

## Candidate open-data fallback, pending protocol freeze

Provider evidence identifies [GAMEEMO v3](https://data.mendeley.com/datasets/b3pn4kwpmn/3), 28 participants and 14-channel EEG plus SAM ratings, and [FACED NEMAR v1.1.4](https://nemar.org/dataset/nm000112?v=v1.1.4), 123 participants, 32-channel BIDS EEG, both with provider-declared CC BY 4.0. These are lawful-first **candidate replacements**, not evaluated corpora. Check actual electrode/reference, self-report alignment, file hashes and permitted derivative reuse before G0. The different game/video induction tasks could invalidate a pooled cross-corpus label mapping; do not force them into a misleading common target. Record a signed M1 choice before starting final held-out analyses.

## FACED source-to-BIDS provenance gate (2026-10-30)

Original authors document **Neuracle NeuSen.W32, reference CPz and ground AFz** (Chen et al., 2023, [DOI](https://doi.org/10.1038/s41597-023-02650-w)). Public derivative BIDS text declares **Biosemi** with undocumented `EEGReference`/`EEGGround`; 32-channel cohorts differ by six recorded names (including `A1/A2` versus `HEOR/HEOL`). [Pinned metadata review](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-faced-provenance-qa.md) verifies the discrepancy but cannot establish the digital reference operator. No automatic mapping or cross-cohort/cross-corpus comparison until authoritative supplemental channel table and source transformations are reconciled. This does **not** freeze M1.

## Acquisition, preprocessing and BIDS conversion paths (2026-10-30)

The [pinned code audit](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-converter-qa.md) separates two processing paths: the original publication's preprocessed EEG (250 Hz, common-average reference and cohort reordering) versus the independent `nemarDatasets/nm000112` BIDS conversion (`read_raw_bdf`, annotation import and `write_raw_bids` without an explicit `set_eeg_reference`). The converter patches corrupt `?V` BDF unit labels in temporary copies as described by its author, a mechanism not yet compared against original raw samples. **Do not pool derived BIDS EEG with the original paper's processed features as if they had identical reference, amplitude or trial layout.** Six cohort-specific electrode identities remain unresolved until S2/S3 or original electrode spreadsheets can be checked. No signal-level evidence or approved M1 freeze.

## Candidate processed-array channel order, not raw montage (2026-10-30)

The [source-pinned read-only preprocessing audit](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-faced-preprocessed-order-qa.md) recovers six *index-level* candidate links from a third-party mirror: T3/T7, T4/T8, T5/P7, T6/P8, A2/HEOR, A1/HEOL. It applies only to the distinct original preprocessed data path that calls `set_eeg_reference('average')` and reorders its output arrays. The separately converted BIDS derivative has not been validated against this path. **These links are not approved aliases** and must not be used for physical electrode equivalence, channel-sparsity estimates, raw/BIDS processing or outcome inference until S2/S3, original code provenance and real signal transformations are verified. M1 remains DRAFT.

## Prospective montage subset QA (2026-10-30)

The [name-level 2/4/8 montage review](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-montage-review-qa.md) can check proposed channel-label sets against two pinned BIDS cohort inventories without EEG data. **Shared names do not imply identical physical positions or reference.** Six cohort-dependent labels and particularly A1/A2 versus HEOR/HEOL require independent S2/S3 verification. No eligible montage or endpoint has been frozen.

## Full NEMAR sidecar census (2026-10-30, metadata only)

A [full 123/123 public text-metadata audit](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-faced-provenance-qa.md) of pinned upstream commit `2577b0bbc089b49e828cd98d80445133634b6d34` finds 55 recordings declared at 250 Hz and 68 at 1000 Hz. The same commit's README and converter narrative claim 31 at 250 Hz and 92 at 1000 Hz. This is a **documentation-versus-BIDS sampling-frequency discrepancy**, not verified signal corruption. All 123 derived JSON sidecars still specify manufacturer Biosemi and unknown EEG reference/ground. Do not train or pool on an assumed acquisition-rate grouping; original `Recording_info.csv`, BDF headers, source-to-BIDS unit/reference provenance and S2/S3 remain validation gates. M1 is **DRAFT**.

## Original Recording_info.csv bridge (2026-10-30)

The [read-only source-rate comparison tool](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-source-recording-qa.md) can compare an **authentic, access-authorized** original FACED `Recording_info.csv` with the 123 publicly audited, source-pinned NEMAR BIDS sample rates without disclosing demographics. The official converter uses source columns `sub`, `Sample_rate`, `Unit`, but warns that `Unit` refers to upstream acquisition files, **not** BDF on-disk amplitude scaling. The actual source CSV was not downloaded, so source-to-BIDS discrepancies remain **unresolved**; do not unfreeze M1 on synthetic fixture checks or numerical count agreement alone.

## Stimulus identity challenge, prospective revision (2026-10-30)

Gerster et al. (bioRxiv preprint 2026, DOI [10.64898/2026.06.12.731889](https://doi.org/10.64898/2026.06.12.731889)) demonstrate a major stimulus-identity confound in FACED classification using target emotion categories. See the [preplanned software controls and study-scope distinction](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-stimulus-confound-qa.md). FACED videos recur between participants, so a **participant-LOSO fold does NOT leave clips unseen**. If a FACED analysis becomes admissible, include a **train-only film-mean self-report baseline** under participant LOSO, an appropriately prespecified jointly participant-and-video-disjoint analysis or independent new-video cohort, and separate all three estimands in figures/tables. A single participant×film test trial cannot yield CCC. For categorical stimulus-assigned labels, leave-film-out may render an emotion class absent from training; report that task as not estimable. The new diagnostic is E0 synthetic-only, not an EEG finding; target choice and inferential design remain **DRAFT**.

## Multi-film joint holdout, still prospective (2026-10-30)

To address the CCC-not-defined limitation of single-film subject×stimulus
intersection tests, the [synthetic blocked-fold QA](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-stimulus-confound-qa.md)
supports externally prespecified **blocks of at least two films** and
holds out a participant and an entire film block together. Other people
watching held-out films, and the held-out person watching other films,
are excluded from model fitting and all train-only transforms.
The held-out participant then contributes multiple independently rated
test films; CCC is computable only if their true ratings vary. A 28-film,
seven-block-of-four example is **illustrative, not an approved or frozen
choice**. Block assignment cannot use emotion labels or outcome-driven
test scores, must document missing participant–film cells and ensure
adequate training representation. All joint folds share training people
and films, so descriptive fold MSE/CCC does not yield population
confidence intervals without a separately justified inference method.
The participant-only LOSO design estimates a different outcome and is
retained as a separate analysis. **M1 remains DRAFT**.

## Source-recording rate alignment correction (2026-10-30)

The earlier offline `Recording_info.csv` comparison utility had an
incorrect per-subject assumption despite correct overall counts.
At pinned NEMAR commit `2577b0b...`, 250-Hz BIDS metadata belong to
`sub-004`, `sub-005` and `sub-008` through `sub-060`;
`sub-006` and `sub-007` are **1000 Hz**. The
[source-rate reconciliation QA](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-source-recording-qa.md)
and regression tests now reflect these record-level facts. The original
source CSV has still not been read, and neither source acquisition rates
nor real signal calibration are certified.

## Unlinked FACED BIDS event markers and trial QC (2026-10-30)

A [targeted public `events.tsv` inspection](https://github.com/MatPomGit/arc-affective/blob/main/reports/P01-event-linkage-qa.md)
found 1171 and 1445 unlinked technical events in `sub-059` and
`sub-060` respectively, despite 28 video-linked, rated trials in each.
The event-to-stimulus validator now triggers **manual review** when such
unlinked markers exceed an operational alert threshold. This flag is
**not** evidence of EEG corruption, not a prospectively chosen exclusion
criterion, and must not silently delete participants or trials. Inspect
original `evt.bdf` and conversion logs before interpreting trigger
timing or accepting signal-label synchronization. M1 remains DRAFT.
