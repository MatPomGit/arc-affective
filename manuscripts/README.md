# ARC Affective — source manuscripts (working drafts)

Version 0.1.0 · 2026-10-30. Manuscript source is English, IEEEtran LaTeX, with independent section files and a paper-specific bibliography. **These are working scientific drafts**, not completed journal submissions or empirical studies. Placeholder sections explicitly mark absent evidence.

- [P01](P01/main.tex): low-channel EEG, montage/reference and corpus shift. Data rights, EEG preprocessing and grouped baselines still pending; no EEG recording from the unverified Muse research interface.
- [P08](P08/main.tex): fault-aware edge scheduling and tail-latency/coverage measurement. Physical benchmark, proposed scheduler and real CPU fallback not yet measured/implemented.

Build locally from each paper directory with `pdflatex -halt-on-error main.tex && bibtex main && pdflatex -halt-on-error main.tex && pdflatex -halt-on-error main.tex` (TeX Live with IEEEtran needed). Do not commit build intermediates or completed-looking figures with invented data. Before M6: journal template/venue check, full reference and novelty audit, methods freeze and independent experimental verification.

Tracked gates: P01 [M0 #14](https://github.com/MatPomGit/arc-affective/issues/14), [M1 #22](https://github.com/MatPomGit/arc-affective/issues/22), [M6 #66](https://github.com/MatPomGit/arc-affective/issues/66); P08 [M0 #21](https://github.com/MatPomGit/arc-affective/issues/21), [M1 #29](https://github.com/MatPomGit/arc-affective/issues/29), [M6 #73](https://github.com/MatPomGit/arc-affective/issues/73).
