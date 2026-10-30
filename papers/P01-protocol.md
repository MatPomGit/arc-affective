# P01 — prospective analysis plan, candidate v0.1.0 (2026-10-30)

**Status: DRAFT, NOT preregistered or frozen.** This is the decision record to be finalized at issue #22 after rights/metadata audit #14 and #2. Sources: [manuscript](https://github.com/MatPomGit/arc-affective/blob/main/manuscripts/P01/main.tex), [methods](../docs/methodology.md).

**Question:** Does the participant-held-out decrement associated with channel sparsity vary when acquisition corpus, physical electrode montage and reference are controlled? No assumption that EEG reveals an unobservable emotional state; labels are retrospective self-report.

**Population and units:** previously recorded participants in legally accessed DEAP, DREAMER or AMIGOS, subject to audit; no recruitment. Outer unit = participant, inner unit = trial/session; overlapping windows never cross evaluation boundaries.

**Eligibility gates:** audit exact downloadable files, lawful use, original participant/trial IDs, EEG channels/coordinates/reference, signal processing history, ratings and timing. Cross-corpus estimands require comparable labels and defendable sensors/reference. An incompatible pair is reported as not estimable rather than interpolated. No Muse-equivalence claim.

**Candidate design:** for each eligible corpus evaluate actual full montage and valid 2/4/8-channel subsets (only where enough known electrodes exist); nested group-aware LOSO; preprocessing, scaling, artifact filtering, model selection and calibration on training folds only. Methods: constant majority, regularized log-bandpower linear baseline, capacity-matched compact CNN if warranted, full-montage comparator. Negative controls: fold-internal label permutation and identity-prior diagnostic. Inductive transfer is separate from adaptation using target-domain observations.

**Endpoints (candidate before freeze):** participant-level balanced accuracy (primary) and Brier calibration; paired full-minus-sparse difference with participant-clustered uncertainty. Report AUROC, macro-F1, ECE as secondary, and all attempted montage/corpus cells including exclusions. Binary thresholds must be declared before held-out testing and not derived from test labels. Record seeds, dataset checksums, training folds and software versions. No claim of improvement without a strong comparator and intervals.

**Stop decisions:** G0 blocks data downloads without rights. No compatible montage/reference -> no cross-corpus transfer claim. No participant-disjoint split -> no primary outcome. Manuscript result tables remain pending until a reproducible run and independent check.

**Scientific overlap check:** Pandilova et al., *Sensors* 2026, DOI [10.3390/s26175327](https://doi.org/10.3390/s26175327), already test identity confounding and compact montage; the proposed novelty must go beyond a generic leakage-free re-evaluation. Cross-dataset transfer literature and consumer EEG baselines also exist ([2024 review](https://doi.org/10.1016/j.neucom.2024.128354), [2025 comparison](https://doi.org/10.3390/s25237262)).
