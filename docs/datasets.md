# Candidate dataset registry — access must be audited

| Dataset | Relevant modalities | Use | Access risk / audit |
|---|---|---|---|
| DEAP | EEG + physiological; facial videos under separate access conditions | P01, potential P02 | Official non-commercial/request conditions; inspect subject IDs and video rights |
| DREAMER | EEG + ECG, emotion self-assessment | P01 | Zenodo record is access-restricted; obtain permission, do not scrape mirrors |
| AMIGOS | EEG/ECG/GSR; face video reported in paper | P01/P02 conditional | Confirm which synchronized video and raw data actually distributed and licence |
| MAHNOB-HCI | EEG, gaze, physiological, video | P02 conditional | Access presently uncertain; do not design a mandatory dependency |
| Aff-Wild2 | Face video, frame-level valence/arousal/AU annotations | P04 | Request dataset access; verify redistributability and splits |
| AFEW-VA | Facial video with affect annotations | P04 alternative | Verify current availability/terms; external evaluation only |

Sources: https://www.eecs.qmul.ac.uk/mmv/datasets/deap/ ; https://zenodo.org/records/546113 ; https://ipatras.github.io/code-and-datasets/ ; https://ibug.doc.ic.ac.uk/resources/aff-wild2/ ; https://ibug.doc.ic.ac.uk/resources/afew-va-database/

## Datasets are NOT committed

Maintain private `data/registry.local.json` with `name, version, citation, access_date, licence, approved_use, download_hash, subjects, sessions, labels, signal_channels, sample_rates, timestamps, exclusions`. Version analysis split definitions in Git only if they contain no personal identifiers.

Each paper must demonstrate: accessible legally obtained original data; modalities actually released, compatible synchronized ground truth, subject-disjoint splits, preprocessing exclusively fitted on train, test-independent hyperparameter search, no per-window subject leakage, bootstrapped uncertainty at **subject or session level** (not correlated windows). Dataset identity is a possible confound; cross-dataset transfer claims require equivalent labels and explicit harmonization.

A dataset named in a plan is only a *candidate*. If its rights, content or timing do not fit, switch to an audited dataset and update the preregistered protocol before any final testing.