# Research portfolio and claim boundaries

Each track is mapped to AEEiTK, ITiT or informatics in [the discipline map](discipline-map.md). Eight distinct contributions share a timestamped event schema and evaluation harness. Each manuscript needs one independent novelty claim, one frozen primary endpoint and a reusable result bundle. Before publication run a recent structured literature review and plagiarism/overlap audit; topic titles below are *proposals*, not novelty guarantees.

| Paper | Main question | Protected contribution (not reused as another paper's main result) | Evidence tier |
|---|---|---|---|
| P01 | Do sparse EEG representations survive dataset/montage shift? | Subject/corpus-disjoint transfer under channel sparsity | External datasets |
| P02 | Can calibrated fusion abstain with absent/corrupt modalities? | Reliability masks, calibrated confidence, modality dropout | External synchronized data |
| P03 | Can an individual's workload predictor track day-to-day drift? | Sequential drift detection and label-efficient recalibration | N=1 repeated sessions |
| P04 | Can facial video be processed without retaining identifiable frames? | End-to-end privacy, resource, utility frontier | External video / webcam |
| P05 | How well do motion-kinematic features reflect task load vs movement? | Movement-confound-controlled workload proxy | Leap N=1–3 |
| P06 | Does uncertainty-gated feedback improve adaptive interaction? | Safety-gated policy evaluated against fixed/random policies | N-of-1 cross-over |
| P07 | How can multimodal intent drive a robot without bypassing safeguards? | Deterministic safety governor and intent-conditioned HRI | Simulator, N=1–3 |
| P08 | What edge architecture preserves deadlines under sensor faults? | Scheduling/backpressure/fallback mechanisms and p95/p99 performance | Benchmarks |

**Issues:** [P01 #5](https://github.com/MatPomGit/arc-affective/issues/5), [P02 #6](https://github.com/MatPomGit/arc-affective/issues/6), [P03 #7](https://github.com/MatPomGit/arc-affective/issues/7), [P04 #8](https://github.com/MatPomGit/arc-affective/issues/8), [P05 #9](https://github.com/MatPomGit/arc-affective/issues/9), [P06 #10](https://github.com/MatPomGit/arc-affective/issues/10), [P07 #11](https://github.com/MatPomGit/arc-affective/issues/11), [P08 #12](https://github.com/MatPomGit/arc-affective/issues/12).

**Evidence tiers:** E0 simulation/unit tests; E1 public dataset held-out tests; E2 repeatable N-of-1 engineering study; E3 independent small-sample replication (optional, never required >3). Gate to submit requires a distinct delta vs strong contemporary baselines, reproducible protocol, meaningful uncertainty intervals, and limitations clearly stated.

**Foundational dependency path:** P08 event/benchmark infrastructure and P01/P04 public-data methods first; P02 thereafter; P03/P05 with devices; P06/P07 on top of tested inference and fallbacks. Publication order can differ from implementation order.

**Human participant ceiling:** own prospective experimental sessions N <= 3 university staff; publicly released datasets may have larger historical cohorts. Do not pool public datasets and own N=1 into unqualified population claims.