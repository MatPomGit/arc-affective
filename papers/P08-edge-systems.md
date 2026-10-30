# P08 — Deadline-Aware Multimodal Affective Inference on Heterogeneous Edge Nodes

**Discipline:** embedded systems, real-time scheduling, computing architectures. **Authors/participants:** up to 3 authors; prospective participants N<=3 (default N=0 or N=1).

## Research question
What workload-aware scheduling policy achieves reliable p95/p99 deadlines during sensor faults on desktop and Raspberry Pi class devices?

## Distinct technical contribution
Reproducible scheduling/backpressure/fallback policies for asynchronous multimodal stream quality with deadline-aware performance.

## Data and feasible instrumentation
Synthetic replay and licensed public datasets, no prospective participants; optional local webcam for end-to-end real stream. Existing Windows workstation and Raspberry Pi 5; GPU optional.

## Experimental design and baselines
Version timestamped event streams; test FIFO, latest-frame, bounded queue, quality-aware drop, CPU fallback. Controlled CPU load/dropout/reconnect; report hardware versions, wall power only if measurable.

## Primary evaluation metrics
p50/p95/p99 end-to-end latency, deadline-miss %, lost events, throughput, CPU/RAM, energy optional, model quality under dropped samples.

## Threats to validity
Mock timing cannot establish real camera/EEG latency; hardware-specific results may not transfer.

## Go/no-go publication gate
Real-clock measurements on at least one physical node, reproducible profiles and non-fabricated fault injection; no affected-state accuracy claim without validated benchmark.

## Agent-sized implementation steps (one JRA each)
- [ ] 1. Implement monotonic timing, manifests and deterministic replay.
- [ ] 2. Benchmark bounded queues and fault handling on one real node.
- [ ] 3. Replicate with second existing node and CPU fallback if available.
- [ ] 4. Quantify deadline/utility trade-off; write P08.

## Status
**PLANNED — no measurements, experiments or publication claims completed.** Follow [methods](../docs/methodology.md), [privacy](../docs/governance.md), [hardware limits](../docs/hardware.md), and [portfolio boundaries](../docs/portfolio.md).


## Manuscript work in progress (2026-10-30)
A substantive [IEEEtran LaTeX draft](https://github.com/MatPomGit/arc-affective/blob/main/manuscripts/P08/main.tex) specifies real-clock event semantics, policy comparators, fault matrix, goodput and p99 reporting. The [candidate experiment protocol](https://github.com/MatPomGit/arc-affective/blob/main/papers/P08-protocol.md) remains **unfrozen** pending device capacity and M0 novelty review. The listed scheduling literature already solves several deadline-aware problems, so measured quality/freshness under modality loss must supply any independently defended contribution. No physical benchmark or system-performance result has been collected.
