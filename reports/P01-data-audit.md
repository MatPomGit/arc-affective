# P01 data provenance and acquisition feasibility: desk audit

Version 0.1.0 · 2026-10-30 · **metadata-level review only**. This is **not** evidence that the author has lawful access to raw files, has signed agreements or has executed a corpus-specific loader. Supports issues #2, #14, #22 and #30.

## Source review and decision matrix

| Dataset | Publisher/author-origin evidence | Dataset summary from published record | Current access evidence | Decision for P01 |
| --- | --- | --- | --- | --- |
| **DEAP** | [Koelstra et al., IEEE TAC 2012](https://doi.org/10.1109/T-AFFC.2011.15); [Queen Mary original dataset location](https://www.eecs.qmul.ac.uk/mmv/datasets/deap/) | 32 original participants, 40 affect-eliciting music clips; EEG and other physiological recordings; 22 participants have associated facial video | Official location and download endpoint timed out or returned an error in the 2026-10-30 check. The [SciCrunch RRID record](https://scicrunch.org/resolver/RRID%3ASCR_001586) labels the service unavailable; the original [DEAP agreement URL](https://eecs.qmul.ac.uk/mmv/datasets/deap/doc/eula.pdf) redirects to a general institutional page in this check. Historical signed-user agreement and restrictions on redistribution are documented in external indexed copies, but **current contract terms must be obtained from the rights holder**. | **BLOCKED: rights and original file access unverified**. Do not download mirrors or presume institutional rights. Ask original custodians for a working application route. |
| **DREAMER** | [Katsigiannis and Ramzan, original Zenodo record](https://zenodo.org/records/546113); [IEEE JBHI DOI](https://doi.org/10.1109/JBHI.2017.2688239) | 23 participants, EEG + ECG; self-reported valence, arousal and dominance after audiovisual stimuli; Emotiv EPOC used for EEG | The Zenodo record is explicitly **Restricted**, offers an access-request form, and requests contact, institution, position and research purpose. Its publicly viewable record is not a license to fetch contents. | **BLOCKED pending an approved individual Zenodo request**, documented legal terms and actual file checksum. |
| **AMIGOS** | [Patras laboratory author dataset index](https://ipatras.github.io/code-and-datasets/); [Miranda-Correa et al., IEEE TAC](https://doi.org/10.1109/TAFFC.2018.2884461) | Existing study with individual/group social settings, EEG/ECG/GSR and valence/arousal; research descriptions report 40 participants, with different completion for long-video trials | Author's dataset index is online, but its linked original Queen Mary dataset site timed out during this check. Data-download permissions and distribution of any EEG/video paired files are **not verified**. | **BLOCKED: actual downloadable modalities and dataset-specific conditions unknown**. Contact rights holder before using a substitute mirror. |

## Scientific compatibility and inclusion gate

1. Collect from the authorized raw release, locally only: signed/access decision, file hashes, official electrode names/3-D positions, physical reference and any rereferencing, sampling rate before and after preprocessing, bad-channel policy, trial IDs, participant IDs and native rating scale with meaning of neutral/zero. These details are **not** proved by the abstract alone.
2. DEAP recordings come from a different acquisition and reference system than Emotiv-based DREAMER; AMIGOS also uses its own protocol and modalities. Even if numeric names match, **channel labels do not imply identical electrode location or reference**. A four-channel subset is not experimentally equivalent to Muse S Athena.
3. Candidate native rating scales and temporal aggregation differ across source studies. Before any cross-corpus test, freeze an explicitly justified common target and a mapping independent of held-out ratings. A transfer cell with incompatible annotation semantics is **not estimable**, rather than a failed/zero-accuracy trial.
4. Use subject-disjoint outer folds; preserve sessions/trials, fit imputation/scalers/models/calibration on training subjects only; never mix windows from one participant across train/test. Report subject-level paired effects and uncertainty. No held-out label-derived binarization thresholds.
5. Before accepting scientific novelty, reproduce an appropriate recent subject-identity-confounding baseline: [Pandilova et al. 2026](https://doi.org/10.3390/s26175327). The P01 claim must rest on the additional montage-reference/corpus compatibility experiment, not on eliminating obvious participant leakage alone.

## Evidence boundary and next permitted work

- **Verified:** publicly visible Zenodo access status, primary research paper metadata, author dataset list, and observed failures of specific website endpoints on the audit date.
- **Not verified:** whether the user's personal or institutional dataset grants already exist, availability at another time, local file content, anonymization terms, exact input schemas, montage harmonization, numerical performance or human-subject ethics clearance.
- **Next:** obtain rights-holder replies/approved access and local cryptographic manifests; then implement fixture-only parser unit tests in #30. If access to at least one legally usable corpus cannot be established, P01 cannot pass G0 as currently formulated.

## Source observations

Audit date 2026-10-30. External access was a website check, not access through an authenticated university session. The DEAP and AMIGOS locations were inaccessible in this session, but this transient observation **does not prove permanent shutdown**. The SciCrunch status flag is third-party metadata rather than a rights-holder announcement. No original dataset, participant video, credentials or raw EEG was downloaded or copied into Git.
