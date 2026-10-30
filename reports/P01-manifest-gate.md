# P01 provenance manifest gate: implementation note

Version 0.1.0, 2026-10-30. Scope: #30, #2. This **does not** establish dataset rights, signal compatibility or a completed dataset loader.

A Python standard-library validator now accepts a private local JSON manifest with required fields `dataset`, `version`, `license`, `approved_use`, `files` (relative path and SHA-256), `sampling_hz`, `reference`, `electrodes` and `rating_scale`. Run:

```bash
PYTHONPATH=src python -m arc_affective.p01_registry data/registry.local.json --root data/dataset-local --verify-hashes
python -m unittest discover -s tests -p test_p01_registry.py -v
```

The manifest is local and excluded from Git under `data/`. Permission must be established by the researcher; a Boolean flag is a human declaration, **not** independently validated legal proof. The code uses an explicit small licence vocabulary to fail closed on unreviewed licence strings; this is not a general-purpose SPDX parser. Optional hash verification is local-only, with stream hashing and path traversal protection; **without** `--verify-hashes`, the output states zero checked files. File contents and participant identifiers are never printed or uploaded.

The validator does **not** parse EEG, validate device channels/coordinate systems, harmonize montage references, verify rating semantics or assert corpus transfer eligibility. It returns `montage_equivalence_established: false` and `cross_corpus_eligibility: unassessed` until independent scientific QC exists. All tests are synthetic fixtures with no actual EEG.
